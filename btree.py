import time
import atexit
import random
import window
import vision
import keyboard
import py_trees
import threading
import numpy as np
import messagequeue

KEY_MEAN = 0.05
KEY_STD = KEY_MEAN * 0.005


class BehaviourWithBlackboard(py_trees.behaviour.Behaviour):
    def __init__(self):
        super().__init__()
        self.bb = self.attach_blackboard_client("Blackboard")


class Animation(BehaviourWithBlackboard):
    def __init__(self, seq, cd=0.0):
        super().__init__()
        self.seq = seq
        self.cd = cd
        self.last_use = 0.0
        self.bb.register_key("/animate_end", py_trees.common.Access.WRITE)

    def initialise(self):
        self.bb.set("/animate_end", 0.0, overwrite=False)

    def animate(self):
        raise NotImplementedError

    def update(self):
        # 这里只判断CD 不判断动画时间
        # 因为可能某些技能具有"强制"属性
        if time.time() - self.last_use < self.cd:
            return py_trees.common.Status.FAILURE
        else:
            self.last_use = self.animate()
            self.bb.set("/animate_end", self.last_use + self.seq)
            return py_trees.common.Status.SUCCESS


class WaitForAnimationEnd(BehaviourWithBlackboard):
    def __init__(self):
        super().__init__()
        self.bb.register_key("/animate_end", py_trees.common.Access.READ)

    def update(self):
        if self.bb.exists("/animate_end") and time.time() <= self.bb.get(
            "/animate_end"
        ):
            return py_trees.common.Status.RUNNING
        else:
            return py_trees.common.Status.SUCCESS


class Skill(Animation):
    def __init__(self, cd, seq, key):
        super().__init__(seq, cd)
        self.key = key
        self.skey = keyboard.key_to_scan(key)

    def animate(self):
        delay = random.normalvariate(KEY_MEAN, KEY_STD)
        use_t = messagequeue.push(lambda: keyboard.press_key(self.skey))
        messagequeue.push(lambda: keyboard.release_key(self.skey), delay)
        return use_t

    def update(self):
        stat = super().update()
        if stat == py_trees.common.Status.SUCCESS:
            self.logger.info("{}".format(self.key))
        return stat


class DoubleJumpSkill(Skill):
    def __init__(self, cd, seq, key):
        super().__init__(cd, seq, key)
        self.jump = keyboard.key_to_scan("LMENU")

    def animate(self):
        delay = np.random.normal(KEY_MEAN, KEY_STD, size=(5,))
        delay = np.cumsum(delay)
        use_t = messagequeue.push(lambda: keyboard.press_key(self.jump))
        messagequeue.push(lambda: keyboard.release_key(self.jump), delay=delay[0])
        messagequeue.push(lambda: keyboard.press_key(self.jump), delay=delay[1])
        messagequeue.push(lambda: keyboard.release_key(self.jump), delay=delay[2])
        messagequeue.push(lambda: keyboard.press_key(self.skey), delay=delay[3])
        messagequeue.push(lambda: keyboard.release_key(self.skey), delay=delay[4])
        return use_t


class DataGather(BehaviourWithBlackboard):
    def __init__(self):
        super().__init__()
        self.game_active = False
        self.player_pos = None
        self.rune_pos = None
        self.map_pos = None

        self.gather = threading.Thread(target=self.run_thread, daemon=True)
        self.stop_event = threading.Event()
        self.data_lock = threading.Lock()
        atexit.register(self.stop_thread)
        self.gather.start()

    def set_value(self, name, value):
        if value is None:
            return

        self.bb.register_key(name, py_trees.common.Access.WRITE)
        self.bb.set(name, value)

    def update(self):
        with self.data_lock:
            if not self.game_active:
                return py_trees.common.Status.FAILURE
            self.set_value("/data/player", self.player_pos)
            self.set_value("/data/rune_pos", self.rune_pos)
            self.set_value("/data/map_pos", self.map_pos)
        return py_trees.common.Status.SUCCESS

    def run_thread(self):
        while not self.stop_event.is_set():
            # window
            hwnd = window.find_window("MapleStory")
            if hwnd == 0:
                continue

            with self.data_lock:
                if window.active_window() != hwnd:
                    self.game_active = False
                    continue
                else:
                    self.game_active = True

                image = window.capture(hwnd)
                if image is None:
                    continue

                self.map_pos = vision.minimap_detect(image, 0.9, self.map_pos)
                if self.map_pos is None:
                    continue

                minimap = vision.split_image(image, self.map_pos)
                self.player_pos = vision.player_detect(minimap, 0.9, self.player_pos)
                self.rune_pos = vision.rune_detect(minimap)
            time.sleep(0.05)

    def stop_thread(self):
        self.stop_event.set()
        self.gather.join()


class AtTarget(BehaviourWithBlackboard):
    def __init__(self, tx=2, ty=2):
        super().__init__()
        self.tx = tx
        self.ty = ty

        self.bb.register_key("/data/player", py_trees.common.Access.READ)
        self.bb.register_key("/move/target", py_trees.common.Access.READ)

    def update(self):
        player = self.bb.get("/data/player")
        target = self.bb.get("/move/target")
        dx = abs(player[0] - target[0])
        dy = abs(player[1] - target[1])
        if dx <= self.tx and dy <= self.ty:
            self.logger.info("AtTarget {} {}".format(dx, dy))
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class TurnToTarget(Animation):
    def __init__(self):
        super().__init__(0.2)
        self.left = keyboard.key_to_scan("LEFT")
        self.right = keyboard.key_to_scan("RIGHT")
        self.bb.register_key("/data/player", py_trees.common.Access.READ)
        self.bb.register_key("/move/target", py_trees.common.Access.READ)

    def animate(self):
        player = self.bb.get("/data/player")
        target = self.bb.get("/move/target")

        if player[0] - target[0] < 0:
            key = self.right
            self.logger.info("Turn Right")
        else:
            key = self.left
            self.logger.info("Turn Left")

        delay = random.normalvariate(KEY_MEAN, KEY_STD)
        use_t = messagequeue.push(lambda: keyboard.press_key(key))
        messagequeue.push(lambda: keyboard.release_key(key), delay)
        return use_t


class GetTargetFarm(BehaviourWithBlackboard):
    def __init__(self):
        super().__init__()
        self.bb.register_key("/data/player", py_trees.common.Access.READ)
        self.bb.register_key("/move/target", py_trees.common.Access.WRITE)
        self.bb.register_key("/data/map_pos", py_trees.common.Access.READ)

    def update(self):
        player = self.bb.get("/data/player")
        map_pos = self.bb.get("/data/map_pos")
        map_width = map_pos[2] - map_pos[0]

        d_left = player[0]
        d_right = map_width - d_left

        if d_left > d_right:
            target = [0, 0, 0, 0]
        else:
            target = [map_width, 0, 0, 0]
        self.bb.set("/move/target", target)
        self.logger.info("GetTarget {}".format(target))
        return py_trees.common.Status.SUCCESS

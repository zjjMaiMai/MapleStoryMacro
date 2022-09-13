import time
import random
import typing
import keyboard

FINISHED = 0
FAILED = 1
RUNNING = 2


class MoveControl:
    def __init__(self, tiles):
        self.tiles = tiles
        self.target = None

        self.last_pos = None
        self.stuck_step = 0

        self.left_scan = keyboard.key_to_scan("LEFT")
        self.right_scan = keyboard.key_to_scan("RIGHT")
        self.up_scan = keyboard.key_to_scan("V")
        self.alt_scan = keyboard.key_to_scan("LMENU")
        self.down_scan = keyboard.key_to_scan("DOWN")

        self.left_down = False
        self.right_down = False

    def distance(self, x, y):
        return abs(x[0] - y[0]) + abs(x[1] - y[1])

    def finished(self):
        print("finish")
        self.target = None
        return FINISHED

    def update(self, pos):
        if self.target is None:
            return self.finished()

        if self.last_pos is not None:
            if pos == self.last_pos:
                if self.stuck_step > 5:
                    print("stuck")
                    return FAILED
                self.stuck_step += 1
            else:
                self.stuck_step = 0

        MAX_DIFF = 2
        self.last_pos = pos
        dx = self.target[0] - pos[0]
        dy = self.target[1] - pos[1]
        if abs(dx) < MAX_DIFF and abs(dy) < MAX_DIFF:
            return self.finished()

        if dx > MAX_DIFF:
            self.move_right(abs(dx) > 15)
        elif dx < -MAX_DIFF:
            self.move_left(abs(dx) > 15)
        elif dy > MAX_DIFF:
            self.move_down()
        elif dy < -MAX_DIFF:
            self.move_up()

        return RUNNING

    def move_to(self, pos):
        self.stuck_step = 0
        self.last_pos = None
        self.target = pos

    def double_jump(self):
        keyboard.press_key(self.alt_scan)
        time.sleep(random.normalvariate(0.08, 0.01))
        keyboard.release_key(self.alt_scan)
        time.sleep(random.normalvariate(0.07, 0.01))
        keyboard.press_key(self.alt_scan)
        time.sleep(random.normalvariate(0.08, 0.01))
        keyboard.release_key(self.alt_scan)
        time.sleep(random.normalvariate(0.08, 0.01))

    def release_left(self):
        if self.left_down:
            keyboard.release_key(self.left_scan)
            self.left_down = False

    def release_right(self):
        if self.right_down:
            keyboard.release_key(self.right_scan)
            self.right_down = False

    def move_left(self, double_jump=False):
        self.release_right()
        if not self.left_down:
            keyboard.press_key(self.left_scan)
            self.left_down = True

        if double_jump:
            self.double_jump()
        return

    def move_right(self, double_jump=False):
        self.release_left()
        if not self.right_down:
            keyboard.press_key(self.right_scan)
            self.right_down = True

        if double_jump:
            self.double_jump()
        return

    def move_up(self):
        self.release_left()
        self.release_right()

        keyboard.press_key(self.up_scan)
        time.sleep(random.normalvariate(0.08, 0.01))
        keyboard.release_key(self.up_scan)
        time.sleep(random.normalvariate(0.5, 0.1))

    def move_down(self):
        self.release_left()
        self.release_right()

        keyboard.press_key(self.down_scan)
        time.sleep(random.normalvariate(0.08, 0.01))
        keyboard.press_key(self.alt_scan)
        time.sleep(random.normalvariate(0.08, 0.01))
        keyboard.release_key(self.alt_scan)
        time.sleep(random.normalvariate(0.08, 0.01))
        keyboard.release_key(self.down_scan)
        time.sleep(random.normalvariate(0.08, 0.01))


class Action:
    """
    https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
    """

    def __init__(self, name, cd, vkey, olevel, duration=1.0):
        self.name = name
        self.cd = cd
        self.vkey = keyboard.key_to_scan(vkey)
        self.olevel = olevel
        self.duration = duration
        self.last_use = 0.0
        self.is_casting = False

    def is_ready(self):
        return not self.is_casting and time.time() - self.last_use > self.cd

    def press(self):
        keyboard.press_key(self.vkey)
        time.sleep(random.normalvariate(0.1, 0.01))
        keyboard.release_key(self.vkey)

    def update(self):
        self.is_casting = True
        print(self.name)
        self.last_use = time.time()
        self.press()
        animation_time = self.duration - (time.time() - self.last_use)
        if animation_time > 0:
            time.sleep(animation_time)
        self.is_casting = False


class DualJumpAttack(Action):
    """
    跳跃攻击至少需要1.1s
    """

    def __init__(self, name, cd, vkey, olevel, duration):
        super().__init__(name, cd, vkey, olevel, duration)
        self.alt = keyboard.key_to_scan("LMENU")

    def press(self):
        keyboard.press_key(self.alt)
        time.sleep(random.normalvariate(0.07, 0.003))
        keyboard.release_key(self.alt)
        time.sleep(random.normalvariate(0.07, 0.003))
        keyboard.press_key(self.alt)
        time.sleep(random.normalvariate(0.07, 0.003))
        keyboard.release_key(self.alt)
        time.sleep(random.normalvariate(0.07, 0.003))

        keyboard.press_key(self.vkey)
        time.sleep(random.normalvariate(0.07, 0.003))
        keyboard.release_key(self.vkey)


class Actor:
    def __init__(self, actions: typing.List[Action]):
        self.actions = sorted(actions, key=lambda x: x.olevel, reverse=True)

    def update(self):
        for a in self.actions:
            if not a.is_ready():
                continue
            a.update()
            break
        return


class MyActor(Actor):
    def __init__(self, move_step):
        actions = [
            Action("5", cd=125.0, vkey="5", olevel=10, duration=0.5),
            Action("1", cd=91.0, vkey="1", olevel=10),
            Action("2", cd=121.0, vkey="2", olevel=10),
            Action("3", cd=181.0, vkey="3", olevel=10),
            # Action("2", cd=125.0, vkey="2", olevel=10),
            # Action("1", cd=95.0, vkey="1", olevel=10),
            # MoveAround("Move", move_time, olevel=9, duration=0.3),
            DualJumpAttack("JumpT", cd=61.0, vkey="T", olevel=9, duration=1.0),
            DualJumpAttack("JumpE", cd=10.5, vkey="E", olevel=8, duration=1.4),
            DualJumpAttack("JumpR", cd=15.1, vkey="R", olevel=7, duration=1.0),
            DualJumpAttack("JumpQ", cd=0.0, vkey="Q", olevel=0, duration=1.0),
        ]
        super().__init__(actions)

        self.move_step = move_step
        self.step = 0
        self.hammer_count = 0

        self.left = keyboard.key_to_scan("LEFT")
        self.right = keyboard.key_to_scan("RIGHT")
        self.to_right = True

    def reset(self):
        self.step = 0
        self.hammer_count = 0
        self.to_right = True

    def update(self):
        for a in self.actions:
            if not a.is_ready():
                continue
            if a.name == "JumpT" and self.hammer_count < 6:
                continue

            a.update()
            if isinstance(a, DualJumpAttack):
                self.step += 1

            if self.step >= (self.move_step[1] if self.to_right else self.move_step[0]):
                keyboard.press_key(self.left if self.to_right else self.right)
                time.sleep(random.normalvariate(0.1, 0.01))
                keyboard.release_key(self.left if self.to_right else self.right)
                time.sleep(random.normalvariate(0.1, 0.01))
                self.to_right = not self.to_right
                self.step = 0

            if a.name == "JumpQ":
                self.hammer_count = min(self.hammer_count + 1, 6)
            elif a.name == "JumpT":
                self.hammer_count = 0

            break
        return
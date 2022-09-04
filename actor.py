import time
import random
import typing
import keyboard


class Action:
    """
    https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
    """

    def __init__(self, name, cd, vkey, olevel, duration):
        self.name = name
        self.cd = cd
        self.vkey = vkey
        self.olevel = olevel
        self.duration = duration
        self.dkey = keyboard.virtual_key_to_scan_code(vkey)
        self.last_use = 0.0
        self.is_casting = False

    def is_ready(self):
        return not self.is_casting and time.time() - self.last_use > self.cd

    def press(self):
        keyboard.press_key(self.dkey)
        time.sleep(random.normalvariate(0.1, 0.01))
        keyboard.release_key(self.dkey)

    def use(self):
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
        self.alt = keyboard.virtual_key_to_scan_code(0xA4)

    def press(self):
        keyboard.press_key(self.alt)
        time.sleep(random.normalvariate(0.08, 0.01))
        keyboard.release_key(self.alt)
        time.sleep(random.normalvariate(0.07, 0.01))
        keyboard.press_key(self.alt)
        time.sleep(random.normalvariate(0.08, 0.01))
        keyboard.release_key(self.alt)
        time.sleep(random.normalvariate(0.08, 0.01))

        keyboard.press_key(self.dkey)
        time.sleep(random.normalvariate(0.1, 0.01))
        keyboard.release_key(self.dkey)


class MoveAround(Action):
    def __init__(self, name, cd, left_vkey, right_vkey, olevel, duration):
        super().__init__(name, cd, left_vkey, olevel, duration)
        self.left = keyboard.virtual_key_to_scan_code(left_vkey)
        self.right = keyboard.virtual_key_to_scan_code(right_vkey)
        self.to_right = False

    def press(self):
        keyboard.release_key(self.right if self.to_right else self.left)
        time.sleep(random.normalvariate(0.2, 0.01))
        keyboard.press_key(self.left if self.to_right else self.right)
        self.to_right = not self.to_right


class Actor:
    def __init__(self, actions: typing.List[Action]):
        self.actions = sorted(actions, key=lambda x: x.olevel, reverse=True)

    def use(self):
        for a in self.actions:
            if not a.is_ready():
                continue
            a.use()
            break
        return


class MyActor(Actor):
    def __init__(self, move_time):
        VK = keyboard.KEY_MAP
        actions = [
            Action("BUFF_5", cd=205.0, vkey=VK["5"], olevel=13, duration=2.0),
            Action("BUFF_F4", cd=95.0, vkey=VK["f4"], olevel=12, duration=1.3),
            MoveAround("Around", move_time, VK["left"], VK["right"], olevel=10, duration=0.5),
            DualJumpAttack("JumpR", cd=10.5, vkey=VK["r"], olevel=9, duration=1.4),
            Action("F3", cd=65.0, vkey=VK["f3"], olevel=8, duration=0.8),
            Action("F1", cd=15.0, vkey=VK["f1"], olevel=7, duration=0.8),
            DualJumpAttack("JumpQ", cd=0.0, vkey=VK["q"], olevel=0, duration=1.1),
        ]
        super().__init__(actions)
        self.hammer_count = 0

    def use(self):
        for a in self.actions:
            if not a.is_ready():
                continue
            if a.name == "F3" and self.hammer_count < 6:
                continue

            a.use()

            if a.name == "JumpQ":
                self.hammer_count = min(self.hammer_count + 1, 6)
            elif a.name == "F3":
                self.hammer_count = 0

            break
        return
import time
import random
import typing
import keyboard


class Action:
    """
    https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
    """

    def __init__(self, name, cd, vkey, olevel, duration=1.0):
        self.name = name
        self.cd = cd
        self.vkey = keyboard.virtual_key_to_scan_code(vkey)
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
        self.alt = keyboard.virtual_key_to_scan_code("alt")

    def press(self):
        keyboard.press_key(self.alt)
        time.sleep(random.normalvariate(0.08, 0.01))
        keyboard.release_key(self.alt)
        time.sleep(random.normalvariate(0.07, 0.01))
        keyboard.press_key(self.alt)
        time.sleep(random.normalvariate(0.08, 0.01))
        keyboard.release_key(self.alt)
        time.sleep(random.normalvariate(0.08, 0.01))

        keyboard.press_key(self.vkey)
        time.sleep(random.normalvariate(0.1, 0.01))
        keyboard.release_key(self.vkey)


class MoveAround(Action):
    def __init__(self, name, cd, olevel, duration):
        super().__init__(name, cd, "left", olevel, duration)
        self.left = keyboard.virtual_key_to_scan_code("left")
        self.right = keyboard.virtual_key_to_scan_code("right")
        self.to_right = False

    def press(self):
        keyboard.release_key(self.right if self.to_right else self.left)
        time.sleep(random.normalvariate(0.2, 0.01))
        keyboard.press_key(self.left if self.to_right else self.right)
        self.to_right = not self.to_right


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
    def __init__(self, move_time):
        VK = keyboard.KEY_MAP
        actions = [
            Action("F4", cd=185.0, vkey="f4", olevel=10),
            Action("F3", cd=185.0, vkey="f3", olevel=10),
            Action("F2", cd=185.0, vkey="f2", olevel=10),
            Action("2", cd=125.0, vkey="2", olevel=10),
            Action("1", cd=95.0, vkey="1", olevel=10),
            Action("F1", cd=185.0, vkey="f1", olevel=10, duration=1.5),
            MoveAround("Move", move_time, olevel=9, duration=0.3),
            DualJumpAttack("JumpE", cd=10.5, vkey="e", olevel=8, duration=1.5),
            DualJumpAttack("JumpQ", cd=0.0, vkey="q", olevel=0, duration=1.2),
            Action("R", cd=17.0, vkey="r", olevel=9),
            Action("T", cd=65.0, vkey="t", olevel=9),
        ]
        super().__init__(actions)
        self.hammer_count = 0

    def update(self):
        for a in self.actions:
            if not a.is_ready():
                continue
            if a.name == "F3" and self.hammer_count < 6:
                continue

            a.update()

            if a.name == "JumpQ":
                self.hammer_count = min(self.hammer_count + 1, 6)
            elif a.name == "F3":
                self.hammer_count = 0

            break
        return
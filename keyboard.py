import ctypes
import ctypes.wintypes
import atexit
import win32con
import threading
import messagequeue

__all__ = [
    "press_key",
    "release_key",
    "key_to_vkey",
    "vkey_to_scan",
    "GlobalHotKey",
]

# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)


class KeyBdInput(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL),
    ]


class HardwareInput(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_short),
        ("wParamH", ctypes.c_ushort),
    ]


class MouseInput(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL),
    ]


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput), ("mi", MouseInput), ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("ii", Input_I)]


VKEY_CODE = {chr(c).upper(): c for c in range(0x30, 0x5B)}


def key_to_vkey(key_str: str):
    """
    https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
    """
    key_str = key_str.upper()
    if key_str in VKEY_CODE:
        return VKEY_CODE[key_str]
    return eval(f"win32con.VK_{key_str}")


def vkey_to_scan(vkey: int):
    return ctypes.windll.user32.MapVirtualKeyExW(vkey, 0, 0)


def key_to_scan(key_str: str):
    return vkey_to_scan(key_to_vkey(key_str))


def press_key(scan_code, extended=False):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    flags_ = 0x0008
    if extended:
        flags_ |= 0x0001
    ii_.ki = KeyBdInput(0, scan_code, flags_, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def release_key(scan_code, extended=False):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    flags_ = 0x0008 | 0x0002
    if extended:
        flags_ |= 0x0001
    ii_.ki = KeyBdInput(0, scan_code, flags_, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


class GlobalHotKey(threading.Thread):
    def __init__(self, key_cb):
        super().__init__(daemon=True)
        self.key_cb = key_cb
        self.stop_event = threading.Event()
        atexit.register(self.stop)
        self.start()

    def stop(self):
        self.stop_event.set()
        self.join()

    def run(self):
        code_cb = dict()

        for ids, (mod_key, cb) in enumerate(self.key_cb.items()):
            mod_str, key_str = mod_key.split("+")
            if mod_str == "NULL":
                mod_code = 0
            else:
                mod_code = eval("win32con.MOD_" + mod_str)
            vkey_code = key_to_vkey(key_str)
            ctypes.windll.user32.RegisterHotKey(None, ids, mod_code, vkey_code)
            print(f"RegisterHotKey {mod_key}!")
            code_cb[(mod_code, vkey_code)] = cb

        timer_id = ctypes.windll.user32.SetTimer(None, None, 50, None)
        msg = ctypes.wintypes.MSG()
        while (
            not self.stop_event.is_set()
            and ctypes.windll.user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0
        ):
            if msg.message == win32con.WM_HOTKEY:
                mod_code = msg.lParam & 0b1111111111111111
                vkey_code = msg.lParam >> 16
                callback = code_cb.get((mod_code, vkey_code), None)
                if callback is not None:
                    messagequeue.push(callback)
                continue
            ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
            ctypes.windll.user32.DispatchMessageA(ctypes.byref(msg))
        ctypes.windll.user32.KillTimer(None, timer_id)
        for ids, (mod_key, cb) in enumerate(self.key_cb.items()):
            ctypes.windll.user32.UnregisterHotKey(None, ids)
            print(f"UnregisterHotKey {mod_key}!")
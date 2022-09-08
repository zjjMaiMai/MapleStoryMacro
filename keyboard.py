import ctypes
import ctypes.wintypes
import atexit
import win32con
import threading

__all__ = [
    "press_key",
    "release_key",
    "virtual_key_to_scan_code",
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


def press_key(scan_code):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, scan_code, 0x0008, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def release_key(scan_code):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, scan_code, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


VKEY_CODE = {chr(c).upper(): c for c in range(0x30, 0x5B)}


def key_str_to_vkey_code(key_str: str):
    key_str = key_str.upper()
    if key_str in VKEY_CODE:
        return VKEY_CODE[key_str]
    return eval("win32con.VK_" + key_str)


def virtual_key_to_scan_code(key_str: str):
    key_code = key_str_to_vkey_code(key_str)
    return ctypes.windll.user32.MapVirtualKeyExW(key_code, 0, 0)


class GlobalHotKey:
    def __init__(self, key_cb):
        self.key_cb = key_cb
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._do, daemon=True)
        atexit.register(self.stop)

    def start(self):
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join()

    def _do(self):
        code_cb = dict()

        for ids, (mod_key, cb) in enumerate(self.key_cb.items()):
            mod_str, key_str = mod_key.split("+")
            if mod_str == "NULL":
                mod_code = 0
            else:
                mod_code = eval("win32con.MOD_" + mod_str)
            vkey_code = key_str_to_vkey_code(key_str)
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
                    callback()
                continue
            ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
            ctypes.windll.user32.DispatchMessageA(ctypes.byref(msg))
        ctypes.windll.user32.KillTimer(None, timer_id)
        for ids, (mod_key, cb) in enumerate(self.key_cb.items()):
            ctypes.windll.user32.UnregisterHotKey(None, ids)
            print(f"UnregisterHotKey {mod_key}!")
import cv2
import mss
import ctypes
import ctypes.wintypes
import numpy as np


def find_window(name):
    return ctypes.windll.user32.FindWindowW(None, name)


def active_window():
    return ctypes.windll.user32.GetForegroundWindow()


def get_window_text(hwnd):
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd) + 1
    title = ctypes.create_unicode_buffer(length)
    ctypes.windll.user32.GetWindowTextW(hwnd, title, length)
    return "".join(title).strip("\0")


def get_window_bbox(hwnd):
    rect = ctypes.wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.pointer(rect))
    return [rect.left, rect.top, rect.right, rect.bottom]


def capture(hwnd):
    bbox = get_window_bbox(hwnd)
    with mss.mss() as sct:
        monitor = {
            "left": bbox[0],
            "top": bbox[1],
            "width": bbox[2] - bbox[0],
            "height": bbox[3] - bbox[1],
        }
        frame = sct.grab(monitor)
        if frame is None:
            return None
        frame = np.array(frame)
        return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
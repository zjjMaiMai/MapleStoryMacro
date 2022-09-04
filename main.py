import time
import ctypes
import argparse
from actor import MyActor


def get_active_windows_text():
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd) + 1
    title = ctypes.create_unicode_buffer(length)
    ctypes.windll.user32.GetWindowTextW(hwnd, title, length)
    return "".join(title).strip("\0")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", type=float, default=5.0)
    args = parser.parse_args()
    print(args)

    actor = MyActor(args.m)
    while True:
        window_name = get_active_windows_text()
        if window_name == "MapleStory":
            actor.use()
        else:
            time.sleep(0.1)


if __name__ == "__main__":
    try:
        script_begin = time.time()
        main()
    except KeyboardInterrupt:
        print("Script Running {:.1f}s !".format(time.time() - script_begin))
    finally:
        print("Over!")

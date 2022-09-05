import time
import argparse
import window
from actor import MyActor


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", type=float, default=5.0)
    args = parser.parse_args()
    print(args)

    hwnd = window.find_window("MapleStory")
    if hwnd == 0:
        print("No MapleStory window!")
        return

    actor = MyActor(args.m)
    while True:
        if window.active_window() == hwnd:
            actor.update()
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

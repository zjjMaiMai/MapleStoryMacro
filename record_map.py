import cv2
import json
import vision
import window
import keyboard
import numpy as np

running = True
player_pos = None
map_pos = None
p1 = None
p2 = None
layers = []


def set_p1():
    global p1
    print("set_p1", player_pos)
    p1 = player_pos


def set_p2():
    print("set_p2")
    global p2
    p2 = player_pos


def save():
    global p1
    global p2
    if p1 is None or p2 is None:
        return

    layers.append([p1, p2])
    print("save")
    p1 = None
    p2 = None


def close():
    print("close")
    with open("layer.json", "wt", encoding="utf-8") as fp:
        json.dump(layers, fp, indent=4)
    global running
    running = False


def main():
    hwnd = window.find_window("MapleStory")
    if hwnd == 0:
        return

    keyboard.GlobalHotKey(
        {
            "SHIFT+1": set_p1,
            "SHIFT+2": set_p2,
            "SHIFT+S": save,
            "SHIFT+Q": close,
        }
    )

    while running:
        if window.active_window() != hwnd:
            continue

        image = window.capture(hwnd)
        if image is None:
            continue

        global map_pos
        if map_pos is None:
            map_pos = vision.minimap_detect(image, 0.8, map_pos)
            continue

        minimap = vision.split_image(image, map_pos)
        global player_pos
        player_pos = vision.player_detect(minimap, 0.8, player_pos)

        if p1 is not None:
            cv2.circle(minimap, (p1[0], p1[1]), 2, (0, 0, 255), -1, cv2.LINE_AA)
        if p2 is not None:
            cv2.circle(minimap, (p2[0], p2[1]), 2, (255, 0, 0), -1, cv2.LINE_AA)
        if p1 is not None and p2 is not None:
            cv2.line(
                minimap, (p1[0], p1[1]), (p2[0], p2[1]), (0, 255, 0), 3, cv2.LINE_AA
            )
        cv2.imshow("minimap", minimap)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
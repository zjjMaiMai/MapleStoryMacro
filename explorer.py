import cv2
import time
import random
import typing
import keyboard
import vision
import window
import numpy as np


def explorer(hwnd):
    occ_image = None
    map_bbox = None

    pp_list = []

    while True:
        image = window.capture(hwnd)
        if image is None:
            continue

        if map_bbox is None:
            map_bbox = vision.minimap_detect(image)
            continue

        image = vision.split_image(image, map_bbox)
        if occ_image is None:
            occ_image = np.zeros((image.shape[:2]), dtype=np.uint8)

        player_pos = vision.player_detect(image)
        if player_pos is None:
            continue
        
        pp = player_pos[:2]

        if not pp_list:
            pp_list.append(pp)

        if all([])
        

        
        print(player_pos_list)
        cv2.imshow("occ_image", occ_image)
        cv2.waitKey(1)


if __name__ == "__main__":

    hwnd = window.find_window("MapleStory")
    if hwnd == 0:
        exit()

    explorer(hwnd)
import os
import time
import json
import vision
import window
import random
import keyboard
import argparse
import winsound
import threading
import tkinter as tk
import actor
from PIL import Image, ImageTk


class App(tk.Frame):
    def __init__(self, move_step, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.move_step = move_step
        self.canvas = tk.Canvas(
            self,
            width=200,
            height=100,
            borderwidth=0,
            highlightthickness=0,
            background="green",
        )
        self.grid(row=0, column=0, sticky="nsew")

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.hwnd = window.find_window("MapleStory")
        if self.hwnd == 0:
            raise RuntimeError
        self.hotkey = keyboard.GlobalHotKey(
            {
                "SHIFT+1": self.callback_p0,
                "SHIFT+2": self.callback_p1,
                "SHIFT+S": self.callback_save,
                "SHIFT+G": self.callback_go,
            }
        )
        self.hotkey.start()
        self.after(30, self.loop)

        # infoj
        self.image = None
        self.map_bbox = None
        self.spos = None
        self.epos = None
        self.tpos = None
        self.tiles = []

        # primitive
        self.image_prim = None
        self.spos_prim = None
        self.epos_prim = None
        self.tpos_prim = None
        self.tiles_prim = []

        # reload tiles
        if os.path.exists("assert/minimap_info.json"):
            with open("assert/minimap_info.json", mode="rt", encoding="utf-8") as fp:
                self.tiles = json.load(fp)

        # flags
        self.running = False

        # actor
        self.actor = actor.MyActor(self.move_step)
        self.warn_detect = threading.Thread(target=self.warning_detect, daemon=True)
        self.warn_detect.start()

    def warning_detect(self):
        image = window.capture(self.hwnd)
        if image is None:
            return

        if self.map_bbox is None:
            self.map_bbox = vision.minimap_detect(image, 0.9)
            return

        minimap = vision.split_image(image, self.map_bbox)
        if vision.rune_detect(minimap, 0.9) is not None:
            winsound.PlaySound(
                "assert/siren.wav", winsound.SND_FILENAME | winsound.SND_ASYNC
            )
        # elif vision.mushrooms_detect(image, 0.9) is not None:
        #     winsound.PlaySound(
        #         "assert/siren.wav", winsound.SND_FILENAME | winsound.SND_ASYNC
        #     )
        else:
            winsound.PlaySound(None, winsound.SND_PURGE)

    def loop(self):
        self.custom_loop()
        self.after(15, self.loop)

    def custom_loop(self):
        # image = window.capture(self.hwnd)
        # if image is None:
        #     return

        # if self.map_bbox is None:
        #     self.map_bbox = vision.minimap_detect(image, 0.9)
        #     return

        # self.image = vision.split_image(image, self.map_bbox)
        # self.tkimage = ImageTk.PhotoImage(image=Image.fromarray(self.image[..., ::-1]))
        # if self.image_prim is None:
        #     self.canvas.config(width=self.tkimage.width(), height=self.tkimage.height())
        #     self.image_prim = self.canvas.create_image(
        #         0, 0, image=self.tkimage, anchor="nw"
        #     )
        # self.canvas.itemconfig(self.image_prim, image=self.tkimage)

        # for ids, t in enumerate(self.tiles):
        #     if ids >= len(self.tiles_prim):
        #         self.tiles_prim.append(
        #             self.canvas.create_line(*t, width=4.0, fill="green1")
        #         )
        #     else:
        #         self.canvas.coords(self.tiles_prim[ids], *t)

        # if self.spos is not None:
        #     if self.spos_prim is None:
        #         self.spos_prim = self.canvas.create_rectangle(
        #             *self.spos, fill="DeepPink"
        #         )
        #     else:
        #         self.canvas.coords(self.spos_prim, *self.spos)
        # else:
        #     self.canvas.delete(self.spos_prim)

        # if self.epos is not None:
        #     if self.epos_prim is None:
        #         self.epos_prim = self.canvas.create_rectangle(
        #             *self.epos, fill="DeepSkyBlue"
        #         )
        #     else:
        #         self.canvas.coords(self.epos_prim, *self.epos)
        # else:
        #     self.canvas.delete(self.epos_prim)

        # if self.tpos is not None:
        #     if self.tpos_prim is None:
        #         self.tpos_prim = self.canvas.create_rectangle(
        #             *self.tpos, fill="dark orange"
        #         )
        #     else:
        #         self.canvas.coords(self.tpos_prim, *self.tpos)
        # else:
        #     self.canvas.delete(self.tpos_prim)

        # script
        if self.running:
            self.script()
        return

    def script(self):
        if self.actor is None:
            return

        if window.active_window() == self.hwnd:
            self.actor.update()

    def prescript(self):
        return

    def callback_p0(self):
        if self.image is None:
            return

        pos = vision.player_detect(self.image)
        if pos is not None:
            self.spos = pos

    def callback_p1(self):
        if self.image is None:
            return

        pos = vision.player_detect(self.image)
        if pos is not None:
            self.epos = pos

    def callback_save(self):
        if self.spos is not None and self.epos is not None:
            self.tiles.append([self.spos[0], self.spos[3], self.epos[2], self.epos[3]])
            self.spos = None
            self.epos = None

            with open("assert/minimap_info.json", mode="wt", encoding="utf-8") as fp:
                json.dump(self.tiles, fp, indent=4, ensure_ascii=False)
            print("Save!")

    def callback_go(self):
        if self.running:
            self.running = False
            return

        self.prescript()
        self.actor.reset()
        self.running = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("move_step", type=int)
    args = parser.parse_args()
    print(args)

    root = tk.Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    app = App(args.move_step, root)
    root.mainloop()
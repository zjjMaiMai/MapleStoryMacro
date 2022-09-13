import os
import time
import json
import vision
import window
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
            width=256,
            height=128,
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
        playing = False
        while True:
            sound = False

            image = window.capture(self.hwnd)
            if image is None:
                continue

            if self.map_bbox is None:
                self.map_bbox = vision.minimap_detect(image)
                continue

            minimap = vision.split_image(image, self.map_bbox)

            rune = vision.rune_detect(minimap)
            if rune is not None:
                rune_debuff = vision.rune_debuff_detect(image)
                if rune_debuff is None:
                    print("RUNE!RUNE!")
                    self.image = vision.split_image(minimap, rune)
                    sound = True
                else:
                    self.image = vision.split_image(image, rune_debuff)
            else:
                mushrooms = vision.mushrooms_detect(image)
                if mushrooms is not None:
                    print("MUSHROOMS!")
                    self.image = vision.split_image(image, mushrooms)
                    sound = True

            if sound == True and playing == False:
                winsound.PlaySound(
                    "assert/siren.wav",
                    winsound.SND_FILENAME + winsound.SND_ASYNC + winsound.SND_LOOP,
                )
                playing = True
            elif sound == False:
                winsound.PlaySound(None, winsound.SND_FILENAME)
                playing = False

            time.sleep(1.0)

    def loop(self):
        self.custom_loop()
        self.after(15, self.loop)

    def custom_loop(self):
        if self.image is not None:
            self.tkimage = ImageTk.PhotoImage(
                image=Image.fromarray(self.image[..., ::-1])
            )
            if self.image_prim is None:
                self.canvas.config(
                    width=max(self.tkimage.width(), 256),
                    height=max(self.tkimage.height(), 128),
                )
                self.image_prim = self.canvas.create_image(
                    0, 0, image=self.tkimage, anchor="nw"
                )
            self.canvas.itemconfig(self.image_prim, image=self.tkimage)

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
    parser.add_argument("move", type=int, nargs=2)
    args = parser.parse_args()
    print(args)

    root = tk.Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    app = App(args.move, root)
    root.mainloop()

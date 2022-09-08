import time
import vision
import window
import keyboard
import tkinter as tk
from PIL import Image, ImageTk


class App(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvas = tk.Canvas(self, width=200, height=100, background="green")
        self.grid(row=0, column=0, sticky="nsew")

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.hwnd = window.find_window("MapleStory")
        if self.hwnd == 0:
            raise RuntimeError
        self.hotkey = keyboard.GlobalHotKey(
            {
                "CONTROL+F": self.callback_p0,
                "CONTROL+G": self.callback_p1,
                "CONTROL+S": self.callback_save,
                "CONTROL+RETURN": self.callback_go,
            }
        )
        self.hotkey.start()
        self.after(10, self.loop)

        # tiles
        self.spos = None
        self.tiles = []

    def loop(self):
        self.custom_loop()
        self.after(10, self.loop)

    def custom_loop(self):
        image = window.capture(self.hwnd)
        if image is None:
            return

        map_bbox = vision.minimap_detect(image)
        if map_bbox is None:
            return

        self.image = vision.split_image(image, map_bbox)
        self.cimage = ImageTk.PhotoImage(image=Image.fromarray(self.image[..., ::-1]))
        self.canvas.config(width=self.cimage.width(), height=self.cimage.height())
        self.canvas.create_image(0, 0, image=self.cimage, anchor="nw")

        if self.spos is not None:
            self.canvas.create_rectangle(*self.spos, fill="red")
        for t in self.tiles:
            self.canvas.create_line(*t, width=4.0, fill="red")
        return

    def callback_p0(self):
        pos = vision.player_detect(self.image)
        if pos is None:
            return

        self.spos = pos
        return

    def callback_p1(self):
        if self.spos is None:
            return

        epos = vision.player_detect(self.image)
        if epos is None:
            return

        self.tiles.append([self.spos[0], self.spos[3], epos[2], epos[3]])
        self.spos = None
        return

    def callback_save(self):
        print("save")

    def callback_go(self):
        print("go")


if __name__ == "__main__":
    root = tk.Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    app = App(root)
    root.mainloop()
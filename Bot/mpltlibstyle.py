import matplotlib
import matplotlib.pyplot as plt
from tkinter import *
import numpy as np
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


import os

# COLOURS
# 0 == Unknown
# 1 == WALL
# 2 == FLOOR
# 3 == Treasure
# 4 == Food
# 5 == Ammo
# 6 == Players
# 7 == Exit
# 8 == Sprite looking N
# 9 == Sprite looking E
# 10 == Sprite looking S
# 11 == Sprite looking W
# 12 == redkey
# 13 == greenkey
# 14 == yellowkey
# 15 == bluekey



botmap=np.full((50,50),0)


def plot(botmap):
    root = Tk()
    root.geometry("700x700+10+10")

    fig = Figure(figsize=(5,5), dpi=100)
    fig.clear()
    fig.add_subplot(111).imshow(botmap)

    canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
    canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
    toolbar = NavigationToolbar2Tk(canvas, root)

    canvas.draw_idle()

    root.after(1, root.destroy)
import matplotlib
import matplotlib.pyplot as plt
from tkinter import *
import numpy as np

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

# COLOURS
# 0 == Unknown
# 1 == WALL
# 2 == FLOOR
# 3 == Keys
# 4 == Food
# 5 == Ammo
# 6 == Players
# 7 == Exit
# 8 == Sprite looking N
# 9 == Sprite looking E
# 10 == Sprite looking S
# 11 == Sprite looking W


# X = np.random.randint(256, size=(100, 100))

window_width = 1000
window_height = 600

root = Tk()

fig = Figure(figsize=(5, 5), dpi=100)

canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
toolbar = NavigationToolbar2Tk(canvas, root)

def draw_chart():
    fig.clear()
    fig.add_subplot(111).plot(np.random.randint(1,10,5), np.random.randint(10,20,5)) #generate random x/y
    canvas.draw_idle()

Button(root,text="Draw",command=draw_chart).pack()

root.mainloop()

def setup():
    # map = np.zeros((500, 500))
    fig = plt.figure(figsize=(8, 8))
    # map[0][10] = 1
    #puts map into the plot
    # plt.imshow(map)
    # invert the y axis so 0 at bottom
    ax = plt.gca()
    ax.invert_yaxis()

    plt.title("Dungeon visualization")
    # return map


# shows in ide
def show(map):
    plt.close()
    plt.imshow(map)
    plt.show()

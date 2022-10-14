import matplotlib
import numpy as np
import matplotlib.pyplot as plt

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
def setup(map):
    fig = plt.figure(figsize=(8, 8))
    # invert the y axis so 0 at bottom
    ax = plt.gca()
    ax.invert_yaxis()

    plt.title("Dungeon visualization")
    plt.imshow(map)
    plt.ion()
    plt.show()
    return map


# shows in ide
def show(map):
    plt.close()
    plt.imshow(map)
    plt.show()
    return map
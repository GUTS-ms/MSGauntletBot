import numpy as np
import matplotlib.pyplot as plt

# COLOURS
# 0 == BLANK
# 1 == WALL
# 2 == FLOOR
# 3 == BLANK
# 4 == BLANK


# X = np.random.randint(256, size=(100, 100))
map = np.zeros((100, 100))

fig = plt.figure(figsize=(8, 8))
map[0][10] = 1
#puts map into the plot
plt.imshow(map)

# invert the y axis so 0 at bottom
ax = plt.gca()
ax.invert_yaxis()

plt.title("Dungeon visualization")
# shows in ide
plt.show()

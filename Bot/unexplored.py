# function to find the start row and column
def find_start(x):
    start = x-1 if x-1 >= 0 else 0
    return start

# function to find the end row and column
def find_end(x, shape):
    end = x+1 if x+1 <= shape else shape
    return end

def find_neighbors(a, i, j):
    neighbors = []
    row_start, row_end = find_start(i), find_end(i, a.shape[0])
    col_start, col_end = find_start(j), find_end(j, a.shape[1])

    for y in range(a.shape[0]):
        for z in range(a.shape[1]):
            if y >= row_start and y <= row_end:
                if z >= col_start and z <= col_end:
                    neighbors.append((a[y][z],y,z))
    return neighbors

def find_unexp(arr):
    for pos, x in np.ndenumerate(arr):
        if x == 0:
            neighb=find_neighbors(arr, pos[0], pos[1])
            for y in neighb:
                if y[0] == 2:
                    print("found unexplored at " + (y[1], y[2]))
                    return (y[1], y[2])
    print("no unexplored found")
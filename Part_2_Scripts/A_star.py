###===--------------------------------------------===###
# Script:        A_star.py
# Authors:       Demir Kucukdemiral 2883935K, Charikleia Nikou 2881802N, Cameron Norrington 2873038N, Adam Burns 2914690B, Ben Maconnachie 2911209M, Jeremi Rozanski 2881882R
# Created on:    2025-04
# Last Modified: 2025-04
# Description:   A* path planning algorithm with Bezier-like smoothing and airstrip highlight
# Version:       1.0
###===--------------------------------------------===###    

import heapq
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev

class Node:
    def __init__(self, x, y, cost, parent=None):
        self.x = x
        self.y = y
        self.cost = cost  
        self.parent = parent

    def __lt__(self, other):
        return self.cost < other.cost


def heuristic(a, b):
    return np.hypot(a[0] - b[0], a[1] - b[1])


def get_neighbors(x, y, grid):
    moves = [(-1,0), (1,0), (0,-1), (0,1),
             (-1,-1), (-1,1), (1,-1), (1,1)]
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid.shape[0] and 0 <= ny < grid.shape[1]:
            if grid[nx, ny] == 0:
                yield (nx, ny)


def a_star(grid, start, goal):
    open_list = []
    start_node = Node(*start, 0.0)
    heapq.heappush(open_list, (0.0, start_node))
    came_from = {}
    cost_so_far = {start: 0.0}

    while open_list:
        _, current = heapq.heappop(open_list)
        if (current.x, current.y) == goal:
            # Reconstruct path
            path = []
            while current:
                path.append((current.x, current.y))
                current = current.parent
            return list(reversed(path))

        for nx, ny in get_neighbors(current.x, current.y, grid):
            new_cost = cost_so_far[(current.x, current.y)] + heuristic((current.x, current.y), (nx, ny))
            if (nx, ny) not in cost_so_far or new_cost < cost_so_far[(nx, ny)]:
                cost_so_far[(nx, ny)] = new_cost
                priority = new_cost + heuristic((nx, ny), goal)
                heapq.heappush(open_list, (priority, Node(nx, ny, new_cost, current)))
    return None


grid = np.zeros((20, 30), dtype=int)
grid[10:12, 5:25] = 1  

start = (0, 0)
goal = (19, 29)
path = a_star(grid, start, goal)

path.extend([(19, 27), (19, 25), (19, 23), (19, 21)])

# Plot
plt.figure(figsize=(8, 5))
plt.imshow(grid, cmap='gray_r')

if path:
    coords = np.array(path)
    py, px = coords[:,0], coords[:,1]
    plt.plot(px, py, linewidth=2, label='A* Path')

    x = px
    y = py
    tck, u = splprep([x, y], s=2)
    u_new = np.linspace(0, 1, 300)
    x_smooth, y_smooth = splev(u_new, tck)
    plt.plot(x_smooth, y_smooth, linewidth=2, linestyle='--', label='Smoothed Path')

    airstrip_points = coords[-4:]
    min_x, max_x = np.min(airstrip_points[:,1]), np.max(airstrip_points[:,1])
    min_y, max_y = np.min(airstrip_points[:,0]), np.max(airstrip_points[:,0])
    plt.gca().add_patch(plt.Rectangle((min_x - 0.5, min_y - 0.5),
                                      (max_x - min_x) + 1, (max_y - min_y) + 1,
                                      linewidth=0, edgecolor='none', facecolor='yellow', alpha=0.3, label='Airstrip'))


    plt.scatter(start[1], start[0], c='green', label='Start')
    plt.scatter(goal[1], goal[0], c='red', label='Goal')

else:
    print("No path found.")

plt.legend()
plt.title("A* Path Planning with Bezier-like Smoothing and Airstrip Highlight")
plt.gca().invert_yaxis()
plt.grid(True)
plt.show()
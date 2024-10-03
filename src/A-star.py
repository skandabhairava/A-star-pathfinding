#!/usr/bin/env python3
import math
import pygame

pygame.init()
WIDTH = 25*2
SIZE = (WIDTH, 11*WIDTH//16) #WIDTH HEIGHT of aspect ratio 16:11
print("SIZE: ", SIZE, "\n\n")
window = pygame.display.set_mode((SIZE[0]*16, SIZE[1]*16))
pygame.display.set_caption("A* Algorithm")
clock = pygame.time.Clock()
running = True

class Node:
    def __init__(self, type: int, coords: tuple[int, int], f: int|float=math.inf, g: int|float=math.inf, h: int|float=math.inf, parent=None) -> None:
        self.type = type
        self.coords: tuple[int, int] = coords
        self.f: int|float = f
        self.g: int|float = g
        self.h: int|float = h
        self.parent: Node|None = parent

    def __repr__(self) -> str:
        return f"{self.coords}||{self.type}>> f: {self.f} | g: {self.g} | h: {self.h}"

# TILE TYPES
# 0 -> open
# 1 -> blocked/wall
# 2 -> start
# 3 -> end
# 4 -> POSSIBLE PATHS
# 5 -> DEFINITE PATH
TILES: list[list[Node]] = [[Node(1, (x, y)) if (x == 0) or (x == SIZE[0]-1) or (y == 0) or (y == SIZE[1]-1) else Node(0, (x, y)) for x in range(SIZE[0])] for y in range(SIZE[1])]
QUEUE = []
C_QUEUE = []

EDIT_MODE = True
# PATH FINDING TYPES
# 0 NOT BEGUN/DONE
# 1 BEGUN
# 2 reverse
# 3 cleanup and reset
PATH_FINDING = 0
START_COORD: tuple[int, int] | None = None
END_COORD: tuple[int, int] | None = None
end_tile: Node|None = None
PATH = []

def propagate2D(coords: tuple, arr: list[list]) -> tuple:
    x, y = coords[0], coords[1]
    top, left, right, bottom, top_left, top_right, bottom_left, bottom_right = None, None, None, None, None, None, None, None
    if y > 0: top = (x, y - 1)
    if y < len(arr)-1: bottom = (x, y + 1)
    if x > 0: left = (x - 1, y)
    if x < len(arr[0])-1: right = (x + 1, y)

    if y > 0 and x > 0: top_left = (x - 1, y - 1)
    if y > 0 and x < len(arr[0])-1: top_right = (x + 1, y - 1)
    if y < len(arr)-1 and x > 0: bottom_left = (x - 1, y + 1)
    if y < len(arr)-1 and x < len(arr[0])-1: bottom_right = (x + 1, y + 1)

    return (top, right, bottom, left, top_right, bottom_right, bottom_left, top_left)

while running:
    clock.tick(120)

    pos = pygame.mouse.get_pos()
    pos = (pos[0]//16, pos[1]//16)
    mouse_buttons = pygame.mouse.get_pressed()
    out_of_bounds = False

    if (pos[0] <= 0) or (pos[0] >= SIZE[0]-1) or (pos[1] <= 0) or (pos[1] >= SIZE[1]-1):
        out_of_bounds = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # CLEAR SCREEN
            if event.key == pygame.K_END and EDIT_MODE:
                START_COORD = None
                END_COORD = None
                TILES = [[Node(1, (x, y)) if (x == 0) or (x == SIZE[0]-1) or (y == 0) or (y == SIZE[1]-1) else Node(0, (x, y)) for x in range(SIZE[0])] for y in range(SIZE[1])]
                end_tile = None
                PATH.clear()
                QUEUE.clear()
                C_QUEUE.clear()

            # TOGGLE EDIT MODE
            elif event.key == pygame.K_RETURN:
                if PATH_FINDING == 0:
                    EDIT_MODE = not EDIT_MODE
                    if EDIT_MODE: pygame.display.set_caption("A* Algorithm")
                    else: pygame.display.set_caption("A* Algorithm [input locked]")

            # SAVE START POSITION
            elif event.key == pygame.K_s and EDIT_MODE and not out_of_bounds:
                if START_COORD:
                    TILES[START_COORD[1]][START_COORD[0]].type = 0
                START_COORD = pos
                TILES[START_COORD[1]][START_COORD[0]].type = 2

            # SAVE END POSITION
            elif event.key == pygame.K_e and EDIT_MODE and not out_of_bounds:
                if END_COORD:
                    TILES[END_COORD[1]][END_COORD[0]].type = 0
                END_COORD = pos
                TILES[END_COORD[1]][END_COORD[0]].type = 3

            # TODO: TOGGLE PATHFINDING
            elif event.key == pygame.K_SPACE and (PATH_FINDING==0) and not EDIT_MODE and START_COORD and END_COORD:
                PATH_FINDING = 1
                PATH.clear()
                for i in TILES:
                    for j in i:
                        if j.type in (4, 5): j.type = 0
                pygame.display.set_caption("A* Algorithm [PATH FINDING]")
                start_tile = TILES[START_COORD[1]][START_COORD[0]]
                start_tile.f = 0
                start_tile.g = 0
                start_tile.h = 0

                end_tile = TILES[END_COORD[1]][END_COORD[0]] # type: ignore
                
                QUEUE.clear()
                C_QUEUE.clear()
                QUEUE.append(start_tile)

    if EDIT_MODE:
        if mouse_buttons[0] and not out_of_bounds and pos != START_COORD and pos != END_COORD: #left mouse pressed
            TILES[pos[1]][pos[0]].type = 1
        if mouse_buttons[2] and not out_of_bounds: #right mouse pressed
            if START_COORD == pos:
                START_COORD = None
            if END_COORD == pos:
                END_COORD = None
            TILES[pos[1]][pos[0]].type = 0

    for _ in range(1):
        if PATH_FINDING==1:
            if len(QUEUE) == 0:
                PATH_FINDING = 3
                print(f"The End point({END_COORD}) isn't accessible from Start point({START_COORD}).\n-----------\n")
                break

            min_f = min(QUEUE, key=lambda k: k.f)
            current_tile: Node = QUEUE.pop(next(i for i, item in enumerate(QUEUE) if item is min_f))
            C_QUEUE.append(current_tile.coords)

            if current_tile.coords == END_COORD:
                PATH_FINDING = 2
                break

            neighbors = propagate2D(current_tile.coords, TILES)
            for i, n_coords in enumerate(neighbors):
                if n_coords is None or n_coords in C_QUEUE:
                    continue
                n_tile: Node = TILES[n_coords[1]][n_coords[0]]

                if (n_tile.type in (1, 2) or n_tile in QUEUE or 
                    (i == 4 and TILES[neighbors[0][1]][neighbors[0][0]].type == 1 and TILES[neighbors[1][1]][neighbors[1][0]].type == 1) or
                    (i == 5 and TILES[neighbors[2][1]][neighbors[2][0]].type == 1 and TILES[neighbors[1][1]][neighbors[1][0]].type == 1) or
                    (i == 6 and TILES[neighbors[2][1]][neighbors[2][0]].type == 1 and TILES[neighbors[3][1]][neighbors[3][0]].type == 1) or
                    (i == 7 and TILES[neighbors[0][1]][neighbors[0][0]].type == 1 and TILES[neighbors[3][1]][neighbors[3][0]].type == 1)
                    ):
                    continue

                length = 10 if i < 4 else 14

                g = current_tile.g + length
                if n_tile.g < g: continue

                h = int(math.sqrt(math.pow(END_COORD[0] - n_coords[0], 2) + math.pow(END_COORD[1] - n_coords[1], 2))*10) # type: ignore
                n_tile.f = g + h
                n_tile.g = g
                n_tile.h = h

                n_tile.type = 4
                n_tile.parent = current_tile

                QUEUE.append(n_tile)

    if PATH_FINDING == 2:
        if end_tile.parent != None: # type: ignore
            end_tile.type = 5 #type: ignore
            end_tile = end_tile.parent #type: ignore
            PATH.append(end_tile.coords)
        else:
            # SHUTDOWN PATHFINDING
            PATH_FINDING = 3

    if PATH_FINDING == 3:
        for i in TILES:
            for j in i:
                if j.type == 4: j.type = 0
        TILES[START_COORD[1]][START_COORD[0]].type = 2 # type: ignore
        TILES[END_COORD[1]][END_COORD[0]].type = 3 # type: ignore
        PATH_FINDING = 0

        end_tile = None
        if len(PATH) != 0:
            PATH.reverse()
            print("PATH:", PATH)
            PATH.clear()

        QUEUE.clear()
        C_QUEUE.clear()
        pygame.display.set_caption("A* Algorithm [input locked]")



    window.fill((50, 50, 50))
    for i, rows in enumerate(TILES):
        for j, col in enumerate(rows):
            match col.type:
                case 0:
                    window.fill((255, 255, 255), (j*16, i*16, 15, 15))
                case 1:
                    window.fill((0, 0, 0), (j*16, i*16, 15, 15))
                case 2:
                    window.fill((50, 255, 50), (j*16, i*16, 15, 15))
                case 3:
                    window.fill((255, 50, 50), (j*16, i*16, 15, 15))
                case 4:
                    window.fill((50, 50, 255), (j*16, i*16, 15, 15))
                case 5:
                    window.fill((255, 215, 0), (j*16, i*16, 15, 15))
                case _:
                    window.fill((0, 0, 0), (j*16, i*16, 15, 15))
    pygame.display.update()
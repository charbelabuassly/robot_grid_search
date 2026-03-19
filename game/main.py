import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pygame
from grid.grid import Grid

# ----------
# CONSTANTS
# ----------

TILE_SIZE = 30 #30 pixels
ROBOT_COUNT = 2

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHTGRAY = (200, 200, 200)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
MAGENTA = (255, 0, 255)

# Color map to use it later for coloring grid tiles
COLOR_MAP = {
    0: LIGHTGRAY,   # Unused (kept for safety)
    1: LIGHTGRAY,   # Open Path (Gray)
    2: BLACK,       # Wall
    3: YELLOW,      # Quicksand
    4: RED,         # Hole
    5: BLUE,        # Gate
    6: GREEN,       # Player spawn
    7: MAGENTA      # Robot spawn
    
}

def main():
    g = Grid() #Creating Grid object instance
    g.generate_grid(ROBOT_COUNT) #Generating the grid
    grid_map = g.getGrid() #Getting the grid as a numpy array
    gridSize = g.getSize() #returns a tuple of (x,y)

    pygame.init() #Init

    # ---------------
    # MAIN CONSTANTS
    # ---------------
    HEIGHT = TILE_SIZE * gridSize[0]
    WIDTH = TILE_SIZE * gridSize[1]

    # Game Window
    screen = pygame.display.set_mode((WIDTH, HEIGHT)) #Size 
    pygame.display.set_caption("AI Project") #Title
    
    while True: #While true loop to keep it from closing (just like in opengl)
        buildGrid(grid_map, gridSize, screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()


def buildGrid(gridArr, gridSize, screen):
    for row in range(0,gridSize[0]):
        for col in range(0, gridSize[1]):
            rect = pygame.Rect(col*TILE_SIZE, row*TILE_SIZE, TILE_SIZE, TILE_SIZE) #pygame places the rectangle on the window using
            #the x and y coordinates of the top-left corner of the rectangle, but we need to multiply x and y by the 
            #tilesize to determine its placement on the window itself. The 2 others args represent the size of the rectangle
            #Another note is that we flip row and column location because unlike in arrays where origin is the top left,
            #here the origin is bottom left (axis form), where horizontal -> x [LEFT -> RIGHT] and vertical -> Y (DOWN -> UP)
            val = gridArr[row, col] #will be used to determine the color
            pygame.draw.rect(screen, COLOR_MAP[val], rect, 0) # (surface, color, shape, border_width)
            

main()

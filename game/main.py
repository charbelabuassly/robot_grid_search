import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from player import Player
from robot import Robot
import pygame
from grid.grid import Grid

# ----------
# CONSTANTS
# ----------
TILE_SIZE = 20 #20 pixels
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
TRANSPARENT_GREEN = (0, 255, 0, 64)

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
    
#Game Init
pygame.init() #Init
valid_inputs = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_RETURN] #valid keys 

def main():
    g = Grid(20, 20) #Creating Grid object instance
    player_spawn, robot_spawn = g.generate_grid(ROBOT_COUNT) #Generating the grid, getting the player spawn (tuple) and the robot spawn (array of tuples)
    grid_map = g.getGrid().T #Getting the grid as a numpy array
    grid_size = g.getSize() #returns a tuple of (x,y)

    #Creating the Player instance
    player = Player(player_spawn[1], player_spawn[0]) # x-> horizontal & y -> vertical
    #Player position represented on the flipped numpy array
    
    #Creating the Robot instances
    robots = [Robot(spawn[1], spawn[0]) for spawn in robot_spawn] #Creating an array of Robot instances 
    
    # ---------------
    # MAIN CONSTANTS
    # ---------------
    HEIGHT = TILE_SIZE * grid_size[0]
    WIDTH = TILE_SIZE * grid_size[1]

    # Game Window
    screen = pygame.display.set_mode((WIDTH, HEIGHT)) #Size 
    pygame.display.set_caption("AI Project") #Title
    #build grid and player at first frame
    buildGrid(grid_map, grid_size, screen) 
    draw_player(screen, player)
    draw_robots(screen, robots)
    #The while loop keeps on running to check for events, the events check for the type of event, if key is prssed, next pos is set
    #then we update the player pos and redraw the grid with the new position
    while True: #While true loop to keep it from closing (just like in opengl)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key in valid_inputs: #If key is pressed, and in the valid key inputs
                buildGrid(grid_map, grid_size, screen) #rebuild the grid at every new input, it will be drawn over the characters and robots
                if event.key == pygame.K_LEFT:
                    next_move = (player.x - 1, player.y) #moving left
                    #print(COLOR_MAP[int(grid_map[next_move[0],next_move[1]])])
                elif event.key == pygame.K_RIGHT:
                    next_move = (player.x + 1, player.y) #moving right
                elif event.key == pygame.K_UP:
                    next_move = (player.x, player.y - 1) #moving down
                elif event.key == pygame.K_DOWN:
                    next_move = (player.x, player.y + 1) #moving up
                elif event.key == pygame.K_RETURN:
                    # Keep Enter for future use (e.g., confirm moves)
                    pass
                if next_move is not None:
                    if grid_map[next_move[0],next_move[1]] == 4: #If hole reset the position
                        player.x , player.y = (player_spawn[1], player_spawn[0])
                    elif not grid_map[next_move[0],next_move[1]] in [0, 2]: #if not blocking
                        player.x, player.y = next_move
                    
                for robot in robots:
                    robot.current_pos = robot.patrol_search(grid_size, grid_map)

                draw_player(screen, player) #redraw the player after each input at new position
                draw_robots(screen, robots)
        #anything drawn here will be redrawn every frame, which is not necessary for our use case
        pygame.display.update() #Display the grid after building it

def buildGrid(gridArr, grid_size, screen):
    for row in range(0,grid_size[0]):
        for col in range(0, grid_size[1]):
            rect = pygame.Rect(row*TILE_SIZE,col*TILE_SIZE,TILE_SIZE, TILE_SIZE) #pygame places the rectangle on the window using
            #the x and y coordinates of the top-left corner of the rectangle, but we need to multiply x and y by the 
            #tilesize to determine its placement on the window itself. The 2 others args represent the size of the rectangle
            #Another note is that we flip row and column location because unlike in arrays where origin is the top left,
            #here the origin is bottom left (axis form), where horizontal -> x [LEFT -> RIGHT] and vertical -> Y (DOWN -> UP)
            val = gridArr[row, col] #will be used to determine the color
            pygame.draw.rect(screen, COLOR_MAP[val], rect, 0) # (surface, color, shape, border_width)

def draw_player(screen, player):
    rect = pygame.Rect(player.x * TILE_SIZE, player.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    pygame.draw.rect(screen, GREEN, rect, 0)

def draw_robots(screen, robots):
    for robot in robots:
        rect = pygame.Rect(robot.current_pos[0] * TILE_SIZE, robot.current_pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, MAGENTA, rect, 0)

main()

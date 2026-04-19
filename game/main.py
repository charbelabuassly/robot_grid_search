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

# key: level number
# tuple first 2 elements : gridsize for that level
# tuple 3rd element : robot count
levels = {
    1: (20, 30, 2),
    2: (20, 30, 3),
    3: (30, 30, 4),
    4: (30, 30, 6),
    5: (30, 60, 8),
    6: (30, 60, 10)
}
#make sure to match this to above
max_lvl = 6
    
#Game Init
pygame.init() #Init
valid_inputs = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_RETURN] #valid keys 

TILE_SIZE= 20 #20 pixels
MAX_LIVES = 5
HEART_SIZE = 16
HEART_GAP = 6 #gap between hearts
HUD_PADDING = 10 #space from edge

def load_tile_images():
    photos_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "photos")
    images = {}
    tile_files = {
        1: "path.png",
        2: "wall.png",
        3: "quicksand.png",
        4: "hole.png",
        5: "gate.png",
    }
    for tile, filename in tile_files.items():
        file_path = os.path.join(photos_dir, filename)
        if os.path.exists(file_path):
            img = pygame.image.load(file_path).convert_alpha()
            images[tile] = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    return images

#loads images , resizes the images
def load_entity_images():
    photos_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "photos") #find photos folder
    images = {} 
    #define image path
    player_path = os.path.join(photos_dir, "player.png")
    robot_path = os.path.join(photos_dir, "robot.png")

    if os.path.exists(player_path):
        p = pygame.image.load(player_path).convert_alpha() #loads the image and keeps transparency
        images["player"] = pygame.transform.scale(p, (TILE_SIZE, TILE_SIZE))#store the images in player
                                                                            #with its tile size
    if os.path.exists(robot_path):
        r = pygame.image.load(robot_path).convert_alpha()
        images["robot"] = pygame.transform.scale(r, (TILE_SIZE, TILE_SIZE))

    return images

#this function draws a heart at a given position given color and size
#draws 2 circles and 1 triangle
def draw_heart(screen, x, y, size, color=(160, 0, 0)):
    r = size // 4 #the heart is divided into portions
    left_center = (x + r, y + r) #define the circles center
    right_center = (x + 3 * r, y + r)
    pygame.draw.circle(screen, color, left_center, r)#draw circle on the screen with radius r
    pygame.draw.circle(screen, color, right_center, r)
    pygame.draw.polygon(screen, color, [(x, y + r), (x + size, y + r), (x + size // 2, y + size)])
#                                       left point     right point        bottom point

#this function draws all the heart as a health bar
def draw_lives(screen, lives, width): 
    total_w = MAX_LIVES * HEART_SIZE + (MAX_LIVES - 1) * HEART_GAP #the total width of the health bar
    start_x = width - HUD_PADDING - total_w #this places the hearts on the top-right corner
    y = HUD_PADDING
    for i in range(MAX_LIVES):#loop on each heart 
        if i < lives :#change color if the heart lost life if not stays the same
            color = (160, 0, 0)
        else :
            color = (90, 90, 90)
        
        x = start_x + i * (HEART_SIZE + HEART_GAP) #each heart postion
        draw_heart(screen, x, y, HEART_SIZE, color)#draw heart

def draw_center_message(screen, message, width, height, color=(255, 255, 255)):
    font = pygame.font.SysFont(None, 72) #creates the font (default font, font size)
    text_surface = font.render(message, True, color) #render message
    text_rect = text_surface.get_rect(center=(width // 2, height // 2)) #the text is centered in the middle

    # Dim the background
    overlay = pygame.Surface((width, height), pygame.SRCALPHA) #create a full screen SRCALPHA-> allows transparency
    overlay.fill((0, 0, 0, 140))#semi-transparent with alpha
    screen.blit(overlay, (0, 0))#covers all the screen with dark layer
    screen.blit(text_surface, text_rect)#plaes the message above overlay

#Shows winner after finishing all the levels
def show_winner_and_exit(screen, width, height):
    print("You Win!")
    draw_center_message(screen, "WINNER", width, height)
    pygame.display.update()
    pygame.time.delay(4000)
    pygame.quit()
    sys.exit()
 
def main():
    cur_lvl = 1
    lives = MAX_LIVES
    g = Grid(levels[cur_lvl][0], levels[cur_lvl][1]) #Creating Grid object instance
    player_spawn, robot_spawn = g.generate_grid(levels[cur_lvl][2]) #Generating the grid, getting the player spawn (tuple) and the robot spawn (array of tuples)
    grid_map = g.getGrid().T #Getting the grid as a numpy array
    #print(grid_map) it's flipped omg
    grid_size = g.getSize() #returns a tuple of (x,y)

    #Creating the Player instance
    player = Player(player_spawn[1], player_spawn[0]) # x-> horizontal & y -> vertical
    #Player position represented on the flipped numpy array
    
    #Creating the Robot instances
    robots = [Robot(spawn[1], spawn[0]) for spawn in robot_spawn] #Creating an array of Robot instances 
    
    # ---------------
    # MAIN CONSTANTS (theyre now main variables loll)
    # ---------------
    height = TILE_SIZE * grid_size[0]
    width = TILE_SIZE * grid_size[1]

    # Game Window
    screen = pygame.display.set_mode((width, height)) #Size 
    pygame.display.set_caption("level 1") #Title
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    clock = pygame.time.Clock()
    tile_images = load_tile_images()
    entity_images = load_entity_images()
    robot_move_interval_ms = 450 #only move once every 450 ms
    robot_timer_ms = 0 #counts passed time
    #build grid and player at first frame
    buildGrid(grid_map, grid_size, screen, tile_images) 
    draw_player(screen, player, entity_images)
    draw_robots(screen, robots, entity_images)
    player_moved = False #flag so robots move after player
    player_sinking = False #flag to handle player in quicksand
    player_sinking_timer = 0 
    player_sinking_time = robot_move_interval_ms * 2 #player impaired for 2 moves
    level_timer = 0
    #The while loop keeps on running to check for events, the events check for the type of event, if key is prssed, next pos is set
    #then we update the player pos and redraw the grid with the new position
    while True: #While true loop to keep it from closing (just like in opengl)
        dt_ms = clock.tick(60)
        robot_timer_ms += dt_ms #Add the time
        #game won't start until the player moves in a level
        if player_moved is True:
            level_timer += dt_ms
        #if the player is sinking...
        if player_sinking == True:
            #... and the player sank for enough time, let him free...
            if player_sinking_timer >= player_sinking_time:
                player_sinking_timer = 0
                player_sinking = False
                pygame.event.clear(pygame.KEYDOWN) #flush the event queue so inputs while stuck dont get detected at once
            #... otherwise, advance the timer and ignore all events (dont let him move)
            else:
                player_sinking_timer += dt_ms
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if player_sinking is True:
                draw_robots(screen, robots, entity_images) #Robot redraw incase the robot hasn't been moved
                continue
            if event.type == pygame.KEYDOWN and event.key in valid_inputs: #If key is pressed, and in the valid key inputs
                player_moved = True
                buildGrid(grid_map, grid_size, screen, tile_images) #rebuild the grid at every new input, it will be drawn over the characters and robots
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
                    # one enter, move to next level, just for debugging purposes, u can delete this safely
                    print(f"GG, level {cur_lvl} completed in {level_timer/1000:.2f} seconds.")
                    if cur_lvl >= max_lvl:#when comlpleting all the levels it runs the function
                        show_winner_and_exit(screen, width, height)
                    if cur_lvl < max_lvl:
                        cur_lvl += 1
                    g = Grid(levels[cur_lvl][0], levels[cur_lvl][1])
                    player_spawn, robot_spawn = g.generate_grid(levels[cur_lvl][2])
                    grid_map = g.getGrid().T
                    grid_size = g.getSize()
                    height = TILE_SIZE * grid_size[0]
                    width = TILE_SIZE * grid_size[1]
                    player = Player(player_spawn[1], player_spawn[0])
                    robots = [Robot(spawn[1], spawn[0]) for spawn in robot_spawn]
                    screen = pygame.display.set_mode((width, height))
                    pygame.display.set_caption(f"level {cur_lvl}")
                    os.environ['SDL_VIDEO_CENTERED'] = '1'
                    buildGrid(grid_map, grid_size, screen, tile_images) 
                    draw_player(screen, player, entity_images)
                    draw_robots(screen, robots, entity_images)
                    player_moved = False
                    level_timer = 0
                    continue
                #an enum wouldn't hurt here
                if next_move is not None:
                    if grid_map[next_move[0],next_move[1]] == 4: #If hole reset the position
                        player.x , player.y = (player_spawn[1], player_spawn[0])
                    elif grid_map[next_move[0],next_move[1]] == 1: #if open path move
                        player.x, player.y = next_move
                    elif grid_map[next_move[0],next_move[1]] == 3: #if quicksand slowdown
                        player.x, player.y = next_move
                        player_sinking = True
                    elif grid_map[next_move[0],next_move[1]] == 5: #if gate, continue to next level
                        print(f"GG, level {cur_lvl} completed in {level_timer/1000:.2f} seconds.")
                        if cur_lvl >= max_lvl:#after completing all the levels in runs this function
                            show_winner_and_exit(screen, width, height)
                        if cur_lvl < max_lvl:
                            cur_lvl += 1
                        g = Grid(levels[cur_lvl][0], levels[cur_lvl][1])
                        player_spawn, robot_spawn = g.generate_grid(levels[cur_lvl][2])
                        grid_map = g.getGrid().T
                        grid_size = g.getSize()
                        height = TILE_SIZE * grid_size[0]
                        width = TILE_SIZE * grid_size[1]
                        player = Player(player_spawn[1], player_spawn[0])
                        robots = [Robot(spawn[1], spawn[0]) for spawn in robot_spawn]
                        screen = pygame.display.set_mode((width, height))
                        pygame.display.set_caption(f"level {cur_lvl}")
                        os.environ['SDL_VIDEO_CENTERED'] = '1'
                        buildGrid(grid_map, grid_size, screen, tile_images) 
                        draw_player(screen, player, entity_images)
                        draw_robots(screen, robots, entity_images)
                        player_moved = False
                        level_timer = 0
                        continue
                        
                draw_player(screen, player, entity_images) #redraw the player after each input at new position
                draw_robots(screen, robots, entity_images)  #Robot redraw incase the robot hasn't been moved
                
        if robot_timer_ms >= robot_move_interval_ms and player_moved == True: #If robot timer has passed the set time, we move the robot
            robot_timer_ms = 0
            for robot in robots:
                next_pos, detected = robot.decide_next_move(
                    (player.x, player.y),
                    grid_map.shape,
                    grid_map
                )
                if grid_map[next_pos[0], next_pos[1]] == 4: #If the next position will be a hole
                    robot.reset_after_hole((next_pos[0], next_pos[1]))
                else:
                    robot.current_pos = next_pos #Set new position 
            buildGrid(grid_map, grid_size, screen, tile_images)
            draw_player(screen, player, entity_images) #We include this here, in case the user didnt move the player at 
            # a specific iteration to redraw it regardless
            draw_robots(screen, robots, entity_images)

            if any(robot.current_pos == (player.x, player.y) for robot in robots):
                lives -= 1
                # Redraw immediately so heart HUD reflects the lost life before any delay.
                buildGrid(grid_map, grid_size, screen, tile_images)
                draw_player(screen, player, entity_images)
                draw_robots(screen, robots, entity_images)
                draw_lives(screen, lives, width)
                pygame.display.update()
                if lives < 1:
                    print("Game Over!")
                    draw_center_message(screen, "GAME OVER", width, height)
                    pygame.display.update()
                    pygame.time.delay(4000) 
                    pygame.quit()
                    sys.exit()
                player.x, player.y = (player_spawn[1], player_spawn[0])
        draw_lives(screen, lives, width)#redraws the hearts according to each loop with the right colors
        #anything drawn here will be redrawn every frame, which is not necessary for our use case
        pygame.display.update() #Display the grid after building it
    

def buildGrid(gridArr, grid_size, screen, tile_images=None):
    if tile_images is None:
        tile_images = {}
    for row in range(0,grid_size[0]):
        for col in range(0, grid_size[1]):
            rect = pygame.Rect(col*TILE_SIZE,row*TILE_SIZE,TILE_SIZE, TILE_SIZE) #pygame places the rectangle on the window using
            #the x and y coordinates of the top-left corner of the rectangle, but we need to multiply x and y by the 
            #tilesize to determine its placement on the window itself. The 2 others args represent the size of the rectangle
            #Another note is that we flip row and column location because unlike in arrays where origin is the top left,
            #here the origin is bottom left (axis form), where horizontal -> x [LEFT -> RIGHT] and vertical -> Y (DOWN -> UP)
            val = gridArr[col, row] #will be used to determine the color
            pygame.draw.rect(screen, COLOR_MAP[val], rect, 0) # (surface, color, shape, border_width)
            if val in tile_images:
                screen.blit(tile_images[val], rect.topleft)

def draw_player(screen, player, entity_images):
    rect = pygame.Rect(player.x * TILE_SIZE, player.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    if entity_images and "player" in entity_images:
        screen.blit(entity_images["player"], rect.topleft)
    else:
        pygame.draw.rect(screen, GREEN, rect, 0)

def draw_robots(screen, robots, entity_images):
    for robot in robots:
        rect = pygame.Rect(robot.current_pos[0] * TILE_SIZE, robot.current_pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        if entity_images and "robot" in entity_images:
            screen.blit(entity_images["robot"], rect.topleft)
        else:
            pygame.draw.rect(screen, MAGENTA, rect, 0)

main()

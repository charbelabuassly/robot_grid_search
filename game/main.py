# Import system and OS libraries for path manipulation and system exit
import sys
import os
# Add the parent directory to Python's path so we can import modules from the project root
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# Import the Player class for handling player mechanics
from player import Player
# Import the Robot class for handling AI enemy mechanics
from robot import Robot
# Import pygame library for graphics, input, and game loop
import pygame
# Import the Grid class for generating game level maps
from grid.grid import Grid

# ----------
# CONSTANTS
# ----------
# Size of each tile in pixels (used for rendering and positioning all game objects)
TILE_SIZE = 20 #20 pixels

# Define colors as RGB tuples (Red, Green, Blue values from 0-255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHTGRAY = (200, 200, 200)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
MAGENTA = (255, 0, 255)
TRANSPARENT_GREEN = (0, 255, 0, 64)

# Dictionary that maps grid tile values to their display colors for rendering
# Allows easy tile type identification and visual feedback
COLOR_MAP = {
    0: LIGHTGRAY,   # Unused (kept for safety)
    1: LIGHTGRAY,   # Open Path (Gray) - walkable tiles
    2: BLACK,       # Wall - solid obstacles
    3: YELLOW,      # Quicksand - slows player movement
    4: RED,         # Hole - instant death hazard
    5: BLUE,        # Gate - level exit/completion trigger
    6: GREEN,       # Player spawn - starting position
    7: MAGENTA      # Robot spawn - enemy starting position
}

# Dictionary defining all 6 levels with (height, width, robot_count)
# Levels increase in difficulty with larger maps and more enemies
levels = {
    1: (20, 30, 2),   # Level 1: 20x30 grid, 2 robots
    2: (20, 30, 3),   # Level 2: 20x30 grid, 3 robots
    3: (30, 30, 4),   # Level 3: 30x30 grid, 4 robots
    4: (30, 30, 6),   # Level 4: 30x30 grid, 6 robots
    5: (30, 60, 8),   # Level 5: 30x60 grid, 8 robots
    6: (30, 60, 10)   # Level 6: 30x60 grid, 10 robots
}
# Store the maximum level number for win condition checking
max_lvl = 6
    
# Initialize pygame library to enable graphics, sound, and input handling
pygame.init()
# Define which keyboard keys are valid inputs for player movement
valid_inputs = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_RETURN]

# UI related values - these control the display of player health/lives
TILE_SIZE = 20           # Size of each tile in pixels (redefined here for consistency)
MAX_LIVES = 5            # Maximum number of lives player can have before game over
HEART_SIZE = 16          # Size of each heart in the health display
HEART_GAP = 6            # Pixel gap between each heart in the HUD
HUD_PADDING = 10         # Padding from screen edges for HUD elements

# Function to load and resize tile images for the game environment
def load_tile_images():
    # Construct the path to the photos directory in the project root
    photos_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "photos")
    # Initialize empty dictionary to store tile images
    images = {}
    # Map tile type IDs to their corresponding image filenames
    tile_files = {
        1: "path.png",           # Open path tile
        2: "wall.png",           # Wall tile
        3: "quicksand.png",      # Quicksand tile
        4: "hole.png",           # Hole tile
        5: "gate.png",           # Gate/exit tile
    }
    # Loop through each tile type and load its image
    for tile, filename in tile_files.items():
        # Construct full file path for the tile image
        file_path = os.path.join(photos_dir, filename)
        # Check if the image file exists before attempting to load
        if os.path.exists(file_path):
            # Load the image with transparency support
            img = pygame.image.load(file_path).convert_alpha()
            # Scale the image to match TILE_SIZE and store in dictionary
            images[tile] = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    # Return dictionary of loaded and scaled tile images
    return images

# Function to load and resize entity images (player and robot sprites)
def load_entity_images():
    # Construct the path to the photos directory in the project root
    photos_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "photos")
    # Initialize empty dictionary to store entity images
    images = {}
    # Construct file paths for player and robot image files
    player_path = os.path.join(photos_dir, "player.png")
    robot_path = os.path.join(photos_dir, "robot.png")

    # Check if player image exists and load it
    if os.path.exists(player_path):
        # Load player image with transparency support (convert_alpha)
        p = pygame.image.load(player_path).convert_alpha()
        # Scale the player image to tile size and store in dictionary
        images["player"] = pygame.transform.scale(p, (TILE_SIZE, TILE_SIZE))
    # Check if robot image exists and load it
    if os.path.exists(robot_path):
        # Load robot image with transparency support
        r = pygame.image.load(robot_path).convert_alpha()
        # Scale the robot image to tile size and store in dictionary
        images["robot"] = pygame.transform.scale(r, (TILE_SIZE, TILE_SIZE))

    # Return dictionary of loaded and scaled entity images
    return images

# Function to draw a single heart shape on the screen (used for health display)
# Parameters: screen (pygame surface), x/y (position), size (heart dimensions), color (RGB tuple)
def draw_heart(screen, x, y, size, color=(160, 0, 0)):
    # Calculate radius of each circular part of the heart
    r = size // 4
    # Calculate center positions for the left and right circular parts of the heart
    left_center = (x + r, y + r)
    right_center = (x + 3 * r, y + r)
    # Draw the left circular part of the heart
    pygame.draw.circle(screen, color, left_center, r)
    # Draw the right circular part of the heart
    pygame.draw.circle(screen, color, right_center, r)
    # Draw the triangular bottom point of the heart using polygon
    # Points represent: left corner, right corner, bottom point
    pygame.draw.polygon(screen, color, [(x, y + r), (x + size, y + r), (x + size // 2, y + size)])

# Function to draw all hearts in the health bar (health display on HUD)
def draw_lives(screen, lives, width):
    # Calculate total width needed to display all 5 hearts with gaps
    total_w = MAX_LIVES * HEART_SIZE + (MAX_LIVES - 1) * HEART_GAP
    # Calculate starting x position to place hearts in top-right corner
    start_x = width - HUD_PADDING - total_w
    # Y position for hearts (near top of screen)
    y = HUD_PADDING
    # Loop through each of the 5 heart positions
    for i in range(MAX_LIVES):
        # If heart index is less than current lives, draw it in red (active heart)
        if i < lives:
            color = (160, 0, 0)  # Red color for active lives
        # Otherwise draw the heart in gray (lost life)
        else:
            color = (90, 90, 90)  # Gray color for lost lives
        
        # Calculate x position for this heart (accounting for spacing)
        x = start_x + i * (HEART_SIZE + HEART_GAP)
        # Draw the heart at the calculated position
        draw_heart(screen, x, y, HEART_SIZE, color)

# Function to display a message centered on the screen with a dark overlay background
# This creates a dramatic effect by darkening the entire screen and displaying text on top
# Parameters: 
#   - message (string): text to display on screen
#   - width (int): screen width in pixels (used for centering)
#   - height (int): screen height in pixels (used for centering)
#   - color (tuple): RGB color values for the text (default is white)
def draw_center_message(screen, message, width, height, color=(255, 255, 255)):
    # Create a font object for rendering text onto the screen
    # Using SysFont with default font and size 72 (large, readable text)
    # None means use the system default font, 72 is the font size in pixels
    font = pygame.font.SysFont(None, 72)
    
    # Render the message text as a pygame Surface
    # Parameters: (text_string, anti_aliasing, color)
    # anti_aliasing=True smooths the text edges for better appearance
    # This creates a renderable image of the text
    text_surface = font.render(message, True, color)
    
    # Get a rectangle object that represents the bounding box (boundaries) of the text
    # get_rect() returns a Rect object with the same size as the text image
    # Without parameters, it would default to position (0, 0)
    # BUT we pass center=(width // 2, height // 2) which REPOSITIONS the rectangle
    # center= tells get_rect to position the rectangle so its CENTER is at screen center
    # This is key: we're not moving the text yet, just calculating WHERE it should go
    # text_rect stores: the x, y, width, and height of where the text will be drawn
    # So text_rect.topleft gives us the top-left corner where we need to draw the text
    text_rect = text_surface.get_rect(center=(width // 2, height // 2))

    # Create a transparent surface layer that covers the entire screen
    # pygame.SRCALPHA allows us to use transparency (alpha blending)
    # (width, height) matches screen dimensions so overlay covers everything
    # This surface will be used to darken the background behind the message
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Fill the overlay surface with semi-transparent black color
    # (0, 0, 0) is black in RGB
    # 140 is the alpha value (transparency level, 0=transparent, 255=opaque)
    # Higher alpha = more opaque/darker overlay
    # This creates the darkening effect that makes the message stand out
    overlay.fill((0, 0, 0, 140))
    
    # Draw (blit) the darkened overlay onto the screen at position (0, 0)
    # This covers the entire screen with the semi-transparent dark layer
    # (0, 0) is the top-left corner, so it fills everything from there
    screen.blit(overlay, (0, 0))
    
    # Draw the message text on top of the darkened overlay
    # Blit the text surface onto the screen at the calculated centered position
    # text_rect.topleft gives the top-left corner of the centered text rectangle
    # Text appears white (or specified color) on top of the dark overlay
    screen.blit(text_surface, text_rect)

# Function to display "WINNER" message and exit the game after completing all levels
def show_winner_and_exit(screen, width, height):
    # Print victory message to console
    print("You Win!")
    # Draw centered "WINNER" message on screen with overlay
    draw_center_message(screen, "WINNER", width, height)
    # Update the display to show the winner screen
    pygame.display.update()
    # Delay for 4 seconds so player can see the victory screen
    pygame.time.delay(4000)
    # Close pygame
    pygame.quit()
    # Exit the entire program
    sys.exit()
 
def main():
    # Initialize current level to 1 (starting level)
    cur_lvl = 1
    # Set player starting lives to maximum
    lives = MAX_LIVES
    # Create a Grid object for the current level with specified dimensions
    g = Grid(levels[cur_lvl][0], levels[cur_lvl][1])
    # Generate the grid and get the player spawn location and all robot spawn locations
    player_spawn, robot_spawn = g.generate_grid(levels[cur_lvl][2])
    # Get the grid as a transposed numpy array (flipped for correct coordinate system)
    grid_map = g.getGrid().T
    # Get the dimensions of the grid (height, width)
    grid_size = g.getSize()

    # Create the Player instance at the spawn position
    # Note: swap x and y because numpy arrays use [row, col] but we need [x, y]
    player = Player(player_spawn[1], player_spawn[0])
    
    # Create a list of Robot instances, one for each robot spawn point
    robots = [Robot(spawn[1], spawn[0]) for spawn in robot_spawn]
    
    # ---------------
    # MAIN CONSTANTS (theyre now main variables loll)
    # ---------------
    # Calculate screen height in pixels (grid height * tile size)
    height = TILE_SIZE * grid_size[0]
    # Calculate screen width in pixels (grid width * tile size)
    width = TILE_SIZE * grid_size[1]

    # Create the pygame window with calculated width and height
    screen = pygame.display.set_mode((width, height))
    # Set the window title to show current level
    pygame.display.set_caption("level 1")
    # Center the window on the screen
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    # Create a clock object to control frame rate
    clock = pygame.time.Clock()
    # Load all tile images and store them for rendering
    tile_images = load_tile_images()
    # Load all entity images (player and robot sprites)
    entity_images = load_entity_images()
    # Set the interval for robot movement (in milliseconds)
    robot_move_interval_ms = 450
    # Initialize robot movement timer counter
    robot_timer_ms = 0
    
    # Draw the initial grid and entities at game start
    buildGrid(grid_map, grid_size, screen, tile_images)
    # Draw player at starting position
    draw_player(screen, player, entity_images)
    # Draw all robots at their starting positions
    draw_robots(screen, robots, entity_images)
    
    # Flag to track whether player has moved (starts robots after first move)
    player_moved = False
    # Flag to track if player is currently stuck in quicksand
    player_sinking = False
    # Timer for how long player has been sinking
    player_sinking_timer = 0
    # Duration player is impaired by quicksand (2 robot move intervals)
    player_sinking_time = robot_move_interval_ms * 2
    # Timer to track level completion time
    level_timer = 0
    
    # Main game loop that runs until player quits or game over
    while True:
        # Get delta time (milliseconds since last frame) and cap frame rate at 60 FPS
        dt_ms = clock.tick(60)
        # Add elapsed time to robot movement timer
        robot_timer_ms += dt_ms
        
        # Only count level time after player has made their first move
        if player_moved is True:
            level_timer += dt_ms
            
        # Handle player being stuck in quicksand
        if player_sinking == True:
            # Check if player has been sinking long enough to be freed
            if player_sinking_timer >= player_sinking_time:
                # Reset the sinking timer
                player_sinking_timer = 0
                # End the sinking state
                player_sinking = False
                # Clear input queue so buffered inputs don't execute immediately
                pygame.event.clear(pygame.KEYDOWN)
            # If still sinking, advance timer and ignore player input
            else:
                # Increment the sinking duration timer
                player_sinking_timer += dt_ms
                
        # Process all pygame events (input, quit, etc.)
        for event in pygame.event.get():
            # Check if player has closed the window
            if event.type == pygame.QUIT:
                # Close pygame
                pygame.quit()
                # Exit the program
                sys.exit()
                
            # If player is sinking, skip input processing but redraw robots
            if player_sinking is True:
                # Redraw robots in case they moved while player was sinking
                draw_robots(screen, robots, entity_images)
                # Skip the rest of the event processing
                continue
                
            # Check if a key was pressed and it's a valid input key
            if event.type == pygame.KEYDOWN and event.key in valid_inputs:
                # Mark that the player has moved (starts robot AI)
                player_moved = True
                # Redraw the grid (clears previous player/robot positions)
                buildGrid(grid_map, grid_size, screen, tile_images)
                
                # Determine next move based on which arrow key was pressed
                if event.key == pygame.K_LEFT:
                    # Move player left (decrease x)
                    next_move = (player.x - 1, player.y)
                elif event.key == pygame.K_RIGHT:
                    # Move player right (increase x)
                    next_move = (player.x + 1, player.y)
                elif event.key == pygame.K_UP:
                    # Move player up (decrease y)
                    next_move = (player.x, player.y - 1)
                elif event.key == pygame.K_DOWN:
                    # Move player down (increase y)
                    next_move = (player.x, player.y + 1)
                elif event.key == pygame.K_RETURN:
                    # DEBUG: Enter key advances to next level (for testing purposes)
                    # Print completion time for current level
                    print(f"GG, level {cur_lvl} completed in {level_timer/1000:.2f} seconds.")
                    # Check if player has completed all levels (win condition)
                    if cur_lvl >= max_lvl:
                        # Call win screen and exit
                        show_winner_and_exit(screen, width, height)
                    # If not at max level, advance to next level
                    if cur_lvl < max_lvl:
                        # Increment level counter
                        cur_lvl += 1
                    # Create new grid for next level
                    g = Grid(levels[cur_lvl][0], levels[cur_lvl][1])
                    # Generate the new level
                    player_spawn, robot_spawn = g.generate_grid(levels[cur_lvl][2])
                    # Get the new grid map
                    grid_map = g.getGrid().T
                    # Get new grid dimensions
                    grid_size = g.getSize()
                    # Calculate new screen dimensions
                    height = TILE_SIZE * grid_size[0]
                    width = TILE_SIZE * grid_size[1]
                    # Create new player at spawn point
                    player = Player(player_spawn[1], player_spawn[0])
                    # Create new robots at their spawn points
                    robots = [Robot(spawn[1], spawn[0]) for spawn in robot_spawn]
                    # Resize the game window for new level dimensions
                    screen = pygame.display.set_mode((width, height))
                    # Update window title to show new level
                    pygame.display.set_caption(f"level {cur_lvl}")
                    # Center the window
                    os.environ['SDL_VIDEO_CENTERED'] = '1'
                    # Draw the new level
                    buildGrid(grid_map, grid_size, screen, tile_images)
                    # Draw player at new spawn
                    draw_player(screen, player, entity_images)
                    # Draw robots at new spawns
                    draw_robots(screen, robots, entity_images)
                    # Reset player moved flag
                    player_moved = False
                    # Reset level timer for new level
                    level_timer = 0
                    # Skip the movement processing below
                    continue
                    
                # Execute the player's movement if a direction key was pressed
                if next_move is not None:
                    # Check if the next tile is a hole (hazard - tile value 4)
                    if grid_map[next_move[0],next_move[1]] == 4:
                        # Decrement player lives when hitting a hole
                        lives -= 1
                        # Redraw grid without player/robot positions
                        buildGrid(grid_map, grid_size, screen, tile_images)
                        # Redraw player at original position
                        draw_player(screen, player, entity_images)
                        # Redraw robots at their positions
                        draw_robots(screen, robots, entity_images)
                        # Update HUD to show reduced lives
                        draw_lives(screen, lives, width)
                        # Update the display
                        pygame.display.update()
                        # Check if player is out of lives (game over condition)
                        if lives < 1:
                            # Print game over message
                            print("Game Over!")
                            # Display game over screen
                            draw_center_message(screen, "Game Over", width, height)
                            # Update display
                            pygame.display.update()
                            # Delay before closing (let player see message)
                            pygame.time.delay(4000)
                            # Close pygame
                            pygame.quit()
                            # Exit program
                            sys.exit()
                        # Reset all robots to spawn points
                        reset_robot(robots, player)
                        # Reset player to spawn point
                        player.x , player.y = (player_spawn[1], player_spawn[0])
                    # Check if next tile is open path (passable - tile value 1)
                    elif grid_map[next_move[0],next_move[1]] == 1:
                        # Move player to new position
                        player.x, player.y = next_move
                    # Check if next tile is quicksand (tile value 3)
                    elif grid_map[next_move[0],next_move[1]] == 3:
                        # Move player to quicksand tile
                        player.x, player.y = next_move
                        # Mark player as sinking (impaired for next 2 moves)
                        player_sinking = True
                    # Check if next tile is the gate/exit (tile value 5)
                    elif grid_map[next_move[0],next_move[1]] == 5:
                        # Print level completion time
                        print(f"GG, level {cur_lvl} completed in {level_timer/1000:.2f} seconds.")
                        # Check if this was the final level
                        if cur_lvl >= max_lvl:
                            # Show winner screen and exit
                            show_winner_and_exit(screen, width, height)
                        # If not final level, advance to next
                        if cur_lvl < max_lvl:
                            # Increment level counter
                            cur_lvl += 1
                        # Create new grid for next level
                        g = Grid(levels[cur_lvl][0], levels[cur_lvl][1])
                        # Generate the new level
                        player_spawn, robot_spawn = g.generate_grid(levels[cur_lvl][2])
                        # Get grid map
                        grid_map = g.getGrid().T
                        # Get grid dimensions
                        grid_size = g.getSize()
                        # Calculate screen dimensions
                        height = TILE_SIZE * grid_size[0]
                        width = TILE_SIZE * grid_size[1]
                        # Create player at spawn
                        player = Player(player_spawn[1], player_spawn[0])
                        # Create robots at their spawns
                        robots = [Robot(spawn[1], spawn[0]) for spawn in robot_spawn]
                        # Resize window for new dimensions
                        screen = pygame.display.set_mode((width, height))
                        # Update window title
                        pygame.display.set_caption(f"level {cur_lvl}")
                        # Center window
                        os.environ['SDL_VIDEO_CENTERED'] = '1'
                        # Draw new level
                        buildGrid(grid_map, grid_size, screen, tile_images)
                        # Draw player
                        draw_player(screen, player, entity_images)
                        # Draw robots
                        draw_robots(screen, robots, entity_images)
                        # Reset player moved flag
                        player_moved = False
                        # Reset level timer
                        level_timer = 0
                        # Skip remaining event processing
                        continue
                        
                # Redraw player at new position after movement
                draw_player(screen, player, entity_images)
                # Redraw robots in case they were positioned differently
                draw_robots(screen, robots, entity_images)
                
        # Execute robot AI movement if enough time has passed and player has started
        if robot_timer_ms >= robot_move_interval_ms and player_moved == True:
            # Reset robot movement timer
            robot_timer_ms = 0
            # Process each robot's movement
            for robot in robots:
                # Calculate the robot's next position using A* or patrol pathfinding
                next_pos, detected = robot.decide_next_move(
                    (player.x, player.y),
                    grid_map.shape,
                    grid_map
                )
                # Check if robot's next position is a hole
                if grid_map[next_pos[0], next_pos[1]] == 4:
                    # Reset robot to spawn point (hole respawn mechanic)
                    robot.reset_after_hole((next_pos[0], next_pos[1]))
                # Otherwise move robot normally
                else:
                    # Update robot's current position
                    robot.current_pos = next_pos
            # Redraw the grid (clears old positions)
            buildGrid(grid_map, grid_size, screen, tile_images)
            # Redraw player (in case they didn't move this frame)
            draw_player(screen, player, entity_images)
            # Redraw all robots at new positions
            draw_robots(screen, robots, entity_images)

            # Check if any robot occupies the same tile as player (collision = caught by robot)
            if any(robot.current_pos == (player.x, player.y) for robot in robots):
                # Decrement player lives
                lives -= 1
                # Redraw everything to reflect life loss
                buildGrid(grid_map, grid_size, screen, tile_images)
                draw_player(screen, player, entity_images)
                draw_robots(screen, robots, entity_images)
                # Update HUD with new life count
                draw_lives(screen, lives, width)
                # Display the update
                pygame.display.update()
                # Check if player is out of lives
                if lives < 1:
                    # Print game over message
                    print("Game Over!")
                    # Display game over screen
                    draw_center_message(screen, "GAME OVER", width, height)
                    # Update display
                    pygame.display.update()
                    # Delay before closing
                    pygame.time.delay(4000)
                    # Close pygame
                    pygame.quit()
                    # Exit program
                    sys.exit()
                # Reset robots to spawn points
                reset_robot(robots, player)
                # Reset player to spawn point
                player.x, player.y = (player_spawn[1], player_spawn[0])
                
        # Draw the health bar on screen (updated each frame)
        draw_lives(screen, lives, width)
        # Update the display with all drawn elements
        pygame.display.update()
    

# Function to render the game grid (all tiles) on the screen
# Parameters: gridArr (numpy array of tile types), grid_size (dimensions), screen (pygame surface), tile_images (dict of loaded images)
def buildGrid(gridArr, grid_size, screen, tile_images=None):
    # Initialize empty tile_images dict if none provided
    if tile_images is None:
        tile_images = {}
    # Loop through each row of the grid
    for row in range(0, grid_size[0]):
        # Loop through each column in the current row
        for col in range(0, grid_size[1]):
            # Create a rectangle for this tile at its screen position
            # X and Y positions are calculated by multiplying grid coords by tile size
            # Width and height are both TILE_SIZE
            rect = pygame.Rect(col*TILE_SIZE, row*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            # Note: We multiply column by TILE_SIZE for x (horizontal) and row by TILE_SIZE for y (vertical)
            # This is because the grid array uses [row, column] but pygame uses (x, y) coordinates
            
            # Get the tile type value from the grid
            val = gridArr[col, row]
            # Draw a solid rectangle with the color corresponding to this tile type
            # Parameters: surface, color, rectangle, border_width (0 = filled)
            pygame.draw.rect(screen, COLOR_MAP[val], rect, 0)
            # If a custom image exists for this tile type, draw it on top
            if val in tile_images:
                # Blit the tile image at the rectangle's top-left position
                screen.blit(tile_images[val], rect.topleft)

# Function to draw the player sprite on the screen
# Parameters: screen (pygame surface), player (Player object), entity_images (dict of loaded images)
def draw_player(screen, player, entity_images):
    # Create a rectangle at the player's grid position, scaled to pixels
    rect = pygame.Rect(player.x * TILE_SIZE, player.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    # Check if player image exists and draw it
    if entity_images and "player" in entity_images:
        # Draw the player sprite image
        screen.blit(entity_images["player"], rect.topleft)
    # If no image is available, draw a green rectangle as placeholder
    else:
        pygame.draw.rect(screen, GREEN, rect, 0)

# Function to draw all robot sprites on the screen
# Parameters: screen (pygame surface), robots (list of Robot objects), entity_images (dict of loaded images)
def draw_robots(screen, robots, entity_images):
    # Loop through each robot in the list
    for robot in robots:
        # Create a rectangle at the robot's current grid position, scaled to pixels
        rect = pygame.Rect(robot.current_pos[0] * TILE_SIZE, robot.current_pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        # Check if robot image exists and draw it
        if entity_images and "robot" in entity_images:
            # Draw the robot sprite image
            screen.blit(entity_images["robot"], rect.topleft)
        # If no image is available, draw a magenta rectangle as placeholder
        else:
            pygame.draw.rect(screen, MAGENTA, rect, 0)

# Function to reset all robots to their spawn positions after being caught or hitting a hole
# Parameters: robots (list of Robot objects), player (Player object)
def reset_robot(robots, player):
    # Loop through each robot
    for robot in robots:
        # Check if the robot is at the same position as the player
        if robot.current_pos == (player.x, player.y):
            # Clear the robot's planned movement path
            robot.path = []
            # Reset robot position to its spawn point
            robot.current_pos = robot.spawn_pos
            # Clear the robot's last seen player position (for AI hunting)
            robot.last_seen = None

# Entry point: call main function to start the game
main()

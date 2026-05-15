# Import system libraries for path manipulation
import sys
import os
# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# Import the State enum for robot AI states
from state import State
# Import random for probabilistic decision making
import random
# Import deque for efficient BFS queue operations
from collections import deque
# Import Grid class for passable tile checking
from grid.grid import Grid
# Import numpy for efficient array operations
import numpy as np

# Robot class representing enemy AI entities in the game
class Robot:    
    # Static constant: probability a robot will risk taking a hole during exploration
    HOLE_PROBABILITY = 0.2
    
    # Initialize a new robot instance
    def __init__(self, x, y):
        # Store the spawn position (starting location) as a tuple (x, y)
        self.spawn_pos = (x,y)
        # Set initial AI state to PATROL (passive wandering behavior)
        self.state = State.PATROL
        # Initialize last seen player position as None (not yet spotted)
        self.last_seen = None
        # Initialize empty path list (will hold planned movement path from pathfinding)
        self.path = []
        # Set current position to spawn position (start at spawn point)
        self.current_pos = (x,y)
        # Initialize empty list to store remembered hole positions (to avoid them)
        self.hole_pos = []
        
    # -----------------
    # HELPER FUNCTIONS
    # -----------------
    # Static method: randomly choose a valid walkable position on the grid
    # Parameters: gridsize (tuple of grid dimensions), grid_map (numpy array of tile types)
    @staticmethod
    def choose_valid_point(gridsize, grid_map):
        # Keep trying until a valid passable point is found
        while True:
            # Generate random x coordinate within grid bounds
            x = random.randint(0, gridsize[0] - 1)
            # Generate random y coordinate within grid bounds
            y = random.randint(0 , gridsize[1] - 1)
            # Check if the randomly chosen tile is passable (walkable)
            if grid_map[x,y] in Grid.passable:
                # Return the valid position as a tuple
                return (x,y)
    
    # -----------------
    # SENSE / DETECTION
    # -----------------
    # Static method: detect if enemy (player) is within range and visible
    # Parameters: player_pos, robot_pos (tuples), grid_map (numpy array), gridsize (tuple)
    @staticmethod
    def detect_enemy(player_pos, robot_pos, grid_map, gridsize):
        # Check if player is within detection range using Manhattan distance
        if not Robot.manhattan_distance(player_pos, robot_pos, gridsize):
            # Player is outside detection range, so not detected
            return False
        # If in range, check if line of sight is blocked by walls or holes
        else:
            # Return True if line of sight is clear (no blocking obstacles)
            return Robot.check_blocking(player_pos, robot_pos, grid_map)

    # Static method: calculate Manhattan distance between two positions
    # Parameters: player_pos, robot_pos (tuples), gridsize (tuple)
    @staticmethod
    def manhattan_distance(player_pos, robot_pos, gridsize):
        # Calculate Manhattan distance: sum of absolute differences in coordinates
        d = abs(player_pos[0] - robot_pos[0]) + abs(player_pos[1] - robot_pos[1])
        # Detection range is at least 5 tiles or 1/8 of the grid size (whichever is larger)
        if d <= max(5, (gridsize[0] + gridsize[1]) // 8):
            # Within detection range
            return True
        # Outside detection range
        return False
    
    # Static method: draw a line between two points to check for blocking obstacles
    # This is used to detect line-of-sight across diagonal angles
    # Parameters: x1, x2, y1, y2 (coordinates), grid_map (numpy array)
    @staticmethod
    def naiveDrawLine(x1, x2, y1, y2, grid_map):
        # Calculate slope between two points (rise over run)
        # m represents the steepness of the line
        m = (y2 - y1) / (x2 - x1)
        # Calculate y-intercept using point-slope form: y = mx + c
        # Rearranged to: c = y - mx
        c = y1 - m * x1

        # Ensure iteration goes left to right (find min and max x values)
        x_start = min(x1, x2)  # Starting x coordinate (smaller value)
        x_end = max(x1, x2)    # Ending x coordinate (larger value)
        
        # Get grid dimensions to check bounds
        height, width = grid_map.shape
        # For each x coordinate along the line, check for obstacles
        for x in range(x_start, x_end + 1):
            # Calculate corresponding y coordinate on the line using linear equation
            # Round to nearest integer to get valid grid coordinate
            y = round(m * x + c)
            # Check if calculated point is outside grid boundaries
            if x < 0 or x >= height or y < 0 or y >= width:
                # Skip this point if out of bounds
                continue
            # Check if this position contains a blocking tile (wall=2 or hole=4)
            if grid_map[x, y] in [2, 4]:
                # Line of sight is blocked
                return False
        # No obstacles found along the entire line
        return True

    # Static method: check if line of sight between robot and player is blocked
    # Parameters: player_pos, robot_pos (tuples), grid_map (numpy array)
    @staticmethod
    def check_blocking(player_pos, robot_pos, grid_map):
        # Check if player and robot share the same row (x-coordinate)
        if player_pos[0] == robot_pos[0]:
            # Extract the horizontal line segment between the two positions
            # Use min/max to ensure we read from left to right
            arr = grid_map[player_pos[0], min(robot_pos[1],player_pos[1]) : max(robot_pos[1],player_pos[1])]
            # Count blocking tiles (walls=2 or holes=4) in the segment
            if np.isin(arr,[2 , 4]).sum() == 0:
                # No blocking tiles found, line of sight is clear
                return True
            else:
                # Blocking tiles exist, line of sight is blocked
                return False
        # Check if player and robot share the same column (y-coordinate)
        elif player_pos[1] == robot_pos[1]:
            # Extract the vertical line segment between the two positions
            # Use min/max to ensure we read from top to bottom
            arr = grid_map[min(robot_pos[0],player_pos[0]) : max(robot_pos[0],player_pos[0]), player_pos[1]]
            # Count blocking tiles in the segment
            if np.isin(arr,[2 , 4]).sum() == 0:
                # No blocking tiles found, line of sight is clear
                return True
            else:
                # Blocking tiles exist, line of sight is blocked
                return False
        # For diagonal or arbitrary angles, use line-drawing algorithm
        # Call naiveDrawLine to check diagonal line of sight
        return Robot.naiveDrawLine(
            robot_pos[0], player_pos[0],
            robot_pos[1], player_pos[1],
            grid_map
        )
        
    # -----------------
    # PATROL FUNCTIONS
    # -----------------
    # Method: create a path for patrol by finding a valid target point using BFS
    # Parameters: gridsize (tuple), grid_map (numpy array), current_pos (tuple)
    def create_path_patrol(self, gridsize, grid_map, current_pos):
        # Maximum attempts to find a valid patrol path
        max_attempts = gridsize[0] * gridsize[1]
        # Try to find a path up to max_attempts times
        for _ in range(max_attempts):
            # Choose a random valid point as patrol target
            target_point = Robot.choose_valid_point(gridsize, grid_map)
            # Use BFS pathfinding to create path to target
            target_path = self.bfs(grid_map, current_pos, target_point)
            # If a valid path was found, return it
            if target_path != []:
                return target_path
        # If no valid path found after all attempts, return empty path
        return []
            
    # Method: breadth-first search pathfinding algorithm
    # Finds shortest path from current position to target position
    # Parameters: grid_map (numpy array), current_pos (tuple), target_point (tuple)
    def bfs(self, grid_map, current_pos, target_point):
        # Initialize queue with starting position
        # Queue stores positions to be explored (breadth-first)
        queue = deque([current_pos])
        # Set to track already visited positions (avoid cycles)
        visited = {current_pos}
        # Dictionary to track parent of each position (for path reconstruction)
        came_from = {}
        # Process queue until empty
        while queue:
            # Dequeue next position to explore
            cx, cy = queue.popleft()
            # Check if we've reached the target position
            if (cx,cy) == target_point:
                # Initialize path stack to reconstruct the path
                path_stack = []
                # Start from target position
                cur = (cx,cy)
                # Add current position to path
                path_stack.append(cur)
                # Trace back to start by following parent pointers
                while cur in came_from:
                    # Get parent position
                    cur = came_from[cur]
                    # Add parent to path
                    path_stack.append(cur)
                # Return the complete path from start to target
                return path_stack
            # Explore all 4 adjacent neighbors (up, down, left, right)
            for dnx, dny in [(-1,0),(1,0),(0,-1),(0,1)]:
                # Calculate neighbor position
                nx, ny = cx + dnx, cy + dny
                # Check if neighbor has already been visited
                if((nx, ny) in visited):
                    # Skip already visited neighbors
                    continue
                # Get the tile type at neighbor position
                tile = grid_map[nx, ny]
                # Check if tile is passable (walkable)
                if tile not in Grid.passable:
                    # Tile is not passable
                    if tile == 4:  # Check if it's a hole (tile type 4)
                        # If robot remembers this hole, skip it
                        if (nx,ny) in self.hole_pos:
                            continue
                        # Probabilistically decide whether to risk the hole
                        elif random.random() < Robot.HOLE_PROBABILITY:
                            # Take the risk and include hole in path
                            pass
                    else:
                        # Not a hole and not passable (wall), skip it
                        continue
                # Add neighbor to queue for exploration
                queue.append((nx, ny))
                # Mark neighbor as visited
                visited.add((nx, ny))
                # Record this position's parent for path reconstruction
                came_from[(nx, ny)] = (cx, cy)
        # No path found to target
        return []

                
    # Method: patrol search - get next move in patrol path
    # If no path exists, create a new one
    # Parameters: gridsize (tuple), grid_map (numpy array)
    def patrol_search(self, gridsize, grid_map):
        # Check if robot has no planned path (empty or None)
        if self.path is None or self.path == []:
            # Create a new patrol path from current position
            self.path = self.create_path_patrol(gridsize, grid_map, self.current_pos)
            
        # Pop and return next position from path (or current position if no path)
        return self.path.pop()

    # -----------------
    # CHASE FUNCTIONS
    # -----------------
    # Method: A* pathfinding algorithm for efficient chase pathfinding
    # Finds path to player using heuristic estimation
    # Parameters: grid_map (numpy array), current_pos (tuple), target_point (tuple)
    def a_star(self, grid_map, current_pos, target_point):
        # Get grid dimensions
        height, width = grid_map.shape
        # Initialize open set with starting position
        open_set = {current_pos}
        # Dictionary to track parent of each position
        came_from = {}
        # Dictionary storing actual cost to reach each position
        g_score = {current_pos: 0}
        # Dictionary storing estimated total cost (actual + heuristic) for each position
        f_score = {current_pos: Robot._heuristic(current_pos, target_point)}

        # Continue until all positions in open set are processed
        while open_set:
            # Find position in open set with lowest f_score (best candidate)
            current = min(open_set, key=lambda p: f_score.get(p, float("inf")))
            # Check if we've reached the target
            if current == target_point:
                # Initialize path stack for reconstruction
                path_stack = []
                # Start from target
                cur = current
                # Add current position
                path_stack.append(cur)
                # Trace back to start by following parent pointers
                while cur in came_from:
                    # Get parent
                    cur = came_from[cur]
                    # Add to path
                    path_stack.append(cur)
                # Return reconstructed path
                return path_stack

            # Remove current from open set (it's been processed)
            open_set.remove(current)
            # Get current position coordinates
            cx, cy = current
            # Explore all 4 neighbors
            for dnx, dny in [(-1,0),(1,0),(0,-1),(0,1)]:
                # Calculate neighbor coordinates
                nx, ny = cx + dnx, cy + dny
                # Check if neighbor is within grid bounds
                if nx < 0 or nx >= height or ny < 0 or ny >= width:
                    # Skip out of bounds neighbors
                    continue
                # Get tile type at neighbor
                tile = grid_map[nx, ny]
                # Check passability rules (same as BFS)
                if tile not in Grid.passable:
                    # Tile is not passable
                    if tile == 4:  # Check if hole
                        # If robot remembers this hole, skip it
                        if (nx, ny) in self.hole_pos:
                            continue
                        # Probabilistically decide whether to risk hole
                        if random.random() >= Robot.HOLE_PROBABILITY:
                            # Decided not to risk it, skip this neighbor
                            continue
                    else:
                        # Not a hole and not passable (wall), skip
                        continue

                # Calculate tentative g_score (cost to reach this neighbor)
                neighbor = (nx, ny)
                # Cost is current g_score + 1 (one step away)
                tentative_g = g_score[current] + 1
                # Check if this path to neighbor is better than previously found
                if tentative_g < g_score.get(neighbor, float("inf")):
                    # Update parent
                    came_from[neighbor] = current
                    # Update actual cost
                    g_score[neighbor] = tentative_g
                    # Update estimated total cost (actual + heuristic)
                    f_score[neighbor] = tentative_g + Robot._heuristic(neighbor, target_point)
                    # Add neighbor to open set for processing
                    open_set.add(neighbor)

        # No path found to target
        return []

    # Static method: Manhattan distance heuristic for A*
    # Estimates remaining distance to goal (always underestimates for admissibility)
    # Parameters: a, b (tuples representing positions)
    @staticmethod
    def _heuristic(a, b):
        # Calculate Manhattan distance between two positions
        # This is the sum of absolute differences in each dimension
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    # Method: generate path to player using A* pathfinding
    # Parameters: player_pos (tuple), gridmap (numpy array)
    def return_path(self, player_pos, gridmap):
        # Execute A* from robot's current position to player's position
        # Returns ordered path list to chase player
        return self.a_star(gridmap, self.current_pos, player_pos)
        
    # ------------------------
    # GLOBAL DECIDER FUNCTION
    # ------------------------
    # Method: main decision function that determines robot's next move based on state
    # Parameters: player_pos (tuple), gridsize (tuple), grid_map (numpy array)
    def decide_next_move(self, player_pos, gridsize, grid_map):
        # Check if robot is in passive state (PATROL or SEARCH)
        if self.state == State.PATROL or self.state == State.SEARCH:
            # Check if player is now within detection range
            if Robot.detect_enemy(player_pos, self.current_pos, grid_map, gridsize):
                # Transition to active CHASE state
                self.state = State.CHASE
            # If still in PATROL state (player not detected)
            if self.state == State.PATROL:
                # Get next patrol move from patrol pathfinding
                # Return tuple of (next_position, detected_flag)
                return (self.patrol_search(gridsize, grid_map), False)
            # If in SEARCH state (placeholder for future implementation)
            elif self.state == State.SEARCH:
                # Search state not yet implemented
                pass
        # Execute active chase behavior
        if self.state == State.CHASE:
            # Check if player has escaped (distance exceeds half grid size)
            if self._heuristic(player_pos, self.current_pos) > gridsize[0] // 2:
                # Lost the player, return to patrol
                self.state = State.PATROL  # TODO: change to SEARCH later
            else:
                # Player still in range, continue chasing
                # Generate path to player using A* pathfinding
                path = self.return_path(player_pos, grid_map)
                # Verify path is not empty
                if path != []:
                    # Ensure we don't return current position (robot must move)
                    if path[-1] == self.current_pos:
                        # Remove current position from end of path
                        # (A* returns path from target->robot, so remove robot's starting position)
                        path.pop()
                    # Check path is still not empty after cleanup
                    if path != []:
                        # Return next move in chase path
                        # detected=True indicates active chase is happening
                        return (path.pop(), True)
                # Path is empty, stay in place but remain in chase state
                return (self.current_pos, True)
        # Default fallback: continue patrol if not in active chase
        return (self.patrol_search(gridsize, grid_map), False)

    # Method: reset robot after hitting a hole
    # Clears path, returns to spawn, resets state
    # Parameters: pos (tuple of hole position where robot hit)
    def reset_after_hole(self, pos):
        # Clear any planned movement path
        self.path = []
        # Return robot to spawn position
        self.current_pos = self.spawn_pos
        # Clear last seen player position (forget where player was)
        self.last_seen = None
        # Reset state to PATROL
        self.state = State.PATROL
        # Remember this hole to avoid it in the future
        self.hole_pos.append(pos)

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from state import State
import random
from collections import deque
from grid.grid import Grid
import numpy as np

class Robot:    
    HOLE_PROBABILITY = 0.2 #Chance to decide to take a hole when exploring
    
    def __init__(self, x, y):
        self.spawn_pos = (x,y) #Spawn position
        self.state = State.PATROL #AI state
        self.last_seen = None #Last seen player postion
        self.path = [] #The full path determined by the search algorithm
        self.current_pos = (x,y) #initially the same position as the spawn
        self.hole_pos = [] #internal memory for all the detected/remembered holes
        
    # -----------------
    # HELPER FUNCTIONS
    # -----------------
    #Chooses the robot's next target, it does so randomly
    @staticmethod
    def choose_valid_point(gridsize, grid_map):
        while True:
            x = random.randint(0, gridsize[0] - 1)
            y = random.randint(0 , gridsize[1] - 1)
            if grid_map[x,y] in Grid.passable:
                return (x,y)
    
    # -----------------
    # SENSE / DETECTION
    # -----------------
    @staticmethod
    def detect_enemy(player_pos, robot_pos, grid_map, gridsize):
        if not Robot.manhattan_distance(player_pos, robot_pos, gridsize): #outside of detection range
            return False
        else: #if in detection range, check if blocking obstacle exists
            return Robot.check_blocking(player_pos, robot_pos, grid_map)

    # Measure the distacne between 2 points
    @staticmethod
    def manhattan_distance(player_pos, robot_pos, gridsize):
        d = abs(player_pos[0] - robot_pos[0]) + abs(player_pos[1] - robot_pos[1])
        if d <= max(5, (gridsize[0] + gridsize[1]) // 8):
            return True
        return False
    
    @staticmethod
    def naiveDrawLine(x1, x2, y1, y2, grid_map): #method used for sight validation across diagonal angles
        # Calculate slope between two points to determine line direction
        m = (y2 - y1) / (x2 - x1) #Slope
        # Calculate y-intercept using point-slope form: y = mx + c, rearranged to c = y - mx
        # We use (x1, y1) as the point, but (x2, y2) would work equally well since both points satisfy the line equation
        c = y1 - m * x1 #Intercept

        # Ensure we iterate from left to right by finding min and max x coordinates (this has the same reasoning as it's parent function)
        x_start = min(x1, x2) #Choosing the smaller x
        x_end = max(x1, x2) #Choosing the bigger x
        
        # This ensures iteration goes from smaller to bigger, avoiding issues with iteration direction
        height, width = grid_map.shape
        # For each x coordinate along the line, check if path is blocked
        for x in range(x_start, x_end + 1):
            # Calculate corresponding y coordinate on the line
            y = round(m * x + c) #we round it in order to actually access the y location with an int
            # Skip if calculated point is outside grid boundaries
            if x < 0 or x >= height or y < 0 or y >= width: #If somehow we are out of bounds
                continue
            # Return False if any blocking tile (wall=2 or hole=4) exists on line of sight
            if grid_map[x, y] in [2, 4]: #If there is a blocing path
                return False
        # If no obstacles found along entire line, line of sight is clear
        return True

    
    @staticmethod
    def check_blocking(player_pos, robot_pos, grid_map): #this function uses the view path between the robot and the player to check if something is blocking
        # Check if player and robot share the same row (x-coordinate)
        if player_pos[0] == robot_pos[0]:
            # Extract horizontal line segment between robot and player on the same row
            arr = grid_map[player_pos[0], min(robot_pos[1],player_pos[1]) : max(robot_pos[1],player_pos[1])] #the reason we do a min and max here is to guarantee that we start from the smallest y to the biggest y
            # If no blocking tiles (2=wall, 4=hole) found in segment, line of sight is clear
            if np.isin(arr,[2 , 4]).sum() == 0: #checks if there is any blocking path or not
                return True
            else:
                return False
        # Check if player and robot share the same column (y-coordinate)
        elif player_pos[1] == robot_pos[1]:
            # Extract vertical line segment between robot and player on the same column
            arr = grid_map[min(robot_pos[0],player_pos[0]) : max(robot_pos[0],player_pos[0]), player_pos[1]] #same reason as above
            # If no blocking tiles (2=wall, 4=hole) found in segment, line of sight is clear
            if np.isin(arr,[2 , 4]).sum() == 0:
                return True
            else:
                return False
        # For diagonal or arbitrary angles, use line-drawing algorithm to check line of sight
        return Robot.naiveDrawLine(
            robot_pos[0], player_pos[0],
            robot_pos[1], player_pos[1],
            grid_map
        )
        
    # -----------------
    # PATROL FUNCTIONS
    # -----------------
    #Uses BFS to create the valid path by validating the target point and its availability
    def create_path_patrol(self, gridsize, grid_map, current_pos):
        max_attempts = gridsize[0] * gridsize[1] #we have m*n attempts to find a path to a chosen target point that changes on each attempt
        for _ in range(max_attempts):
            target_point = Robot.choose_valid_point(gridsize, grid_map)
            target_path = self.bfs(grid_map, current_pos, target_point)
            if target_path != []:
                return target_path
        return []
            
    #Building the path
    def bfs(self, grid_map, current_pos, target_point):
        # the current position will be treated as the source
        queue = deque([current_pos]) # -> source is ready
        visited = {current_pos}
        came_from = {}
        while queue:
            cx, cy = queue.popleft() #dequeue and check if target point
            if (cx,cy) == target_point: #if we have reached the target point chosen by choose_valid_point
                path_stack = [] #We start by creating a path stack list that will hold the path stack, traced from the target point back to the
                #source using the came_from list of dict which we built down
                cur = (cx,cy) #the current coordinates we are at
                path_stack.append(cur) #append the source, then get the parent and append its parent then get the grandparent and add it as well, and so on
                while cur in came_from:
                    cur = came_from[cur]
                    path_stack.append(cur)
                return path_stack
            for dnx, dny in [(-1,0),(1,0),(0,-1),(0,1)]: #start exploring neighbors
                nx, ny = cx + dnx, cy + dny
                #Check if already visited
                if((nx, ny) in visited): 
                    continue
                tile = grid_map[nx, ny]
                #Check if passable (normal) or risky (hole)
                if tile not in Grid.passable: #If it is not passable
                    if tile == 4: #if it is a tile hole ->
                        #If the hole is stored by the robot, skip
                        if (nx,ny) in self.hole_pos:
                            continue
                        elif random.random() < Robot.HOLE_PROBABILITY: #we hit the probability to fall in the hole -> then add it to the path
                            pass
                    else: #Else we do not add to the path, since its a none hole blocking
                        continue
                #We need to check if we are at the goal or not
                queue.append((nx, ny)) #append neighbor if not visited and passable
                visited.add((nx, ny)) #add it to the visited
                came_from[(nx, ny)] = (cx, cy) #record who the parent of this added tile is, this will be used to trace the path stack
        return [] 

                
    def patrol_search(self, gridsize, grid_map): #This function is a decider function, it checks whether we already have a path or not,
        #If no path, pick target, try bfs -> if fail retry
        #else we take one step of planned path
        if self.path is None or self.path == []:
            self.path = self.create_path_patrol(gridsize, grid_map, self.current_pos)
            
        return self.path.pop()

    # -----------------
    # CHASE FUNCTIONS
    # -----------------
    def a_star(self, grid_map, current_pos, target_point):
        height, width = grid_map.shape
        open_set = {current_pos}
        came_from = {}
        g_score = {current_pos: 0}
        f_score = {current_pos: Robot._heuristic(current_pos, target_point)}

        while open_set:
            # pick node in open_set with lowest f_score
            current = min(open_set, key=lambda p: f_score.get(p, float("inf")))
            if current == target_point:
                # rebuild path (same style as bfs: stack/list of coords)
                path_stack = []
                cur = current
                path_stack.append(cur)
                while cur in came_from:
                    cur = came_from[cur]
                    path_stack.append(cur)
                return path_stack

            open_set.remove(current)
            cx, cy = current
            for dnx, dny in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = cx + dnx, cy + dny
                if nx < 0 or nx >= height or ny < 0 or ny >= width:
                    continue
                tile = grid_map[nx, ny]
                # Passability rule (match bfs behavior)
                #in other words it checks if the tile is a passable and a hole to inject a probabilistic decision taking
                if tile not in Grid.passable:
                    if tile == 4:
                        if (nx, ny) in self.hole_pos:
                            continue
                        if random.random() >= Robot.HOLE_PROBABILITY:
                            continue
                    else:
                        continue #else blocked and not a hole

                neighbor = (nx, ny)
                tentative_g = g_score[current] + 1
                if tentative_g < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + Robot._heuristic(neighbor, target_point)
                    open_set.add(neighbor)

        return []

    @staticmethod
    def _heuristic(a, b):
        # Calculate Manhattan distance between two positions (estimated cost to goal)
        # Used by A* algorithm to guide search toward target point
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def return_path(self, player_pos, gridmap):
        # Execute A* pathfinding from robot's current position to player's position
        # Returns ordered path stack (list of coordinates) to chase the player
        return self.a_star(gridmap,self.current_pos, player_pos)
        
    # ------------------------
    # GLOBAL DECIDER FUNCTION
    # ------------------------
    def decide_next_move(self, player_pos, gridsize, grid_map):
        # Check if robot is in PATROL or SEARCH states (passive states)
        if self.state == State.PATROL or self.state == State.SEARCH:
            # If player detected (line of sight exists and within detection range), transition to CHASE
            if Robot.detect_enemy(player_pos, self.current_pos, grid_map, gridsize):
                self.state = State.CHASE
            # If still in PATROL state, continue patrolling with pre-planned path
            if self.state == State.PATROL:
                return (self.patrol_search(gridsize, grid_map), False) #will check if we already have a path stack for the patrol bfs
                #if yes then pops whatever is in the path, or creates a new one using the patrol search functions
            # If in SEARCH state (placeholder for future implementation)
            elif self.state == State.SEARCH:
                pass
        # If in active CHASE state, pursue the player
        if self.state == State.CHASE:
            # If player distance exceeds half the grid size, lose track and return to PATROL
            if self._heuristic(player_pos, self.current_pos) > gridsize[0] // 2:
                self.state = State.PATROL # to be changed to SEARCH later
            else:
                # Execute A* pathfinding to generate chase path toward player
                path = self.return_path(player_pos, grid_map)
                # Ensure path exists and is not empty
                if path != []: #We need to do to make sure we never return the current position of the robot, else it will never move
                    # Remove current position from path if it's at the end (shouldn't move to current position)
                    if path[-1] == self.current_pos: #Last Position is the current position
                        path.pop() #returns the end positionm and since a_star returns a stack from [player_pos -> robot_pos] then obviously we need to remove the last robot_pos or 
                        #it will be returned everytime causing the robot to not move
                    # After cleanup, verify path still has moves available
                    if path != []: #Checking if we didnt empty the entire list
                        # Return next move in path, flag as True indicates active chase
                        return (path.pop(), True)
                # If path is empty, stay in place during chase
                return (self.current_pos, True)
        # Default fallback: if not in CHASE state, return to PATROL with planned path movement
        return (self.patrol_search(gridsize, grid_map), False)

    #Wipes path and resets the robot to its spawn point (used when falling in a hole)
    def reset_after_hole(self, pos):
        self.path = []
        self.current_pos = self.spawn_pos
        self.last_seen = None
        self.state = State.PATROL
        self.hole_pos.append(pos)

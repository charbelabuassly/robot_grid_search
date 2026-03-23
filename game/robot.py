import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from state import State
import random
from collections import deque
from grid.grid import Grid
import numpy as np

class Robot:    
    
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
    #Chooses the robot's next target
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
    def detect_enemy(player_pos, robot_pos, grid_map):
        if not Robot.manhattan_distance(player_pos, robot_pos): #outside of detection range
            return False
        else: #if in detection range, check if blocking obstacle exists
            return Robot.check_blocking(player_pos, robot_pos, grid_map)

    # Measure the distacne between 2 points
    @staticmethod
    def manhattan_distance(player_pos, robot_pos):
        d = abs(player_pos[0] - robot_pos[0]) + abs(player_pos[1] - robot_pos[1])
        if d <= 7:
            return True
        return False
    
    @staticmethod
    def naiveDrawLine(x1, x2, y1, y2, grid_map):
        m = (y2 - y1) / (x2 - x1) #Slope
        c = y1 - m * x1 #Intercept

        x_start = min(x1, x2) #Choosing the smaller x
        x_end = max(x1, x2) #Choosing the bigger x
        
        #This is done in order to move from from smaller to bigger in the loop, else it will break

        height, width = grid_map.shape
        for x in range(x_start, x_end + 1):
            y = round(m * x + c)
            if x < 0 or x >= height or y < 0 or y >= width: #If somehow we are out of bounds
                continue
            if grid_map[x, y] in [2, 4]: #If there is a blocing path
                return False
            #We need to check for blocking corners in the adjacent tiles
            if grid_map[x + 1, y] in [2, 4] or grid_map[x , y+1] in [2, 4]:
                return False
        return True

    
    @staticmethod
    def check_blocking(player_pos, robot_pos, grid_map):
        #Check if same row px = rx
        if player_pos[0] == robot_pos[0]:
            arr = grid_map[player_pos[0], min(robot_pos[1],player_pos[1]) : max(robot_pos[1],player_pos[1])]
            if np.isin(arr,[2 , 4]).sum() == 0:
                return True
            else:
                return False
        #Check if same column, py = ry
        elif player_pos[1] == robot_pos[1]:
            arr = grid_map[min(robot_pos[0],player_pos[0]) : max(robot_pos[0],player_pos[0]), player_pos[1]]
            if np.isin(arr,[2 , 4]).sum() == 0:
                return True
            else:
                return False
        # Diagonal/other case: use naive line-of-sight check
        return Robot.naiveDrawLine(
            robot_pos[0], player_pos[0],
            robot_pos[1], player_pos[1],
            grid_map
        )
        
    # -----------------
    # PATROL FUNCTIONS
    # -----------------
    #Uses BFS to create the valid path by validating the target point and its availability
    @staticmethod
    def create_path_patrol(gridsize, grid_map, current_pos):
        max_attempts = gridsize[0] * gridsize[1]
        for _ in range(max_attempts):
            target_point = Robot.choose_valid_point(gridsize, grid_map)
            target_path = Robot.bfs(grid_map, current_pos, target_point)
            if target_path != []:
                return target_path
        return []
            
    #Building the path
    @staticmethod
    def bfs(grid_map, current_pos, target_point):
        # the current position will be treated as the source
        queue = deque([current_pos]) # -> source is ready
        visited = {current_pos}
        came_from = {}
        while queue:
            cx, cy = queue.popleft()
            if (cx,cy) == target_point:
                path_stack = []
                cur = (cx,cy)
                path_stack.append(cur)
                while cur in came_from:
                    cur = came_from[cur]
                    path_stack.append(cur)
                return path_stack
            for dnx, dny in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = cx + dnx, cy + dny
                #Check if already visited
                if((nx, ny) in visited):
                    continue
                #Check if passable
                if (grid_map[nx, ny]) not in Grid.passable:
                    continue
                #We need to check if we are at the goal or not
                queue.append((nx, ny))
                visited.add((nx, ny))
                came_from[(nx, ny)] = (cx, cy)
        return []
                
    def patrol_search(self, gridsize, grid_map):
        #If no path, pick target, try bfs -> if fail retry
        #else we take one step of planned path
        if self.path is None or self.path == []:
            self.path = self.create_path_patrol(gridsize, grid_map, self.current_pos)
            
        return self.path.pop()

    # ------------------------
    # GLOBAL DECIDER FUNCTION
    # ------------------------
    def decide_next_move(self, player_pos, gridsize, grid_map):
        if Robot.detect_enemy(player_pos, self.current_pos, grid_map):
            self.state = State.CHASE
            return (self.current_pos, True)
        else:
            self.state = State.PATROL
            return (self.patrol_search(gridsize, grid_map), False)

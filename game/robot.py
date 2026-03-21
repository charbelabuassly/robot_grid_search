import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from state import State
import random
from collections import deque
from grid.grid import Grid

class Robot:    
    
    def __init__(self, x, y):
        self.spawn_pos = (x,y) #Spawn position
        self.state = State.PATROL #AI state
        self.last_seen = None #Last seen player postion
        self.path = [] #The full path determined by the search algorithm
        self.current_pos = (x,y) #initially the same position as the spawn
        
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
            self.path = self.create_path_patrol(gridsize, grid_map, self.current_pos )
            
        return self.path.pop()

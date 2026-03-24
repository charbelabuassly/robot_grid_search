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
    def naiveDrawLine(x1, x2, y1, y2, grid_map):
        height, width = grid_map.shape
        x, y = x1, y1 #x and y will be used to navigate towards x1 and y1
        dx = abs(x2 - x1) #Distance between x source and x target
        dy = abs(y2 - y1) #Distane between y source and y target
        sx = 1 if x1 < x2 else -1 #This is the step, it is in the x direction. If x source is below the x target, we step in negative direction (up)
        sy = 1 if y1 < y2 else -1 #This is step, it is in the y direction. If y source is after the y target, then we must go in the negative direction (left)
        err = dx - dy   #This error will be used to check how much the line has deviated, this error tracks how much we should move in x vs y  to keep the slope correct

        while True:
            if 0 <= x < height and 0 <= y < width: #If in bounds
                if grid_map[x, y] in [2, 4]: #if the tile is blocking return False
                    return False
                for dx_adj, dy_adj in [(-1, 0), (1, 0), (0, -1), (0, 1)]: #Checking the adjacent ones, if theyre blocked
                    nx, ny = x + dx_adj, y + dy_adj
                    if 0 <= nx < height and 0 <= ny < width:
                        if grid_map[nx, ny] in [2, 4]:
                            return False
            if x == x2 and y == y2: #If we reached the tile, break the loop and return true
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
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
    def create_path_patrol(self, gridsize, grid_map, current_pos):
        max_attempts = gridsize[0] * gridsize[1]
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
            cx, cy = queue.popleft()
            if (cx,cy) == target_point:
                path_stack = []
                cur = (cx,cy)
                path_stack.append(cur)
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
                    if tile == 4: #if it is a tile ->
                        #If the hole is stored by the robot, skip
                        if (nx,ny) in self.hole_pos:
                            continue
                        elif random.random() < Robot.HOLE_PROBABILITY: #we hit the probability to fall in the hole -> then add it to the path
                            pass
                    else: #Else we do not add to the path
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
                if tile not in Grid.passable:
                    if tile == 4:
                        if (nx, ny) in self.hole_pos:
                            continue
                        if random.random() >= Robot.HOLE_PROBABILITY:
                            continue
                    else:
                        continue

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
        # Manhattan distance heuristic
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def return_path(self, player_pos, gridmap):    
        return self.a_star(gridmap,self.current_pos, player_pos)
        
    # ------------------------
    # GLOBAL DECIDER FUNCTION
    # ------------------------
    def decide_next_move(self, player_pos, gridsize, grid_map):
        # Helper chase state
        if self.state == State.PATROL or self.state == State.SEARCH:
            if Robot.detect_enemy(player_pos, self.current_pos, grid_map, gridsize):
                self.state = State.CHASE
            if self.state == State.PATROL:
                return (self.patrol_search(gridsize, grid_map), False)
            elif self.state == State.SEARCH:
                pass
        if self.state == State.CHASE:
            if self._heuristic(player_pos, self.current_pos) > gridsize[0] // 2:
                self.state = State.PATROL # to be changed to SEARCH later
            else:
                path = self.return_path(player_pos, grid_map)
                if path != []: #We need to do to make sure we never return the current position of the robot, else it will never move
                    if path[-1] == self.current_pos: #Last Position is the current position
                        path.pop()
                    if path != []: #Checking if we didnt empty the entire list
                        return (path.pop(), True)
                return (self.current_pos, True)
        #Non CHASE STATE conditions below: -> return to default state, PATROL
        return (self.patrol_search(gridsize, grid_map), False)

    #Wipes path and resets the robot to its spawn point (used when falling in a hole)
    def reset_after_hole(self, pos):
        self.path = []
        self.current_pos = self.spawn_pos
        self.last_seen = None
        self.state = State.PATROL
        self.hole_pos.append(pos)

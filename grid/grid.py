import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import random as random
from collections import deque


class Grid:
    #------------------------------------------------------ Static Variables
    obstacles = [2, 3, 4]
    passable = [1, 3] #obstacles which allow passage   
    # ----------------------------------------------------- Constructor & Getters    
    def __init__(self, x, y):
        self.gridsize = (x,y) #max should be 38x38 for tilesize 20 + rows must always be equal to cols as long as we double transpose in main
        #it would be better for gridsize to just be one number since they have to be equal for the transposing to work, either that or avoid double transposing ofc
        #i kept it a tuple for compatibility and if we have time to fix later on
        self.grid = np.ones(self.gridsize)
        # House walls
        temp1 = self.gridsize[1] - 4 
        temp2 = self.gridsize[0] - 4
        self.vertical_wall = [(1,temp1),(2,temp1),(3,temp1),(4,temp1)]
        self.horizontal_wall = [(4,temp2),(4,temp2 + 1),(4, temp2 + 2)]
        
    def setGate(self,coords):
        self.coords = coords
        
    def getGrid(self):
        return self.grid
    
    def getSize(self):
        return self.gridsize
    #----------------------------------------------------- Builder Methods
    
    #Main Builder Function
    def build_grid(self):
        grid = self.getGrid()
        gridsize = self.getSize()
        #Building border walls
        self.build_wall(grid)

        num_of_squares = gridsize[0]*gridsize[1]
        max_blocked_count = int(num_of_squares*0.35) #35% of the grid must be blocked (any obstacle)
        max_hole_count = int(num_of_squares*0.012) #1.2% of the grid must be holes
        blocked_count = 0
        hole_count = 0

        while blocked_count < max_blocked_count :
            #picking x and y by avoiding the edges
            x = random.randint(1,grid.shape[0]-2) 
            y = random.randint(1,grid.shape[1]-2)
            if (x,y) in self.vertical_wall or (x,y) in self.horizontal_wall:
                continue
            #making sure , the hole count does not exceed 2% of the map grid count
            obstacle = self.choose_obstacle(hole_count,max_hole_count)
            #Direct Neighbors
            up = (x-1,y)
            down = (x+1,y)
            left = (x,y-1)
            right = (x,y+1)
            temp = [up,down,left,right]
            #It is prohibited for any obstacle of any kind to block the gate.
            check = [1 if  grid[n[0],n[1]] == 5 else 0 for n in temp]
            if sum(check) != 0:
                continue    
            
            if obstacle == 3: #3 for quicksand
                grid[x,y] = 3
                blocked_count+=1
            else: #obstacle NOT passable (wall)
                count = 0 #passable neigbors count
                passable_neigbors = [] #store all the passable neighbors
                
                for neighbor in temp:
                    if grid[neighbor[0], neighbor[1]] in Grid.passable:
                        passable_neigbors.append((neighbor[0], neighbor[1]))
                        count+=1
                    
                if count < 2:
                    #safe to add the obstacle
                    grid[x,y] = obstacle
                    blocked_count+=1
                elif count >= 2:
                    #choose a random neighbor and check the connectivity between all passable neighbors
                    chosen = random.choice(passable_neigbors)
                    state = self.bfs(grid,chosen,passable_neigbors,x,y)
                    if state:
                        #safe to add
                        grid[x,y] = obstacle
                        blocked_count+=1
        return grid
    
    #BFS for ensuring atleast 1 neighbor connectivity
    def bfs(self,grid, chosen , passable_neighbors,x,y):
        queue = deque([chosen]) #putting the source
        visited = {chosen}  #add all what we visited to this array, set of coordinates 
        #We need to temporarily block the {x,y} tile, so that the system doesn't mistake it for a path
        grid[x,y] = 2
        while queue:
            cx, cy = queue.popleft()
            
            #We need to explore its direct neighbors
            for dnx, dny in [(-1,0),(1,0),(0,-1),(0,1)]:
                #check if already visited
                if((cx+dnx,cy+dny) in visited):
                    continue
                #check if passable
                if(grid[cx+dnx,cy+dny] not in Grid.passable):
                    continue
                #check if in the neighbors 
                if((cx+dnx,cy+dny) in passable_neighbors):
                    grid[x,y] = 1 #Unblock it
                    return True
                #neither of both, we add it as visited and we add it to the queue
                queue.append((cx+dnx,cy+dny))
                visited.add((cx+dnx,cy+dny))
            
        grid[x,y] = 1
        return False
    
    #Building walls around the map border
    def build_wall(self,grid):
        #Creating walls around the map
        grid[0, :] = 2
        grid[: , 0] = 2
        grid[-1, : ] = 2
        grid[:, -1] = 2
        #building the walls
        for x,y in self.horizontal_wall:
            grid[x,y] = 2
        for x,y in self.vertical_wall:
            grid[x,y] = 2
        #Installing the gate (gridsize[] - 3?)
        coords = random.choice([(2,self.gridsize[1] - 4),(3,self.gridsize[1] - 4)]) #gate coords
        grid[coords[0],coords[1]] = 5

    #Choosing valid obstacle
    def choose_obstacle(self,hole_count, max_hole_count):
        while(True):
                obstacle = random.choice(Grid.obstacles)
                if obstacle == 4:
                    #check hole counter
                    if hole_count == max_hole_count :
                        continue
                    else:
                        hole_count+=1
                        break
                else:
                    break
        return obstacle

    #Cleaning grid house path
    def clean_grid(self):
        #clean outside
        grid = self.getGrid()
        for x,y in self.vertical_wall:
            grid[x,y-1] = 1
            grid[x,y-2] = 1
            if x!=4: #to avoid removing part of the horizontal wall, the part below clears the house from inside
                grid[x,y+1] = 1
                grid[x,y+2] = 1
        for x,y in self.horizontal_wall: 
            grid[x+1,y] = 1
            grid[x+2,y] = 1
        grid[self.vertical_wall[-1][0]+1, self.horizontal_wall[0][1]-1] = 1 #cleaning the direct diagonal of the house vertex

    #Sets a random passable spawn point for the player
    def set_spawn_player(self):
        grid = self.getGrid()
        while True:
            x = random.randint((grid.shape[0] // 2) + 1, grid.shape[0] - 2) #Can spawn at the lower half
            y = random.randint(1, grid.shape[1] - 2)
            if (x, y) in self.vertical_wall or (x, y) in self.horizontal_wall:
                continue
            if grid[x, y] == 1:
                self.spawn = (x, y)
                return self.spawn
            
    #Sets a random passable spawn point for the robot
    def set_spawn_robot(self):
        grid = self.getGrid()
        while True:
            x = random.randint(1, grid.shape[0] // 2) #Can spawn at the upper half
            y = random.randint(1, grid.shape[1] - 2)
            if (x, y) in self.vertical_wall or (x, y) in self.horizontal_wall:
                continue
            # Avoid the house area (around the blue gate)
            if 1 <= x <= 4 and 16 <= y <= 18:
                continue
            if grid[x, y] == 1:
                self.spawn = (x, y)
                return self.spawn

    #Validates that a path exists between spawn and the gate (value 5) via BFS
    def validate_spawn_to_gate(self, spawn):
        grid = self.getGrid()
        queue = deque([spawn])
        visited = {spawn}
        while queue:
            x, y = queue.popleft()
            # if we reached the gate
            if grid[x, y] == 5:
                return True
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]: #moves to the neighbors (direct NOT DIAGONAL)
                nx, ny = x + dx, y + dy
                if (nx, ny) in visited:
                    continue
                # Allow traversal on passable tiles (grey + yellow) and the gate (blue)
                if grid[nx, ny] in Grid.passable or grid[nx, ny] == 5:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        #No path found -> 
        return False

    #Main Generator Function, You will use this when generating 
    def generate_grid(self, robot_count):
        while True:
            # Reset grid on each attempt
            robot_arr = []
            self.grid = np.ones(self.gridsize)
            self.build_grid()
            self.clean_grid()
            player_spawn = self.set_spawn_player()
            for i in range(0,robot_count):
                robot_arr.append(self.set_spawn_robot())
            if self.validate_spawn_to_gate(player_spawn):
                all_ok = all(self.validate_spawn_to_gate(r) for r in robot_arr) #validate each robot spawn
                if not all_ok:
                    continue
                #grid = self.getGrid()
                #grid[player_spawn[0], player_spawn[1]] = 6
                return player_spawn, robot_arr
            #print(self.grid)
            
    
    #Grid Visualizer
    def showGrid(self):
        colors = ['grey', 'black', 'yellow', 'red', 'blue', 'green', 'magenta' ]
        cmap = ListedColormap(colors)
        plt.imshow(self.getGrid(), cmap = cmap, vmin = 1, vmax = 7)

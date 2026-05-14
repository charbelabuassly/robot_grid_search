import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import random as random
from collections import deque


class Grid:
    #------------------------------------------------------ Static Variables ALWAYS EXISTING IN EACH GRID INSTANCE
    obstacles = [2, 3, 4]
    passable = [1, 3] #obstacles which allow passage   
    # ----------------------------------------------------- Constructor & Getters    
    def __init__(self, x, y):
        self.gridsize = (x,y) #KEEPING THE GRID SIZE IN A TUPLE FOR FUTURE USE
        self.grid = np.ones(self.gridsize) #BUILDING THE ACTUAL GRID ITSELF AS A NUMPY ARRAY
        # House walls
        self.temp = self.gridsize[1] - 4 #This represents the column where the vertical wall will sit at
        self.vertical_wall = [(1,self.temp),(2,self.temp),(3,self.temp),(4,self.temp)] #vertical wall, y is set, we go down by increasing x
        self.horizontal_wall = [(4,self.temp),(4,self.temp + 1),(4, self.temp + 2)] #This represents the horizontal wall that comes at the base of
        #the vertical wall, its at x =  (4th row) 
        
    def setGate(self,coords): 
        self.coords = coords
        
    def getGrid(self): #used to get the grid itself
        return self.grid
    
    def getSize(self): #used to get the grid size
        return self.gridsize
    #----------------------------------------------------- Builder Methods
    
    #Main Builder Function
    def build_grid(self):
        grid = self.getGrid() #gets the grid initialized in the constructor automatically upon calling the function
        gridsize = self.getSize() #the same can be said for the gridsize
        #Building border walls
        self.build_wall(grid) #1st step is to build the walls

        num_of_squares = gridsize[0]*gridsize[1] #we can have in our system m*n squares
        max_blocked_count = int(num_of_squares*0.35) #35% of the grid must be blocked (any obstacle)
        max_hole_count = int(num_of_squares*0.012) #1.2% of the grid must be holes
        blocked_count = 0 #used to count the number of blocking tiles placed
        hole_count = 0 #used to count the number of holes placed

        while blocked_count < max_blocked_count : #A while loop that keeps on adding blocked tiles as long as it is within the accepted range
            #picking x and y by avoiding the edges
            x = random.randint(1,grid.shape[0]-2) 
            y = random.randint(1,grid.shape[1]-2)
            if (x,y) in self.vertical_wall or (x,y) in self.horizontal_wall: #Additional redundant check
                continue
            #making sure , the hole count does not exceed 2% of the map grid count
            obstacle = self.choose_obstacle(hole_count,max_hole_count) #chooses valid obstacle, decides if valid to use hole or not
            #Direct Neighbors, for navigation
            up = (x-1,y)
            down = (x+1,y)
            left = (x,y-1)
            right = (x,y+1)
            temp = [up,down,left,right]
            #It is prohibited for any obstacle of any kind to block the gate.
            check = [1 if  grid[n[0],n[1]] == 5 else 0 for n in temp] #Looping over the neigbors, if any is the gate add 1, else 0
            if sum(check) != 0: #If sum !=0, that means the list has at least 1 one, meaning there is a neighbor which IS the gate
                continue    
            
            if obstacle == 3: #3 for quicksand, we can add it wherever we need (except the gate), it isn't blocking, it only slows down
                grid[x,y] = 3 #Placing it
                blocked_count+=1 #Increasing block count
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
                    grid[x,y] = 1 #Unblock it, since here it blocks with obstacle 1 always
                    return True
                #neither of both, we add it as visited and we add it to the queue, meaning that its passable
                queue.append((cx+dnx,cy+dny))
                visited.add((cx+dnx,cy+dny))
            
        grid[x,y] = 1
        return False
    
    #Building walls around the map border
    def build_wall(self,grid):
        #Creating walls around the map
        grid[0, :] = 2 #Putting upper row as a block wall
        grid[: , 0] = 2 #putting left wall as a block wall
        grid[-1, : ] = 2 #Putting lower row as a block wall
        grid[:, -1] = 2 #putting right wal as a block wall
        #building the walls of the house itself, the walls below are hardcoded and static
        for x,y in self.horizontal_wall:
            grid[x,y] = 2
        for x,y in self.vertical_wall:
            grid[x,y] = 2
        #Installing the gate (gridsize[] - 3?)
        coords = random.choice([(2,self.gridsize[1] - 4),(3,self.gridsize[1] - 4)]) #gate coords
        grid[coords[0],coords[1]] = 5

    #Choosing valid obstacle
    def choose_obstacle(self,hole_count, max_hole_count): #chooses obstacles, and checks if we can add more holes or if its capped
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

    #Cleaning grid house path, ensure 100% no blocked path around the house itself
    def clean_grid(self):
        #clean outside
        grid = self.getGrid()
        for x,y in self.vertical_wall: #Cleaning 2 tiles in the left direction of the vertical wall
            grid[x,y-1] = 1
            grid[x,y-2] = 1
            if x!=4: #to avoid removing part of the horizontal wall, the part below clears the house from inside
                grid[x,y+1] = 1
                grid[x,y+2] = 1
        for x,y in self.horizontal_wall: #same for the x part
            grid[x+1,y] = 1
            grid[x+2,y] = 1
        grid[self.vertical_wall[-1][0]+1, self.horizontal_wall[0][1]-1] = 1 #cleaning the direct diagonal of the house vertex

    #Sets a random passable spawn point for the player
    def set_spawn_player(self):
        grid = self.getGrid()
        while True:
            x = random.randint((grid.shape[0] // 2) + 1, grid.shape[0] - 2) #Can spawn at the lower half
            y = random.randint(1, grid.shape[1] - 2)
            if (x, y) in self.vertical_wall or (x, y) in self.horizontal_wall: #Safety check to ensure no spawn inside the house walls
                continue
            if grid[x, y] == 1: #if spawned in valid position in the lower half, then its valid, set the spawn posiiton to be given to the PYGAME
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
            # Avoid the house area (inside the house)
            if 1 <= x <= 4 and (y >= self.temp):
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
                # Allow traversal on passable tiles (grey + yellow) and the gate (blue), we confirm we reached the gate during dequeing up
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

# AI-Powered Grid-Based Game - Project Report

## Project Overview
A grid-based pursuit game where AI-controlled robots hunt a player navigating through a dynamically generated environment. The project implements sophisticated pathfinding algorithms and state-based AI decision-making.

---

## Tools & Technologies Used

### Development & Version Control
- **GitHub** - Source code repository and version control
- **VS Code** - Primary development environment with integrated debugging
- **Jupyter Notebook** - Grid testing and algorithm visualization (grid_testing.ipynb)
- **Python 3.13** - Core programming language

### Game & Visualization
- **Pygame** - 2D graphics rendering and game loop management
- **NumPy** - Grid-based calculations and array operations
- **Matplotlib** - Data visualization and debugging visualization

---

## Core Libraries & Dependencies

```
pygame           # Game rendering and event handling
numpy            # Multi-dimensional array operations for grid
matplotlib       # Visualization and analysis
collections     # deque for efficient queue operations (BFS/A*)
enum            # State management for robot AI
random          # Random tile generation and hole probability
```

---

## Project Architecture

### File Structure
```
game/
  ├── main.py        # Game loop, rendering, level management
  ├── player.py      # Player entity class
  ├── robot.py       # Robot AI agent with pathfinding
  ├── state.py       # State enumeration (PATROL, CHASE, SEARCH)
grid/
  ├── grid.py        # Grid generation and management
  ├── grid_testing.ipynb  # Algorithm testing and visualization
  └── __init__.py
photos/             # Sprite assets for tiles and entities
```

### Core Classes

**Player**
- Tracks player position
- Responds to keyboard input (arrow keys)

**Robot**
- Manages AI state and behavior
- Implements multiple pathfinding algorithms
- Handles line-of-sight detection

**Grid**
- Procedurally generates level layouts
- Manages tile types and obstacles
- Ensures connectivity and valid paths

**State**
- Enumeration: PATROL, CHASE, SEARCH
- State machine for robot AI decision-making

---

## Algorithms Implemented

### Pathfinding Algorithms

1. **Breadth-First Search (BFS)**
   - Used for patrol route planning
   - Guarantees shortest path to random targets
   - Handles probabilistic hole traversal

2. **A* Search Algorithm**
   - Optimal pathfinding for chase behavior
   - Heuristic: Manhattan distance
   - Guides robot toward player with cost optimization
   - Integrated hole probability handling

### Detection & Visibility

3. **Line-of-Sight Detection**
   - **Manhattan Distance Check** - Initial range detection
   - **Naive Line Drawing (Bresenham-like)** - Diagonal/arbitrary angle visibility
   - **Axis-Aligned Segment Check** - Optimized horizontal/vertical blocking detection

### Grid Generation

4. **Constraint Satisfaction (Grid Building)**
   - BFS connectivity validation
   - Obstacle density: 35% of grid
   - Hole density: 1.2% of grid
   - Prevents dead-ends while maintaining challenge

---

## Key Functionalities

### Game Features
- **6-Level Progression** - Increasing grid size and robot count
- **Dynamic Obstacle Generation** - Walls, holes, quicksand, gates
- **Multi-Robot AI** - 2-10 robots depending on level
- **Sprite-Based Rendering** - Custom tile and entity graphics
- **Health System** - Lives display with heart rendering
- **Tile-Based Movement** - 20x20 pixel tiles

### Robot AI Behaviors

**Patrol State**
- Explores grid with random target selection
- Uses BFS to reach targets
- Stateless exploration behavior

**Chase State**
- Activates when player detected in range (line-of-sight)
- Uses A* for optimal pursuit
- Probabilistic hole avoidance based on memory
- Reverts to PATROL if player escapes (>half grid distance)

**Search State**
- Placeholder for future implementation
- Intended for player tracking after detection loss

### Memory System
- Hole position memory - Robots remember detected holes
- Last seen position tracking
- State persistence across decisions

---

## Technical Details

### Game Constants
- **Tile Size:** 20×20 pixels
- **Grid Sizes:** 20×30 (early), 30×60 (late levels)
- **Max Lives:** 5
- **Hole Probability:** 20% chance to traverse known holes

### Tile Types
- `1` - Open path (passable)
- `2` - Wall (blocking)
- `3` - Quicksand (passable, aesthetic)
- `4` - Hole (hazard, probabilistic)
- `5` - Gate (goal)
- `6` - Player spawn
- `7` - Robot spawn

### AI Decision Flow
1. Check detection (manhattan distance + line-of-sight)
2. Transition state if conditions met
3. Execute movement based on current state
4. Return next position and chase flag

---

## Algorithms Complexity Analysis

| Algorithm | Time | Space | Use Case |
|-----------|------|-------|----------|
| BFS | O(V+E) | O(V) | Patrol pathfinding |
| A* | O(E·log(V)) | O(V) | Chase pathfinding |
| Line-of-Sight | O(max(x,y)) | O(1) | Detection validation |
| Grid Gen (BFS) | O(V+E) per obstacle | O(V) | Level creation |

---

## Development Notes

### Debugging Tools
- Jupyter notebook for BFS/A* algorithm testing
- Matplotlib visualization for grid analysis
- VS Code breakpoint debugging for game state inspection

### State Machine Diagram
```
PATROL ←→ CHASE ← (detection + line-of-sight)
                → (distance > grid[0]//2)
                ↓
              SEARCH (future)
```

### Performance Considerations
- Pathfinding runs only when state changes or path exhausted
- Manhattan heuristic provides efficient A* guidance
- Line-of-sight cached in come_from dictionary

---

## Future Enhancements
- Implement SEARCH state for tracked player
- Add interception algorithm for predictive chasing
- Multi-threading for concurrent robot pathfinding
- Difficulty scaling with ML-based robot behavior
- Sound effects and music system

---

## How to Use This Report
This report can be used as a comprehensive prompt to generate detailed README.md, technical documentation, or project presentations. It covers all major technical and architectural aspects of the project.

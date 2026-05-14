# 🤖 AI-Powered Grid-Based Game

A dynamic grid-based pursuit game where intelligent AI robots hunt down a player navigating through procedurally generated environments.

This project focuses on combining **game development**, **pathfinding algorithms**, and **state-driven AI behavior** into one cohesive system.

---

## 🎮 Overview

* Navigate through a **procedurally generated grid**
* Avoid or outmaneuver **AI-controlled robots**
* Progress through **multiple levels** with increasing difficulty
* Experience intelligent behavior powered by **real-time decision-making**

---

## 🛠️ Tech Stack

### 💻 Development & Environment

* **GitHub** – Version control & project management
* **VS Code** – Development & debugging
* **Jupyter Notebook** – Algorithm testing & visualization
* **Python 3** – Core programming language

---

### 🎨 Game & Visualization

* **Pygame** – Game loop, rendering, and interaction
* **NumPy** – Efficient grid and array operations
* **Matplotlib** – Debugging and visualization

---

## 📁 Project Structure

```
game/
  ├── main.py        # Game loop & rendering
  ├── player.py      # Player logic
  ├── robot.py       # AI behavior & pathfinding
  ├── state.py       # AI state machine

grid/
  ├── grid.py        # Grid generation
  ├── grid_testing.ipynb
  └── __init__.py

photos/              # Game assets
```

---

## 🧠 Core Features

### 🤖 Smart Robot AI

* **Patrol Mode** → explores randomly
* **Chase Mode** → actively hunts the player
* **(Future) Search Mode** → tracks last known position

### 🧭 Pathfinding

* BFS for exploration
* A* for intelligent chasing
* Manhattan heuristic for efficiency

### 👁️ Detection System

* Range-based detection
* Line-of-sight validation
* Obstacle-aware visibility

### 🗺️ Procedural Grid

* Randomized layouts
* Balanced obstacles & hazards
* Always ensures playable paths

---

## 🎯 Gameplay Features

* 🔢 **Multiple levels** with scaling difficulty
* 🤖 **2–10 AI robots** depending on level
* 🧱 Dynamic obstacles (walls, holes, etc.)
* ❤️ Health/lives system
* 🎨 Tile-based rendering (20x20 grid)

---

## ⚙️ How It Works

1. Robots check if the player is within detection range
2. If visible → switch to **CHASE mode**
3. Otherwise → continue **PATROL**
4. Movement decisions are updated dynamically using pathfinding

---

## 🚀 Getting Started

```bash
# Clone the repository
git clone <your-repo-link>

# Navigate into project
cd your-project

# Install dependencies
pip install pygame numpy matplotlib

# Run the game
python game/main.py
```

---

## 🔮 Future Improvements

* 🧠 Implement full **Search behavior**
* 🎯 Predictive chasing (interception AI)
* ⚡ Performance optimization (multi-agent scaling)
* 🔊 Sound effects & music
* 🤖 Advanced AI (learning-based behavior)

---

## 📌 Why This Project Stands Out

This project isn’t just a game — it’s a **practical AI system** combining:

* Real-time decision making
* Algorithmic problem solving
* Clean modular architecture
* Game + AI integration

---

* Add a **demo section with gameplay screenshots**
* Or tailor it for **recruiters / portfolio use**

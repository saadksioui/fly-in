*This project has been created as part of the 42 curriculum by sksioui*

# Fly-in

## Description
**Fly-in** is a Python-based simulation engine and pathfinding algorithm designed to route a fleet of autonomous drones through a complex, dynamic network.

The primary goal of the project is to navigate multiple drones from a starting hub to an ending hub in the absolute minimum number of discrete time steps (turns). The simulation strictly enforces complex routing mechanics, including:
*   **Zone Capacities:** Nodes can only hold a specific number of drones at a time.
*   **Connection Capacities:** Edges have traffic limits.
*   **Restricted Zones:** Dangerous zones that take 2 turns to enter, forcing drones to occupy the connecting edge during transit.
*   **Simultaneous Movement:** Drones moving out of a zone instantly free up capacity for drones moving in during the exact same turn.

This project successfully solves the "Impossible Dream" Challenger map in **44 turns**, beating the official reference record of 45 turns.

---

## Instructions

### Prerequisites
*   Python 3.10 or later
*   `make`

### Installation
To install the required dependencies (`pygame`, `flake8`, `mypy`), run:
```bash
make install
```

### Execution
You can run the simulation using the Makefile or directly via Python.

# Run the default Challenger map
```bash
make run

make run MAP=maps/easy/01_linear_path.txt

python3 -m src maps/medium/02_circular_loop.txt
```

## Algorithm Explanation

To achieve optimal performance and beat the Challenger map, standard pathfinding algorithms (like basic Dijkstra or A*) are insufficient because they are "time-blind" and route all drones into massive traffic jams.

This project uses an **Iterative Dijkstra with Soft-Decaying Weight Penalties**.

**Implementation Strategy:**
1.  **Base Routing:** The algorithm routes drones one by one using Dijkstra's algorithm. The base cost of a node is determined by its type (Normal = 1.0, Restricted = 2.0, Priority = 0.9).
2.  **Capacity-Aware Penalties:** Once a path is found for a drone, a mathematical penalty is applied to every zone on that path. The penalty is inversely proportional to the zone's capacity (`0.4 / max_drones`). This means a bottleneck zone gets a massive penalty, while a wide-open zone gets a tiny penalty.
3.  **The "Soft Decay" (Simulating Time):** To prevent paths from being permanently ruined, the algorithm simulates the passage of time. Every 4 drones routed, the entire map "cools down," and all penalties are reduced by `0.4`. 

**Why this works:** This creates a "pulsing" effect. Drones 1-2 take the absolute shortest path. Drones 3-4 see the traffic jam and take a slight detour. By the time Drones 5-6 are routed, the first path has cooled down, and they reuse it. This perfectly balances traffic across the map and maximizes throughput.

---

## Visual Representation

The project includes a graphical visualizer built with **Pygame**. 

**Features:**
*   **Auto-Scaling Camera:** The visualizer automatically calculates the bounding box of the parsed map, scaling and centering the network to perfectly fit the window regardless of the map's coordinate sizes.
*   **Smooth Animation:** Drone movements are animated using Linear Interpolation (`lerp`), providing clear visual feedback of drones traveling between zones.
*   **State Tracking:** Drones traveling to `restricted` zones are visibly halted at the exact midpoint of the connection lines, perfectly representing the 2-turn transit rule.
*   **Color Mapping:** Zones are dynamically colored based on the `[color=...]` metadata provided in the map files, with safe fallbacks for unrecognized color strings.

---

## Example Input and Output

**Input Map Snippet:**
```text
nb_drones: 2
start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [zone=restricted color=blue]
end_hub: goal 2 0 [color=red]
connection: start-waypoint1
connection: waypoint1-goal
```

**Expected Output (Stdout):**
```text
D1-start-waypoint1
D1-waypoint1
D1-goal D2-start-waypoint1
D2-waypoint1
D2-goal
Total turns: 5
```

---

## Resources & AI Usage

**References:**
*   *Multi-Agent Path Finding (MAPF)*: Academic concepts regarding Makespan vs. Flowtime optimization.
*   *Dijkstra's Algorithm*: Core graph traversal logic.
*   *Pygame Documentation*: Vector math and rendering.

**AI Usage Declaration:**
Artificial Intelligence (LLM) was used as a senior mentor during this project to:
1.  Understand the academic formalization of MAPF and the difference between Makespan and Flowtime.
2.  Brainstorm strategies to overcome the "Traffic Jam" problem, leading to the development of the Soft-Decaying Penalty math.
3.  Debug Pygame coordinate scaling and linear interpolation math.
4.  Refine Python strict typing (`mypy`) syntax for complex nested dictionaries.
No code was blindly copy-pasted. AI was used strictly for conceptual understanding, debugging guidance, and architectural feedback.

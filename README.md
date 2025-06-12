# Dynamic Programming for Robotics Navigation

## 🔍 Project Overview

This project presents a dynamic programming solution for an autonomous agent navigating a "Door & Key" grid-world. The core objective is to compute an optimal policy that minimizes the total energy (cost) for the agent to travel from a starting position to a goal location. The task is complicated by environmental obstacles, including a locked door that requires the agent to first find and collect a key. The problem is cast as a finite-horizon deterministic Markov Decision Process (MDP), and the solution handles two distinct scenarios: environments with a fully "Known Map" and a set of "Random Maps" where the key, goal, and door states are variable.

## 🛠️ Technical Components

### 1️⃣ Markov Decision Process (MDP) Formulation

  * **State Space**: The agent's state is defined by its `(x, y)` position, heading `h`, key possession status `k`, and the open/closed status `d` of the door(s).
  * **Actions**: The agent can perform five distinct actions: Move Forward (MF), Turn Left (TL), Turn Right (TR), Pickup Key (PK), and Unlock Door (UD).
  * **Transitions & Costs**: State transitions are deterministic based on the current state and action. Each action incurs a positive energy cost, with movement costing more than turning or object interaction.

### 2️⃣ Backward Dynamic Programming

  * An optimal policy is computed by solving the Bellman equation using a finite-horizon, backward dynamic programming approach.
  * The algorithm starts from a terminal cost at the goal and iteratively computes the optimal value function (cost-to-go) for all states at each time step, moving backward from a horizon `T`.
  * The final optimal policy is extracted by selecting the action that minimizes the cost-to-go at each state.

### 3️⃣ "Known Map" Solution

  * For each of the 7 predefined "Known Map" environments, a separate optimal control policy is computed offline.
  * The policy is then executed on the corresponding environment to guide the agent to the goal.

### 4️⃣ "Random Map" Universal Policy

  * For the "Random Map" scenario, policies for all 36 possible map configurations are pre-computed offline.
  * These individual policies are merged into a single universal look-up table.
  * At runtime, the agent identifies the specific map configuration and uses the look-up table to execute the optimal action sequence with zero online planning cost.

## 📂 Project Structure

```
.
├── code/
│   ├── partA.py        # Solution for the Known Map scenario
│   ├── partB.py        # Solution for the Random Map scenario
│   ├── doorkey.py      # Main script to run the project
│   ├── utils.py        # Helper functions for environment interaction
│   ├── create_env.py   # Script to generate the environment files
│   ├── requirements.txt # Python dependencies
│   └── envs/           # Directory containing environment files
└── report/
    └── ECE276B_Project1_Report.pdf # Project report
```

## 📈 Results & Performance

  * Achieved a 100% success rate, solving all 7 "Known Map" and all 36 "Random Map" environments.
  * The implemented policies successfully guide the agent along trajectories that match the theoretical minimum cost.
  * The universal policy for the "Random Map" scenario operates with zero-overhead online execution by leveraging the pre-computed look-up table.

## 🛠️ Technologies

  * **Python** for implementation.
  * **NumPy** for efficient numerical operations.
  * **Gymnasium & MiniGrid** for the grid-world environment simulation.
  * **Matplotlib & Imageio** for visualization and GIF generation.

## 📚 Documentation

Detailed implementation, problem formulation, and results are available in the project report: [`report/ECE276B_Project1_Report.pdf`](https://www.google.com/search?q=report/ECE276B_Project1_Report.pdf).

---

## 📧 Contact
- **Brian (Shou-Yu) Wang**  
  - Email: briansywang541@gmail.com  
  - LinkedIn: [linkedin.com/in/sywang541](https://linkedin.com/in/sywang541)
  - GitHub: [BrianSY541](https://github.com/BrianSY541)

---

**Project developed as part of ECE 276B: Planning & Learning in Robotics at UC San Diego.**

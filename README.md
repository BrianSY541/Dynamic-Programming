# ECE 276B: Project 1 - Dynamic Programming

This repository contains the solution for Project 1 of ECE 276B: Planning & Learning in Robotics at UC San Diego. The project focuses on using dynamic programming to solve a navigation and object interaction problem in a "Door & Key" grid-world environment.

![5x5 Normal Map](httpss://github.com/your-username/your-repo/blob/main/plot/5x5_normal/doorkey-5x5-normal.gif)

## Project Overview

The goal of this project is to implement a dynamic programming algorithm that enables an agent to find the optimal (lowest cost) path from a starting position to a goal position in a 2D grid environment. The environment may contain walls, a key, and a locked door. To reach the goal, the agent may need to pick up the key and use it to unlock the door.

This project is divided into two main parts:
* [cite_start]**Part A: Known Map** - The agent must find the optimal policy for several predefined environments where all details are known beforehand. 
* [cite_start]**Part B: Random Map** - The agent must derive a single, universal policy that is optimal for a set of 36 randomly generated 10x10 environments.  [cite_start]In these environments, the locations of the key and goal, and the status of the doors, are randomly chosen from a predefined set of possibilities. 

[cite_start]The solution formulates the problem as a finite deterministic Markov Decision Process (MDP)  [cite_start]and uses backward dynamic programming to find the optimal policy. 

## Repository Structure
├── code/
│   ├── partA.py        # Solution for the Known Map scenario
│   ├── partB.py        # Solution for the Random Map scenario
│   ├── doorkey.py      # Main script to run the project
│   ├── utils.py        # Helper functions for environment interaction
│   ├── create_env.py   # Script to generate the environment files
│   ├── requirements.txt # Python dependencies
│   └── envs/           # Directory containing environment files
├── plot/
│   └── ...             # Saved GIFs of the agent's trajectories
└── report/
    └── ECE276B_Project1_Report.pdf # Project report
    
## Getting Started

### Prerequisites

This project requires Python and the libraries listed in `requirements.txt`.

### Installation

1.  Clone the repository:
    ```bash
    git clone [https://github.com/your-username/your-repo.git](https://github.com/your-username/your-repo.git)
    cd your-repo/code
    ```
2.  Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Code

You can run the entire project, which will solve for both Part A and Part B and generate GIFs of the optimal trajectories, by executing the `doorkey.py` script:

```bash
python doorkey.py
```
The script will save the resulting GIFs in the plot/ directory.

---

## 📧 Contact
- **Brian (Shou-Yu) Wang**  
  - Email: briansywang541@gmail.com  
  - LinkedIn: [linkedin.com/in/sywang541](https://linkedin.com/in/sywang541)
  - GitHub: [BrianSY541](https://github.com/BrianSY541)

---

**Project developed as part of ECE 276A: Sensing & Estimation in Robotics at UC San Diego.**

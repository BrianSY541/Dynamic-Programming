from utils import *
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------
# Direction tables
# ---------------------------------------------------------------------

# Mapping: heading‑id → unit vector (dx, dy)
Direction = {0: (1, 0), 1: (0, 1), 2: (-1, 0), 3: (0, -1)}  # right,down,left,up
# Heading update when turning
LEFT = {0: 3, 1: 0, 2: 1, 3: 2}   # h←LEFT[h]
RIGHT = {0: 1, 1: 2, 2: 3, 3: 0}  # h←RIGHT[h]


# ---------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------

def to_tuple(xy) -> Tuple[int, int]:
    """Cast a numpy array / list / tuple into a **hashable** `(x, y)` pair.

    Parameters
    ----------
    xy : array-like
        Length-2 coordinate container.
    """
    return tuple(int(v) for v in xy)


# ---------------------------------------------------------------------
# ❶  State‑space construction
# ---------------------------------------------------------------------

def enumerate_state(info: dict) -> List[Tuple]:
    """Enumerate **all** logical states for a *specific* environment.

    A state is encoded as
        `(x, y, h, has_key, door_0_open, door_1_open, …)`

    * `x, y`: agent position, (0 ≤ x < W).
    * `h`   : heading id ∈ {0,1,2,3} (→,↓,←,↑).
    * `has_key`: 1 if the key has been collected, else 0.
    * `door_i_open`: bit per door (1=open, 0=closed).

    Notes
    -----
    The function adapts to **any** number of doors; for known maps
    (≤ 1 door) the loop simply iterates over 1-bit masks.
    """
    W, H = info["width"], info["height"]
    door_bits = max(1, len(info.get("door_pos", [])))  # at least one bit

    states: List[Tuple] = []
    for x in range(W):
        for y in range(H):
            for h in range(4):
                for k in (0, 1):
                    for d_mask in range(1 << door_bits):
                        doors = [(d_mask >> i) & 1 for i in range(door_bits)]
                        states.append((x, y, h, k, *doors))
    return states


# ---------------------------------------------------------------------
# ❷  Collision queries
# ---------------------------------------------------------------------

def is_wall(coord: Tuple[int, int], info: dict) -> bool:
    """Return **True** if *coord* is outside world bounds **or** occupied by wall."""
    x, y = coord
    W, H = info["width"], info["height"]
    if x < 0 or x >= W or y < 0 or y >= H:
        return True  # out‑of‑bounds treated as walls
    return coord in info.get("wall_pos", set())


# ---------------------------------------------------------------------
# ❸  Action feasibility & transition model
# ---------------------------------------------------------------------

def legal_actions(state: Tuple, info: dict) -> List[int]:
    """Return the **subset** of actions {MF, TL, TR, PK, UD} legal from *state*.

    - Turning (TL/TR) is *always* legal.
    - Forward move requires target cell not wall **and** not a closed door.
    - Pickup (PK) legal iff **key is in front** and agent has not taken it.
    - Unlock (UD) legal iff **door in front is closed** *and* agent has key.
    """
    x, y, h, k, *doors = state
    acts = [TL, TR]  # turning is free of constraints

    # cell in front of the agent
    dx, dy = Direction[h]
    fx, fy = x + dx, y + dy

    # Check if a door occupies the front cell & its index
    front_door_idx = None
    for idx, dpos in enumerate(info.get("door_pos", [])):
        if to_tuple(dpos) == (fx, fy):
            front_door_idx = idx
            break

    front_is_wall = is_wall((fx, fy), info)
    front_is_key = to_tuple(info.get("key_pos")) == (fx, fy)

    # ---- Move Forward -------------------------------------------------
    if not front_is_wall and not (
        front_door_idx is not None and doors[front_door_idx] == 0
    ):
        acts.append(MF)
    # ---- Pick up key ---------------------------------------------------
    if not k and front_is_key:
        acts.append(PK)
    # ---- Unlock door ---------------------------------------------------
    if front_door_idx is not None and doors[front_door_idx] == 0 and k:
        acts.append(UD)

    return acts


def transition(state: Tuple, action: int, info: dict):
    """Deterministic transition (x,u)→(x',u') returning next-state & stage-cost."""
    x, y, h, k, *doors = state
    doors = list(doors)

    if action == TL:
        h = LEFT[h]
    elif action == TR:
        h = RIGHT[h]
    elif action == MF:
        dx, dy = Direction[h]
        x, y = x + dx, y + dy
    elif action == PK:
        k = 1
    elif action == UD:
        # open the door right in front
        dx, dy = Direction[h]
        fx, fy = x + dx, y + dy
        for idx, dpos in enumerate(info.get("door_pos", [])):
            if to_tuple(dpos) == (fx, fy):
                doors[idx] = 1
                break

    return (x, y, h, k, *doors), step_cost(action)


# ---------------------------------------------------------------------
# ❹  Cost functions
# ---------------------------------------------------------------------

def terminal_cost(state: Tuple, info: dict) -> float:
    """Return 0 if *state* reaches goal, else a large penalty (→ discourages stop)."""
    x, y, *_ = state
    gx, gy = info.get("goal_pos")
    return 0.0 if (x, y) == (gx, gy) else 1e4


# ---------------------------------------------------------------------
# ❺  Backward Dynamic Programming (finite horizon)
# ---------------------------------------------------------------------

def backward_dp(info: dict, T: int = 200, gamma: float = 0.99):
    """Compute optimal value V0 and greedy policy pi0.

    Parameters
    ----------
    info   : dict
        Environment description (positions of key/door/goal, walls, size…).
    T      : int, optional
        Planning horizon — should exceed any optimal path length; the loop
        stops earlier if value iteration converges.
    gamma  : float ∈ (0,1]
        Discount factor for *stage costs*.  Because all costs are positive,
        choosing y<1 encourages shorter paths, but y≈1 typically suffices.
    """
    X = enumerate_state(info)
    V_next: Dict[Tuple, float] = {x: terminal_cost(x, info) for x in X}  # V_T
    PI: Dict[Tuple, int] = {}

    for t in reversed(range(T)):
        V_curr: Dict[Tuple, float] = {}
        for x in X:
            best_q, best_u = float("inf"), None
            for u in legal_actions(x, info):
                x_next, l_cost = transition(x, u, info)
                q = l_cost + gamma * V_next[x_next]
                if q < best_q:
                    best_q, best_u = q, u
            V_curr[x] = min(best_q, terminal_cost(x, info))
            PI[x] = best_u
        # —— Early stopping: value has converged ——
        if all(abs(V_curr[s] - V_next[s]) < 1e-6 for s in X):
            break
        V_next = V_curr
    return PI, V_next

# ---------------------------------------------------------------------
# ❻  Front‑end helper for *Part A*
# ---------------------------------------------------------------------

def extract_static_walls(env) -> set:
    """Return a set of (x,y) coordinates that are walls. Outer boundary excluded
    because we treat out-of-bounds automatically as walls."""
    walls = set()
    for i in range(env.unwrapped.height):
        for j in range(env.unwrapped.width):
            cell = env.unwrapped.grid.get(j, i)
            if cell is not None and cell.type == "wall":
                walls.add((j, i))
    return walls

def plan_once(env, info) -> List[int]:
    """Solve **one** known-map instance and return the optimal action list.

    Workflow:
        1.  Augment *info* with static walls extracted from `env`.
        2.  Solve DP → obtain *policy*.
        3.  Roll out policy from the *true* initial logical state until the
            goal is reached (or a loop is detected).
    """
    # 1) add wall coordinates for collision checks
    info = dict(info)  # shallow copy → safe to edit
    info["wall_pos"] = extract_static_walls(env)

    # 2) solve DP
    policy, _ = backward_dp(info)

    # 3) logical initial state
    ix, iy = info["init_agent_pos"]
    heading_table = {(1, 0): 0, (0, 1): 1, (-1, 0): 2, (0, -1): 3}
    ih = heading_table[tuple(info["init_agent_dir"])]
    door_bits = len(info.get("door_pos", [])) or 1
    doors0 = [1 if o else 0 for o in info.get("door_open", [0] * door_bits)]
    state = (ix, iy, ih, 0, *doors0)

    # rollout -----------------------------------------------------------
    seq: List[int] = []
    visited = set()
    while terminal_cost(state, info) > 0:
        if state in visited:
            raise RuntimeError("Loop detected — horizon T too small?")
        visited.add(state)
        a = policy[state]
        if a is None:
            raise RuntimeError(f"No legal action from state {state}")
        seq.append(a)
        state, _ = transition(state, a, info)

    return seq
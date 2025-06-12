from utils import *
from partA import *
import itertools, numpy as np
from functools import lru_cache

# ---------------------------------------------------------------------------
# Problem constants (dictated by the assignment)
# ---------------------------------------------------------------------------
SIZE = 10  # Grid width = height

# Candidate positions for key and goal (converted to numpy later)
KEY_CAND: List[Tuple[int, int]] = [(2, 2), (2, 3), (1, 6)]
GOAL_CAND: List[Tuple[int, int]] = [(6, 1), (7, 3), (6, 6)]

# Two doors embedded in the vertical wall at x = 5
DOOR_POS: List[Tuple[int, int]] = [(5, 3), (5, 7)]

# A convenience set of the *non‑door* wall tiles used by legal‑action check
WALL_POS = {(5, y) for y in range(SIZE)} - set(DOOR_POS)


# ---------------------------------------------------------------------------
# Helper – static part of the `info` dict common to all scenarios
# ---------------------------------------------------------------------------

def _base_info() -> dict:
    """Return an *info* dictionary that already contains all *static*
    map information - walls & doors - but *no* key/goal/door-state.
    """
    return {
        "width": SIZE,
        "height": SIZE,
        "door_pos": [np.array(p) for p in DOOR_POS],
        "wall_pos": WALL_POS,  # for legality checks in partA.legal_actions
    }


# ---------------------------------------------------------------------------
# 1)  Offline pre‑computation (cached)
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def precompute_policies() -> Dict[Tuple[int, int, int, int], Dict[Tuple, int]]:
    """Compute and store the optimal policy for **every** of the 36 parameter
    combinations.

    Returns
    -------
    dict
        Mapping  *(k_idx, g_idx, d1, d2)* → *policy* where
        *policy* itself maps **state tuples** to optimal actions.

    The heavy lifting is delegated to :pyfunc:`partA.backward_dp`.
    The result is cached (LRU) so subsequent calls are O(1).
    """
    policies = {}
    for k_idx, key_xy in enumerate(KEY_CAND):
        for g_idx, goal_xy in enumerate(GOAL_CAND):
            # d1/d2 are *booleans* indicating whether each door starts open
            for d1, d2 in itertools.product((0, 1), repeat=2):
                info = _base_info()
                info.update(
                    {
                        "key_pos": np.array(key_xy),
                        "goal_pos": np.array(goal_xy),
                        "door_open": [bool(d1), bool(d2)],
                    }
                )
                π, _ = backward_dp(info, T=300, gamma=0.99)
                policies[(k_idx, g_idx, d1, d2)] = π
    print("[partB] finished backward DP for 36 scenarios → policies cached")
    return policies


# ---------------------------------------------------------------------------
# Helper – infer the 4‑tuple index from an *info* dict at run‑time
# ---------------------------------------------------------------------------

def _scenario_from_info(info: dict) -> Tuple[int, int, int, int]:
    """Convert a runtime `info` dict (as produced by utils.load_*_env) into the
    canonical 4-tuple key used by :pyfunc:`precompute_policies`.
    """
    k_idx = KEY_CAND.index(tuple(info["key_pos"]))
    g_idx = GOAL_CAND.index(tuple(info["goal_pos"]))
    d1, d2 = (int(b) for b in info["door_open"])
    return (k_idx, g_idx, d1, d2)


# ---------------------------------------------------------------------------
# 2)  Online rollout
# ---------------------------------------------------------------------------

def rollout(env, info: dict) -> List[int]:
    """Execute the pre-computed policy starting from the *true* initial state.

    Parameters
    ----------
    env
        Gym-MiniGrid environment object (already reset to the scenario).
    info
        The metadata dictionary returned alongside *env* by
        :pyfunc:`utils.load_random_env` **or** `utils.load_all_random_env`.

    Returns
    -------
    list[int]
        Optimal action sequence leading the agent from its spawn to the
        goal.  Each action is one of `MF, TL, TR, PK, UD`.
    """
    # We need walls for legality; extract once here to avoid re‑parsing later
    info = dict(info)  # shallow copy so we can mutate safely
    info["wall_pos"] = extract_static_walls(env)

    # Ensure door ordering matches the global DOOR_POS list so that the two
    # booleans (d1, d2) are in consistent order.  The random map loader does
    # not guarantee this.
    ordered_pos, ordered_bits = [], []
    for wanted in DOOR_POS:  # deterministic order
        idx = next(i for i, p in enumerate(info["door_pos"]) if tuple(p) == wanted)
        ordered_pos.append(info["door_pos"][idx])
        ordered_bits.append(info["door_open"][idx])
    info["door_pos"] = ordered_pos
    info["door_open"] = ordered_bits

    # Retrieve the correct policy dict
    π = precompute_policies()[_scenario_from_info(info)]

    # Build initial MDP state (x, y, heading, has_key, door1, door2)
    x0, y0 = info["init_agent_pos"]
    heading_map = {(1, 0): 0, (0, 1): 1, (-1, 0): 2, (0, -1): 3}
    h0 = heading_map[tuple(info["init_agent_dir"])]
    state = (x0, y0, h0, 0, *[int(b) for b in ordered_bits])

    seq, visited = [], set()
    while terminal_cost(state, info) > 0:
        if state in visited:
            raise RuntimeError("DP horizon too short — policy loops detected")
        visited.add(state)
        action = π[state]
        seq.append(action)
        state, _ = transition(state, action, info)
    return seq
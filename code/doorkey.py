from utils import *
from example import example_use_of_gym_env
from gymnasium.envs.registration import register
from minigrid.envs.doorkey import DoorKeyEnv
from partA import *
from partB import *

MF = 0  # Move Forward
TL = 1  # Turn Left
TR = 2  # Turn Right
PK = 3  # Pickup Key
UD = 4  # Unlock Door

ACTION_STR = {MF: "MF", TL: "TL", TR: "TR", PK: "PK", UD: "UD"}

class DoorKey10x10Env(DoorKeyEnv):
    def __init__(self, **kwargs):
        super().__init__(size=10, **kwargs)

register(
    id='MiniGrid-DoorKey-10x10-v0',
    entry_point='__main__:DoorKey10x10Env'
)

def doorkey_problem(env):
    """
    You are required to find the optimal path in
        doorkey-5x5-normal.env
        doorkey-6x6-normal.env
        doorkey-8x8-normal.env

        doorkey-6x6-direct.env
        doorkey-8x8-direct.env

        doorkey-6x6-shortcut.env
        doorkey-8x8-shortcut.env

    Feel Free to modify this fuction
    """
    optim_act_seq = [TL, MF, PK, TL, UD, MF, MF, MF, MF, TR, MF]
    return optim_act_seq


def partA():
    env_paths = [
        "./envs/known_envs/doorkey-5x5-normal.env",
        "./envs/known_envs/doorkey-6x6-direct.env",
        "./envs/known_envs/doorkey-6x6-normal.env",
        "./envs/known_envs/doorkey-6x6-shortcut.env",
        "./envs/known_envs/doorkey-8x8-direct.env",
        "./envs/known_envs/doorkey-8x8-normal.env",
        "./envs/known_envs/doorkey-8x8-shortcut.env",
    ]
    for p in env_paths:
        env, info = load_env(p)
        seq = plan_once(env, info)
        total_cost = sum(step_cost(a) for a in seq)
        print(f"\n{p}: cost={total_cost:.1f}, length={len(seq)}")
        print(" → ".join(ACTION_STR[a] for a in seq))
        draw_gif_from_seq(seq, env, path="./gif" + p[len("./envs"):-3] + "gif")


def partB():
    for i in range(1, 37):
        env_path = f"./envs/random_envs/DoorKey-10x10-{i}.env"
        env, info = load_all_random_env(env_path)
        seq = rollout(env, info)
        total_cost = sum(step_cost(a) for a in seq)
        print(f"\n{env_path}: cost={total_cost:.1f}, length={len(seq)}")
        print(" → ".join(ACTION_STR[a] for a in seq))
        draw_gif_from_seq(seq, env, path="./gif" + env_path[len("./envs"):-3] + "gif")


if __name__ == "__main__":
    env_path = "./envs/example-8x8.env"
    env, info = load_env(env_path)
    seq = plan_once(env, info)
    total_cost = sum(step_cost(a) for a in seq)
    print(f"\n{env_path}: cost={total_cost:.1f}  len={len(seq)}")
    print(" → ".join(ACTION_STR[a] for a in seq))
    draw_gif_from_seq(seq, env)
    partA()
    partB()


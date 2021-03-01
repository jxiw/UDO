import math
import random
import time

import gym
from gym_opgame.envs import index

import constants
from mcts import global_inter

env = gym.make('opgame-v0')

tree_height = 12
init_state = env.map_number_to_state(0)
total_round = 50000

root = global_inter.Global_Inter_Node(0, 0, tree_height, init_state, env)

best_performance = 0
prev_index_action = []
idx_build_time = 0

reset_database = 1

index_card_info = list(map(lambda x: x[3], index.candidate_indices))

env.reset()
default_throughput = env.evaluate()

start_time = time.time()
reset_time = 0

for round in range(1, total_round, 1):
    selected_actions = root.sample(round)
    # show those actions
    print(selected_actions)
    env.reset()
    previous_reward = default_throughput
    performance_info = dict()
    for action in selected_actions:
        observation, current_reward, done, info = env.step(action)
        delta_reward = max(current_reward - previous_reward, 0)
        performance_info[action] = delta_reward

    # selected_actions
    print("actions:", selected_actions)
    print("performance info:", performance_info)
    root.update_statistics(performance_info, selected_actions)
    current_time = time.time()
    print("duration:", current_time - start_time - reset_time)
    print("index time:", idx_build_time)
    print("current best action:", root.best_actions())
    start_reset = time.time()
    if round % reset_database == reset_database - 1:
        print("reset database")
        env.reset_database()
    end_reset = time.time()
    reset_time += (end_reset - start_reset)

# return the best performance action
print("best action:")
print("best performance:", best_performance)


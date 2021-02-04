import math
import random
import time

import gym
from gym_opgame.envs import index

import constants
from mcts import global_node

env = gym.make('opgame-v0')

tree_height = 11
init_state = env.map_number_to_state(0)
total_round = 50000

root = global_node.Global_Node(0, 0, tree_height, init_state, env)

best_performance = 0
prev_index_action = []
idx_build_time = 0

reset_database = 100

index_card_info = list(map(lambda x: x[3], index.candidate_indices))

env.reset()
default_throughput = env.evaluate()

start_time = time.time()

for round in range(1, total_round, 1):
    selected_actions = root.sample(round)
    # show those actions
    print(selected_actions)
    env.reset()
    for action in selected_actions:
        # observation, reward, done, info = env.step(selected_action)
        if action < env.nA_reorder or action >= (env.nA_reorder + env.nA_index):
            state = env.step_without_evaluation(action)
    current_index_action = [action for action in selected_actions if
                            (env.nA_reorder + env.nA_index) > action >= env.nA_reorder]
    # build indices
    print("current_index_action:", current_index_action)
    print("prev_index_action:", prev_index_action)
    add_action = set(current_index_action) - set(prev_index_action)
    drop_action = set(prev_index_action) - set(current_index_action)
    print("add action:", add_action)
    print("drop action:", drop_action)
    # build the indices
    time_start = time.time()
    env.index_step(add_action, drop_action)
    time_end = time.time()
    idx_build_time += (time_end - time_start)
    total_throughput = env.evaluate()
    reward = total_throughput / default_throughput
    root.update_statistics(reward, selected_actions)
    current_time = time.time()
    print("duration:", current_time - start_time)
    print("index time:", idx_build_time)
    print("current best action:", root.best_actions())
    best_performance = total_throughput
    print("best performance:", best_performance)
    prev_index_action = current_index_action
    if round % reset_database == reset_database - 1:
        print("reset database")
        env.reset_database()
        prev_index_action = []

# return the best performance action
print("best action:")
print("best performance:", best_performance)


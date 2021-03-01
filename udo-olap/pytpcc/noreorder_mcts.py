import math
import random
import time

import gym
from gym_olapgame.envs import index

import constants
from mcts import global_node

env = gym.make('olapgame-v0')

tree_height = 9
init_state = env.map_number_to_state(0)
total_round = 20000

root = global_node.Global_Node(0, 0, tree_height, init_state, env)
# heavy_configure_range = set(range(env.nA_reorder, env.nA_reorder + env.nA_index))
# heavy_configure_frequency = dict()
# for heavy_idx in heavy_configure_range:
#     heavy_configure_frequency[heavy_idx] = 0
#
# heavy_configure_actions = dict()
# threshold = 5

# while round < total_round:
#     selected_actions = root.sample(round)
#     # show those actions
#     print(selected_actions)
#     # detect the heavy configuration
#     for selected_action in selected_actions:
#         heavy_configure_frequency[selected_action] = heavy_configure_frequency[selected_action] + 1
#
#     # evaluate those actions
#     round = round + 1

best_performance = 0
# best_action = []
prev_index_action = []
idx_build_time = 0

all_queries = list(constants.QUERIES.keys())
nr_query = len(all_queries)

query_info = {all_queries[idx]: idx for idx in range(nr_query)}
index_card_info = list(map(lambda x: x[4], index.candidate_indices))
index_query_info = list(map(lambda x: list(map(lambda y: query_info[y], x[3])), index.candidate_indices))

env.reset()
constants.default_runtime = env.evaluate_light_under_heavy(all_queries, [0] * len(all_queries))
# constants.default_runtime = [1] * len(all_queries)
start_time = time.time()

for round in range(1, total_round, 1):
    selected_actions = root.sample(round)
    # show those actions
    print(selected_actions)
    env.reset()
    for action in selected_actions:
        # observation, reward, done, info = env.step(selected_action)
        if action >= env.index_candidate_num:
            state = env.step_without_evaluation(action)
    current_index_action = [action for action in selected_actions if action < env.index_candidate_num]
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
    query_to_consider = set(
        [item for sublist in list(map(lambda x: index_query_info[x], current_index_action)) for item in
         sublist])
    if len(query_to_consider) == 0:
        query_to_consider = set(range(nr_query))
    sample_num = math.ceil(constants.sample_rate * len(query_to_consider))
    sampled_query_list = random.sample(list(query_to_consider), k=sample_num)
    run_time = env.evaluate_light_under_heavy([all_queries[select_query] for select_query in sampled_query_list],
                                              [constants.default_runtime[select_query] for select_query in
                                               sampled_query_list])
    total_run_time = sum(run_time)
    default_time = sum(constants.default_runtime[select_query] for select_query in sampled_query_list)
    reward = default_time / total_run_time

    root.update_statistics(reward, selected_actions)
    current_time = time.time()
    print("duration:", current_time - start_time)
    print("index time:", idx_build_time)

    other_default_time = sum(constants.default_runtime[select_query] for select_query in range(nr_query) if
                             select_query not in sampled_query_list)
    print("estimate whole workload time:", (other_default_time + total_run_time))

    print("current best action:")
    # print(best_action)
    root.print()
    print("best performance:%d"%best_performance)
    prev_index_action = current_index_action

# return the best performance action
print("best action:")
# print(best_action)
print("best performance:%d"%best_performance)


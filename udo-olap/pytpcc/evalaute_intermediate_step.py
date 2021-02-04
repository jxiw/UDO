import math
from typing import Dict, List, Any

import gym
import gym_olapgame
from gym_olapgame.envs import index

from mcts import delay_uct_node
from mcts import uct_node
import time
import constants
import random
import order_optimizer

all_queries = list(constants.QUERIES.keys())
nr_query = len(all_queries)

# print(all_queries)
query_info = {all_queries[idx]: idx for idx in range(nr_query)}
index_card_info = list(map(lambda x: x[4], index.candidate_indices))
index_query_info = list(map(lambda x: list(map(lambda y: query_info[y], x[3])), index.candidate_indices))

print("start:", time.time())

optimizer = order_optimizer.OrderOptimizer(index_card_info)
env = gym.make('olapgame-v0')

# number of indices equal heavy_tree_height + 1
heavy_tree_height = 4
light_tree_height = 8

init_state = env.map_number_to_state(0)
macro_episode = 10000
micro_episode = 5

terminate_action = env.index_candidate_num
light_tree_cache = dict()

# prepare the heavy configurations
delay_time = 20

global_max_reward = 0
global_max_action = []

env.reset()
constants.default_runtime = env.evaluate_light_under_heavy(all_queries, [0] * len(all_queries))

heavy_root = delay_uct_node.Delay_Uct_Node(0, 0, heavy_tree_height, terminate_action, init_state, env)
idx_build_time = 0

t1 = 1
while t1 < macro_episode:
    selected_heavy_action_batch = []
    configuration_to_evaluate = []
    # remove_terminate_action_batch = []
    for d in range(delay_time):
        selected_heavy_actions = heavy_root.sample(t1 + d)
        selected_heavy_action_batch.append(selected_heavy_actions)
        # add all intermediate steps
        remove_terminate_heavy_actions = [heavy_action for heavy_action in selected_heavy_actions if
                                          heavy_action != terminate_action]
        for i in range(len(remove_terminate_heavy_actions)):
            current_actions = frozenset(remove_terminate_heavy_actions[:i + 1])
            if current_actions not in configuration_to_evaluate:
                configuration_to_evaluate.append(current_actions)
    # show those actions
    print(selected_heavy_action_batch)
    print("evaluate configurations:", configuration_to_evaluate)
    # evaluated_order = range(0, len(remove_terminate_action_batch))
    evaluated_order = optimizer.min_cost_order(configuration_to_evaluate)
    print("evaluated order:", evaluated_order)
    macro_performance_info = dict()
    for current_order_idx in range(len(evaluated_order)):
        current_order = evaluated_order[current_order_idx]
        selected_heavy_action_frozen = frozenset(configuration_to_evaluate[current_order])
        # generate add action
        add_action = set(selected_heavy_action_frozen)
        drop_action = set()
        if current_order_idx > 0:
            # take the previous created indices
            previous_set = set(configuration_to_evaluate[evaluated_order[current_order_idx - 1]])
        if t1 > 1 or current_order_idx > 0:
            add_action = add_action - previous_set
            drop_action = previous_set - set(selected_heavy_action_frozen)
            print("invoke action")
            print(add_action)
            print("drop action")
            print(drop_action)
        # build the indices
        time_start = time.time()
        env.index_step(add_action, drop_action)
        time_end = time.time()
        idx_build_time += (time_end - time_start)

        print("selected_heavy_action_frozen:", selected_heavy_action_frozen)
        if selected_heavy_action_frozen in light_tree_cache:
            light_root = light_tree_cache[selected_heavy_action_frozen]
        else:
            light_root = uct_node.Uct_Node(0, 0, light_tree_height, init_state, env)
            light_tree_cache[selected_heavy_action_frozen] = light_root
        # for the light tree
        best_reward = 0
        # query to consider for the current select heavy configuration
        query_to_consider = set(
            [applicable_query for applicable_queries in
             list(map(lambda x: index_query_info[x], selected_heavy_action_frozen)) for applicable_query in
             applicable_queries])
        print("query to consider:", query_to_consider)
        # best performance of the sampled each query
        best_micro_performance = dict()
        for t2 in range(1, micro_episode + 1):
            # for the micro episode
            env.reset()
            selected_light_actions = light_root.sample(t1 * micro_episode + t2)
            # evaluate the light actions
            for selected_light_action in selected_light_actions:
                # move to next state
                state = env.step_without_evaluation(selected_light_action)
            # obtain sample number
            sample_num = math.ceil(constants.sample_rate * len(query_to_consider))
            # generate sample queries
            sampled_query_list = random.choices(list(query_to_consider), k=sample_num)
            # obtain run time info by running queries within timeout
            run_time = env.evaluate_light_under_heavy(
                [all_queries[select_query] for select_query in sampled_query_list],
                [constants.default_runtime[select_query] for select_query in sampled_query_list])
            # the total time of sampled queries
            total_run_time = sum(run_time)
            # the default time of sampled queries
            default_time = sum(constants.default_runtime[select_query] for select_query in sampled_query_list)
            # the relative ration of the improvement, the less of total_run_time, the better
            light_reward = default_time / total_run_time
            print("light_action:", selected_light_actions)
            print("light_reward:", light_reward)
            light_root.update_statistics(light_reward, selected_light_actions)
            # update the best gain for each query
            for sample_query_id in range(len(sampled_query_list)):
                sample_query = sampled_query_list[sample_query_id]
                if sample_query in best_micro_performance:
                    # if we get better improvement, then set it to better time
                    if run_time[sample_query_id] < best_micro_performance[sample_query]:
                        best_micro_performance[sample_query] = run_time[sample_query_id]
                else:
                    best_micro_performance[sample_query] = run_time[sample_query_id]
            if sum(run_time) < best_reward:
                best_reward = sum(run_time)
        # save the performance of current selected heavy action
        macro_performance_info[selected_heavy_action_frozen] = best_micro_performance

    print("macro_performance_info:", macro_performance_info)
    # ### obtain the best macro performances info
    best_slot_performance = dict()
    for selected_heavy_action_frozen, performance in macro_performance_info.items():
        for query, query_run_time in performance.items():
            if query in best_slot_performance:
                if query_run_time < best_slot_performance[query]:
                    best_slot_performance[query] = query_run_time
            else:
                best_slot_performance[query] = query_run_time
    print("best_slot_performance", best_slot_performance)
    # after testing the performance of each configuration
    # generate the update information based on delta improvement
    update_info_slot = []
    for selected_heavy_actions in selected_heavy_action_batch:
        # generate intermediate result
        update_reward = []
        previous_performance = dict()
        for i in range(len(selected_heavy_actions)):
            if selected_heavy_actions[i] != terminate_action:
                selected_heavy_action_frozen = frozenset(selected_heavy_actions[:i + 1])
                print("current selected_heavy_action_frozen:", selected_heavy_action_frozen)
                current_performance = macro_performance_info[selected_heavy_action_frozen]
                # generate reward based on the difference between previous performance and current performance
                # the query for current indices
                query_to_consider = index_query_info[selected_heavy_actions[i]]
                # get the query to consider
                delta_improvement = 0
                for query in query_to_consider:
                    previous_runtime = constants.default_runtime[query]
                    current_runtime = constants.default_runtime[query]
                    if query in current_performance:
                        current_runtime = current_performance[query]
                    if query in previous_performance:
                        previous_runtime = previous_performance[query]
                    delta_improvement += max(previous_runtime - current_runtime, 0)
                update_reward.append(delta_improvement)
        # update the tree based on the simulation results
        update_info_slot.append((update_reward, [heavy_action for heavy_action in selected_heavy_actions if heavy_action != terminate_action]))
    print("update_info_slot:", update_info_slot)
    heavy_root.update_batch(update_info_slot)
    previous_set = set(configuration_to_evaluate[evaluated_order[-1]])
    heavy_root.print()
    print("time for indices:", idx_build_time)
    print("best heavy action", heavy_root.best_actions())
    t1 += delay_time

print("best heavy action", heavy_root.best_actions())

print("end:", time.time())

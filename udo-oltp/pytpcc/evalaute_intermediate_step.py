import math
from typing import Dict, List, Any

import gym
from gym_opgame.envs import index

from mcts import delay_uct_node
from mcts import uct_node
import time
import constants
import random
import order_optimizer

index_card_info = list(map(lambda x: x[3], index.candidate_indices))

print("start:", time.time())

env = gym.make('opgame-v0')

# number of indices equal heavy_tree_height + 1
heavy_tree_height = 3
light_tree_height = 8

init_state = env.map_number_to_state(0)
macro_episode = 10000
micro_episode = 5

terminate_action = env.nA_reorder + env.nA_index
light_tree_cache = dict()

optimizer = order_optimizer.OrderOptimizer(index_card_info, env.nA_reorder)

print("terminate_action:", terminate_action)
# prepare the heavy configurations
delay_time = 15

global_max_reward = 0
global_max_action = []

heavy_root = delay_uct_node.Delay_Uct_Node(0, 0, heavy_tree_height, terminate_action, init_state, env)
idx_build_time = 0

# global_max_reward = 0
# global_max_action = []

env.reset()
default_throughput = env.evaluate()

total_time = 0

# reset_database = 2

t1 = 1
while t1 < macro_episode:
    total_start = time.time()
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
    print("select batch action:", selected_heavy_action_batch)
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
        best_throughput = 0
        best_actions = []
        for t2 in range(1, micro_episode + 1):
            # for the micro episode
            env.reset()
            selected_light_actions = light_root.sample(t1 * micro_episode + t2)
            print("selected_light_actions:", selected_light_actions)
            # evaluate the light actions
            for selected_light_action in selected_light_actions:
                # move to next state
                state = env.step_without_evaluation(selected_light_action)
            total_throughput = env.evaluate()
            light_reward = max(float(total_throughput) / default_throughput, 0)
            light_root.update_statistics(light_reward, selected_light_actions)
            print("throughput:", total_throughput)
            print("reward:", light_reward)
            print("light tree best action:", light_root.best_actions())
            if total_throughput > best_throughput:
                best_throughput = total_throughput
                best_actions = selected_light_actions
        # save the performance of current selected heavy action
        print("best macro throughput:",  best_throughput)
        macro_performance_info[selected_heavy_action_frozen] = best_throughput
    print("performances", macro_performance_info)
    # generate the update information based on delta improvement
    update_info_slot = []
    for selected_heavy_actions in selected_heavy_action_batch:
        # generate intermediate result
        update_reward = []
        previous_performance = dict()
        previous_throughput = default_throughput
        for i in range(len(selected_heavy_actions)):
            if selected_heavy_actions[i] != terminate_action:
                selected_heavy_action_frozen = frozenset(selected_heavy_actions[:i + 1])
                print("current selected_heavy_action_frozen:", selected_heavy_action_frozen)
                current_throughput = macro_performance_info[selected_heavy_action_frozen]
                delta_improvement = max(current_throughput - previous_throughput, 0)
                update_reward.append(delta_improvement)
        # update the tree based on the simulation results
        update_info_slot.append((update_reward, [heavy_action for heavy_action in selected_heavy_actions if heavy_action != terminate_action]))
    print("update_info_slot:", update_info_slot)
    heavy_root.update_batch(update_info_slot)
    # try the reset database method
    print("reset database")
    env.reset_database()
    heavy_root.print()
    print("time for indices:", idx_build_time)
    print("best heavy action:", heavy_root.best_actions())
    total_end = time.time()
    total_time += (total_end - total_start)
    print("total time:", total_time)
    # evaluate those actions
    previous_set = set()
    t1 += delay_time

print("best heavy action", heavy_root.best_actions())

print("end:", time.time())

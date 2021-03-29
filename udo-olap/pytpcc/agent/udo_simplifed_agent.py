import random

import gym
import gym_olapoptimization
import time

import constants
from mcts import uct_node

def run_simplifed_udo_agent(duration, horizon):
    env = gym.make('olapoptimization-v0')
    env.reset()
    duration_in_seconds = duration * 3600
    init_state = env.state_decoder(0)
    light_root = uct_node.Uct_Node(0, 0, horizon, init_state, env)

    all_queries = list(constants.QUERIES.keys())
    start_time = time.time()
    current_time = time.time()

    # micro_episode = 100000
    # for t2 in range(micro_episode):
    ep = 0
    while (current_time - start_time) < duration_in_seconds:
        # for the micro episode
        selected_light_actions = light_root.sample(ep)
        print("selected_light_actions:", selected_light_actions)
        # evaluate the light actions
        env.reset()
        for selected_light_action in selected_light_actions:
            # move to next state
            state = env.step_without_evaluation(selected_light_action)
        # obtain run time info by running queries within timeout
        run_time = env.evaluate_light(all_queries, constants.default_runtime)
        # the total time of sampled queries
        total_run_time = sum(run_time)
        # the default time of sampled queries
        default_time = sum(constants.default_runtime)
        # the relative ration of the improvement, the less of total_run_time, the better
        # light_reward = default_time / total_run_time
        light_reward = max(default_time - total_run_time, 0)
        print("light reward:", light_reward)
        light_root.update_statistics(light_reward, selected_light_actions)
        light_root.print()
        current_best = light_root.best_actions()
        print("current best action:", current_best)
        # print("each time:", run_time)
        print("runtime:", total_run_time)
        # add more episode
        ep += 1

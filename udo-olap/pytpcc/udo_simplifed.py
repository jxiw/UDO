import random

import gym
import gym_olapgame

import constants
from mcts import uct_node

def run_simplifed_udo_agent(duration, horizon):
    light_tree_height = 8

    env = gym.make('olapgame-v0')
    env.reset()
    init_state = env.state_decoder(0)
    light_root = uct_node.Uct_Node(0, 0, light_tree_height, init_state, env)

    all_queries = list(constants.QUERIES.keys())
    constants.default_runtime = [2.105151653289795, 0.31378817558288574, 0.8337562084197998, 0.2568848133087158,
                                 0.9468960762023926, 0.3262817859649658, 0.7299606800079346, 0.4448833465576172,
                                 1.339064359664917, 0.7460975646972656, 0.12022900581359863, 0.8601398468017578,
                                 0.9646978378295898, 0.37630248069763184, 0.7101349830627441, 0.6010422706604004,
                                 2.0279109477996826, 3.7307093143463135, 0.460712194442749, 1.31988525390625,
                                 0.8085336685180664, 0.4129042625427246]
    # env.evaluate_light_under_heavy(all_queries, [0] * len(all_queries))

    micro_episode = 100000
    for t2 in range(micro_episode):
        # for the micro episode
        selected_light_actions = light_root.sample(micro_episode)
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
        t2 += 1
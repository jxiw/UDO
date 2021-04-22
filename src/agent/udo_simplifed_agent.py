# -----------------------------------------------------------------------
# Copyright (c) 2021    Cornell Database Group
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
# -----------------------------------------------------------------------

import logging
import time

import gym

from mcts.mcts_node import SpaceType
from mcts.uct_node import uct_node


def run_simplifed_udo_agent(driver, queries, candidate_indices, tuning_config):
    start_tune_time = time.time()
    env = gym.make('udo_optimization-v0', driver=driver, queries=queries, candidate_indices=candidate_indices,
                   config=tuning_config)
    env.reset()
    duration_in_seconds = tuning_config['duration'] * 3600
    init_state = env.state_decoder(0)
    root = uct_node(0, 0, tuning_config['horizon'], init_state, env, space_type=SpaceType.All)

    all_queries = list(queries.values())
    start_time = time.time()
    current_time = time.time()

    ep = 0
    logging.debug(f"start: {time.time()}")
    while (current_time - start_time) < duration_in_seconds:
        # for the micro episode
        selected_light_actions = root.sample(ep)
        logging.debug(f"selected_light_actions: {selected_light_actions}")
        # evaluate the light actions
        env.reset()
        for selected_light_action in selected_light_actions:
            # move to next state
            state = env.step_without_evaluation(selected_light_action)
        # obtain run time info by running queries within timeout
        run_time = env.evaluate(all_queries)
        # the total time of sampled queries
        total_run_time = sum(run_time)
        # the default time of sampled queries
        default_time = sum(env.default_runtime)
        # the relative ration of the improvement, the less of total_run_time, the better
        # light_reward = default_time / total_run_time
        light_reward = max(default_time - total_run_time, 0)
        logging.debug(f"light reward: {light_reward}")
        root.update_statistics_with_mcts_reward(light_reward, selected_light_actions)
        root.print_reward_info()
        current_best = root.best_actions()
        logging.debug(f"current best action: {current_best}")
        logging.debug(f"runtime: {total_run_time}")
        # add more episode
        ep += 1
    final_tune_time = time.time()
    logging.debug(f"end: {final_tune_time}")
    # tuning summary
    best_actions = root.best_actions()
    logging.info(f"Summary: Total Tuning Time {(final_tune_time - start_tune_time) / 3600} hours")
    env.print_action_summary(best_actions)

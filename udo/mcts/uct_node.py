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
import math
import random

from .mcts_node import *


class uct_node(mcts_node):
    def __init__(self, round, tree_level, tree_height, state, env, space_type=SpaceType.All,
                 selection_policy=SelectionPolicy.UCBV, update_policy=UpdatePolicy.RAVE, terminate_action=None,
                 ucb1_er=1.2, ucbv_bound=0.1, ucbv_const=0.1):
        self.create_in = round
        # construct the transaction space, index space and parameter space
        self.env = env
        self.state = state
        if space_type is SpaceType.Light:
            self.actions = env.retrieve_light_actions(state)
        elif space_type is SpaceType.Heavy:
            self.actions = env.retrieve_heavy_actions(state)
        else:
            self.actions = env.retrieve_actions(state)
        self.nr_action = len(self.actions)
        self.tree_level = tree_level
        # for the children node
        self.children = [None] * self.nr_action
        # for the number of tries of children node
        self.nr_tries = [0] * self.nr_action
        self.first_moment = [0] * self.nr_action
        self.second_moment = [0] * self.nr_action
        self.total_visit = 0
        self.priority_actions = self.actions.copy()
        self.tree_height = tree_height
        self.terminate_action = terminate_action
        # update policy
        self.selection_policy = selection_policy
        self.update_policy = update_policy
        self.space_type = space_type
        # tuning parameters for UCB1
        self.explore_rate = ucb1_er
        # tuning parameters for UCBV
        self.bound = ucbv_bound
        self.const = ucbv_const

    def select_action(self):
        """select action according to rl policy"""
        if len(self.priority_actions) > 0:
            selected_action = random.choice(self.priority_actions)
            self.priority_actions.remove(selected_action)
            selected_action_idx = self.actions.index(selected_action)
            return selected_action, selected_action_idx
        else:
            # select actions according to ucb1
            best_action_idx = -1
            best_ucb_score = -1
            for action_idx in range(self.nr_action):
                if self.nr_tries[action_idx] > 0:
                    mean = self.first_moment[action_idx] / self.nr_tries[action_idx]
                    variance = max((self.second_moment[action_idx] / self.nr_tries[action_idx] - (mean * mean)), 0)
                    if self.selection_policy == SelectionPolicy.UCB1:
                        ucb_score = mean + self.explore_rate * math.sqrt(
                            math.log(self.total_visit) / self.nr_tries[action_idx])
                    elif self.selection_policy == SelectionPolicy.UCBV:
                        ucb_score = mean + math.sqrt(
                            self.const * variance * math.log(self.total_visit) / self.nr_tries[action_idx]) + (
                                            3 * self.bound * math.log(self.total_visit) / self.nr_tries[action_idx])
                    else:
                        raise ValueError('Selection policy is unavailable.')
                    if ucb_score > best_ucb_score:
                        best_ucb_score = ucb_score
                        best_action_idx = action_idx
            return self.actions[best_action_idx], best_action_idx

    def playout(self, current_level_action):
        """randomly select other actions until reaching to terminate state"""
        current_level_state = self.state
        selected_action_path = []
        for current_level in range(self.tree_level + 1, self.tree_height):
            current_level_state, current_state_id = self.env.transition(current_level_state,
                                                                        current_level_action)
            if self.space_type is SpaceType.Light:
                current_candidate_actions = self.env.retrieve_light_actions(current_level_state)
            elif self.space_type is SpaceType.Heavy:
                current_candidate_actions = self.env.retrieve_heavy_actions(current_level_state)
            elif self.space_type == SpaceType.All:
                current_candidate_actions = self.env.retrieve_actions(current_level_state)
            # choose one random action from the action space
            if self.terminate_action is not None:
                current_candidate_actions.append(self.terminate_action)
            current_level_action = random.choice(current_candidate_actions)
            selected_action_path.append(current_level_action)
        return selected_action_path

    def sample(self, round):
        """sample actions from search tree"""
        if self.nr_action == 0:
            return []
        else:
            # inner node
            selected_action, selected_action_idx = self.select_action()
            if self.terminate_action is not None and selected_action == self.terminate_action:
                # for the terminate action, stop expansion
                return [selected_action]
            can_expand = (self.create_in != round) and (self.tree_level < self.tree_height)
            if can_expand and not self.children[selected_action_idx]:
                state, state_idx = self.env.transition(self.state, selected_action)
                self.children[selected_action_idx] = uct_node(round=0, tree_level=self.tree_level + 1,
                                                              tree_height=self.tree_height, state=state, env=self.env,
                                                              space_type=self.space_type,
                                                              selection_policy=self.selection_policy,
                                                              update_policy=self.update_policy,
                                                              terminate_action=self.terminate_action,
                                                              ucb1_er=self.explore_rate,
                                                              ucbv_bound=self.bound,
                                                              ucbv_const=self.const)
            child = self.children[selected_action_idx]
            # recursively sample the tree
            if child:
                return [selected_action] + child.sample(round)
            else:
                return [selected_action] + self.playout(selected_action)

    def update_statistics_with_mcts_reward(self, reward, selected_actions):
        """update mcts statistics using reward information"""
        rewards = {selected_action: reward for selected_action in selected_actions}
        self.update_statistics_with_delta_reward(rewards, selected_actions)

    def update_statistics_with_delta_reward(self, rewards, selected_actions):
        """update mcts statistics using intermediate reward information"""
        if self.update_policy is UpdatePolicy.RAVE:
            for action_idx in range(self.nr_action):
                current_action = self.actions[action_idx]
                # we use the RAVE update policy
                if current_action in selected_actions:
                    reward = rewards[current_action]
                    self.total_visit += 1
                    self.nr_tries[action_idx] += 1
                    self.first_moment[action_idx] += reward
                    self.second_moment[action_idx] += reward * reward
                    if current_action in self.priority_actions:
                        self.priority_actions.remove(current_action)
                    # update the reward for subtree
                    if self.children[action_idx] is not None:
                        next_selected_actions = list(filter(lambda x: x != current_action, selected_actions))
                        self.children[action_idx].update_statistics_with_delta_reward(rewards, next_selected_actions)
        else:
            current_action = selected_actions[self.tree_level]
            for action_idx in range(self.nr_action):
                if self.actions[action_idx] == current_action:
                    reward = rewards[current_action]
                    self.total_visit += 1
                    self.nr_tries[action_idx] += 1
                    self.first_moment[action_idx] += reward
                    self.second_moment[action_idx] += reward * reward
                    # self.mean_reward[action_idx] = self.first_moment[action_idx] / self.nr_tries[action_idx]
                    if self.children[action_idx] is not None:
                        self.children[action_idx].update_statistics_with_delta_reward(rewards, selected_actions)

    def update_batch(self, update_infos):
        for (rewards, select_actions) in update_infos:
            rewards = {select_actions[i]: rewards[i] for i in range(len(rewards))}
            self.update_statistics_with_delta_reward(rewards, select_actions)

    def print_reward_info(self):
        """print the reward information"""
        mean_reward = [0] * self.nr_action
        for i in range(self.nr_action):
            if self.nr_tries[i] > 0:
                mean_reward[i] = self.first_moment[i] / self.nr_tries[i]
            else:
                mean_reward[i] = 0
        logging.debug(f"first layer avg reward {mean_reward}")
        return mean_reward

    def best_actions(self):
        """best actions from the search tree"""
        best_mean = 0
        best_action_idx = -1
        for action_idx in range(self.nr_action):
            if self.nr_tries[action_idx] > 0:
                mean = self.first_moment[action_idx] / self.nr_tries[action_idx]
                if mean > best_mean:
                    best_mean = mean
                    best_action_idx = action_idx
        if self.children[best_action_idx] is not None:
            return [self.actions[best_action_idx]] + self.children[best_action_idx].best_actions()
        else:
            return [self.actions[best_action_idx]]

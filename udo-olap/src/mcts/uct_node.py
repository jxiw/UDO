import math
import random

from .mcts_node import *


class uct_node(mcts_node):
    def __init__(self, round, tree_level, tree_height, state, env, space_type=SpaceType.All,
                 selection_policy=SelectionPolicy.UCBV, update_policy=UpdatePolicy.RAVE):
        self.create_in = round
        # construct the transaction space, index space and parameter space
        self.env = env
        self.state = state
        self.actions = env.choose_all_light_actions(state)
        self.nr_action = len(self.actions)
        self.tree_level = tree_level
        # for the children node
        self.children = [None] * self.nr_action
        # for the number of tries of children node
        self.nr_tries = [0] * self.nr_action
        self.first_moment = [0] * self.nr_action
        self.second_moment = [0] * self.nr_action
        # self.mean_reward = [0] * self.nr_action
        self.total_visit = 0
        self.priority_actions = self.actions.copy()
        self.tree_height = tree_height
        # update policy
        self.selection_policy = selection_policy
        self.update_policy = update_policy
        self.space_type = space_type
        # tuning parameters for UCB1
        self.explore_rate = 1.2
        # tuning parameters for UCBV
        self.bound = 1
        self.const = 1

    # uct selection
    def select_action(self):
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
        # obtain the current actions
        current_level_state = self.state
        selected_action_path = []
        for current_level in range(self.tree_level + 1, self.tree_height):
            current_level_state, current_state_id = self.env.transition(current_level_state,
                                                                        current_level_action)
            # current_candidate_actions = self.env.choose_all_actions(current_level_state)
            if self.space_type == SpaceType.Light:
                current_candidate_actions = self.env.choose_all_light_actions(current_level_state)
            elif self.space_type == SpaceType.Heavy:
                current_candidate_actions = self.env.choose_all_heavy_actions(current_level_state)
            elif self.space_type == SpaceType.All:
                current_candidate_actions = self.env.choose_all_actions(current_level_state)
            # choose one random action from the action space
            current_level_action = random.choice(current_candidate_actions)
            selected_action_path.append(current_level_action)
        return selected_action_path

    def sample(self, round):
        if self.nr_action == 0:
            # leaf node
            return []
        else:
            # inner node
            selected_action, selected_action_idx = self.select_action()
            can_expand = (self.create_in != round) and (self.tree_level < self.tree_height)
            # print(selected_action_idx)
            if can_expand and not self.children[selected_action_idx]:
                # expend
                state, state_idx = self.env.transition(self.state, selected_action)
                self.children[selected_action_idx] = uct_node(round, self.tree_level + 1, self.tree_height, state,
                                                              self.env)
            child = self.children[selected_action_idx]
            # recursively sample the tree
            if child:
                return [selected_action] + child.sample(round)
            else:
                return [selected_action] + self.playout(selected_action)

    def update_statistics(self, reward, selected_actions):
        for action_idx in range(self.nr_action):
            current_action = self.actions[action_idx]
            # we use the RAVE
            if current_action in selected_actions:
                self.total_visit += 1
                self.nr_tries[action_idx] += 1
                self.first_moment[action_idx] += reward
                self.second_moment[action_idx] += reward * reward
                # update the reward for subtree
                if self.children[action_idx] is not None:
                    next_selected_actions = list(filter(lambda x: x != current_action, selected_actions))
                    self.children[action_idx].update_statistics(reward, next_selected_actions)

        # selected_action_current_node = selected_actions[self.tree_level]
        # for action_idx in range(self.nr_action):
        #     if self.actions[action_idx] == selected_action_current_node:
        #         self.total_visit += 1
        #         self.nr_tries[action_idx] += 1
        #         self.first_moment[action_idx] += reward
        #         self.second_moment[action_idx] += reward * reward
        #         # self.mean_reward[action_idx] = self.first_moment[action_idx] / self.nr_tries[action_idx]
        #         if self.children[action_idx] is not None:
        #             self.children[action_idx].update_statistics(reward, selected_actions)

    def print(self):
        mean_reward = [0] * self.nr_action
        for i in range(self.nr_action):
            if self.nr_tries[i] > 0:
                mean_reward[i] = self.first_moment[i] / self.nr_tries[i]
            else:
                mean_reward[i] = 0
        # print("first layer avg reward:", mean_reward)

    def best_actions(self):
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

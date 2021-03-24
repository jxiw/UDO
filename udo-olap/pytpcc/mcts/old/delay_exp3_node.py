import gym
import gym_olapgame
import random
import math
import numpy as np
import itertools

class Delay_Exp3_Node:
    def __init__(self, round, tree_level, tree_height, state, env):
        self.create_in = round
        # construct the transaction space, index space and parameter space
        self.env = env
        self.state = state
        self.actions = env.choose_all_heavy_actions(state)
        self.nr_action = len(self.actions)
        self.tree_level = tree_level
        # for the children node
        self.children = [None] * self.nr_action
        self.probability = [1.0 / self.nr_action] * self.nr_action
        # for the number of tries of children node
        self.nr_tries = [0] * self.nr_action
        self.accumulated_reward = [0] * self.nr_action
        # self.untried_actions = self.actions.copy()
        self.priority_actions = self.actions.copy()
        self.tree_height = tree_height
        self.learning_rate = 0.05
        # self.eta1 = 1E10
        # self.eta2 = 1E-10
        self.eta1 = 20
        self.eta2 = 0.01

    def select_action(self):
        if len(self.priority_actions) > 0:
            selected_action = random.choice(self.priority_actions)
            self.priority_actions.remove(selected_action)
            selected_action_idx = self.actions.index(selected_action)
            return selected_action, selected_action_idx
        else:
            # we apply the exp3 rule to draw action according to some probability
            # sample action according to its probability
            rand_num = random.random()
            selected_action_idx = 0
            current_accumulate = 0.0
            for action_idx in range(self.nr_action):
                if (current_accumulate + self.probability[action_idx] > rand_num):
                    selected_action_idx = action_idx
                    break
                current_accumulate += self.probability[action_idx]
            selected_action = self.actions[selected_action_idx]
            self.nr_tries[selected_action_idx] += 1
            return selected_action, selected_action_idx

    def playout(self, current_level_action):
        # obtain the current actions
        current_level_state = self.state
        selected_action_path = []
        for current_level in range(self.tree_level + 1, self.tree_height + 1):
            current_level_state, current_state_id = self.env.transition(current_level_state, current_level_action)
            # current_candidate_actions = self.env.choose_all_actions(current_level_state)
            current_candidate_actions = self.env.choose_all_heavy_actions(current_level_state)
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
                self.children[selected_action_idx] = Delay_Exp3_Node(round, self.tree_level + 1, self.tree_height, state, self.env)
            child = self.children[selected_action_idx]
            # recursively sample the tree
            if child:
                return [selected_action] + child.sample(round)
            else:
                return [selected_action] + self.playout(selected_action)

    def update_batch(self, update_info):
        current_prob = self.probability.copy()
        child_info = dict()
        # generate more update information via rave
        # rave_update_info=[]
        # for (loss_infos, selected_actions) in update_info:
        #     rave_updates = list(itertools.permutations(selected_actions))
        #     for rave_update in rave_updates:
        #         rave_update_info.append((loss_infos, rave_update))
        for (reward_infos, selected_actions) in update_info:
            # each simulation
            for current_action in selected_actions:
                reward = reward_infos[current_action]
                # correct indices
                current_action_idx = self.actions.index(current_action)
                normalized_reward = reward / self.probability[current_action_idx]
                current_action_weight = current_prob.copy()
                current_action_weight[current_action_idx] = current_prob[current_action_idx] * math.exp(self.learning_rate * min(self.eta1, normalized_reward))
                # for action in range(self.nr_action):
                #     if action != current_action_idx:
                #         current_action_weight[action] = current_prob[action]
                sum_current_action_weight = sum(current_action_weight)
                normalized_current_action_weight = [max(weight / sum_current_action_weight, self.eta2 / self.nr_action) for
                                                    weight in current_action_weight]
                sum_normalized_current_action_weight = sum(normalized_current_action_weight)
                current_prob = [weight / sum_normalized_current_action_weight for weight in
                                normalized_current_action_weight]
                if current_action_idx in child_info:
                    child_info[current_action_idx].append((reward_infos, set(filter(lambda a: a!= current_action, selected_actions))))
                else:
                    child_info[current_action_idx] = []
                    child_info[current_action_idx].append((reward_infos, set(filter(lambda a: a!= current_action, selected_actions))))
        self.probability = current_prob.copy()
        for action_idx, info in child_info.items():
            if self.children[action_idx] is not None:
                self.children[action_idx].update_batch(info)

    def opt_policy(self):
        best_action_idx = np.argmax(self.probability)
        if self.children[best_action_idx] is not None:
            return [self.actions[best_action_idx]] + self.children[best_action_idx].best_actions()
        else:
            return [self.actions[best_action_idx]]

    def print(self):
        print("first layer action:", self.actions)
        print("first layer probability:", self.probability)


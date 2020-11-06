import gym
import gym_opgame
import random
import math

class Delay_Node:
    def __init__(self, round, tree_height, state, env):
        self.create_in = round
        # construct the transaction space, index space and parameter space
        self.env = env
        self.state = state
        self.actions = env.choose_all_actions(state)
        self.nr_action = len(self.actions)
        self.tree_level = 0
        # for the children node
        self.children = [None] * self.nr_action
        self.probability = [1.0 / self.nr_action] * self.nr_action
        # for the number of tries of children node
        self.nr_tries = [0] * self.nr_action
        self.accumulated_reward = [0] * self.nr_action
        self.untried_actions = self.actions.copy()
        self.priority_actions = self.actions.copy()
        self.tree_height = tree_height
        self.learning_rate = 0.01
        self.eta1 = 0.1
        self.eta2 = 0.1

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
            return selected_action, selected_action_idx

    def playout(self, current_level_action):
        # obtain the current actions
        current_level_state = self.state
        selected_action_path = []
        for current_level in range(self.tree_level + 1, self.tree_height):
            current_level_state, current_state_id = self.env.obtain_next_state(current_level_state, current_level_action)
            current_candidate_actions = self.env.choose_all_actions(current_level_state)
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
            can_expand = (self.create_in != round)
            print(selected_action_idx)
            if can_expand and not self.children[selected_action_idx]:
                # expend
                state, state_idx = self.env.obtain_next_state(self.state, selected_action)
                self.children[selected_action_idx] = Delay_Node(round, self.tree_height, state, self.env)
            child = self.children[selected_action_idx]
            # recursively sample the tree
            if child:
                return [selected_action] + child.sample(round)
            else:
                return [selected_action] + self.playout(selected_action)

    def update_probability(self, update_info):
        current_prob = self.probability.copy()
        for (loss, selected_actions) in update_info:
            # update the probability of the node
            current_action = selected_actions[self.tree_level]
            current_action_idx = self.actions.index(current_action)
            normalized_loss = loss / self.probability[current_action_idx]
            current_action_weight = [0] * self.nr_action
            current_action_weight[current_action_idx] = current_prob[current_action_idx] * math.exp(- self.learning_rate * min(self.eta1, normalized_loss))
            for action in range(self.nr_action):
                if action != current_action_idx:
                    current_action_weight[action] = current_prob[action]
            sum_current_action_weight = sum(current_action_weight)
            normalized_current_action_weight = [max(weight / sum_current_action_weight, self.eta2 / self.nr_action) for
                                                weight in current_action_weight]
            sum_normalized_current_action_weight = sum(normalized_current_action_weight)
            current_prob = [weight / sum_normalized_current_action_weight for weight in
                            normalized_current_action_weight]
        self.probability = current_prob.copy()

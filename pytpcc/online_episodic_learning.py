import gym
import gym_opgame
import numpy as np
import random
import math
import collections

env = gym.make('opgame-v0')

n_state = env.nS
n_action = env.nA

T = 1000
D = 30
pi = []
# state, timestamp, action
weight = dict()
state_x_id = 0
eta = 0.1
gamma = 0.2
N = 5
history_state_x = []
history_action_a = []
r = dict()

# start each episode
for t1 in range(0, T):
    # within one episode
    # choose a policy \pi
    pi_t = []
    # generate the traverses path
    for t2 in range(0, D):
        # generate the path mu
        # given the state identifier to obtain the state
        state_x = env.map_number_to_state(state_x_id)
        # obtain all actions at the given state
        actions = env.choose_all_actions(state_x)
        # sample action according to its probability
        rand_num = random.random()
        select_action = 0
        current_accumulate = 0.0
        for action_idx in range(len(actions)):
            if (current_accumulate + pi_t[state_x_id][action_idx] > rand_num):
                select_action = action_idx
                break
            current_accumulate += pi_t[state_x_id][action_idx]
        # select actions
        state_x_plus_1, reward = env.one_step(state_x, select_action)
        # record trajectory from init timestamp
        history_state_x.append(state_x_id)
        history_action_a.append(select_action)
        state_x_id = env.map_state_to_num(state_x_plus_1)
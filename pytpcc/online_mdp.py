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

for t in range(0, T):
    # create policy pi_t, which is the policy for timestamp t
    pi_t = dict()
    # init the policy for the current state
    pi_t[state_x_id] = []
    # given the state identifier to obtain the state
    state_x = env.map_number_to_state(state_x_id)
    # obtain all actions at the given state
    actions = env.choose_all_actions(state_x)
    if t == 0:
        # initial state
        # obtain number of validate actions at the current state
        nr_action_in_current_state = len(actions)
        # init the weight matrix
        weight[state_x_id] = dict()
        # for the timestamp from 1 to 2 N
        for i in range(1, 2 * N + 1):
            # all the w[s][i][a] = 1
            weight[state_x_id][i] = np.ones(nr_action_in_current_state)
            # we calculate the weight information and the policy probability
            total_weight_in_state_x = sum(action_weight for action_weight in weight[state_x_id][t])
            for action_idx in range(len(actions)):
                pi_t[state_x_id][action_idx] = (1 - gamma) * weight[state_x][t][action_idx] / total_weight_in_state_x + gamma / total_weight_in_state_x
    # sample action according to its probability
    rand_num = random.random()
    select_action = 0
    current_accumulate = 0.0
    for action_idx in range(len(actions)):
        if (current_accumulate + pi_t[state_x_id][action_idx] > rand_num):
            select_action = action_idx
            break
        current_accumulate += pi_t[state_x_id][action_idx]
    # after choosing a action, go to the next state s_{x + 1} from s_x
    state_x_plus_1, reward = env.one_step(state_x, select_action)
    # record trajectory from init timestamp
    history_state_x.append(state_x_id)
    history_action_a.append(select_action)
    pi.append(pi_t)
    if t >= N + 1:
        # compute the mu_t^N
        # calculate the frequency of each state among the trajectory
        # get the last N element of the trajectory
        last_N_states = history_state_x[-N:]
        state_frequency = collections.Counter(last_N_states)
        mu_t = dict()
        # construct mu_t
        for state, frequency in state_frequency:
            # we have total N states among this trajectory, so the prob of mu_t is frequency / N
            mu_t[state] = frequency / N
        # compute r and q
        # r_t_up for current state
        r_t_up = reward / (pi[state_x_id][select_action] * mu_t[state_x_id])
        # calculate the rho_t, only the current_state, current_action entity is nnz, others are all 0
        rho_t_up = mu_t[state_x_id] * pi_t[state_x_id][select_action] * r_t_up
        # q_t_up = r_t_up - rho_t_up
        # v_t = dict()
        # q_t = dict()
        # for state in range(n_state):
        #     for action in range(n_action):
        #         v_t = v_t_x + pi_t[state_x_id][action]
        q_t_up = dict()
        q_t_up[state_x] = dict()
        q_t_up[state_x][select_action] = reward - rho_t_up
        # update matrix w_(t+n)
        for state in range(n_state):
            for action in range(n_action):
                weight[state][t+N][action] = weight[state][t+N-1][action] * math.exp(eta * q_t_up[state][action])


# # if
# if not pi_t[state_x_id]:
#     pi_t[state_x_id] = []


#     # the total weight is the number of actions
#     total_weight_in_state_x = len(actions)
#     # for each action, we calculate its probability and construct the policy
#     for action_idx in range(len(actions)):
#         # for policy pi at timestamp t, calculate the probability of taking that action
#         pi_t[state_x_id][action_idx] = (1 - gamma) / total_weight_in_state_x + gamma / total_weight_in_state_x
# else:
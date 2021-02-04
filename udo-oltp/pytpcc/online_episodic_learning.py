import gym
import gym_opgame
import numpy as np
import random
import math
import collections
from scipy.optimize import minimize

env = gym.make('opgame-v0')
env.reset()

# n_state = env.nS
# n_action = env.nA

T = 1000
L = 2
pi = []
# state, timestamp, action
weight = dict()
# initial state
state_x_id = 0
eta = 0.1
gamma = 0.2
N = 5
history_state_x = []
history_action_a = []
r = dict()
q = collections.defaultdict(dict)

# given the state identifier to obtain the state
state_x = env.map_number_to_state(state_x_id)

# construct matrix p and level information
p=collections.defaultdict(dict)
state_level_id = dict()
state_level_id[0] = [0]
state_level = dict()
state_level[0] = [state_x]
discount = dict()
discount[0] = [1]
state_map={0:0}
n_state = 1

for l in range(0, L):
    # next level state information
    state_level[l + 1] = []
    state_level_id[l + 1] = []
    discount[l + 1] = []
    for current_state, current_state_id, current_discount in zip(state_level[l], state_level_id[l], discount[l]):
        actions = env.choose_all_actions(current_state)
        next_discount = current_discount / len(actions)
        for action in actions:
            # print(action)
            next_state, next_state_id = env.obtain_next_state(current_state, action)
            # print(next_state_id)
            # print(next_state)
            state_level[l + 1].append(next_state)
            state_level_id[l + 1].append(next_state_id)
            p[current_state_id][action] = next_state_id
            # next probability
            discount[l + 1].append(next_discount)
            q[current_state_id][action] = next_discount
            state_map[next_state_id] = n_state
            n_state += 1
    # n_state += len(state_level[l])

# for l in range(2, 3):
#     print("level%d"%l)
#     for state in state_level[l]:
#         print(str(state))
# print(env.nS)
# print("finish the construction")

# init the start value
print("total number of state")
print(n_state)

# n_state_1 = 0
# for l in range(0, L + 1):
#     n_state_1 += len(state_level_id[l])
# print(n_state_1)

# start each episode
for t1 in range(0, T):
    # within one episode
    # choose a policy \pi
    r_t = collections.defaultdict(dict)
    state_trajectory = []
    action_trajectory = []
    # generate the traverses path
    current_state = state_x
    current_state_id = state_x_id
    for t2 in range(0, L):
        # generate the path mu according to the pi_t distribution
        # obtain all actions at the given state
        actions = env.choose_all_actions(current_state)
        n_action = len(actions)
        # not visit that state, randomly choose next state
        # rescale q_t
        total = sum(q[current_state_id].values())
        pi_current_state = {k: (v / total) for k, v in q[current_state_id].items()}
        # sample action according to its probability
        rand_num = random.random()
        select_action = 0
        current_accumulate = 0.0
        for action in actions:
            if (current_accumulate + pi_current_state[action] > rand_num):
                select_action = action
                break
            current_accumulate += pi_current_state[action]
        # select actions
        next_state, reward, terminate, info = env.step(select_action)
        # print("next state")
        # print(next_state)
        next_state_id = env.map_state_to_num(next_state)
        # record trajectory from init timestamp
        state_trajectory.append(state_x_id)
        action_trajectory.append(select_action)
        r_t[state_x_id][select_action] = 1 / reward
        # move the next state
        current_state = next_state
        current_state_id = next_state_id
    # obtain the trajectory of state, action pairs.
    # fist step
    # for state, action, reward in zip(state_trajectory, action_trajectory, r_t):
    #     p[state][action] = p[state][action] * math.exp(eta * reward)
    # projection step
    # solve the optimization problem.

    def objective(v):
        prob = 0
        for l in range(0, L):
            z_l = 0
            for state_id in state_level_id[l]:
                for action_id, value in p[state_id].items():
                    r = 0
                    if state_id in r_t and action_id in r_t[state_id]:
                        r = r_t[state_id][action_id]
                    next_state_id = p[state_id][action_id]
                    if next_state_id not in v:
                        v[state_map[next_state_id]] = 0
                    if state_id not in v:
                        v[state_map[state_id]] = 0
                    delta_t = r + v[state_map[next_state_id]] - v[state_map[state_id]]
                    z_l += p[state_id][action_id] * math.exp(delta_t)
            prob += math.log(z_l)
        return prob

    # v = collections.defaultdict(dict)
    v = [0] * n_state
    v_star = minimize(objective, v,  method='nelder-mead', options={'xtol': 1e-4, 'disp': True})
    print("res")
    for key, value in v_star:
        if value > 0:
            print(key)
    z = collections.defaultdict(dict)
    for l in range(0, L):
        z_state_sum = 0
        for state_id in state_level_id[l]:
            for action_id, value in p[state_id]:
                r = 0
                if state_id in r_t and action_id in r_t[state_id]:
                    r = r_t[state_id][action_id]
                next_state_id = p[state_id][action_id]
                delta_t = r + v_star[state_map[next_state_id]] - v_star[state_map[state_id]]
                z_value = p[state_id][action_id] * math.exp(delta_t)
                z_state_sum += z_value
                z[state_id][action_id] = z_value
        for state_id in state_level_id[l]:
            for action_id, value in p[state_id].items():
                p[state_id][action_id] = z[state_id][action_id] / z_state_sum

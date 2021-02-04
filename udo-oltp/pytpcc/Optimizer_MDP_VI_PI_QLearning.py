#!/usr/bin/env python
# coding: utf-8

# # MDP Algorithms with OpenAI Gym

# ## 1. Setup the 'Python'ic stage

# In[1]:


import numpy as np
import gym
import gym_opgame
import time


# ## 2. Setup the gym for playing with your policy

# Choos an OpenAI-gym enviorment $\mathcal{E}$ and play the environment according to the given policy $\pi$.

# In[3]:

def play_episodes(env, n_episodes, policy, random = False):
    """
    This fucntion plays the given number of episodes given by following a policy or sample randomly from action_space.
    
    Parameters:
        enviorment: OpenAI-gym object
        n_episodes: number of episodes to run
        policy: Policy to follow while playing an episode
        random: Flag for taking random actions. if True no policy would be followed and action will be taken randomly
        
    Return:
        wins: Total number of wins playing n_episodes
        total_reward: Total reward of n_episodes
        avg_reward: Average reward of n_episodes
    
    """
    # intialize wins and total reward
    total_reward = 0
    
    # loop over number of episodes to play
    for episode in range(n_episodes):
        
        # flag to check if the game is finished
        terminated = False
        
        # reset the enviorment every time when playing a new episode
        state = env.reset()
        
        while not terminated:
            
            # check if the random flag is not true then follow the given policy other wise take random action
            if random:
                action = env.cho
            else:
                action = policy[state]

            # take the next step
            next_state, reward,  terminated, info = env.step(action)
            
            env.render()
            
            # accumalate total reward
            total_reward += reward
            
            # change the state
            state = next_state

                
    # calculate average reward
    average_reward = total_reward / n_episodes
    
    return total_reward, average_reward
            


# ## 3. Implement Value Iteration (VI)

# In[4]:


def one_step_lookahead(env, state, V , discount_factor = 0.99):
    """
    Helper function to  calculate state-value function
    
    Arguments:
        env: openAI GYM Enviorment object
        state: state to consider
        V: Estimated Value for each state. Vector of length nS
        discount_factor: MDP discount factor
        
    Return:
        action_values: Expected value of each action in a state. Vector of length nA
    """
    
    # initialize vector of action values
    actions = env.choose_all_actions(state)
    # print actions
    action_num = len(actions)
    action_values = np.zeros(action_num)
    # print state
    # loop over the actions we can take in an environment
    for action_idx in range(action_num):
        # loop over the P_sa distribution.
        action = actions[action_idx]
        next_state, reward, info1, info2 = env.one_step(state, action)
        next_state_idx = env.map_state_to_num(next_state)
        # if we are in state s and take action a. then sum over all the possible states we can land into.
        # print action_idx
        print next_state
        print next_state_idx
        action_values[action_idx] += reward + (discount_factor * V[next_state_idx])

    return action_values

# In[5]:


def update_policy(env, policy, V, discount_factor):
    
    """
    Helper function to update a given policy based on given value function.
    
    Arguments:
        env: openAI GYM Enviorment object.
        policy: policy to update.
        V: Estimated Value for each state. Vector of length nS.
        discount_factor: MDP discount factor.
    Return:
        policy: Updated policy based on the given state-Value function 'V'.
    """
    
    for state_num in range(env.nS):
        # for a given state compute state-action value.
        state = env.map_number_to_state(state_num)
        action_values = one_step_lookahead(env, state, V, discount_factor)
        # choose the action which maximizez the state-action value.
        policy[state] =  np.argmax(action_values)
        
    return policy
    


# In[6]:


def value_iteration(env, discount_factor = 0.999, max_iteration = 100):
    """
    Algorithm to solve MDP.
    
    Arguments:
        env: openAI GYM Enviorment object.
        discount_factor: MDP discount factor.
        max_iteration: Maximum No.  of iterations to run.
        
    Return:
        V: Optimal state-Value function. Vector of lenth nS.
        optimal_policy: Optimal policy. Vector of length nS.
    
    """
    # intialize value function
    V = np.zeros(env.nS)
    
    # iterate over max_iterations
    for i in range(max_iteration):

        print "iteration:"
        print i
        
        #  keep track of change with previous value function
        prev_v = np.copy(V) 
    
        # loop over all states
        for state_num in range(env.nS):
            
            # Asynchronously update the state-action value
            # action_values = one_step_lookahead(env, state, V, discount_factor)
            
            # Synchronously update the state-action value
            state = env.map_number_to_state(state_num)
            action_values = one_step_lookahead(env, state, prev_v, discount_factor)
            
            # select best action to perform based on highest state-action value
            best_action_value = np.max(action_values)
            
            # update the current state-value fucntion
            V[state_num] =  best_action_value
            
        # if policy not changed over 10 iterations it converged.
        if i % 10 == 0:
            # if values of 'V' not changing after one iteration
            if (np.all(np.isclose(V, prev_v))):
                print('Value converged at iteration %d' %(i+1))
                break

    # intialize optimal policy
    optimal_policy = np.zeros(env.nS, dtype = 'int8')
    
    # update the optimal polciy according to optimal value function 'V'
    optimal_policy = update_policy(env, optimal_policy, V, discount_factor)
    
    return V, optimal_policy


# ## Run VI Run

# In[7]:


env = gym.make('opgame-v0')
tic = time.time()
opt_V, opt_Policy = value_iteration(env, max_iteration = 100)
toc = time.time()
elapsed_time = (toc - tic) * 1000
print ("Time to converge: {elapsed_time: 0.3} ms")
print('Optimal Value function: ')
print(opt_V.reshape((4, 4)))
print('Final Policy: ')
print(opt_Policy)


# ## Let's Play Now

# In[8]:


n_episode = 10
total_reward, avg_reward = play_episodes(env, n_episode, opt_Policy, random = False)


# In[9]:

print("Average rewards with value iteration: {avg_reward}")


# # ## 4. Implement Policy Iteration (PI)
#
# # In[10]:
#
#
# def policy_eval(env, policy, V, discount_factor):
#     """
#     Helper function to evaluate a policy.
#
#     Arguments:
#         env: openAI GYM Enviorment object.
#         policy: policy to evaluate.
#         V: Estimated Value for each state. Vector of length nS.
#         discount_factor: MDP discount factor.
#     Return:
#         policy_value: Estimated value of each state following a given policy and state-value 'V'.
#
#     """
#     policy_value = np.zeros(env.nS)
#     for state, action in enumerate(policy):
#         for probablity, next_state, reward, info in env.P[state][action]:
#             policy_value[state] += probablity * (reward + (discount_factor * V[next_state]))
#
#     return policy_value
#
#
# # In[11]:
#
#
# def policy_iteration(env, discount_factor = 0.999, max_iteration = 1000):
#     """
#     Algorithm to solve MPD.
#
#     Arguments:
#         env: openAI GYM Enviorment object.
#         discount_factor: MDP discount factor.
#         max_iteration: Maximum No.  of iterations to run.
#
#     Return:
#         V: Optimal state-Value function. Vector of lenth nS.
#         new_policy: Optimal policy. Vector of length nS.
#
#     """
#     # intialize the state-Value function
#     V = np.zeros(env.nS)
#
#     # intialize a random policy
#     policy = np.random.randint(0, 4, env.nS)
#     policy_prev = np.copy(policy)
#
#     for i in range(max_iteration):
#
#         # evaluate given policy
#         V = policy_eval(env, policy, V, discount_factor)
#
#         # improve policy
#         policy = update_policy(env, policy, V, discount_factor)
#
#         # if policy not changed over 10 iterations it converged.
#         if i % 10 == 0:
#             if (np.all(np.equal(policy, policy_prev))):
#                 print('policy converged at iteration %d' %(i+1))
#                 break
#             policy_prev = np.copy(policy)
#
#     return V, policy
#
#
# # ## Run PI Runn..
#
# # In[12]:
#
#
# env = gym.make('opgame-v0')
# tic = time.time()
# opt_V2, opt_policy2 = policy_iteration(env, discount_factor = 0.999, max_iteration = 1000)
# toc = time.time()
# elapsed_time = (toc - tic) * 1000
# print ("Time to converge: {elapsed_time: 0.3} ms")
# print('Optimal Value function: ')
# print(opt_V2.reshape((4, 4)))
# print('Final Policy: ')
# print(opt_policy2.reshape(4,4))
#
#
# # ## Let's Play Now
#
# # In[13]:
#
#
# n_episode = 10
# total_reward, avg_reward = play_episodes(env, n_episode, opt_policy2, random = False)
#
#
# # In[14]:
#
#
# print("Average rewards with Policy iteration: {avg_reward}")


# ## 5. Implementation of Q-learning

# In[15]:


def QLearning(env, gamma, epsilon, decay, max_iteration):
    
    # intialize a random policy
    policy = np.random.randint(0, 4, env.nS)
    policy_prev = np.copy(policy)
    
    Q = np.random.rand(env.nS, env.nA).tolist()
    terminated = False
    state = env.reset()
    state_idx = env.map_state_to_num(state)
    steps = 0

    for steps in range(max_iteration):
        os.system('clear')
        print("Steps: %d" %(steps))
        #env.render()

        # count steps to finish game
        steps += 1

        # state_idx = env.choose_all_actions(state)

        # act randomly sometimes to allow exploration
        if np.random.uniform() < epsilon:
            action = env.choose_all_actions(state)
            action_idx = env.map_state_to_num(state)
            # action = np.random.choice(env.nA)
        # if not select max action in Qtable (act greedy)
        else:
            action_idx = Q[state].index(max(Q[state]))

        # take the next step
        next_state, reward,  terminated, info = env.step(action)
            
        #environment.render()

        # update qtable value with Bellman equation
        Q[state][action_idx] = reward + gamma * max(Q[next_state])

        # update state
        state = next_state
        # improve policy
        policy = update_policy(env, policy, np.apply_along_axis(np.sum, 1, np.reshape(Q, (16, 4))), gamma)
        
        # if policy not changed over 10 iterations it converged.
        if steps % 10 == 0:
           if (np.all(np.equal(policy, policy_prev))):
               print('\nPolicy converged at iteration %d' %(steps+1))
               break
           policy_prev = np.copy(policy)
            
    # The more we learn, the less we take random actions
    epsilon -= decay*epsilon
    
    return policy, Q


# In[16]:


import os

envq = gym.make('opgame-v0')
tic = time.time()

# hyperparameters
opt_policy_q, opt_Q= QLearning(envq, gamma = 0.999, epsilon = 0.1, decay = 0.0, max_iteration=1000)

toc = time.time()
elapsed_time = (toc - tic) * 1000
print ("Time to converge: {elapsed_time: 0.3} ms")
print('Optimal Q-value function: ')
print(np.reshape(opt_Q, (4, 4, 4)))
print('Optimal Value function: ')
print(np.apply_along_axis(np.sum, 1, np.reshape(opt_Q, (16, 4))))
print('Final Policy: ')
print(opt_policy_q)


# ## Run Q-learning run...

# In[17]:


n_episode = 10
total_reward, avg_reward = play_episodes(envq, n_episode, opt_policy_q, random = False)


# In[18]:


print("Average rewards with Policy iteration: {avg_reward}")


# In[ ]:





# import gym
# import gym_opgame
# import numpy as np
# import random
# import math
# import collections
# from scipy.optimize import minimize
#
# env = gym.make('opgame-v0')
# env.reset()
#
# # n_state = env.nS
# # n_action = env.nA
#
# def exp3(node):
#     #
#
# class Node:
#     def __init__(self, round, action):
#         self.create = round
#         self.action = action
#         self.children = []
#         self.probability = []
#         self.explored_children = 0
#         self.visits = 0
#         self.value = 0
#
# n_palyouts = 100
#
# root = Node(None, None)
#
# for i in range(0, n_palyouts):
#     # explore tree from root to bottom
#     current_state = env.reset()
#     node = root
#     # selection
#     while node.children:
#         actions = []
#         terminal = False
#         # selection
#         # if there is an arm which have not tried yet
#         while node.children:
#             if node.explored_children < len(node.children):
#                 child = node.children[node.explored_children]
#                 node.explored_children += 1
#                 node = child
#             else:
#                 action_idx = max(node.children, key=exp3)
#
#             actions.append(node.action)
#
#         # expansion
#         if not terminal:
#             actions = env.choose_all_actions(current_state)
#             children = []
#             for idx in range(len(actions)):
#                 children.append(Node(i, node, ))
#             node.children = children
#             random.shuffle(node.children)
#
#         # playout
#         while not terminal:
#             action = state.action_space.sample()
#             _, reward, terminal, _ = state.step(action)
#             sum_reward += reward
#             actions.append(action)
#
#

import gym
from mcts import delay_node

env = gym.make('opgame-v0')

tree_height = 8
init_state = env.map_number_to_state(0)
total_round = 300

root = delay_node.Delay_Node(0, tree_height, init_state, env)
# heavy_configure_range = set(range(env.nA_reorder, env.nA_reorder + env.nA_index))
# heavy_configure_frequency = dict()
# for heavy_idx in heavy_configure_range:
#     heavy_configure_frequency[heavy_idx] = 0
#
# heavy_configure_actions = dict()
# threshold = 5

# while round < total_round:
#     selected_actions = root.sample(round)
#     # show those actions
#     print(selected_actions)
#     # detect the heavy configuration
#     for selected_action in selected_actions:
#         heavy_configure_frequency[selected_action] = heavy_configure_frequency[selected_action] + 1
#
#     # evaluate those actions
#     round = round + 1

best_performance = 0
best_action = []
previous_selected_actions = []
for round in range(1, total_round, 1):
    selected_actions = root.sample(round)
    # show those actions
    print(selected_actions)
    previous_selected_actions.append(selected_actions)
    print(round % 5)
    if round % 5 == 4:
        # evaluate all previous actions
        update_info = []
        for selected_actions in previous_selected_actions:
            env.reset()
            # total_reward = 0
            for selected_action_idx in range(len(selected_actions)):
                # evaluate those actions
                selected_action = selected_actions[selected_action_idx]
                # observation, reward, done, info = env.step(selected_action)
                state = env.step_without_evaluation(selected_action)
            # after obtain the total reward
            reward = env.evalute()
            # total_reward = total_reward + reward
            if best_performance < reward:
                best_action = selected_actions[:selected_action + 1]
                best_performance = reward
            loss = 1.0 / reward
            update_info.append((loss, selected_actions))
        print(update_info)
        root.update_probability(update_info)
        previous_selected_actions = []
        print("current best action:")
        print(best_action)
        print("best performance:%d"%best_performance)

# return the best performance action
print("best action:")
print(best_action)
print("best performance:%d"%best_performance)


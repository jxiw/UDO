import gym
import gym_opgame
from mcts import delay_node
from mcts import uct_node
import random

env = gym.make('opgame-v0')

heavy_tree_height = 2
light_tree_height = 8
init_state = env.map_number_to_state(0)
macro_episode = 3000
micro_episode = 20

heavy_root = delay_node.Delay_Node(0, 0, heavy_tree_height, init_state, env)
light_tree_cache = dict()

# prepare the heavy configurations
heavy_configure_range = set(range(env.nA_reorder, env.nA_reorder + env.nA_index))

delay_time = 5

global_max_reward = 0
global_max_action = []

env.reset()
baseline = env.evaluate()
current_scale = 1
retest_baseline = 4
reset_database = 2

t1 = 1
while t1 < macro_episode:
    selected_heavy_action_batch = []
    for d in range(delay_time):
        selected_heavy_actions = heavy_root.sample(t1 + d)
        print("selected_heavy_action_size:")
        print(len(selected_heavy_actions))
        selected_heavy_action_batch.append(selected_heavy_actions)
    # show those actions
    print("select batch action:", selected_heavy_action_batch)
    # evaluated_order = min_cost_order(selected_heavy_action_batch)
    evaluated_order = range(0, len(selected_heavy_action_batch))
    print("evaluated_order:", evaluated_order)
    update_info = []
    for d in range(delay_time):
        current_action_idx = evaluated_order[d]
        selected_heavy_actions = selected_heavy_action_batch[current_action_idx]
        # print the current select actions
        print(selected_heavy_actions)
        add_action = set(selected_heavy_actions)
        drop_action = []
        if d > 0:
            previous_set = set(selected_heavy_action_batch[evaluated_order[d - 1]])
        if t1 > 1 or d > 0:
            add_action = add_action - previous_set
            drop_action = previous_set - set(selected_heavy_actions)
            print("invoke action")
            print(add_action)
            print("drop action")
            print(drop_action)
        # build the indices
        env.index_step(add_action, drop_action)
        # run the simulation on other parameters
        selected_heavy_action_frozen = frozenset(selected_heavy_actions)
        if selected_heavy_action_frozen in light_tree_cache:
            light_root = light_tree_cache[selected_heavy_action_frozen]
        else:
            light_root = uct_node.Uct_Node(0, 0, light_tree_height, init_state, env)
            light_tree_cache[selected_heavy_action_frozen] = light_root
        best_reward = 0
        best_actions = []
        for t2 in range(1, micro_episode):
            env.reset()
            selected_light_actions = light_root.sample(t2)
            # evaluate the light actions
            for selected_light_action in selected_light_actions:
                # observation, reward, done, info = env.step(selected_action)
                state = env.step_without_evaluation(selected_light_action)
            # after obtain the total reward
            reward = env.evaluate()
            # reward = 1
            # if 29 in selected_heavy_actions:
            #     reward += 10
            # if 28 in selected_heavy_actions:
            #     reward += 5
            # reward = reward * 1000 + sum(selected_light_actions)
            scale_reward = reward * current_scale
            light_root.update_statistics(scale_reward, selected_light_actions)
            print("reward: %d" % reward)
            print("scale reward: %.2f" % scale_reward)
            if reward > best_reward:
                best_reward = reward
                best_actions = selected_light_actions
        print("best micro-episode reward: %d" % best_reward)
        loss = 1E3 / best_reward
        update_info.append((loss, selected_heavy_actions))
        # update_info.append((best_reward, selected_heavy_actions))
    previous_set = set(selected_heavy_action_batch[evaluated_order[-1]])
    heavy_root.update_batch(update_info)
    # scale back to origin reward
    if t1 % retest_baseline == (retest_baseline - 1):
        print("reset baseline")
        env.reset()
        env.index_step(set(), previous_set)
        previous_set=set()
        current_performance = env.evaluate()
        current_scale = baseline / current_performance
        print("current_scale:%.2f"%current_scale)
    # try the reset database method
    if t1 % reset_database == (reset_database - 1):
        print("reset database")
        env.reset_database()
    # evaluate those actions
    t1 += delay_time



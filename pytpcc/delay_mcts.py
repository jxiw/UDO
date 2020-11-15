import gym
import gym_opgame
from mcts import delay_node
from mcts import uct_node
import random

def min_cost_order(selected_action_batch):
    # determine the order to evaluate those actions of the given batch
    # dp algorithm
    batch_size = len(selected_action_batch)
    if batch_size < 3:
        return range(batch_size)
    else:
        selected_action_batch_set = [set(batch) for batch in selected_action_batch]
        # take the first
        first_action = selected_action_batch_set[0]
        second_action = selected_action_batch_set[1]
        # cost for the first two elements
        common = first_action.intersection(second_action)
        cost = len(first_action) + len(second_action) - len(common)
        order = [0, 1]
        for selected_action_idx in range(2, len(selected_action_batch_set)):
            # obtain select action
            selected_action = selected_action_batch_set[selected_action_idx]
            # consider to insert the new action to the first or last element
            # if insert to first element
            current_cost1 = cost + len(selected_action) - len(
                selected_action.intersection(selected_action_batch_set[order[0]]))
            current_cost2 = cost + len(selected_action) - len(
                selected_action.intersection(selected_action_batch_set[order[-1]]))
            if current_cost2 > current_cost1:
                min_cost = current_cost1
                min_pos = -1
            else:
                min_cost = current_cost2
                min_pos = len(order) - 1
            # consider to insert the new action to the middle element
            for insert_pos in range(0, len(order) - 1):
                prev_pos = order[insert_pos]
                next_pos = order[insert_pos + 1]
                current_cost = cost - (len(selected_action_batch_set[next_pos]) - len(
                    selected_action_batch_set[prev_pos].intersection(
                        selected_action_batch_set[next_pos])))
                + len(selected_action) - len(
                    selected_action.intersection(selected_action_batch_set[prev_pos]))
                + len(selected_action_batch_set[next_pos]) - len(
                    selected_action.intersection(selected_action_batch_set[next_pos]))
                if current_cost < min_cost:
                    min_cost = current_cost
                    min_pos = insert_pos
            # update the order
            order.insert(min_pos + 1, selected_action_idx)
            # print("current order")
            # print(order)
        return order


env = gym.make('opgame-v0')

heavy_tree_height = 3
light_tree_height = 8
init_state = env.map_number_to_state(0)
macro_episode = 200
micro_episode = 100

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
retest_baseline = 5

t1 = 1
while t1 < macro_episode:
    selected_heavy_action_batch = []
    for d in range(delay_time):
        selected_heavy_actions = heavy_root.sample(t1 + d)
        print("selected_heavy_action_size:")
        print(len(selected_heavy_actions))
        selected_heavy_action_batch.append(selected_heavy_actions)
    # show those actions
    print(selected_heavy_action_batch)
    evaluated_order = min_cost_order(selected_heavy_action_batch)
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
            scale_reward = reward * current_scale
            light_root.update_statistics(scale_reward, selected_light_actions)
            print("reward: %d" % reward)
            print("scale reward: %.2f" % scale_reward)
            if reward > best_reward:
                best_reward = reward
                best_actions = selected_light_actions
        print("best micro-episode reward: %d" % best_reward)
        loss = 1 / best_reward
        update_info.append((loss, selected_heavy_actions))
    previous_set = set(selected_heavy_action_batch[evaluated_order[-1]])
    heavy_root.update_probability(update_info)
    if t1 % retest_baseline == (retest_baseline - 1):
        print("reset baseline")
        env.reset()
        env.index_step(set(), previous_set)
        previous_set=set()
        current_performance = env.evaluate()
        current_scale = baseline / current_performance
        print("current_scale:%.2f"%current_scale)
    # evaluate those actions
    t1 += delay_time



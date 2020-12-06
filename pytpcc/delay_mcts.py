import gym
import gym_olapgame
from gym_olapgame.envs import index

from mcts import delay_node
from mcts import uct_node
import time
import constants

all_queries= ["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10", "q11", "q12",
                   "q13", "q14", "q15", "q16", "q17", "q18", "q19", "q20", "q21", "q22"]
query_info = {all_queries[idx]: idx for idx in range(len(all_queries))}
index_card_info = list(map(lambda x: x[4], index.candidate_indices))
index_query_info = list(map(lambda x: list(map(lambda y: query_info[y], x[3])), index.candidate_indices))
print(index_query_info)
# print(index_card_info)
def index_build_cost(current_index_list):
    return sum(index_card_info[current_index] for current_index in current_index_list)

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
        cost = index_build_cost(first_action) + index_build_cost(second_action) - index_build_cost(common)
        order = [0, 1]
        for selected_action_idx in range(2, len(selected_action_batch_set)):
            # obtain select action
            selected_action = selected_action_batch_set[selected_action_idx]
            # consider to insert the new action to the first or last element
            # if insert to first element
            # current_cost1 = cost + len(selected_action) - len(
            #     selected_action.intersection(selected_action_batch_set[order[0]]))
            # current_cost2 = cost + len(selected_action) - len(
            #     selected_action.intersection(selected_action_batch_set[order[-1]]))
            current_cost1 = cost + index_build_cost(selected_action) - index_build_cost(selected_action.intersection(selected_action_batch_set[order[0]]))
            current_cost2 = cost + index_build_cost(selected_action) - index_build_cost(selected_action.intersection(selected_action_batch_set[order[-1]]))
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
                current_cost = cost - (index_build_cost(selected_action_batch_set[next_pos]) - index_build_cost(
                    selected_action_batch_set[prev_pos].intersection(
                        selected_action_batch_set[next_pos])))
                + index_build_cost(selected_action) - index_build_cost(
                    selected_action.intersection(selected_action_batch_set[prev_pos]))
                + index_build_cost(selected_action_batch_set[next_pos]) - index_build_cost(
                    selected_action.intersection(selected_action_batch_set[next_pos]))
                if current_cost < min_cost:
                    min_cost = current_cost
                    min_pos = insert_pos
            # update the order
            order.insert(min_pos + 1, selected_action_idx)
            # print("current order")
            # print(order)
        return order

env = gym.make('olapgame-v0')

# number of indices equal heavy_tree_height + 1
heavy_tree_height = 3
light_tree_height = 3

init_state = env.map_number_to_state(0)
macro_episode = 10000
micro_episode = 3

terminate_action = env.index_candidate_num
heavy_root = delay_node.Delay_Node(0, 0, heavy_tree_height, terminate_action, init_state, env)
light_tree_cache = dict()

# prepare the heavy configurations
delay_time = 5

global_max_reward = 0
global_max_action = []

env.reset()
# baseline_runtime = env.evaluate_light_under_heavy()
idx_build_time = 0

t1 = 1
while t1 < macro_episode:
    selected_heavy_action_batch = []
    remove_terminate_action_batch = []
    for d in range(delay_time):
        selected_heavy_actions = heavy_root.sample(t1 + d)
        print("selected_heavy_action_size:")
        print(len(selected_heavy_actions))
        selected_heavy_action_batch.append(selected_heavy_actions)
        remove_terminate_action_batch.append([heavy_action for heavy_action in selected_heavy_actions if heavy_action != terminate_action])
    # show those actions
    print(selected_heavy_action_batch)
    # evaluated_order = range(0, len(remove_terminate_action_batch))
    evaluated_order = min_cost_order(remove_terminate_action_batch)
    print("evaluated_order:", evaluated_order)
    update_info = []
    # evaluate selected actions one by one
    for d in range(delay_time):
        current_action_idx = evaluated_order[d]
        selected_heavy_actions = selected_heavy_action_batch[current_action_idx]
        remove_terminate_heavy_actions = remove_terminate_action_batch[current_action_idx]
        # print the current select actions
        print(remove_terminate_heavy_actions)
        add_action = set(remove_terminate_heavy_actions)
        drop_action = set()
        if d > 0:
            # take the previous created indices
            previous_set = set(remove_terminate_action_batch[evaluated_order[d - 1]])
        if t1 > 1 or d > 0:
            add_action = add_action - previous_set
            drop_action = previous_set - set(remove_terminate_heavy_actions)
            print("invoke action")
            print(add_action)
            print("drop action")
            print(drop_action)
        # build the indices
        time_start = time.time()
        env.index_step(add_action, drop_action)
        time_end = time.time()
        idx_build_time += (time_end - time_start)
        # run the simulation on other parameters
        selected_heavy_action_frozen = frozenset(remove_terminate_heavy_actions)
        if selected_heavy_action_frozen in light_tree_cache:
            light_root = light_tree_cache[selected_heavy_action_frozen]
        else:
            light_root = uct_node.Uct_Node(0, 0, light_tree_height, init_state, env)
            light_tree_cache[selected_heavy_action_frozen] = light_root
        best_reward = 1000000
        # best_actions = []
        query_to_consider_list = list(map(lambda x: index_query_info[x], remove_terminate_heavy_actions)) #index_query_info
        query_to_consider = set([item for sublist in query_to_consider_list for item in sublist])
        print("query to consider:", query_to_consider)
        best_performance = dict()
        for t2 in range(1, micro_episode):
            env.reset()
            selected_light_actions = light_root.sample(t2)
            # evaluate the light actions
            for selected_light_action in selected_light_actions:
                # move to next state
                state = env.step_without_evaluation(selected_light_action)
            # after obtain the total reward
            # run_time = env.evaluate_light_under_heavy()
            run_time = [11] * 22
            if 10 in selected_heavy_actions:
                run_time[3] = 9
            if 8 in selected_heavy_actions:
                run_time[8] = 5
            if 6 in selected_heavy_actions:
                run_time[19] = 3
            total_run_time = sum(run_time)
            light_reward = constants.light_reward_scale / total_run_time
            light_root.update_statistics(light_reward, selected_light_actions)
            for query in query_to_consider:
                if query in best_performance:
                    if run_time[query] < best_performance[query]:
                        best_performance[query] = run_time[query]
                else:
                    best_performance[query] = run_time[query]
            if sum(run_time) < best_reward:
                best_reward = sum(run_time)
        print("best micro-episode reward: %d" % best_reward)
        # calculate the improvement of each index
        improvements = []
        for action in remove_terminate_heavy_actions:
            # get related queries
            queries = index_query_info[action]
            # index_improvement = sum(baseline_runtime[query] - best_performance[query] for query in queries)
            index_improvement = sum(constants.timeout - best_performance[query] for query in queries)
            improvements.append(index_improvement)
        if selected_heavy_actions[-1] == terminate_action:
            improvements.append(0)
        print("improvement:", improvements)
        update_info.append((improvements, selected_heavy_actions))
        # loss = best_reward
        # update_info.append((loss, selected_heavy_actions))
    previous_set = set(remove_terminate_action_batch[evaluated_order[-1]])
    heavy_root.update_batch(update_info)
    heavy_root.print()
    print("time for indices:", idx_build_time)
    t1 += delay_time

print("")



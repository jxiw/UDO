from typing import Dict, List, Any

import gym
import gym_olapgame
from gym_olapgame.envs import index

from mcts import delay_uct_node
from mcts import uct_node
import time
import constants
import random

all_queries = list(constants.QUERIES.keys())
# print(all_queries)
query_info = {all_queries[idx]: idx for idx in range(len(all_queries))}
index_card_info = list(map(lambda x: x[4], index.candidate_indices))
index_query_info = list(map(lambda x: list(map(lambda y: query_info[y], x[3])), index.candidate_indices))

print("start:", time.time())

# print(index_query_info)

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
            current_cost1 = cost + index_build_cost(selected_action) - index_build_cost(
                selected_action.intersection(selected_action_batch_set[order[0]]))
            current_cost2 = cost + index_build_cost(selected_action) - index_build_cost(
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
light_tree_height = 5

init_state = env.map_number_to_state(0)
macro_episode = 100000
micro_episode = 10

terminate_action = env.index_candidate_num
heavy_root = delay_uct_node.Delay_Uct_Node(0, 0, heavy_tree_height, terminate_action, init_state, env)
light_tree_cache = dict()

# prepare the heavy configurations
delay_time = 5

global_max_reward = 0
global_max_action = []

env.reset()
# baseline_runtime = env.evaluate_light_under_heavy(all_queries, [0] * len(all_queries))
baseline_runtime = [0.9940712451934814, 0.6042485237121582, 0.6398360729217529, 0.7888808250427246, 1.339827060699463,
                    1.229813575744629, 1.1687071323394775, 4.970311880111694, 9.041927099227905, 4.719568252563477,
                    6.273277997970581, 0.8070902824401855, 0.7040481567382812, 0.823775053024292, 0.4171473979949951,
                    0.3651401996612549, 6.004456043243408, 12.974314451217651, 7.618359088897705, 7.9508116245269775,
                    19.459794998168945, 11.769405364990234, 21.801249980926514, 20.709392070770264, 26.559233903884888,
                    35.339061975479126, 8.91144871711731, 8.461608648300171, 16.969313621520996, 18.16647171974182,
                    10.793412208557129, 7.7689361572265625, 9.712358474731445, 22.28636598587036, 12.667174339294434,
                    7.4198689460754395, 12.633104085922241, 1.943755865097046, 0.9538013935089111, 0.8982651233673096,
                    0.8930871486663818, 8.767508745193481, 4.951838493347168, 6.710262775421143, 11.714922666549683,
                    17.991100549697876, 6.716376066207886, 17.61158299446106, 8.391687631607056, 6.339285612106323,
                    6.856660604476929, 5.9427289962768555, 5.4410741329193115, 5.932071685791016, 6.144399642944336,
                    16.90151596069336, 28.16093945503235, 23.83449077606201, 25.914294719696045, 28.996219158172607,
                    17.953474283218384, 13.207022190093994, 13.725465297698975, 27.772254943847656, 28.611818552017212,
                    21.141791343688965, 19.451528549194336, 26.658838987350464, 17.442588090896606, 25.725683450698853,
                    17.36896014213562, 38.401965618133545, 18.268529176712036, 11.438706636428833, 14.362481594085693,
                    10.970466136932373, 5.588280200958252, 7.266705751419067, 8.865687370300293, 6.623289346694946,
                    8.38484525680542, 9.030463695526123, 5.721858263015747, 5.525036811828613, 6.141709566116333,
                    18.705531120300293, 22.926883459091187, 21.824620246887207, 21.26836848258972, 26.503443002700806,
                    14.728663921356201, 7.927353382110596, 18.853444814682007, 9.887370347976685, 5.495664596557617,
                    83.96899724006653, 9.560714721679688, 5.8471856117248535, 7.837913513183594, 21.042979955673218,
                    23.669015884399414, 19.072806358337402, 24.907282829284668, 19.933234453201294, 19.062625646591187,
                    23.07475519180298, 21.40514349937439, 23.089293479919434, 1.2680790424346924, 1.3159940242767334,
                    2.810530185699463, 1.3043646812438965, 1.0104424953460693]
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
        remove_terminate_action_batch.append(
            [heavy_action for heavy_action in selected_heavy_actions if heavy_action != terminate_action])
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
        best_reward = 0
        # best_actions = []
        query_to_consider_list = list(
            map(lambda x: index_query_info[x], remove_terminate_heavy_actions))  # index_query_info
        query_to_consider = set([item for sublist in query_to_consider_list for item in sublist])
        print("query to consider:", query_to_consider)
        # best_performance: Dict[List[Any], int] = dict()
        if len(query_to_consider) == 0:
            best_reward = 0
        else:
            for t2 in range(1, micro_episode):
                env.reset()
                selected_light_actions = light_root.sample(t2)
                # evaluate the light actions
                for selected_light_action in selected_light_actions:
                    # move to next state
                    state = env.step_without_evaluation(selected_light_action)

                # run_time = [11] * 22
                # if 10 in selected_heavy_actions:
                #     run_time[3] = 10
                # if 8 in selected_heavy_actions:
                #     run_time[8] = 10
                # if 6 in selected_heavy_actions:
                #     run_time[19] = 3
                # if 4 in selected_heavy_actions and 5 in selected_heavy_actions:
                #     run_time[20] = 4

                # after obtain the total reward
                query_to_run = random.sample(query_to_consider, constants.sample_num)
                run_time = env.evaluate_light_under_heavy([all_queries[select_query] for select_query in query_to_run],
                                                          [baseline_runtime[select_query] for select_query in query_to_run])
                total_run_time = sum(run_time)
                # another update method
                # current_reward = constants.light_reward_scale / total_run_time

                # update the best gain for each query
                # for query in query_to_consider:
                #     if query in best_performance:
                #         if run_time[query] < best_performance[query]:
                #             best_performance[query] = run_time[query]
                #     else:
                #         best_performance[query] = run_time[query]

                # whether we find better run time
                current_reward = (max(sum(baseline_runtime[query] for query in query_to_run) - total_run_time, 0)) * len(query_to_consider) / constants.sample_num

                light_root.update_statistics(current_reward, selected_light_actions)
                if best_reward < current_reward:
                    best_reward = current_reward

        print("best micro-episode reward: %d" % best_reward)
        # calculate the improvement of each index

        # a different approach
        # improvements = []
        # for action in remove_terminate_heavy_actions:
        #     # get related queries
        #     queries = index_query_info[action]
        #     # index_improvement = sum(baseline_runtime[query] - best_performance[query] for query in queries)
        #     index_improvement = sum(constants.timeout - best_performance[query] for query in queries)
        #     improvements.append(index_improvement)
        # if selected_heavy_actions[-1] == terminate_action:
        #     improvements.append(0)
        # print("improvement:", improvements)
        # update_info.append((improvements, selected_heavy_actions))

        # another update method
        # improvement = constants.timeout * len(all_queries) - best_reward

        update_info.append((best_reward, selected_heavy_actions))
        # if we use exp3, we need to minimize the loss
        # update_info.append((loss, selected_heavy_actions))
    previous_set = set(remove_terminate_action_batch[evaluated_order[-1]])
    heavy_root.update_batch(update_info)
    heavy_root.print()
    print("time for indices:", idx_build_time)
    t1 += delay_time

print("best heavy action", heavy_root.best_actions())

print("end:", time.time())
import math

import gym
from gym_olapgame.envs import index

from mcts import delay_uct_node
from mcts import uct_node
import time
import constants
import random
from old import order_optimizer

all_queries = list(constants.QUERIES.keys())
nr_query = len(all_queries)

# print(all_queries)
query_info = {all_queries[idx]: idx for idx in range(nr_query)}
index_card_info = list(map(lambda x: x[4], index.candidate_indices))
index_query_info = list(map(lambda x: list(map(lambda y: query_info[y], x[3])), index.candidate_indices))

print("start:", time.time())

optimizer= order_optimizer.OrderOptimizer(index_card_info)
env = gym.make('olapgame-v0')

# number of indices equal heavy_tree_height + 1
heavy_tree_height = 4
light_tree_height = 5

init_state = env.state_decoder(0)
macro_episode = 10000
micro_episode = 5

terminate_action = env.index_candidate_num
light_tree_cache = dict()

# prepare the heavy configurations
delay_time = 20

global_max_reward = 0
global_max_action = []

env.reset()
constants.default_runtime = env.evaluate_light(all_queries, [0] * len(all_queries))
# [11] * nr_query
    # [0.9940712451934814, 0.6042485237121582, 0.6398360729217529, 0.7888808250427246, 1.339827060699463,
    #                 1.229813575744629, 1.1687071323394775, 4.970311880111694, 9.041927099227905, 4.719568252563477,
    #                 6.273277997970581, 0.8070902824401855, 0.7040481567382812, 0.823775053024292, 0.4171473979949951,
    #                 0.3651401996612549, 6.004456043243408, 12.974314451217651, 7.618359088897705, 7.9508116245269775,
    #                 19.459794998168945, 11.769405364990234, 21.801249980926514, 20.709392070770264, 26.559233903884888,
    #                 35.339061975479126, 8.91144871711731, 8.461608648300171, 16.969313621520996, 18.16647171974182,
    #                 10.793412208557129, 7.7689361572265625, 9.712358474731445, 22.28636598587036, 12.667174339294434,
    #                 7.4198689460754395, 12.633104085922241, 1.943755865097046, 0.9538013935089111, 0.8982651233673096,
    #                 0.8930871486663818, 8.767508745193481, 4.951838493347168, 6.710262775421143, 11.714922666549683,
    #                 17.991100549697876, 6.716376066207886, 17.61158299446106, 8.391687631607056, 6.339285612106323,
    #                 6.856660604476929, 5.9427289962768555, 5.4410741329193115, 5.932071685791016, 6.144399642944336,
    #                 16.90151596069336, 28.16093945503235, 23.83449077606201, 25.914294719696045, 28.996219158172607,
    #                 17.953474283218384, 13.207022190093994, 13.725465297698975, 27.772254943847656, 28.611818552017212,
    #                 21.141791343688965, 19.451528549194336, 26.658838987350464, 17.442588090896606, 25.725683450698853,
    #                 17.36896014213562, 38.401965618133545, 18.268529176712036, 11.438706636428833, 14.362481594085693,
    #                 10.970466136932373, 5.588280200958252, 7.266705751419067, 8.865687370300293, 6.623289346694946,
    #                 8.38484525680542, 9.030463695526123, 5.721858263015747, 5.525036811828613, 6.141709566116333,
    #                 18.705531120300293, 22.926883459091187, 21.824620246887207, 21.26836848258972, 26.503443002700806,
    #                 14.728663921356201, 7.927353382110596, 18.853444814682007, 9.887370347976685, 5.495664596557617,
    #                 83.96899724006653, 9.560714721679688, 5.8471856117248535, 7.837913513183594, 21.042979955673218,
    #                 23.669015884399414, 19.072806358337402, 24.907282829284668, 19.933234453201294, 19.062625646591187,
    #                 23.07475519180298, 21.40514349937439, 23.089293479919434, 1.2680790424346924, 1.3159940242767334,
    #                 2.810530185699463, 1.3043646812438965, 1.0104424953460693]

heavy_root = delay_uct_node.Delay_Uct_Node(0, 0, heavy_tree_height, terminate_action, init_state, env)
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
    evaluated_order = optimizer.min_cost_order(remove_terminate_action_batch)
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
        best_reward = 10000000
        query_to_consider = set([item for sublist in list(map(lambda x: index_query_info[x], remove_terminate_heavy_actions)) for item in sublist])
        if len(remove_terminate_heavy_actions) == 0:
            query_to_consider = set(range(nr_query))
        print("query to consider:", query_to_consider)
        # best performance for each query
        best_performance = dict()
        for t2 in range(1, micro_episode + 1):
            env.reset()
            selected_light_actions = light_root.sample(t2)
            # evaluate the light actions
            for selected_light_action in selected_light_actions:
                # move to next state
                state = env.step_without_evaluation(selected_light_action)

            sample_num = math.ceil(constants.sample_rate * len(query_to_consider))
            sampled_query_list = random.choices(list(query_to_consider), k=sample_num)
            run_time = env.evaluate_light([all_queries[select_query] for select_query in sampled_query_list],
                                          [constants.default_runtime[select_query] for select_query in sampled_query_list])

            # run_time = [11] * nr_query
            # if 10 in selected_heavy_actions:
            #     run_time[1] = 10
            # if 8 in selected_heavy_actions:
            #     run_time[2] = 10
            # if 6 in selected_heavy_actions:
            #     run_time[0] = 3
            # if 4 in selected_heavy_actions and 5 in selected_heavy_actions:
            #     run_time[-1] = 1

            total_run_time = sum(run_time)
            default_time = sum(constants.default_runtime[select_query] for select_query in sampled_query_list)
            light_reward = default_time / total_run_time
            light_root.update_statistics(light_reward, selected_light_actions)
            # update the best gain for each query
            for invoke_id in range(len(sampled_query_list)):
                query = sampled_query_list[invoke_id]
                if query in best_performance:
                    if run_time[invoke_id] < best_performance[query]:
                        best_performance[query] = run_time[invoke_id]
                else:
                    best_performance[query] = run_time[invoke_id]
            if sum(run_time) < best_reward:
                best_reward = sum(run_time)

        print("best micro-episode reward: %d" % best_reward)
        # calculate the improvement of each index

        # a different approach
        improvement = sum(constants.default_runtime[query] - best_performance[query] for query in best_performance)
        print("improvement:", improvement)
        improvement = max(improvement, 0)
        update_info.append((improvement, selected_heavy_actions))

        # if we use exp3, we need to minimize the loss
        # update_info.append((loss, selected_heavy_actions))
    previous_set = set(remove_terminate_action_batch[evaluated_order[-1]])
    heavy_root.update_batch(update_info)
    heavy_root.print()
    print("time for indices:", idx_build_time)
    print("best heavy action", heavy_root.best_actions())
    t1 += delay_time

print("best heavy action", heavy_root.best_actions())

print("end:", time.time())
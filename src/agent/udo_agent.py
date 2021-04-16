import math
import random
import time

import gym

from mcts.mcts_node import SpaceType
from mcts.uct_node import uct_node
from optimizer import order_optimizer


def run_udo_agent(driver, queries, candidate_indices, duration, heavy_horizon, light_horizon, delay_time=5):
    duration_in_seconds = duration * 3600
    env = gym.make('udo_optimization-v0', driver=driver, queries=queries, candidate_indices=candidate_indices)

    nr_query = len(queries)  # number of queries
    query_ids = env.query_ids  # queries names
    query_to_id = {query_ids[idx]: idx for idx in range(nr_query)}  # query number to query name

    index_card_info = list(map(lambda x: x[4], candidate_indices))
    index_to_applicable_queries = env.index_to_applicable_queries

    start_tune_time = time.time()
    print("start:", start_tune_time)

    optimizer = order_optimizer.OrderOptimizer(index_card_info)

    # number of indices equal heavy_tree_height + 1
    heavy_tree_height = heavy_horizon
    light_tree_height = light_horizon

    init_state = env.state_decoder(0)
    # macro_episode = 10000
    micro_episode = 5

    terminate_action = env.index_candidate_num
    light_tree_cache = dict()
    query_evaluate_sample_rate = 1

    # prepare the heavy configurations
    # delay_time = 5

    global_max_reward = 0
    global_max_action = []

    env.reset()
    default_runtime = env.default_runtime

    heavy_root = uct_node(round=0, tree_level=0, tree_height=heavy_tree_height, state=init_state, env=env,
                          space_type=SpaceType.Heavy)
    idx_build_time = 0
    best_simulation_time = sum(default_runtime)
    best_configs = {}
    t1 = 1
    start_time = time.time()
    end_episode_time = time.time()
    while (end_episode_time - start_time) < duration_in_seconds:
        selected_heavy_action_batch = []
        configuration_to_evaluate = []
        # remove_terminate_action_batch = []
        print("delay_time:", delay_time)
        for d in range(delay_time):
            selected_heavy_actions = heavy_root.sample(t1 + d)
            selected_heavy_action_batch.append(selected_heavy_actions)
            # add all intermediate steps
            remove_terminate_heavy_actions = [heavy_action for heavy_action in selected_heavy_actions if
                                              heavy_action != terminate_action]
            for i in range(len(remove_terminate_heavy_actions)):
                current_actions = frozenset(remove_terminate_heavy_actions[:i + 1])
                if current_actions not in configuration_to_evaluate:
                    configuration_to_evaluate.append(current_actions)
        # show those actions
        print(selected_heavy_action_batch)
        print("evaluate configurations:", configuration_to_evaluate)
        # evaluated_order = range(0, len(remove_terminate_action_batch))
        evaluated_order = optimizer.greedy_min_cost_order(configuration_to_evaluate)
        print("evaluated order:", evaluated_order)
        macro_performance_info = dict()
        for current_order_idx in range(len(evaluated_order)):
            current_order = evaluated_order[current_order_idx]
            selected_heavy_action_frozen = frozenset(configuration_to_evaluate[current_order])
            # generate add action
            add_action = set(selected_heavy_action_frozen)
            drop_action = set()
            if current_order_idx > 0:
                # take the previous created indices
                previous_set = set(configuration_to_evaluate[evaluated_order[current_order_idx - 1]])
            if t1 > 1 or current_order_idx > 0:
                add_action = add_action - previous_set
                drop_action = previous_set - set(selected_heavy_action_frozen)
                print("invoke action")
                print(add_action)
                print("drop action")
                print(drop_action)
            # build the indices
            time_start = time.time()
            env.index_step(add_action, drop_action)
            time_end = time.time()
            idx_build_time += (time_end - time_start)

            print("selected_heavy_action_frozen:", selected_heavy_action_frozen)
            if selected_heavy_action_frozen in light_tree_cache:
                light_root = light_tree_cache[selected_heavy_action_frozen]
            else:
                light_root = uct_node(round=0, tree_level=0, tree_height=light_tree_height, state=init_state, env=env,
                                      space_type=SpaceType.Light)
                light_tree_cache[selected_heavy_action_frozen] = light_root
            # for the light tree
            best_reward = 0
            # query to consider for the current select heavy configuration
            query_to_consider = set(
                [applicable_query for applicable_queries in
                 list(map(lambda x: index_to_applicable_queries[x], selected_heavy_action_frozen)) for applicable_query
                 in
                 applicable_queries])
            print("query to consider:", query_to_consider)
            # best performance of the sampled each query
            best_micro_performance = dict()
            for t2 in range(1, micro_episode + 1):
                # for the micro episode
                env.reset()
                selected_light_actions = light_root.sample(t1 * micro_episode + t2)
                # evaluate the light actions
                for selected_light_action in selected_light_actions:
                    # move to next state
                    state = env.step_without_evaluation(selected_light_action)
                # obtain sample number
                sample_num = math.ceil(query_evaluate_sample_rate * len(query_to_consider))
                # generate sample queries
                sampled_query_list = random.sample(list(query_to_consider), k=sample_num)
                print("sampled_query_list:", sampled_query_list)
                # obtain run time info by running queries within timeout
                run_time = env.evaluate_light(sampled_query_list)
                # the total time of sampled queries
                total_run_time = sum(run_time)
                # the default time of sampled queries
                default_runtime_of_sampled_queries = [default_runtime[select_query] for select_query in
                                                      sampled_query_list]
                sum_default_time_of_sampled_queries = sum(default_runtime_of_sampled_queries)
                # the relative ration of the improvement, the less of total_run_time, the better
                light_reward = sum_default_time_of_sampled_queries / total_run_time
                print("default_runtime_of_sampled_queries", default_runtime_of_sampled_queries)
                print("light_action:", selected_light_actions)
                print("light_reward:", light_reward)

                other_default_time = sum(default_runtime[select_query] for select_query in range(nr_query) if
                                         select_query not in sampled_query_list)
                estimate_workload_time = (other_default_time + total_run_time)
                print("estimate whole workload time:", estimate_workload_time)
                if estimate_workload_time < best_simulation_time:
                    best_simulation_time = estimate_workload_time
                    best_configs = {"heavy": selected_heavy_action_frozen, "light": selected_light_actions}

                current_time = time.time()
                print("current global time:", (current_time - start_time))
                print("global time for indices:", idx_build_time)

                light_root.update_statistics_with_mcts_reward(light_reward, selected_light_actions)
                # update the best gain for each query
                for sample_query_id in range(len(sampled_query_list)):
                    sample_query = sampled_query_list[sample_query_id]
                    run_time_of_sampled_query = run_time[sample_query_id]
                    if sample_query in best_micro_performance:
                        # if we get better improvement, then set it to better time
                        if run_time_of_sampled_query < best_micro_performance[sample_query]:
                            best_micro_performance[sample_query] = run_time_of_sampled_query
                    else:
                        best_micro_performance[sample_query] = run_time[sample_query_id]
                if sum(run_time) < best_reward:
                    best_reward = sum(run_time)
            # save the performance of current selected heavy action
            macro_performance_info[selected_heavy_action_frozen] = best_micro_performance

        print("macro_performance_info:", macro_performance_info)
        # sys.stdout.flush()
        # ### obtain the best macro performances info
        best_slot_performance = dict()
        for selected_heavy_action_frozen, performance in macro_performance_info.items():
            for query, query_run_time in performance.items():
                if query in best_slot_performance:
                    if query_run_time < best_slot_performance[query]:
                        best_slot_performance[query] = query_run_time
                else:
                    best_slot_performance[query] = query_run_time
        print("best_slot_performance", best_slot_performance)
        # after testing the performance of each configuration
        # generate the update information based on delta improvement
        update_info_slot = []
        for selected_heavy_actions in selected_heavy_action_batch:
            # generate intermediate result
            update_reward = []
            previous_performance = dict()
            for i in range(len(selected_heavy_actions)):
                if selected_heavy_actions[i] != terminate_action:
                    selected_heavy_action_frozen = frozenset(selected_heavy_actions[:i + 1])
                    print("current selected_heavy_action_frozen:", selected_heavy_action_frozen)
                    applicable_query_performance = macro_performance_info[selected_heavy_action_frozen]
                    # generate reward based on the difference between previous performance and current performance
                    # the query for current indices
                    query_to_consider_new = index_to_applicable_queries[selected_heavy_actions[i]]
                    # get the query to consider
                    delta_improvement = 0
                    for query in query_to_consider_new:
                        previous_runtime = default_runtime[query]
                        current_runtime = default_runtime[query]
                        if query in applicable_query_performance:
                            current_runtime = applicable_query_performance[query]
                        if query in previous_performance:
                            previous_runtime = previous_performance[query]
                        delta_improvement += (previous_runtime - current_runtime)
                    previous_performance = applicable_query_performance
                    print("applicable_query_performance:", applicable_query_performance)
                    print("previous_performance:", previous_performance)
                    delta_improvement = max(delta_improvement, 0)
                    update_reward.append(delta_improvement)
            # update the tree based on the simulation results
            update_info_slot.append((update_reward, [heavy_action for heavy_action in selected_heavy_actions if
                                                     heavy_action != terminate_action]))
        print("update_info_slot:", update_info_slot)
        heavy_root.update_batch(update_info_slot)
        previous_set = set(configuration_to_evaluate[evaluated_order[-1]])
        heavy_root.print()
        end_episode_time = time.time()
        print("current time:", (end_episode_time - start_time))
        print("time for indices:", idx_build_time)
        print("current best heavy action", heavy_root.best_actions())
        t1 += delay_time
        # sys.stdout.flush()

    best_heavy_configs = heavy_root.best_actions()
    # best frozen heavy configs
    best_frozen_heavy_configs = frozenset(best_heavy_configs)
    if best_frozen_heavy_configs in light_tree_cache:
        light_root = light_tree_cache[best_frozen_heavy_configs]
    else:
        light_root = uct_node(round=0, tree_level=0, tree_height=light_tree_height, state=init_state, env=env,
                              space_type=SpaceType.Light)

    # additional step, tuning the final index configuration
    # build the indices
    add_action = set(best_heavy_configs) - previous_set
    drop_action = previous_set - set(best_heavy_configs)
    env.index_step(add_action, drop_action)
    micro_episode_final_tune = 50
    for t2 in range(1, micro_episode_final_tune):
        # for the micro episode
        env.reset()
        selected_light_actions = light_root.sample(t1 * micro_episode + t2)
        # evaluate the light actions
        for selected_light_action in selected_light_actions:
            # move to next state
            state = env.step_without_evaluation(selected_light_action)
        # obtain run time info by running queries within timeout
        run_time = env.evaluate_light([query for query in range(nr_query)])
        # the total time of total queries
        total_run_time = sum(run_time)
        default_time = sum(default_runtime)
        # the relative ration of the improvement, the less of total_run_time, the better
        light_reward = default_time / total_run_time
        print("light_action:", selected_light_actions)
        print("light_reward:", light_reward)
        light_root.update_statistics_with_mcts_reward(light_reward, selected_light_actions)
    best_light_configs = light_root.best_actions()
    # best heavy action from tree search
    print("best configurations during the simulation", best_configs)
    print("best heavy action from tree search", heavy_root.best_actions())
    print("best_light_config:", best_light_configs)

    final_tune_time = time.time()
    print("end:", final_tune_time)

    print(f"Summary: Total Tuning Time {(final_tune_time - start_tune_time) / 3600} hours")
    best_candidate_indices = [candidate_indices[config] for config in best_heavy_configs]
    print(f"Best index configurations:")
    for best_candidate_index in best_candidate_indices:
        print(driver.build_index_command(best_candidate_index))
    print(f"Best system parameters:")
    for light_config in best_light_configs:
        print(env.retrieve_light_action_command(light_config))

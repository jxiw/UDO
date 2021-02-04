import time

from gym_olapgame.envs import index

from drivers.postgresdriver import PostgresDriver

current_opt_action = [
    # [5, 3, 8],
    # [5], [36], [5, 8], [5, 8], [5, 8], [5, 8], [5, 8], [36, 40, 30], [36, 40, 30], [36, 40, 30], [36, 40, 30],
    # [36, 40, 30], [36, 34], [40, 34], [36, 40, 34], [36, 40, 34], [36, 40, 34], [36, 40, 34], [36, 40, 34],
    # [36, 40, 34], [36, 3, 48, 45], [36, 3, 48, 45], [36, 3, 48, 45], [36, 3, 48, 45], [36, 3, 48, 45], [5, 36, 3],
    # [5, 36, 3], [5, 36, 3], [36, 3, 48, 45], [36, 3, 48, 45], [36, 3, 48, 45], [36, 3, 48, 45], [36, 3, 48, 45],
    # [36, 3, 48, 45], [36, 3, 48, 45], [5, 36, 3], [5, 36, 3], [5, 36, 3], [5, 36, 3], [5, 48, 42, 33], [5, 48, 42, 33],
    # [36, 3, 48, 45], [36, 3, 48, 45], [5, 48, 42, 33], [5, 48, 42, 33], [5, 36, 3, 42], [36, 3, 48, 45], [5, 36, 3, 42],
    # [5, 36, 3, 42], [5, 36, 3, 42], [5, 36, 3, 42], [5, 36, 3, 42], [5, 36, 3, 42], [5, 36, 3, 42], [5, 48, 42, 51],
    # [5, 48, 34, 26], [5, 36, 3, 42], [5, 3, 34, 7], [5, 36, 3, 42], [5, 36, 3, 42], [5, 48, 42, 17], [5, 48, 42, 17],
    # [5, 48, 34, 46], [5, 48, 34, 46], [5, 48, 34, 46], [5, 36, 3, 42], [5, 36, 3, 42], [5, 36, 3, 42], [5, 36, 3, 42],
    # [5, 40, 42, 36], [5, 36, 40, 48], [5, 36, 40, 48], [5, 36, 40, 48], [5, 42, 48, 8], [5, 36, 40, 48], [5, 42, 48, 8],
    # [5, 42, 48, 8], [5, 42, 48, 16], [5, 36, 40, 48], [5, 40, 48, 52], [5, 36, 40, 48], [5, 36, 40, 48],
    # [5, 36, 40, 48], [5, 48, 34, 46], [5, 48, 34, 46], [5, 42, 48, 16], [5, 36, 40, 48], [5, 36, 40, 48],
    # [5, 36, 40, 48], [5, 36, 40, 42, 59], [5, 36, 40, 42, 59], [5, 36, 40, 42, 46], [5, 36, 40, 42, 46],
    # [5, 36, 40, 42, 46], [5, 36, 40, 42, 46], [5, 36, 40, 42, 46], [5, 36, 40, 42, 46], [5, 36, 40, 48, 59],
    # [5, 36, 40, 48, 57], [5, 36, 40, 48, 57], [5, 36, 40, 48, 57], [5, 36, 40, 48, 57], [5, 36, 40, 48, 57],
    # [5, 36, 40, 48, 57], [5, 36, 40, 48, 57], [5, 36, 40, 48, 57], [5, 36, 40, 48, 57], [5, 36, 40, 48, 57],
    # [5, 42, 48, 16], [5, 36, 40, 48, 57], [5, 42, 54, 36, 27], [5, 42, 54, 36, 27], [5, 36, 40, 48, 57],
    # [5, 36, 40, 48, 57], [5, 36, 40, 48, 57], [5, 36, 40, 48, 57], [5, 36, 40, 48, 57], [5, 36, 48, 7, 16],
    # [5, 36, 48, 7, 16], [5, 36, 40, 48, 22], [5, 36, 48, 7, 16], [5, 36, 48, 7, 16], [5, 36, 48, 34, 26],
    # [5, 36, 48, 34, 26]
    [5]
]

# current_opt_action = [
#     # [5], [3], [14], [34], [36], [40], [42], [48]
#     # [8], [16], [26], [57], [7]
#     # [5, 47, 30, 19],
#     # [5, 47, 30],
#     [5, 3, 8]
# ]

t1 = 0
idx_build_time = 0
macro_episode = len(current_opt_action)
driver = PostgresDriver()
driver.connect()

parameter_opt_sql = [
    "set random_page_cost = 100;",
    "set seq_page_cost = 10;",
    "set enable_bitmapscan = on;",
    "set enable_mergejoin = on;",
    "set force_parallel_mode = off;",
    "set temp_buffers = 102400;",
    "set enable_hashagg = on;",
    "set enable_indexscan = on;",
    "set force_parallel_mode = on;",
    "set enable_seqscan = on;",
    "set max_parallel_workers_per_gather = 100;",
    "set enable_tidscan = on;",
    "set enable_nestloop = on;"
]

terminate_action = 59
cache_performance = dict()
# while t1 < macro_episode:
#     current_best_indices =  [action for action in current_opt_action[t1] if action != terminate_action]
#     current_best_indices_frozen = frozenset(current_best_indices)
#
#     if current_best_indices_frozen not in cache_performance:
#         # generate add action
#         add_action = set(current_best_indices)
#         drop_action = set()
#
#         if t1 > 0:
#             add_action = add_action - previous_set
#             drop_action = previous_set - set(current_best_indices)
#             print("invoke action")
#             print(add_action)
#             print("drop action")
#             print(drop_action)
#
#         # build the indices
#         time_start = time.time()
#         for action in add_action:
#             index_to_create = index.candidate_indices[action]
#             # build index action
#             print("create index")
#             print(index_to_create)
#             driver.buildIndex(index_to_create)
#         for action in drop_action:
#             index_to_drop = index.candidate_indices[action]
#             # drop index action
#             print("drop index")
#             print(index_to_drop)
#             driver.dropIndex(index_to_drop)
#         time_end = time.time()
#         idx_build_time += (time_end - time_start)
#
#         for parameter_change_sql in parameter_opt_sql:
#             print(parameter_change_sql)
#             driver.setSystemParameter(parameter_change_sql)
#
#         run_time = driver.runQueriesWithoutTimeout()
#         previous_set = set(current_best_indices)
#         cache_performance[current_best_indices_frozen] = run_time
#     else:
#         run_time = cache_performance[current_best_indices_frozen]
#     print("current_best_indices:", current_best_indices)
#     print("runtime:", run_time)
#     t1 += 1

config1 = ["set random_page_cost = 100;",
           "set random_page_cost = 1000;",
           "set random_page_cost = 10000;",
           "set random_page_cost = 100000;",
           ]

config2 = [
    "set seq_page_cost = 0;",
    "set seq_page_cost = 10;",
    "set seq_page_cost = 100;",
    "set seq_page_cost = 1000;",
]

config3 = [
    "set max_parallel_workers_per_gather = 2;",
    "set max_parallel_workers_per_gather = 0;",
    "set max_parallel_workers_per_gather = 10;",
    "set max_parallel_workers_per_gather = 100;",
    "set max_parallel_workers_per_gather = 1000;",
]

config4 = [
    "set force_parallel_mode = on;",
    "set force_parallel_mode = off;",
]

parameter_other_sqls = [
    "set enable_bitmapscan = on;",
    "set enable_mergejoin = on;",
    "set temp_buffers = 102400;",
    "set enable_hashagg = on;",
    "set enable_indexscan = on;",
    "set force_parallel_mode = on;",
    "set enable_seqscan = on;",
    "set enable_tidscan = on;",
    "set enable_nestloop = on;"
]

for parameter_other_sql in parameter_other_sqls:
    driver.setSystemParameter(parameter_other_sql)

import itertools
for (a, b, c, d) in itertools.product(config1, config2, config3, config4):
    driver.setSystemParameter(a)
    driver.setSystemParameter(b)
    driver.setSystemParameter(c)
    driver.setSystemParameter(d)

    run_time = driver.runQueriesWithoutTimeout()
    print(a)
    print(b)
    print(c)
    print(d)
    print("runtime:", run_time)
    print("========")


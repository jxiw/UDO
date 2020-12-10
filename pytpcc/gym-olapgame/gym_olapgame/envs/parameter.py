# should define different incremental strategy
# candidate_dbms_parameter = [
#     # [
#     #     "set global innodb_buffer_pool_size =  53687091200;",
#     #     "set global innodb_buffer_pool_size =  75161927680;",
#     #     "set global innodb_buffer_pool_size = 112742891520;",
#     #     "set global innodb_buffer_pool_size = 343597383680;",
#     #     "set global innodb_buffer_pool_size = 687194767360;"
#     # ],
#     [
#         "set max_heap_table_size = 16777216;",
#         "set max_heap_table_size = 3221225472;",
#         "set max_heap_table_size = 53687091200;",
#         "set max_heap_table_size = 75161927680; "
#     ], [
#         "set transaction_prealloc_size = 4096;",
#         "set transaction_prealloc_size = 20480;",
#         "set transaction_prealloc_size = 40960;",
#         "set transaction_prealloc_size = 81920;"
#     ], [
#         "set transaction_alloc_block_size = 8192; ",
#         "set transaction_alloc_block_size = 20480; ",
#         "set transaction_alloc_block_size = 40960; ",
#         "set transaction_alloc_block_size = 81920; "
#     ], [
#         "set GLOBAL table_open_cache = 2000;",
#         "set GLOBAL table_open_cache = 8000;",
#         "set GLOBAL table_open_cache = 20000;",
#         "set GLOBAL table_open_cache = 40000;"
#     ], [
#         "set global binlog_cache_size = 32768;",
#         "set global binlog_cache_size = 65536;",
#         "set global binlog_cache_size = 131072;",
#         "set global binlog_cache_size = 262144;"
#     ]
# ]

# notice the first one is the default value
candidate_dbms_parameter = [
    [
        "set random_page_cost = 4;",
        "set random_page_cost = 0;",
        "set random_page_cost = 100;",
        "set random_page_cost = 1000;",
        "set random_page_cost = 10000;",
        "set random_page_cost = 100000;",
    ], [
        "set seq_page_cost = 0;",
        "set seq_page_cost = 0;",
        "set seq_page_cost = 10;",
        "set seq_page_cost = 100;",
        "set seq_page_cost = 1000;",
        "set seq_page_cost = 10000;",
    ], [
        "set enable_bitmapscan = on;",
        "set enable_bitmapscan = off;",
    ], [
        "set enable_mergejoin = on;",
        "set enable_mergejoin = off;",
    ], [
        "set force_parallel_mode = off;",
        "set force_parallel_mode = on;",
    ], [
        "set temp_buffers = 1024;",
        "set temp_buffers = 100;",
        "set temp_buffers = 1000;",
        "set temp_buffers = 10000;",
        "set temp_buffers = 100000;",
    ],
    # [
    #     "set shared_buffers = 1024;",
    #     "set shared_buffers = 100;",
    #     "set shared_buffers = 1000;",
    #     "set shared_buffers = 10000;",
    #     "set shared_buffers = 100000;",
    #     "set shared_buffers = 1000000;",
    # ], [
    #     "set wal_buffers = -1;",
    #     "set wal_buffers = 1024;",
    #     "set wal_buffers = 10000;",
    #     "set wal_buffers = 100000;",
    #     "set wal_buffers = 1000000;",
    # ],
    [
        "set enable_hashagg = on;",
        "set enable_hashagg = off;",
    ], [
        "set enable_indexscan = on;",
        "set enable_indexscan = off;",
    ], [
        "set force_parallel_mode = on;",
        "set force_parallel_mode = off;",
    ], [
        "set enable_seqscan = on;",
        "set enable_seqscan = off;",
    ], [
        "set max_parallel_workers_per_gather = 2;",
        "set max_parallel_workers_per_gather = 0;",
        "set max_parallel_workers_per_gather = 10;",
        "set max_parallel_workers_per_gather = 100;",
        "set max_parallel_workers_per_gather = 1000;",
    ], [
        "set enable_tidscan = on;",
        "set enable_tidscan = off;",
    ], [
        "SET enable_nestloop = on;",
        "SET enable_nestloop = false;",
    ]
]

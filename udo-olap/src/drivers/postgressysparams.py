# notice the first one is the default value
pg_candidate_dbms_parameter = [
    [
        "set random_page_cost = 4;",
        "set random_page_cost = 0;",
        "set random_page_cost = 100;",
        "set random_page_cost = 1000;",
        "set random_page_cost = 10000;",
        "set random_page_cost = 100000;",
    ], [
        "set seq_page_cost = 1;",
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
    ],
    [
        "set force_parallel_mode = off;",
        "set force_parallel_mode = on;",
    ],
    [
        "set temp_buffers = 1024;",
        "set temp_buffers = 100;",
        "set temp_buffers = 1000;",
        "set temp_buffers = 10000;",
        "set temp_buffers = 100000;",
    ],
    [
        "set enable_hashagg = on;",
        "set enable_hashagg = off;",
    ], [
        "set enable_indexscan = on;",
        "set enable_indexscan = off;",
    ],
    [
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
        "SET enable_nestloop = off;",
    ]
    # ,
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
]

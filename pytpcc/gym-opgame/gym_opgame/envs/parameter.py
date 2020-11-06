# should define different incremental strategy
candidate_dbms_parameter = [
    # [
    #     "set global innodb_buffer_pool_size =  53687091200;",
    #     "set global innodb_buffer_pool_size =  75161927680;",
    #     "set global innodb_buffer_pool_size = 112742891520;",
    #     "set global innodb_buffer_pool_size = 343597383680;",
    #     "set global innodb_buffer_pool_size = 687194767360;"
    # ],
    [
        "set max_heap_table_size = 10737418240;",
        "set max_heap_table_size = 32212254720;",
        "set max_heap_table_size = 53687091200;",
        "set max_heap_table_size = 75161927680; "
    ], [
        "set transaction_prealloc_size = 8192;",
        "set transaction_prealloc_size = 20480;",
        "set transaction_prealloc_size = 40960;",
        "set transaction_prealloc_size = 81920;"
    ], [
        "set transaction_alloc_block_size = 8192; ",
        "set transaction_alloc_block_size = 20480; ",
        "set transaction_alloc_block_size = 40960; ",
        "set transaction_alloc_block_size = 81920; "
    ], [
        "set GLOBAL table_open_cache = 7000;",
        "set GLOBAL table_open_cache = 10000;",
        "set GLOBAL table_open_cache = 20000;",
        "set GLOBAL table_open_cache = 40000;"
    ], [
        "set global binlog_cache_size = 32768;",
        "set global binlog_cache_size = 65536;",
        "set global binlog_cache_size = 131072;",
        "set global binlog_cache_size = 262144;"
    ]
]
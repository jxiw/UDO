# candidate_indices_creation = [
#     # lineitem
#     "CREATE INDEX IDX_LINEITEM_a ON LINEITEM (L_SHIPDATE, L_DISCOUNT, L_QUANTITY) USING BTREE;",
#     "CREATE INDEX IDX_LINEITEM_b ON LINEITEM (L_SHIPDATE, L_DISCOUNT) USING BTREE;",
#     "CREATE INDEX IDX_LINEITEM_c ON LINEITEM (L_SHIPDATE, L_QUANTITY) USING BTREE;",
#     "CREATE INDEX IDX_LINEITEM_d ON LINEITEM (L_SHIPDATE) USING BTREE;",
#     "CREATE INDEX IDX_LINEITEM_e ON LINEITEM (L_DISCOUNT) USING BTREE;",
#     "CREATE INDEX IDX_LINEITEM_f ON LINEITEM (L_QUANTITY) USING BTREE;",
#     "CREATE INDEX IDX_LINEITEM_g ON LINEITEM (L_ORDERKEY, L_SUPPKEY) USING BTREE;",
#     "CREATE INDEX IDX_LINEITEM_h ON LINEITEM (L_RECEIPTDATE) USING BTREE;",
#     "CREATE INDEX IDX_LINEITEM_i ON LINEITEM (L_COMMITDATE) USING BTREE;",
#     "CREATE INDEX IDX_LINEITEM_j ON LINEITEM (L_SHIPMODE) USING BTREE;",
#     "CREATE INDEX IDX_LINEITEM_k ON LINEITEM (L_SHIPINSTRUCT) USING BTREE;",
#     # partsupp
#     "CREATE INDEX IDX_PARTSUPP_a ON PARTSUPP (PS_PARTKEY, PS_SUPPKEY, PS_SUPPLYCOST) USING BTREE;",
#     "CREATE INDEX IDX_PARTSUPP_b ON PARTSUPP (PS_SUPPLYCOST) USING BTREE;",
#     # part
#     "CREATE INDEX IDX_PART_a ON PART (P_SIZE) USING BTREE;",
#     "CREATE INDEX IDX_PART_b ON PART (P_TYPE) USING BTREE;",
#     "CREATE INDEX IDX_PART_c ON PART (P_SIZE, P_TYPE) USING BTREE;",
#     "CREATE INDEX IDX_PART_d ON PART (P_CONTAINER, P_BRAND, P_SIZE) USING BTREE;",
#     # order
#     "CREATE INDEX IDX_ORDERS_a ON ORDERS (O_ORDERDATE) USING BTREE;",
#     "CREATE INDEX IDX_ORDERS_b ON ORDERS (O_ORDERSTATUS) USING BTREE;",
#     # customer
#     # "CREATE INDEX IDX_CUSTOMER_a ON CUSTOMER (C_NATIONKEY, C_CUSTKEY) USING BTREE;"
# ]
#
# candidate_indices_drop = [
#     # lineitem
#     "ALTER TABLE LINEITEM drop index IDX_LINEITEM_a;",
#     "ALTER TABLE LINEITEM drop index IDX_LINEITEM_b;",
#     "ALTER TABLE LINEITEM drop index IDX_LINEITEM_c;",
#     "ALTER TABLE LINEITEM drop index IDX_LINEITEM_d;",
#     "ALTER TABLE LINEITEM drop index IDX_LINEITEM_e;",
#     "ALTER TABLE LINEITEM drop index IDX_LINEITEM_f;",
#     "ALTER TABLE LINEITEM drop index IDX_LINEITEM_g;",
#     "ALTER TABLE LINEITEM drop index IDX_LINEITEM_h;",
#     "ALTER TABLE LINEITEM drop index IDX_LINEITEM_i;",
#     "ALTER TABLE LINEITEM drop index IDX_LINEITEM_j;",
#     "ALTER TABLE LINEITEM drop index IDX_LINEITEM_k;",
#     # parsupp
#     "ALTER TABLE PARTSUPP drop index IDX_PARTSUPP_a;",
#     "ALTER TABLE PARTSUPP drop index IDX_PARTSUPP_b;",
#     # part
#     "ALTER TABLE PART drop index IDX_PART_a;",
#     "ALTER TABLE PART drop index IDX_PART_b;",
#     "ALTER TABLE PART drop index IDX_PART_c;",
#     "ALTER TABLE PART drop index IDX_PART_d;",
#     # order
#     "ALTER TABLE ORDERS drop index IDX_ORDERS_a;",
#     "ALTER TABLE ORDERS drop index IDX_ORDERS_b;",
#     # customer
#     # "ALTER TABLE CUSTOMER drop index IDX_CUSTOMER_a;"
# ]


candidate_indices = [
    # lineitem
    ("IDX_LINEITEM_a", "LINEITEM", "L_SHIPDATE, L_DISCOUNT, L_QUANTITY"),
    ("IDX_LINEITEM_b", "LINEITEM", "L_SHIPDATE, L_DISCOUNT"),
    ("IDX_LINEITEM_c", "LINEITEM", "L_SHIPDATE, L_QUANTITY"),
    ("IDX_LINEITEM_d", "LINEITEM", "L_SHIPDATE"),
    ("IDX_LINEITEM_e", "LINEITEM", "L_DISCOUNT"),
    ("IDX_LINEITEM_f", "LINEITEM", "L_ORDERKEY"), # rank 1
    ("IDX_LINEITEM_g", "LINEITEM", "L_PARTKEY, L_SUPPKEY"),
    ("IDX_LINEITEM_h", "LINEITEM", "L_QUANTITY"),
    ("IDX_LINEITEM_i", "LINEITEM", "L_ORDERKEY, L_SUPPKEY"),
    ("IDX_LINEITEM_j", "LINEITEM", "L_RECEIPTDATE"),
    ("IDX_LINEITEM_k", "LINEITEM", "L_COMMITDATE"),
    ("IDX_LINEITEM_l", "LINEITEM", "L_SHIPMODE"),
    ("IDX_LINEITEM_m", "LINEITEM", "L_SHIPINSTRUCT"),
    ("IDX_LINEITEM_n", "LINEITEM", "L_TAX"),
    ("IDX_LINEITEM_o", "LINEITEM", "L_SHIPDATE, L_RETURNFLAG, L_LINESTATUS"),
    ("IDX_LINEITEM_p", "LINEITEM", "L_SHIPDATE"),
    ("IDX_LINEITEM_q", "LINEITEM", "L_RETURNFLAG"),
    ("IDX_LINEITEM_r", "LINEITEM", "L_LINESTATUS"),
    ("IDX_LINEITEM_s", "LINEITEM", "L_PARTKEY"),
    ("IDX_LINEITEM_t", "LINEITEM", "L_SHIPMODE, L_PARTKEY"),
    # partsupp
    ("IDX_PARTSUPP_a", "PARTSUPP", "PS_PARTKEY, PS_SUPPKEY, PS_SUPPLYCOST"),
    ("IDX_PARTSUPP_b", "PARTSUPP", "PS_SUPPLYCOST"),
    ("IDX_PARTSUPP_c", "PARTSUPP", "PS_SUPPKEY"),
    ("IDX_PARTSUPP_d", "PARTSUPP", "PS_PARTKEY"),
    ("IDX_PARTSUPP_e", "PARTSUPP", "PS_PARTKEY, PS_SUPPKEY"),
    ("IDX_PARTSUPP_f", "PARTSUPP", "PS_AVAILQTY"),
    # supplier
    ("IDX_SUPPLIER_a", "SUPPLIER", "S_NATIONKEY"),
    # part
    ("IDX_PART_a", "PART", "P_SIZE"),
    ("IDX_PART_b", "PART", "P_TYPE"),
    ("IDX_PART_c", "PART", "P_SIZE, P_TYPE"),
    ("IDX_PART_d", "PART", "P_CONTAINER, P_BRAND, P_SIZE"),
    ("IDX_PART_e", "PART", "P_PARTKEY"),
    ("IDX_PART_f", "PART", "P_CONTAINER"),
    ("IDX_PART_g", "PART", "P_BRAND"),
    ("IDX_PART_h", "PART", "P_NAME"),
    ("IDX_PART_i", "PART", "P_MFGR"),
    ("IDX_PART_j", "PART", "P_RETAILPRICE"),
    # order
    ("IDX_ORDERS_a", "ORDERS", "O_ORDERDATE"),
    ("IDX_ORDERS_b", "ORDERS", "O_ORDERSTATUS"),
    ("IDX_ORDERS_c", "ORDERS", "O_CUSTKEY"),
    ("IDX_ORDERS_d", "ORDERS", "O_SHIPPRIORITY"),
    ("IDX_ORDERS_e", "ORDERS", "O_ORDERKEY, O_SHIPPRIORITY, O_ORDERDATE"),
    ("IDX_ORDERS_f", "ORDERS", "O_ORDERPRIORITY"),
    ("IDX_ORDERS_g", "ORDERS", "O_CLERK"),
    ("IDX_ORDERS_h", "ORDERS", "O_CUSTKEY, O_ORDERKEY"),
    ("IDX_ORDERS_i", "ORDERS", "O_CUSTKEY, O_ORDERKEY, O_SHIPPRIORITY"),
    ("IDX_ORDERS_j", "ORDERS", "O_CUSTKEY, O_ORDERKEY, O_ORDERDATE"),
    ("IDX_ORDERS_k", "ORDERS", "O_CUSTKEY, O_ORDERKEY, O_ORDERSTATUS"),
    # region
    # ("IDX_REGION_a", "REGION", "R_REGIONKEY"),
    ("IDX_REGION_b", "REGION", "R_NAME"),
    # nation
    # ("IDX_NATION_a", "NATION", "N_NATIONKEY"),
    ("IDX_NATION_b", "NATION", "N_REGIONKEY"),
    ("IDX_NATION_c", "NATION", "N_NAME"),
    ("IDX_NATION_d", "NATION", "N_NATIONKEY, N_REGIONKEY"),
    # customer
    ("IDX_CUSTOMER_a", "CUSTOMER", "C_NATIONKEY"),
    ("IDX_CUSTOMER_b", "CUSTOMER", "C_CUSTKEY"),
    ("IDX_CUSTOMER_c", "CUSTOMER", "C_MKTSEGMENT"),
    ("IDX_CUSTOMER_d", "CUSTOMER", "C_NATIONKEY, C_CUSTKEY"),
    ("IDX_CUSTOMER_e", "CUSTOMER", "C_ACCTBAL"),
    ("IDX_CUSTOMER_f", "CUSTOMER", "C_PHONE"),
    ("IDX_CUSTOMER_g", "CUSTOMER", "C_CUSTKEY, C_ACCTBAL, C_PHONE"),
    ("IDX_CUSTOMER_h", "CUSTOMER", "C_NAME"),
    ("IDX_CUSTOMER_i", "CUSTOMER", "C_CUSTKEY, C_NATIONKEY, C_NAME"),
    ("IDX_CUSTOMER_j", "CUSTOMER", "C_CUSTKEY, C_NATIONKEY, C_PHONE"),
    ("IDX_CUSTOMER_k", "CUSTOMER", "C_CUSTKEY, C_NATIONKEY, C_ACCTBAL"),
    ("IDX_CUSTOMER_l", "CUSTOMER", "C_CUSTKEY, C_NATIONKEY, C_MKTSEGMENT"),
    ("IDX_CUSTOMER_m", "CUSTOMER", "C_CUSTKEY, C_NATIONKEY, C_ACCTBAL, C_PHONE"),
    ("IDX_CUSTOMER_n", "CUSTOMER", "C_CUSTKEY, C_NATIONKEY, C_ACCTBAL, C_MKTSEGMENT"),
]

import constants
queries = constants.QUERIES
cardinality = constants.cardinality_info
for i in range(len(candidate_indices)):
    contain_query = []
    for query_id, query_str in queries.items():
        # print(candidate_indices[i][2])
        if "where" in query_str:
            where_clause = query_str[query_str.index("where"):]
        else:
            where_clause = query_str
        contain_columns = candidate_indices[i][2].lower().split(",")
        if all(contain_column in where_clause for contain_column in contain_columns):
            contain_query.append(query_id)
    index_cardinality = cardinality[candidate_indices[i][1]]
    candidate_indices[i] += (contain_query, index_cardinality, )

# print(candidate_indices)


# def print_create_info():
#     index_creation_format = "CREATE INDEX %s ON %s (%s);"
#     for index_to_create in candidate_indices:
#         print(index_creation_format%(index_to_create[0], index_to_create[1], index_to_create[2]))
#
# def print_drop_info():
#     index_drop_format = "drop index %s;"
#     for index_to_drop in candidate_indices:
#         print(index_drop_format%(index_to_drop[0]))
#
# print_create_info()
# print_drop_info()

#
# index = set()
# for i in candidate_indices:
#     key = i[0]
#     if key in index:
#         print("error")
#     else:
#         index.add(key)
# print(index)
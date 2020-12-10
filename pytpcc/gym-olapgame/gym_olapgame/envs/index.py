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


# candidate_indices = [
#     # lineitem
#     ("IDX_LINEITEM_a", "LINEITEM", "L_SHIPDATE, L_DISCOUNT, L_QUANTITY"),
#     ("IDX_LINEITEM_b", "LINEITEM", "L_SHIPDATE, L_DISCOUNT"),
#     ("IDX_LINEITEM_c", "LINEITEM", "L_SHIPDATE, L_QUANTITY"),
#     ("IDX_LINEITEM_d", "LINEITEM", "L_SHIPDATE"),
#     ("IDX_LINEITEM_e", "LINEITEM", "L_DISCOUNT"),
#     ("IDX_LINEITEM_f", "LINEITEM", "L_ORDERKEY"), # rank 1
#     ("IDX_LINEITEM_g", "LINEITEM", "L_PARTKEY, L_SUPPKEY"),
#     ("IDX_LINEITEM_h", "LINEITEM", "L_QUANTITY"),
#     ("IDX_LINEITEM_i", "LINEITEM", "L_ORDERKEY, L_SUPPKEY"),
#     ("IDX_LINEITEM_j", "LINEITEM", "L_RECEIPTDATE"),
#     ("IDX_LINEITEM_k", "LINEITEM", "L_COMMITDATE"),
#     ("IDX_LINEITEM_l", "LINEITEM", "L_SHIPMODE"),
#     ("IDX_LINEITEM_m", "LINEITEM", "L_SHIPINSTRUCT"),
#     ("IDX_LINEITEM_n", "LINEITEM", "L_TAX"),
#     ("IDX_LINEITEM_o", "LINEITEM", "L_SHIPDATE, L_RETURNFLAG, L_LINESTATUS"),
#     ("IDX_LINEITEM_p", "LINEITEM", "L_SHIPDATE"),
#     ("IDX_LINEITEM_q", "LINEITEM", "L_RETURNFLAG"),
#     ("IDX_LINEITEM_r", "LINEITEM", "L_LINESTATUS"),
#     ("IDX_LINEITEM_s", "LINEITEM", "L_PARTKEY"),
#     ("IDX_LINEITEM_t", "LINEITEM", "L_SHIPMODE, L_PARTKEY"),
#     # partsupp
#     ("IDX_PARTSUPP_a", "PARTSUPP", "PS_PARTKEY, PS_SUPPKEY, PS_SUPPLYCOST"),
#     ("IDX_PARTSUPP_b", "PARTSUPP", "PS_SUPPLYCOST"),
#     ("IDX_PARTSUPP_c", "PARTSUPP", "PS_SUPPKEY"),
#     ("IDX_PARTSUPP_d", "PARTSUPP", "PS_PARTKEY"),
#     ("IDX_PARTSUPP_e", "PARTSUPP", "PS_PARTKEY, PS_SUPPKEY"),
#     ("IDX_PARTSUPP_f", "PARTSUPP", "PS_AVAILQTY"),
#     # supplier
#     ("IDX_SUPPLIER_a", "SUPPLIER", "S_NATIONKEY"),
#     # part
#     ("IDX_PART_a", "PART", "P_SIZE"),
#     ("IDX_PART_b", "PART", "P_TYPE"),
#     ("IDX_PART_c", "PART", "P_SIZE, P_TYPE"),
#     ("IDX_PART_d", "PART", "P_CONTAINER, P_BRAND, P_SIZE"),
#     ("IDX_PART_e", "PART", "P_PARTKEY"),
#     ("IDX_PART_f", "PART", "P_CONTAINER"),
#     ("IDX_PART_g", "PART", "P_BRAND"),
#     ("IDX_PART_h", "PART", "P_NAME"),
#     ("IDX_PART_i", "PART", "P_MFGR"),
#     ("IDX_PART_j", "PART", "P_RETAILPRICE"),
#     # order
#     ("IDX_ORDERS_a", "ORDERS", "O_ORDERDATE"),
#     ("IDX_ORDERS_b", "ORDERS", "O_ORDERSTATUS"),
#     ("IDX_ORDERS_c", "ORDERS", "O_CUSTKEY"),
#     ("IDX_ORDERS_d", "ORDERS", "O_SHIPPRIORITY"),
#     ("IDX_ORDERS_e", "ORDERS", "O_ORDERKEY, O_SHIPPRIORITY, O_ORDERDATE"),
#     ("IDX_ORDERS_f", "ORDERS", "O_ORDERPRIORITY"),
#     ("IDX_ORDERS_g", "ORDERS", "O_CLERK"),
#     ("IDX_ORDERS_h", "ORDERS", "O_CUSTKEY, O_ORDERKEY"),
#     ("IDX_ORDERS_i", "ORDERS", "O_CUSTKEY, O_ORDERKEY, O_SHIPPRIORITY"),
#     ("IDX_ORDERS_j", "ORDERS", "O_CUSTKEY, O_ORDERKEY, O_ORDERDATE"),
#     ("IDX_ORDERS_k", "ORDERS", "O_CUSTKEY, O_ORDERKEY, O_ORDERSTATUS"),
#     # region
#     # ("IDX_REGION_a", "REGION", "R_REGIONKEY"),
#     ("IDX_REGION_b", "REGION", "R_NAME"),
#     # nation
#     # ("IDX_NATION_a", "NATION", "N_NATIONKEY"),
#     ("IDX_NATION_b", "NATION", "N_REGIONKEY"),
#     ("IDX_NATION_c", "NATION", "N_NAME"),
#     ("IDX_NATION_d", "NATION", "N_NATIONKEY, N_REGIONKEY"),
#     # customer
#     ("IDX_CUSTOMER_a", "CUSTOMER", "C_NATIONKEY"),
#     ("IDX_CUSTOMER_b", "CUSTOMER", "C_CUSTKEY"),
#     ("IDX_CUSTOMER_c", "CUSTOMER", "C_MKTSEGMENT"),
#     ("IDX_CUSTOMER_d", "CUSTOMER", "C_NATIONKEY, C_CUSTKEY"),
#     ("IDX_CUSTOMER_e", "CUSTOMER", "C_ACCTBAL"),
#     ("IDX_CUSTOMER_f", "CUSTOMER", "C_PHONE"),
#     ("IDX_CUSTOMER_g", "CUSTOMER", "C_CUSTKEY, C_ACCTBAL, C_PHONE"),
#     ("IDX_CUSTOMER_h", "CUSTOMER", "C_NAME"),
#     ("IDX_CUSTOMER_i", "CUSTOMER", "C_CUSTKEY, C_NATIONKEY, C_NAME"),
#     ("IDX_CUSTOMER_j", "CUSTOMER", "C_CUSTKEY, C_NATIONKEY, C_PHONE"),
#     ("IDX_CUSTOMER_k", "CUSTOMER", "C_CUSTKEY, C_NATIONKEY, C_ACCTBAL"),
#     ("IDX_CUSTOMER_l", "CUSTOMER", "C_CUSTKEY, C_NATIONKEY, C_MKTSEGMENT"),
#     ("IDX_CUSTOMER_m", "CUSTOMER", "C_CUSTKEY, C_NATIONKEY, C_ACCTBAL, C_PHONE"),
#     ("IDX_CUSTOMER_n", "CUSTOMER", "C_CUSTKEY, C_NATIONKEY, C_ACCTBAL, C_MKTSEGMENT"),
# ]

#candidate indices for imdb
candidate_indices=[
    ('IDX_company_type_0','company_type','id'),
    ('IDX_company_type_1','company_type','kind'),
    ('IDX_company_type_2','company_type','id,kind'),
    ('IDX_info_type_0','info_type','id'),
    ('IDX_movie_companies_0','movie_companies','movie_id'),
    ('IDX_movie_companies_1','movie_companies','company_type_id'),
    ('IDX_movie_companies_3','movie_companies','company_id'),
    ('IDX_movie_companies_4','movie_companies','movie_id,company_type_id'),
    ('IDX_movie_companies_6','movie_companies','movie_id,company_id'),
    ('IDX_movie_companies_8','movie_companies','company_type_id,company_id'),
    ('IDX_movie_companies_11','movie_companies','movie_id,company_type_id,company_id'),
    ('IDX_movie_info_idx_0','movie_info_idx','movie_id'),
    ('IDX_movie_info_idx_1','movie_info_idx','info_type_id'),
    ('IDX_movie_info_idx_3','movie_info_idx','movie_id,info_type_id'),
    ('IDX_title_0','title','id'),
    ('IDX_title_1','title','production_year'),
    ('IDX_title_2','title','title'),
    ('IDX_title_3','title','kind_id'),
    ('IDX_title_4','title','episode_nr'),
    ('IDX_title_5','title','id,production_year'),
    ('IDX_title_6','title','id,title'),
    ('IDX_title_7','title','id,kind_id'),
    ('IDX_title_8','title','id,episode_nr'),
    ('IDX_title_9','title','production_year,title'),
    ('IDX_title_10','title','production_year,kind_id'),
    ('IDX_title_11','title','production_year,episode_nr'),
    ('IDX_title_12','title','title,kind_id'),
    ('IDX_title_13','title','title,episode_nr'),
    ('IDX_title_14','title','kind_id,episode_nr'),
    ('IDX_title_15','title','id,production_year,title'),
    ('IDX_title_16','title','id,production_year,kind_id'),
    ('IDX_title_17','title','id,production_year,episode_nr'),
    ('IDX_title_18','title','id,title,kind_id'),
    ('IDX_title_19','title','id,title,episode_nr'),
    ('IDX_title_20','title','id,kind_id,episode_nr'),
    ('IDX_title_21','title','production_year,title,kind_id'),
    ('IDX_title_22','title','production_year,title,episode_nr'),
    ('IDX_title_23','title','production_year,kind_id,episode_nr'),
    ('IDX_title_24','title','title,kind_id,episode_nr'),
    ('IDX_title_25','title','id,production_year,title,kind_id'),
    ('IDX_title_26','title','id,production_year,title,episode_nr'),
    ('IDX_title_27','title','id,production_year,kind_id,episode_nr'),
    ('IDX_title_28','title','id,title,kind_id,episode_nr'),
    ('IDX_title_29','title','production_year,title,kind_id,episode_nr'),
    ('IDX_title_30','title','id,production_year,title,kind_id,episode_nr'),
    ('IDX_company_name_0','company_name','id'),
    ('IDX_company_name_1','company_name','country_code'),
    ('IDX_company_name_2','company_name','name'),
    ('IDX_company_name_3','company_name','id,country_code'),
    ('IDX_company_name_4','company_name','id,name'),
    ('IDX_company_name_5','company_name','country_code,name'),
    ('IDX_company_name_6','company_name','id,country_code,name'),
    ('IDX_keyword_0','keyword','id'),
    ('IDX_keyword_1','keyword','keyword'),
    ('IDX_keyword_2','keyword','id,keyword'),
    ('IDX_movie_keyword_0','movie_keyword','movie_id'),
    ('IDX_movie_keyword_1','movie_keyword','keyword_id'),
    ('IDX_movie_keyword_2','movie_keyword','movie_id,keyword_id'),
    ('IDX_movie_info_0','movie_info','movie_id'),
    ('IDX_movie_info_2','movie_info','info_type_id'),
    ('IDX_movie_info_5','movie_info','movie_id,info_type_id'),
    ('IDX_cast_info_0','cast_info','person_id'),
    ('IDX_cast_info_1','cast_info','movie_id'),
    ('IDX_cast_info_3','cast_info','role_id'),
    ('IDX_cast_info_4','cast_info','person_role_id'),
    ('IDX_cast_info_5','cast_info','person_id,movie_id'),
    ('IDX_cast_info_7','cast_info','person_id,role_id'),
    ('IDX_cast_info_8','cast_info','person_id,person_role_id'),
    ('IDX_cast_info_10','cast_info','movie_id,role_id'),
    ('IDX_cast_info_11','cast_info','movie_id,person_role_id'),
    ('IDX_cast_info_14','cast_info','role_id,person_role_id'),
    ('IDX_cast_info_16','cast_info','person_id,movie_id,role_id'),
    ('IDX_cast_info_17','cast_info','person_id,movie_id,person_role_id'),
    ('IDX_cast_info_20','cast_info','person_id,role_id,person_role_id'),
    ('IDX_cast_info_23','cast_info','movie_id,role_id,person_role_id'),
    ('IDX_name_0','name','id'),
    ('IDX_name_1','name','name'),
    ('IDX_name_2','name','gender'),
    ('IDX_name_3','name','name_pcode_cf'),
    ('IDX_name_4','name','id,name'),
    ('IDX_name_5','name','id,gender'),
    ('IDX_name_6','name','id,name_pcode_cf'),
    ('IDX_name_7','name','name,gender'),
    ('IDX_name_8','name','name,name_pcode_cf'),
    ('IDX_name_9','name','gender,name_pcode_cf'),
    ('IDX_name_10','name','id,name,gender'),
    ('IDX_name_11','name','id,name,name_pcode_cf'),
    ('IDX_name_12','name','id,gender,name_pcode_cf'),
    ('IDX_name_13','name','name,gender,name_pcode_cf'),
    ('IDX_name_14','name','id,name,gender,name_pcode_cf'),
    ('IDX_aka_name_0','aka_name','person_id'),
    ('IDX_aka_name_1','aka_name','name'),
    ('IDX_aka_name_2','aka_name','person_id,name'),
    ('IDX_link_type_0','link_type','id'),
    ('IDX_link_type_1','link_type','link'),
    ('IDX_link_type_2','link_type','id,link'),
    ('IDX_movie_link_0','movie_link','linked_movie_id'),
    ('IDX_movie_link_1','movie_link','link_type_id'),
    ('IDX_movie_link_2','movie_link','movie_id'),
    ('IDX_movie_link_3','movie_link','linked_movie_id,link_type_id'),
    ('IDX_movie_link_4','movie_link','linked_movie_id,movie_id'),
    ('IDX_movie_link_5','movie_link','link_type_id,movie_id'),
    ('IDX_movie_link_6','movie_link','linked_movie_id,link_type_id,movie_id'),
    ('IDX_person_info_0','person_info','person_id'),
    ('IDX_person_info_1','person_info','info_type_id'),
    ('IDX_person_info_4','person_info','person_id,info_type_id'),
    ('IDX_role_type_0','role_type','id'),
    ('IDX_role_type_1','role_type','role'),
    ('IDX_role_type_2','role_type','id,role'),
    ('IDX_char_name_0','char_name','id'),
    ('IDX_char_name_1','char_name','name'),
    ('IDX_char_name_2','char_name','id,name'),
    ('IDX_kind_type_0','kind_type','id'),
    ('IDX_kind_type_1','kind_type','kind'),
    ('IDX_kind_type_2','kind_type','id,kind'),
    ('IDX_aka_title_0','aka_title','movie_id'),
    ('IDX_comp_cast_type_0','comp_cast_type','id'),
    ('IDX_comp_cast_type_1','comp_cast_type','kind'),
    ('IDX_comp_cast_type_2','comp_cast_type','id,kind'),
    ('IDX_complete_cast_0','complete_cast','movie_id'),
    ('IDX_complete_cast_1','complete_cast','subject_id'),
    ('IDX_complete_cast_2','complete_cast','status_id'),
    ('IDX_complete_cast_3','complete_cast','movie_id,subject_id'),
    ('IDX_complete_cast_4','complete_cast','movie_id,status_id'),
    ('IDX_complete_cast_5','complete_cast','subject_id,status_id'),
    ('IDX_complete_cast_6','complete_cast','movie_id,subject_id,status_id'),
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


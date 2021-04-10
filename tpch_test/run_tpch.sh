python3 ../src/run.py -system postgres -db tpch -username postgres -queries tpch_queries -indices tpch_index.txt -sys_params postgressysparams.json -duration 5 -agent ddpg -horizon 8 > ddpg_latest.log
psql -U postgres -d tpch -f tpch_drop_index.sql
python3 ../src/run.py -system postgres -db tpch -username postgres -queries tpch_queries -indices tpch_index.txt -duration 5 -sys_params postgressysparams.json -agent sarsa -horizon 8 > sarsa_latest.log
psql -U postgres -d tpch -f tpch_drop_index.sql
python3 ../src/run.py -system postgres -db tpch -username postgres -queries tpch_queries -indices tpch_index.txt -sys_params postgressysparams.json -duration 5 -agent udo -horizon 8 -heavy_horizon 3 -rl_max_delay_time 4 > udo_latest.log
psql -U postgres -d tpch -f tpch_drop_index.sql
python3 ../src/run.py -system postgres -db tpch -username postgres -queries tpch_queries -indices tpch_index.txt -duration 5 -sys_params postgressysparams.json -agent udo-s -horizon 8 > udo-s_latest.log
psql -U postgres -d tpch -f tpch_drop_index.sql

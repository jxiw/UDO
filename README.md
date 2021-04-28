# UDO Quickstart

## Install from github

1. Download UDO package from UDO repository.

    ```
    git clone git@github.com:OVSS/UDO.git
    ```

2. Install the mandatory DBMS packages. `bash ./install.sh`

3. Install the required packages `python3 -m pip install -r requirements.txt`

3. Install UDO Gym environment

    ```
    cd UDO/udo-optimization/
    python3 -m pip install -e .
    ```

4. Optional, using the UDO tool to extract indexes. The output format should be `index name;table;columns`, which is the index format required by UDO.

    ```
    usage: extract_index.py [-h] [-db_schema DB_SCHEMA] [-queries QUERIES]
    
    UDO index candidate generator.
    
    optional arguments:
      -h, --help            show this help message and exit
      -db_schema DB_SCHEMA  the database schmea to optimizes
      -queries QUERIES      queries
    ```

## Install from PIP

1. Install the mandatory DBMS packages. `bash ./install.sh` in case of Postgres or MySQL are not installed.

2. Use the `python3 -m pip install UDO-DB` to install package.

## TPC-H test

The TPC-H schema, dataset and queries are available in https://drive.google.com/drive/folders/123pwHaoz8C1dakvUef8AjKqci3_JNG47

## Running 

1. Optional, using the UDO tool to extract indexes. The output format should be `index name;table;columns`, which is the index format required by UDO.

    ```
    usage: extract_index.py [-h] [-db_schema DB_SCHEMA] [-queries QUERIES]
    
    UDO index candidate generator.
    
    optional arguments:
      -h, --help            show this help message and exit
      -db_schema DB_SCHEMA  the database schmea to optimizes
      -queries QUERIES      queries
    ```

2. ```echo "PATH=$PATH:/home/ubuntu/.local/bin" >> ~/.bashrc```

2. Run agents 

   ```
    usage: run.py [-h] [-system {mysql,postgres}] [-db DB] [-username USERNAME] [-password PASSWORD] [-queries QUERIES]
              [-indices INDICES] [-sys_params SYS_PARAMS] [-duration DURATION] [-agent {udo,udo-s,ddpg,sarsa}]
              [-horizon HORIZON] [-heavy_horizon HEAVY_HORIZON] [-rl_update {RAVE,MCTS}] [-rl_select {UCB1,UCBV}]
              [-rl_reward {delta,accumulate}] [-rl_delay {UCB,Exp3}] [-rl_max_delay_time RL_MAX_DELAY_TIME]
              [-sample_rate SAMPLE_RATE] [-default_query_time_out DEFAULT_QUERY_TIME_OUT] [-time_out_ratio TIME_OUT_RATIO]
              [--load_json LOAD_JSON]

    UDO optimizer.
    
    optional arguments:
      -h, --help            show this help message and exit
      -system {mysql,postgres}
                            Target system driver
      -db DB                the database to optimizes
      -username USERNAME    username
      -password PASSWORD    password
      -queries QUERIES      the input query file
      -indices INDICES      the input query file
      -sys_params SYS_PARAMS
                            the input system params json file
      -duration DURATION    time for tuning in hours
      -agent {udo,udo-s,ddpg,sarsa}
                            reinforcement learning agent
      -horizon HORIZON      the number horizon for reinforcement agent
      -heavy_horizon HEAVY_HORIZON
                            the number horizon for heavy parameters in UDO
      -rl_update {RAVE,MCTS}
                            the update policy of UDO tree search
      -rl_select {UCB1,UCBV}
                            the selection policy of UDO tree search
      -rl_reward {delta,accumulate}
                            the reward of reinforcement learning agent
      -rl_delay {UCB, Exp3}  the delay selection policy
      -rl_max_delay_time RL_MAX_DELAY_TIME
                            the delay selection policy
      -sample_rate SAMPLE_RATE
                            sampled rate from workload
      -default_query_time_out DEFAULT_QUERY_TIME_OUT
                            default timeout in seconds for each query
      -time_out_ratio TIME_OUT_RATIO
                            timeout ratio respect to default time
      --load_json LOAD_JSON
                            Load settings from file in json format. Command line options override values in file.
   ```

For example

for TPC-H with scaling factor 1

   ```
   python3 UDO/run.py -system postgres -db tpch_sf10 -username postgres -queries tpch_queries -indices tpch_index.txt -sys_params postgressysparams.json -duration 5 -agent udo -horizon 8 -heavy_horizon 3 -rl_max_delay_time 5 -default_query_time_out 6
   ```

for TPC-H with scaling factor 10

   ```
   python3 UDO/run.py -system postgres -db tpch_sf10 -username postgres -queries tpch_queries -indices tpch_index.txt -sys_params postgressysparams.json -duration 5 -agent udo -horizon 8 -heavy_horizon 3 -rl_max_delay_time 5 -default_query_time_out 18
   ```

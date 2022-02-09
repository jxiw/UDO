# UDO Quickstart

The following installation procedure was tested on Ubuntu 20.04 with Python 3. More precisely, we used a t3.medium EC2 instance and the "Ubuntu Server 20.04 LTS (HVM), SSD Volume Type" AMI.

## Installation from GitHub

1. Download UDO package from UDO repository and switch to UDO directory.

    ```
    git clone https://[username]@github.com/OVSS/UDO.git
    cd UDO
    ```

2. Install DBMS packages. `bash ./install.sh`

3. Install UDO packages.

    ```
    cd udo
    python3 -m pip install -r requirement.txt`
    ```

4. Install UDO Gym environment. 
    
    ```
    cd udo-optimization/
    python3 -m pip install -e .
    ```

## Installation via PIP

1. Install DBMS packages via `bash ./install.sh` if Postgres and MySQL are not installed.

2. Use `python3 -m pip install UDO-DB` to install packages.

## Prepare TPC-H Database

The TPC-H schema, dataset, and queries are available at https://drive.google.com/drive/folders/123pwHaoz8C1dakvUef8AjKqci3_JNG47. 

1. To download data from Google Drive, install gdown via `python3 -m pip install gdown`.

2. Download TPC-H .zip file using `/home/ubuntu/.local/bin/gdown https://drive.google.com/uc?id=1IgzHMOc75Km9h-FLMepV-t9lrQhWGTwt`.

3. Install unzip via `sudo apt install unzip` and use it to extract files via `unzip TPC-H.zip`

4. Create TPC-H database via `sudo -u postgres createdb tpch_sf10`.

5. Create TPC-H database schema via `sudo -u postgres psql tpch_sf10 < tpch_schema.sql`.

6. Load TPC-H data via `sudo -u postgres psql tpch_sf10 < tpch_sf10_data.sql`.

## Use UDO to Tune Postgres for TPC-H

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

3. Run agents after installing udo from pip

   ```
    usage: python3 -m udo [-h] [-system {mysql,postgres}] [-db DB] [-username USERNAME] [-password PASSWORD] [-queries QUERIES]
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
   python3 -m udo -system postgres -db tpch_sf1 -username postgres -queries tpch_queries -indices tpch_index.txt -sys_params postgressysparams.json -duration 5 -agent udo -horizon 8 -heavy_horizon 3 -rl_max_delay_time 5 -default_query_time_out 6
   ```

for TPC-H with scaling factor 10

   ```
   python3 -m udo -system postgres -db tpch_sf10 -username postgres -queries tpch_queries -indices tpch_index.txt -sys_params postgressysparams.json -duration 5 -agent udo -horizon 8 -heavy_horizon 3 -rl_max_delay_time 5 -default_query_time_out 18
   ```

# Citation

```
@article{wang2021udo,
  title={UDO: universal database optimization using reinforcement learning},
  author={Wang, Junxiong and Trummer, Immanuel and Basu, Debabrota},
  journal={Proceedings of the VLDB Endowment},
  volume={14},
  number={13},
  pages={3402--3414},
  year={2021},
  publisher={VLDB Endowment}
}

@inproceedings{wang2021demonstrating,
  title={Demonstrating UDO: A Unified Approach for Optimizing Transaction Code, Physical Design, and System Parameters via Reinforcement Learning},
  author={Wang, Junxiong and Trummer, Immanuel and Basu, Debabrota},
  booktitle={Proceedings of the 2021 International Conference on Management of Data},
  pages={2794--2797},
  year={2021}
}
```
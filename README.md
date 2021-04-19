# UDO
Step 1. Install packages `python3 -m pip install -r requirements.txt`


Step 2. Install udo environment

```
cd src/udo-optimization/
python3 -m pip install -e .
```

Step 3: optional, 

```
usage: extract_index.py [-h] [-db_schema DB_SCHEMA] [-queries QUERIES]

UDO index candidate generator.

optional arguments:
  -h, --help            show this help message and exit
  -db_schema DB_SCHEMA  the database schmea to optimizes
  -queries QUERIES      queries
```

Step 3. Run agents 

```
usage: run.py [-h] [-db DB] [-username USERNAME] [-password PASSWORD]
              [-queries QUERIES] [-indices INDICES] [-duration DURATION]
              [-agent {udo,udo-s,ddpg,sarsa}] [-horizon HORIZON]
              [-heavy_horizon HEAVY_HORIZON] [-rl_update {RAVE,MCTS}]
              [-rl_select {UCB1,UCBV}] [-rl_reward {delta,accumulate}]
              [-rl_delay {UCB,Exp3}] [-rl_max_delay_time RL_MAX_DELAY_TIME]
              [--load_json LOAD_JSON]
              {mysql,postgres}
```



Step 3.

Step 4.
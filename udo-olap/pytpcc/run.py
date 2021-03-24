import argparse

from drivers.mysqldriver import MysqlDriver
from drivers.postgresdriver import PostgresDriver
from sarsa_agent import run_sarsa_agent
from ddpg_agent import run_ddpg_agent
from udo_optimizer import run_udo
from udo_simplifed import run_simplifed_udo_agent
import index
import json
import constants

udo_parser = argparse.ArgumentParser(description='UDO optimizer.')
# database setting
udo_parser.add_argument('system', choices=('mysql', 'postgres'),
                        help='Target system driver')
udo_parser.add_argument('-db', default="tpcc",
                        help='the database to optimizes')
udo_parser.add_argument('-username', default="udo",
                        help='username')
udo_parser.add_argument('-password', default="udo",
                        help='password')
udo_parser.add_argument('-queries', default="tpcc_query.sql",
                        help='the input query file')
udo_parser.add_argument('-indices',
                        help='the input query file')
# tuning time
udo_parser.add_argument('-duration', default=5,
                        help='time for tuning in hours')
# rl algorithm
udo_parser.add_argument('-agent', default='udo', choices=('udo', 'udo-s', 'ddpg', 'sarsa'),
                        help='reinforcement learning agent')
udo_parser.add_argument('-horizon', default=5,
                        help='the number horizon for reinforcement agent')
# mcts algorithm
udo_parser.add_argument('-rl_update', choices=('RAVE', 'MCTS'),
                        help='the update policy of UDO tree search')
udo_parser.add_argument('-rl_select', choices=('UCB1', 'UCBV'),
                        help='the selection policy of UDO tree search')
udo_parser.add_argument('-rl_reward', choices=('delta', 'accumulate'),
                        help='the reward of reinforcement learning agent')
udo_parser.add_argument('-rl_delay', choices=('UCB', 'Exp3'),
                        help='the delay selection policy')
# load json file
udo_parser.add_argument('--load_json',
                        help='Load settings from file in json format. Command line options override values in file.')

args = udo_parser.parse_args()

# json file the higher priority
if args.load_json:
    with open(args.load_json, 'rt') as f:
        t_args = argparse.Namespace()
        t_args.__dict__.update(json.load(f))
        args = udo_parser.parse_args(namespace=t_args)

# init queries
if args['queries']:
    with open(args['queries']) as f:
        content = f.readlines()
        queries = [x.strip() for x in content]
        constants.QUERIES = {i: queries[i] for i in range(len(queries))}

# init indices with external files
if args['indices']:
    # analyze queries to extract indexes
    with open(args['indices']) as f:
        content = f.readlines()
        indices = [x.strip() for x in content]
        index.candidate_indices = []
        for index_str in indices:
            index = index_str.split(";")
            index.candidate_indices.append((index[0], index[1], index[2]))

dbms_conf = {
    "host": "127.0.0.1",
    "db": args['db'],
    "user": args['username'],
    "passwd": args['password'],
}

# create a dbms driver
if args['system'] == "mysql":
    driver = MysqlDriver(dbms_conf)
elif args['system'] == "postgres":
    driver = PostgresDriver(dbms_conf)

# obtain index cardinality information
driver.connect()
if not constants.cardinality_info:
    constants.cardinality_info = driver.cardinalities()

# obtain index applicable queries
for i in range(len(index.candidate_indices)):
    contain_query = []
    for query_id, query_str in constants.QUERIES.items():
        # print(candidate_indices[i][2])
        if "where" in query_str:
            where_clause = query_str[query_str.index("where"):].lower()
        else:
            where_clause = query_str.lower()
        contain_columns = index.candidate_indices[i][2].lower().split(",")
        if all(contain_column in where_clause for contain_column in contain_columns):
            # if any(contain_column in where_clause for contain_column in contain_columns):
            contain_query.append(query_id)
    index_cardinality = constants.cardinality_info[index.candidate_indices[i][1]]
    index.candidate_indices[i] += (contain_query, index_cardinality,)

# filter indices which contains at least has one appliable query
index.candidate_indices = [candidate_index for candidate_index in index.candidate_indices if
                           len(candidate_index[3]) > 0]
# print(len(index.
# candidate_indices))

# if the agent is udo
if args['agent'] == 'udo':
    # run udo
    run_udo_agent(duration=args['duration'], horizon=args['horizon'])
elif args['agent'] == 'udo-s':
    # run simplified udo
    run_simplifed_udo_agent(duration=args['duration'], horizon=args['horizon'])
elif args['agent'] == 'ddpg':
    # run ddpg deep rl
    run_ddpg_agent(duration=args['duration'], horizon=args['horizon'])
elif args['agent'] == 'sarsa':
    # run sarsa deep rl
    run_sarsa_agent(duration=args['duration'], horizon=args['horizon'])

# print(args.accumulate(args.integers))

import argparse
from sarsa_agent import run_sarsa_agent
from ddpg_agent import run_ddpg_agent
from udo_simplifed import run_simplifed_udo_agent
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
udo_parser.add_argument('-pass', default="udo",
                        help='password')
udo_parser.add_argument('-queries', default="tpcc_query.sql",
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

if args['queries']:
    with open(args['queries']) as f:
        content = f.readlines()
        queries = [x.strip() for x in content]
        constants.QUERIES = {i: queries[i] for i in range(len(queries))}

# if the agent is udo
if args['agent'] == 'udo':
    # run udo
    run_udo()
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

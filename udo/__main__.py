#!/usr/bin/env python3
# -----------------------------------------------------------------------
# Copyright (c) 2021    Cornell Database Group
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
# -----------------------------------------------------------------------

import argparse
import json
import logging
import os
import random
import sys

import numpy as np

from udo.agent.ddpg_agent import run_ddpg_agent
from udo.agent.sarsa_agent import run_sarsa_agent
from udo.agent.udo_agent import run_udo_agent
from udo.agent.udo_simplifed_agent import run_simplifed_udo_agent
from udo.drivers.mysqldriver import MysqlDriver
from udo.drivers.postgresdriver import PostgresDriver

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(funcName)s:%(lineno)03d] %(levelname)-5s: %(message)s",
                        datefmt="%m-%d-%Y %H:%M:%S",
                        stream=sys.stdout)

    udo_parser = argparse.ArgumentParser(description='UDO optimizer.')
    # database setting
    udo_parser.add_argument('-system', choices=('mysql', 'postgres'),
                            help='Target system driver')
    udo_parser.add_argument('-db', default="tpch",
                            help='the database to optimizes')
    udo_parser.add_argument('-username', default="udo",
                            help='username')
    udo_parser.add_argument('-password', default="udo",
                            help='password')
    udo_parser.add_argument('-queries', default="tpch_query.sql",
                            help='the input query file')
    udo_parser.add_argument('-indices',
                            help='the input query file')
    udo_parser.add_argument('-sys_params',
                            help='the input system params json file')
    # tuning time
    udo_parser.add_argument('-duration', default=5, type=float,
                            help='time for tuning in hours')

    # rl algorithm
    udo_parser.add_argument('-agent', default='udo', choices=('udo', 'udo-s', 'ddpg', 'sarsa'),
                            help='reinforcement learning agent')
    udo_parser.add_argument('-horizon', default=5, type=int,
                            help='the number horizon for reinforcement agent')
    udo_parser.add_argument('-heavy_horizon', default=3, type=int,
                            help='the number horizon for heavy parameters in UDO')
    # mcts algorithm
    udo_parser.add_argument('-rl_update', choices=('RAVE', 'MCTS'), default='RAVE',
                            help='the update policy of UDO tree search')
    udo_parser.add_argument('-rl_select', choices=('UCB1', 'UCBV'), default='UCBV',
                            help='the selection policy of UDO tree search')
    udo_parser.add_argument('-rl_reward', choices=('delta', 'accumulate'),
                            help='the reward of reinforcement learning agent')
    udo_parser.add_argument('-rl_delay', choices=('UCB', 'Exp3'),
                            help='the delay selection policy')
    udo_parser.add_argument('-rl_max_delay_time', type=int, default=5,
                            help='the delay selection policy')

    # tuning configuration
    udo_parser.add_argument('-sample_rate', type=int, default="1",
                            help='sampled rate from workload')
    udo_parser.add_argument('-default_query_time_out', type=int, default="5",
                            help='default timeout in seconds for each query')
    udo_parser.add_argument('-time_out_ratio', type=float, default="1.1",
                            help='timeout ratio respect to default time')

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

    # change
    args = vars(args)

    # init queries
    if args['queries']:
        queries = dict()
        for file_name in sorted(os.listdir(args['queries'])):
            if file_name.endswith(".sql"):
                with open(os.path.join(args['queries'], file_name)) as f:
                    content = f.read()
                    queries[file_name] = content
    else:
        print("please specify queries")
        exit()
        # print(constants.QUERIES)

    # init indices with external files
    if args['indices']:
        # analyze queries to extract indexes
        with open(args['indices']) as f:
            content = f.readlines()
            indices = [x.strip() for x in content]
            candidate_indices = []
            for index_str in indices:
                index_information = index_str.split(";")
                candidate_indices.append((index_information[0], index_information[1], index_information[2]))
    else:
        print("please specify candidate indices")
        exit()

    # check the validate of configurations file
    if not args['system'] or not args['db']:
        print("Please specific a database")
        exit()

    if not args['duration'] or not args['horizon']:
        print("Wrong parameters. Please check the input parameters")
        exit()

    if not args['sys_params']:
        print("Please specify the system parameters")
        exit()

    dbms_conf = {
        "host": "127.0.0.1",
        "db": args['db'],
        "user": args['username'],
        "passwd": args['password'],
    }

    with open(args['sys_params'], 'rt') as f:
        sys_params = json.load(f)

    # create a dbms driver
    driver = None
    if args['system'] == "mysql":
        driver = MysqlDriver(dbms_conf, sys_params)
    elif args['system'] == "postgres":
        driver = PostgresDriver(dbms_conf, sys_params)

    # obtain index cardinality information
    driver.connect()
    cardinality_info = driver.cardinalities()

    # obtain index applicable queries
    for i in range(len(candidate_indices)):
        contain_query = []
        for query_id, query_str in queries.items():
            # print(candidate_indices[i][2])
            if "where" in query_str:
                where_clause = query_str[query_str.index("where"):].lower()
            else:
                where_clause = query_str.lower()
            contain_columns = candidate_indices[i][2].lower().split(",")
            if all(contain_column in where_clause for contain_column in contain_columns):
                # if any(contain_column in where_clause for contain_column in contain_columns):
                contain_query.append(query_id)
        index_cardinality = cardinality_info[candidate_indices[i][1].lower()]
        candidate_indices[i] += (contain_query, index_cardinality,)

    # filter indices which contains at least has one appliable query
    candidate_indices = [candidate_index for candidate_index in candidate_indices if len(candidate_index[3]) > 0]

    # print(len(index.candidate_indices))

    tuning_config = {
        "duration": args['duration'],
        "horizon": args['horizon'],
        "sample_rate": args['sample_rate'],
        "default_query_time_out": args['default_query_time_out'],
        "time_out_ratio": args['time_out_ratio']
    }

    # if the agent is udo
    if args['agent'] == 'udo':
        if not args['heavy_horizon']:
            print("Please specific the step of heavy configurations")
            exit()
        # run udo
        print(tuning_config)
        horizon = args['horizon']
        tuning_config['heavy_horizon'] = args['heavy_horizon']
        tuning_config['light_horizon'] = horizon - int(args['heavy_horizon'])
        tuning_config['rl_max_delay_time'] = args['rl_max_delay_time']
        tuning_config['rl_update'] = args['rl_update']
        tuning_config['rl_select'] = args['rl_select']
        run_udo_agent(driver=driver, queries=queries, candidate_indices=candidate_indices, tuning_config=tuning_config)
    elif args['agent'] == 'udo-s':
        # run simplified udo
        run_simplifed_udo_agent(driver=driver, queries=queries, candidate_indices=candidate_indices,
                                tuning_config=tuning_config)
    elif args['agent'] == 'ddpg':
        # run ddpg deep rl
        run_ddpg_agent(driver=driver, queries=queries, candidate_indices=candidate_indices, tuning_config=tuning_config)
    elif args['agent'] == 'sarsa':
        # run sarsa deep rl
        run_sarsa_agent(driver=driver, queries=queries, candidate_indices=candidate_indices,
                        tuning_config=tuning_config)

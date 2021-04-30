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

import logging
import math
import random
import time

import gym
import numpy as np
from gym import spaces

class UDOEnv(gym.Env):
    """the environment of DBMS optimizer"""

    def __init__(self, driver, queries, candidate_indices, config):
        """ init method
        Args:
            driver: DBMS connector
            queries: queries to optimize
            candidate_indices: candidate indices to select
            config: the configuration for tuning

        Return: the environment
        """
        super(UDOEnv, self).__init__()

        self.driver = driver

        # initial index action tuning space
        self.candidate_indices = candidate_indices
        self.index_candidate_num = len(self.candidate_indices)
        logging.debug(f"the total number of index candidates is {self.index_candidate_num}")

        # initial system parameter space
        self.parameter_candidate = self.driver.get_system_parameter_space()
        self.parameter_candidate_num = len(self.parameter_candidate)
        logging.debug(f"the total number of tuning system parameters is {self.parameter_candidate_num}")

        # combine the actions from 2 sub actions
        # action space
        self.nA_index = self.index_candidate_num
        self.nA_parameter = sum(self.parameter_candidate)
        self.nA = int(self.nA_index + self.nA_parameter)
        self.action_space = spaces.Discrete(self.nA)
        logging.debug(f"action space {self.nA}")

        # state space
        self.nS_index = int(math.pow(2, self.index_candidate_num))
        self.nS_parameter = np.prod(self.parameter_candidate)
        # self.nS = self.nS_index * self.nS_parameter
        logging.debug(f"index state space {self.nS_index}")
        logging.debug(f"parameter state space {self.nS_parameter}")

        # our transition matrix is a deterministic matrix
        # the observation space
        observation_space_array = np.concatenate([np.full(self.index_candidate_num, 1), self.parameter_candidate])
        self.observation_space = spaces.MultiDiscrete(observation_space_array)
        self.current_state = np.concatenate(
            [np.zeros(self.index_candidate_num), np.zeros(self.parameter_candidate_num)])

        # the MDP init setting
        # index build time

        # horizon
        self.horizon = config['horizon']
        self._step = 0
        # current step
        # for runtime statistics
        self.accumulated_index_time = 0
        self.start_time = time.time()

        # get all queries in the given benchmark
        self.queries = queries
        self.query_ids = list(self.queries.keys())
        self.nr_query = len(self.queries)
        self.query_sqls = [self.queries[query_id] for query_id in self.query_ids]
        query_to_id = {self.query_ids[idx]: idx for idx in range(self.nr_query)}
        self.index_to_applicable_queries = list(
            map(lambda x: list(map(lambda y: query_to_id[y], x[3])), self.candidate_indices))

        # the default run time
        default_time_out_per_query = 6
        # config['default_query_time_out']
        time_out_ratio = 1.1
        # config['time_out_ratio']
        input_runtime_out = [default_time_out_per_query] * self.nr_query
        self.default_runtime = self.driver.run_queries_with_timeout(self.query_sqls, input_runtime_out)
        self.runtime_out = [
            time_out_ratio * query_runtime if query_runtime < default_time_out_per_query
            else default_time_out_per_query for query_runtime in self.default_runtime]

        self.sample_rate = 1
        # config['sample_rate']
        self.best_state = None
        self.best_run_performance = sum(self.default_runtime)
        logging.info("start to tuning your database")
        logging.info(f"timeout for queries {self.runtime_out}")

    def state_decoder(self, num):
        """decode a vector to a state number"""
        index_pos = int(num % self.nS_index)
        index_state_string = np.binary_repr(int(index_pos), width=self.index_candidate_num)[::-1]
        # index stata represented in string
        index_state = list(map(int, index_state_string))
        parameter_value = int(num / self.nS_index)
        parameter_pos = [0] * self.parameter_candidate_num
        for i in range(self.parameter_candidate_num):
            parameter_pos[i] = (parameter_value % self.parameter_candidate[i])
            parameter_value = int(parameter_value / self.parameter_candidate[i])
        return index_state + parameter_pos

    def state_encoder(self, state):
        """encode a state number to a vector"""
        index_state = state[:self.index_candidate_num]
        parameter_state = state[self.index_candidate_num:]
        index_pos = int("".join([str(int(a)) for a in reversed(index_state)]), 2)
        parameter_pos = 0
        parameter_base = 1
        for i in range(len(self.parameter_candidate)):
            parameter_pos = parameter_pos + parameter_state[i] * parameter_base
            parameter_base = parameter_base * self.parameter_candidate[i]
        pos = index_pos + parameter_pos * self.nS_index
        return int(pos)

    def retrieve_heavy_actions(self, state):
        """obtain available heavy actions given a state"""
        index_state = state[:self.index_candidate_num]
        # check which indices are available or not
        candidate_index_action = [i for i in range(len(index_state)) if index_state[i] == 0]
        return candidate_index_action

    def retrieve_light_actions(self, state):
        """obtain available light actions given a state"""
        parameter_state = state[self.index_candidate_num:]
        candidate_parameter_action = []
        parameter_sum = 0
        for i in range(len(parameter_state)):
            # if the current parameter state is a default state, we switch its value
            if parameter_state[i] == 0:
                for j in range(1, self.parameter_candidate[i]):
                    candidate_parameter_action.append(self.nA_index + parameter_sum + j)
            parameter_sum += self.parameter_candidate[i]
        all_light_actions = candidate_parameter_action
        return all_light_actions

    def retrieve_actions(self, state):
        """retrieve available actions for a state including both light actions and heavy actions"""
        heavy_action = self.retrieve_heavy_actions(state)
        light_action = self.retrieve_light_actions(state)
        return heavy_action + light_action

    def transition(self, state, action):
        """transition from a state and an action to a next state"""
        assert action < self.nA
        index_state = state[:self.index_candidate_num]
        parameter_state = state[self.index_candidate_num:]
        if (action < self.nA_index):
            # action is the index action
            index_action = action
            index_state[index_action] = 1
        else:
            # action is the parameter action
            parameter_action = action - self.nA_index
            parameter_value = 0
            parameter_type = 0
            while parameter_type < len(self.parameter_candidate):
                parameter_range = self.parameter_candidate[parameter_type]
                # test whether cover this range
                if parameter_action < (parameter_value + parameter_range):
                    parameter_value = parameter_action - parameter_value
                    break
                parameter_value = parameter_value + parameter_range
                parameter_type += 1
            parameter_state[parameter_type] = parameter_value
        next_state = index_state + parameter_state
        return next_state, self.state_encoder(next_state)

    def step_without_evaluation(self, action):
        """move to the next state given the action and current state"""
        state = self.current_state
        # parameter state and action
        index_current_state = state[:self.index_candidate_num]
        parameter_current_state = state[self.index_candidate_num:]
        parameter_action = action - self.nA_index
        parameter_value = 0
        for parameter_type in range(len(self.parameter_candidate)):
            parameter_range = self.parameter_candidate[parameter_type]
            if parameter_action < (parameter_value + parameter_range):
                parameter_value = parameter_action - parameter_value
                break
            parameter_value = parameter_value + parameter_range
        parameter_current_state[parameter_type] = parameter_value
        next_state = np.concatenate([index_current_state, parameter_current_state])
        self.current_state = next_state
        return next_state

    def retrieve_light_action_command(self, action):
        parameter_action = action - self.nA_index
        parameter_value = 0
        parameter_type = 0
        for parameter_type in range(len(self.parameter_candidate)):
            parameter_range = self.parameter_candidate[parameter_type]
            if parameter_action < (parameter_value + parameter_range):
                parameter_value = parameter_action - parameter_value
                break
            parameter_value = parameter_value + parameter_range
        return self.driver.get_system_parameter_command(parameter_type, parameter_value)

    def evaluate(self, sampled_queries):
        """evaluate current state using the sampled queries"""
        state = self.current_state
        index_current_state = state[:self.index_candidate_num]
        parameter_current_state = state[self.index_candidate_num:]
        # change system parameter
        self.driver.change_system_parameter(parameter_current_state)
        # invoke queries
        run_time = self.driver.run_queries_with_timeout(
            [self.query_sqls[sampled_query] for sampled_query in sampled_queries],
            [self.runtime_out[sampled_query] for sampled_query in sampled_queries])
        logging.debug(f"evaluate time {sum(run_time)}")
        return run_time

    def index_step(self, add_actions, remove_actions):
        """index step"""
        for add_action in add_actions:
            index_to_create = self.candidate_indices[add_action]
            # build index action
            logging.debug(f"create index {index_to_create}")
            self.driver.build_index(index_to_create)
        for remove_action in remove_actions:
            index_to_drop = self.candidate_indices[remove_action]
            # drop index action
            logging.debug(f"drop index {index_to_drop}")
            self.driver.drop_index(index_to_drop)

    def index_add_step(self, add_action):
        """create indexes"""
        index_to_create = self.candidate_indices[add_action]
        # an index build action
        logging.debug(f"create index {index_to_create}")
        self.driver.build_index(index_to_create)

    def index_drop_step(self, remove_actions):
        """drop indexes"""
        for remove_action in remove_actions:
            index_to_drop = self.candidate_indices[remove_action]
            # drop index action
            logging.debug(f"drop index {index_to_drop}")
            self.driver.drop_index(index_to_drop)

    def step(self, action):
        """invoke an action and move to the next step"""
        state = self.current_state
        # parameter state and action
        index_current_state = state[:self.index_candidate_num]
        parameter_current_state = state[self.index_candidate_num:]
        if action < self.nA_index:
            # index action, create indices
            if index_current_state[action] == 0:
                index_start_time = time.time()
                self.index_add_step(action)
                index_end_time = time.time()
                index_time = (index_end_time - index_start_time)
                self.accumulated_index_time = self.accumulated_index_time + index_time
                index_current_state[action] = 1
        else:
            # parameter action, switch to different parameters
            parameter_action = action - self.nA_index
            parameter_value = 0
            for parameter_type in range(len(self.parameter_candidate)):
                parameter_range = self.parameter_candidate[parameter_type]
                if parameter_action < (parameter_value + parameter_range):
                    parameter_value = parameter_action - parameter_value
                    break
                parameter_value = parameter_value + parameter_range
            parameter_current_state[parameter_type] = parameter_value
            self.driver.change_system_parameter(parameter_current_state)

        # heavy actions, and we only consider queries applicable to selected indices
        active_indices = [index_pos for index_pos in range(self.nA_index) if index_current_state[index_pos] == 1]
        query_to_consider = set(
            [applicable_query for applicable_queries in
             list(map(lambda x: self.index_to_applicable_queries[x], active_indices)) for applicable_query in
             applicable_queries])

        if len(query_to_consider) == 0:
            query_to_consider = range(self.nr_query)

        # obtain sample number
        sample_num = math.ceil(self.sample_rate * len(query_to_consider))
        # generate sample queries
        sample_queries = random.sample(list(query_to_consider), k=sample_num)

        # invoke queries
        run_time = self.driver.run_queries_with_timeout(
            [self.query_sqls[sample_query] for sample_query in sample_queries],
            [self.runtime_out[sampled_query] for sampled_query in sample_queries])

        next_state = np.concatenate([index_current_state, parameter_current_state])
        self.current_state = next_state

        # scale the reward
        reward = sum(self.default_runtime) / sum(run_time)
        current_time = time.time()
        estimate_workload_time = sum(run_time) + sum(
            [self.default_runtime[query] for query in range(self.nr_query) if query not in sample_queries])

        logging.debug(f"run time: {run_time}")
        logging.debug(f"index time: {self.accumulated_index_time}")
        logging.debug(f"evaluate time: {sum(run_time)}")
        logging.debug(f"next state: {next_state}")
        logging.debug(f"tuning duration: {(current_time - self.start_time)}", )
        logging.debug(f"estimate whole workload time: {estimate_workload_time}")

        if estimate_workload_time < self.best_run_performance:
            self.best_run_performance = estimate_workload_time
            self.best_state = self.current_state

        self._step += 1
        if self._step == self.horizon:
            self._step = 0
            return next_state, reward, True, {}
        else:
            return next_state, reward, False, {}

    def reset(self):
        """reset the state"""
        if self.current_state is not None:
            state = self.current_state
            index_current_state = state[:self.index_candidate_num]
            parameter_current_state = state[self.index_candidate_num:]
            # drop all indices at the current state
            for i in range(self.index_candidate_num):
                if index_current_state[i] == 1:
                    index_drop_sql = self.candidate_indices[i]
                    self.driver.drop_index(index_drop_sql)
            # set the parameter to default value, the first value
            self.driver.change_system_parameter(np.zeros(self.parameter_candidate_num))
        self.current_state = np.concatenate(
            [np.zeros(self.index_candidate_num), np.zeros(self.parameter_candidate_num)])
        return self.current_state

    def print_state_summary(self, state):
        index_state = state[:self.index_candidate_num]
        parameter_state = state[self.index_candidate_num:]
        logging.info(f"Best index configurations:")
        for i in range(len(index_state)):
            if index_state[i] == 1:
                index_to_create = self.candidate_indices[i]
                self.driver.build_index_command(index_to_create)
        logging.info(f"Best system parameters:")
        for i in range(len(parameter_state)):
            logging.info(self.driver.get_system_parameter_command(i, parameter_state[i]))

    def print_action_summary(self, actions):
        """print action summary given actions"""
        logging.info(f"Best index configurations:")
        best_indices = [self.candidate_indices[action_idx] for action_idx in actions if action_idx < self.nA_index]
        best_sys_actions = [action_idx for action_idx in actions if action_idx >= self.nA_index]
        for best_index in best_indices:
            logging.info(self.driver.build_index_command(best_index))
        logging.info(f"Best system parameters:")
        for sys_action in best_sys_actions:
            logging.info(self.retrieve_light_action_command(sys_action))

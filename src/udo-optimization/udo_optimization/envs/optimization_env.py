import math
import random
import time

import gym
import numpy as np
from gym import spaces

# from drivers.mysqldriver import MysqlDriver
# from drivers.postgresdriver import PostgresDriver

class OptimizationEnv(gym.Env):

    def __init__(self, driver, queries, candidate_indices):
        # init
        super(OptimizationEnv, self).__init__()

        # our transition matrix is a deterministic matrix
        self.driver = driver

        # initial index action tuning space
        # total number of indices to consider is 20
        self.candidate_indices = candidate_indices
        self.index_candidate_num = len(self.candidate_indices)

        # initial system parameter space
        self.parameter_candidate = self.driver.get_system_parameter_space()
        self.parameter_candidate_num = len(self.parameter_candidate)
        print(self.parameter_candidate_num)

        # combine the actions from 2 sub actions
        # action space
        self.nA_index = self.index_candidate_num
        self.nA_parameter = sum(self.parameter_candidate)
        self.nA = int(self.nA_index + self.nA_parameter)
        self.action_space = spaces.Discrete(self.nA)
        # print(self.nA)

        # state space
        self.nS_index = int(math.pow(2, self.index_candidate_num))
        self.nS_parameter = np.prod(self.parameter_candidate)
        self.nS = int(self.nS_index * self.nS_parameter)
        # print(self.nS)

        # change the observation space
        # observation space
        observation_space_array = np.concatenate([np.full(self.index_candidate_num, 1), self.parameter_candidate])
        self.observation_space = spaces.MultiDiscrete(observation_space_array)
        self.current_state = np.concatenate(
            [np.zeros(self.index_candidate_num), np.zeros(self.parameter_candidate_num)])

        # the MDP init setting
        # index build time
        self.accumulated_index_time = 0
        # horizon
        self.horizon = 9
        # current step
        self.cr_step = 0
        # start time
        self.start_time = time.time()

        # get all queries in the given benchmark
        self.queries = queries
        self.query_ids = list(self.queries.keys())
        self.nr_query = len(self.queries)
        query_to_id = {self.query_ids[idx]: idx for idx in range(self.nr_query)}
        print("query_to_id:", query_to_id)
        self.index_to_applicable_queries = list(
            map(lambda x: list(map(lambda y: query_to_id[y], x[3])), self.candidate_indices))

        # the default run time
        self.default_runtime = self.driver.run_queries_without_timeout(list(self.queries.values()))

    # map a number to a state
    def state_decoder(self, num):
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

    # map a state to a number
    def state_encoder(self, state):
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

    # available heavy actions for a state
    def choose_all_heavy_actions(self, state):
        index_state = state[:self.index_candidate_num]
        # check which indices are available or not
        candidate_index_action = [i for i in range(len(index_state)) if index_state[i] == 0]
        return candidate_index_action

    # available light actions for a state
    def choose_all_light_actions(self, state):
        # only allow to change the non-changed parameter
        # print("index_candidate_nums:", self.index_candidate_num)
        # print("parameter_candidate_num:", self.parameter_candidate_num)
        # print("parameter_candidate:", self.parameter_candidate)
        parameter_state = state[self.index_candidate_num:]
        # print("parameter_state:", parameter_state)
        candidate_parameter_action = []
        parameter_sum = 0
        for i in range(len(parameter_state)):
            if parameter_state[i] == 0:
                for j in range(1, self.parameter_candidate[i]):
                    candidate_parameter_action.append(self.nA_index + parameter_sum + j)
            parameter_sum += self.parameter_candidate[i]
            print(parameter_state)
        print(parameter_state)
        # we only consider the change of parameter
        all_light_actions = candidate_parameter_action
        return all_light_actions

    # available actions for a state
    def choose_all_actions(self, state):
        heavy_action = self.choose_all_heavy_actions(state)
        light_action = self.choose_all_light_actions(state)
        return heavy_action + light_action

    # transition from a state and an action
    def transition(self, state, action):
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
            # print(parameter_action)
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

    # step without evaluation
    def step_without_evaluation(self, action):
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

    # evaluate the current state
    def evaluate_light(self, queries):
        state = self.current_state
        # print("current state:")
        # print(state)
        index_current_state = state[:self.index_candidate_num]
        parameter_current_state = state[self.index_candidate_num:]
        # change system parameter
        self.driver.change_system_parameter(parameter_current_state)
        # invoke queries
        run_time = self.driver.run_queries_with_timeout(queries, self.default_runtime)
        print("evaluate time:", sum(run_time))
        return run_time

    # index step
    def index_step(self, add_actions, remove_actions):
        # one index build or drop action
        for add_action in add_actions:
            index_to_create = self.candidate_indices[add_action]
            # build index action
            print("create index")
            print(index_to_create)
            self.driver.build_index(index_to_create)
        for remove_action in remove_actions:
            index_to_drop = self.candidate_indices[remove_action]
            # drop index action
            print("drop index")
            print(index_to_drop)
            self.driver.drop_index(index_to_drop)

    def index_add_step(self, add_action):
        # add action
        index_to_create = self.candidate_indices[add_action]
        # build index action
        print("create index")
        print(index_to_create)
        self.driver.build_index(index_to_create)

    def index_drop_step(self, remove_actions):
        # drop actions
        for remove_action in remove_actions:
            index_to_drop = self.candidate_indices[remove_action]
            # drop index action
            print("drop index")
            print(index_to_drop)
            self.driver.drop_index(index_to_drop)

    def step(self, action):
        state = self.current_state
        # print("action:", action)
        # print("state:", state)
        # parameter state and action
        index_current_state = state[:self.index_candidate_num]
        parameter_current_state = state[self.index_candidate_num:]
        if action < self.nA_index:
            # index action, create indices
            if index_current_state[action] == 0:
                start_time = time.time()
                self.index_add_step(action)
                end_time = time.time()
                index_time = (end_time - start_time)
                self.accumulated_index_time = self.accumulated_index_time + index_time
                index_current_state[action] = 1
        else:
            # else parameter switch action
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

        # heavy actions
        active_indices = [index_pos for index_pos in range(self.nA_index) if index_current_state[index_pos] == 1]
        query_to_consider = set(
            [applicable_query for applicable_queries in
             list(map(lambda x: self.index_to_applicable_queries[x], active_indices)) for applicable_query in
             applicable_queries])

        # obtain sample number
        sample_rate = 1
        sample_num = math.ceil(sample_rate * len(query_to_consider))
        # generate sample queries
        sample_queries = random.sample(list(query_to_consider), k=sample_num)

        # invoke queries
        run_time = self.driver.run_queries_with_timeout([self.queries[self.query_ids[sample_query]] for sample_query in sample_queries],
                                                        self.default_runtime)
        print("run time:", run_time)
        print("index time:", self.accumulated_index_time)
        print("evaluate time:", sum(run_time))

        next_state = np.concatenate([index_current_state, parameter_current_state])
        self.current_state = next_state
        print("next state:", next_state)

        # scale the reward
        reward = sum(self.default_runtime) / sum(run_time)
        current_time = time.time()
        print("current time:", (current_time - self.start_time))

        self.cr_step += 1
        if self.cr_step == self.horizon:
            self.cr_step = 0
            return next_state, reward, True, {}
        else:
            return next_state, reward, False, {}

    # reset the state
    def reset(self):
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

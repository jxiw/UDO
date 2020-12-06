import math

import gym
import numpy as np
from gym import spaces

from drivers.mysqldriver import MysqlDriver
from drivers.postgresdriver import PostgresDriver

from . import index
from . import parameter


class OLAPOptimizationGameEnv(gym.Env):

    def check_constraint(self, constraints, prev_unit, next_unit):
        for constraint in constraints:
            if constraint[0] == prev_unit and constraint[1] == next_unit:
                return False
        return True

    def __init__(self):
        # init
        super(OLAPOptimizationGameEnv, self).__init__()

        # index action space
        # total number of indices to consider is 20
        self.index_candidate_num = len(index.candidate_indices)

        # parameter action space
        self.parameter_candidate = [len(specific_parameter) for specific_parameter in
                                    parameter.candidate_dbms_parameter]
        self.parameter_candidate_num = len(self.parameter_candidate)

        # combine the actions from 2 sub actions
        # define action and observation space
        self.nA_index = self.index_candidate_num
        self.nA_parameter = sum(self.parameter_candidate)
        self.nA = int((self.nA_index + self.nA_parameter))
        print(self.nA)

        self.nS_index = int(math.pow(2, self.index_candidate_num))
        self.nS_parameter = np.prod(self.parameter_candidate)
        self.nS = int(self.nS_index * self.nS_parameter)

        # action space
        self.action_space = spaces.Discrete(self.nA)

        # change the observation space
        observation_space_array = np.concatenate([np.full(self.index_candidate_num, 1), self.parameter_candidate])
        self.observation_space = spaces.MultiDiscrete(observation_space_array)

        # our transition matrix is a deterministic matrix
        # self.driver = MysqlDriver()
        self.driver = PostgresDriver()
        self.driver.connect()
        self.current_state = None

    def map_number_to_state(self, num):
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

    def map_state_to_num(self, state):
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

    def choose_all_heavy_actions(self, state):
        index_state = state[:self.index_candidate_num]
        # check which indices are available or not
        candidate_index_action = [i for i in range(len(index_state)) if index_state[i] == 0]
        return candidate_index_action

    def choose_all_light_actions(self, state):
        # only allow to change the non-changed parameter
        parameter_state = state[self.index_candidate_num:]
        candidate_parameter_action = []
        parameter_sum = 0
        for i in range(len(parameter_state)):
            if parameter_state[i] == 0:
                for j in range(1, self.parameter_candidate[i]):
                    candidate_parameter_action.append(self.nA_index + parameter_sum + j)
            parameter_sum += self.parameter_candidate[i]
        # we only consider the change of parameter
        all_light_actions = candidate_parameter_action
        return all_light_actions

    def obtain_next_state(self, state, action):
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
        return next_state, self.map_state_to_num(next_state)

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

    def evaluate_light_under_heavy(self):
        state = self.current_state
        print ("current state:")
        print (state)
        index_current_state = state[:self.index_candidate_num]
        parameter_current_state = state[self.index_candidate_num:]
        # change system parameter
        for i in range(self.parameter_candidate_num):
            parameter_choice = int(parameter_current_state[i])
            parameter_change_sql = parameter.candidate_dbms_parameter[i][parameter_choice]
            print(parameter_change_sql)
            self.driver.setSystemParameter(parameter_change_sql)

        # invoke queries
        run_time = self.driver.runQueries()
        print("evaluate time:", sum(run_time))
        return run_time

    def index_step(self, add_actions, remove_actions):
        # one index build or drop action
        for add_action in add_actions:
            index_to_create = index.candidate_indices[add_action]
            # build index action
            print("create index")
            print(index_to_create)
            self.driver.buildIndex(index_to_create)
        for remove_action in remove_actions:
            index_to_drop = index.candidate_indices[remove_action]
            # drop index action
            print("drop index")
            print(index_to_drop)
            self.driver.dropIndex(index_to_drop)

    def reset(self):
        if self.current_state is not None:
            state = self.current_state
            index_current_state = state[:self.index_candidate_num]
            parameter_current_state = state[self.index_candidate_num:]
            # drop all indices at the current state
            for i in range(self.index_candidate_num):
                if index_current_state[i] == 1:
                    index_drop_sql = index.candidate_indices[i]
                    self.driver.dropIndex(index_drop_sql)
            # set the parameter to default value
            for i in range(self.parameter_candidate_num):
                parameter_change_sql = parameter.candidate_dbms_parameter[i][0]
                self.driver.setSystemParameter(parameter_change_sql)
        self.current_state = np.concatenate([np.zeros(self.index_candidate_num), np.zeros(self.parameter_candidate_num)])
        return self.current_state

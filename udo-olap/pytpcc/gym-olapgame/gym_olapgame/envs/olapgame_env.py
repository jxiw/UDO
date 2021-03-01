import math
import random
import time

import gym
import numpy as np
from gym import spaces

# from drivers.mysqldriver import MysqlDriver
import constants
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
        self.start_time = time.time()
        self.accumulated_index_time = 0
        self.horizon = 9
        self.cr_step = 0

        self.all_queries = list(constants.QUERIES.keys())
        nr_query = len(self.all_queries)
        query_info = {self.all_queries[idx]: idx for idx in range(nr_query)}
        self.current_state = np.concatenate([np.zeros(self.index_candidate_num), np.zeros(self.parameter_candidate_num)])
        self.index_query_info = list(map(lambda x: list(map(lambda y: query_info[y], x[3])), index.candidate_indices))
        self.default_default_runtime = self.evaluate_light_under_heavy(self.all_queries, [0] * len(self.all_queries))

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

    def choose_all_actions(self, state):
        heavy_action = self.choose_all_heavy_actions(state)
        light_action = self.choose_all_light_actions(state)
        return heavy_action + light_action

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

    def evaluate_light_under_heavy(self, query_list, timeout):
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
        run_time = self.driver.runQueries(query_list, timeout)
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

    def index_add_step(self, add_action):
        # add action
        index_to_create = index.candidate_indices[add_action]
        #build index action
        print("create index")
        print(index_to_create)
        self.driver.buildIndex(index_to_create)

    def index_drop_step(self, remove_actions):
        # drop actions
        for remove_action in remove_actions:
            index_to_drop = index.candidate_indices[remove_action]
            # drop index action
            print("drop index")
            print(index_to_drop)
            self.driver.dropIndex(index_to_drop)

    def step(self, action):
        state = self.current_state
        print("action:", action)
        print("state:", state)
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
            parameter_action = action - self.nA_index
            parameter_value = 0
            for parameter_type in range(len(self.parameter_candidate)):
                parameter_range = self.parameter_candidate[parameter_type]
                if parameter_action < (parameter_value + parameter_range):
                    parameter_value = parameter_action - parameter_value
                    break
                parameter_value = parameter_value + parameter_range
            parameter_current_state[parameter_type] = parameter_value
            for i in range(self.parameter_candidate_num):
                parameter_choice = int(parameter_current_state[i])
                parameter_change_sql = parameter.candidate_dbms_parameter[i][parameter_choice]
                print(parameter_change_sql)
                self.driver.setSystemParameter(parameter_change_sql)

        heavy_actions = []
        for index_pos in range(self.nA_index):
            if index_current_state[index_pos] == 1:
                heavy_actions.append(index_pos)

        query_to_consider = set(
            [applicable_query for applicable_queries in
             list(map(lambda x: self.index_query_info[x], heavy_actions)) for applicable_query in
             applicable_queries])

        # obtain sample number
        sample_num = math.ceil(constants.sample_rate * len(query_to_consider))
        # generate sample queries
        sampled_query_list = random.sample(list(query_to_consider), k=sample_num)

        # invoke queries
        run_time = self.driver.runQueries([self.all_queries[select_query] for select_query in sampled_query_list], self.default_default_runtime)
        print("run time:", run_time)
        print("index time:", self.accumulated_index_time)
        print("evaluate time:", sum(run_time))

        next_state = np.concatenate([index_current_state, parameter_current_state])
        self.current_state = next_state
        print("next state:", next_state)

        # default_timeout = [10.693569898605347, 0.11094331741333008, 3.72650408744812, 1.0694530010223389, 1.0730197429656982,
        #            2.2397916316986084, 2.0279834270477295, 3.822448968887329, 7.970007419586182, 1.4352169036865234,
        #            0.515200138092041, 2.6003406047821045, 12.872627019882202, 2.3702046871185303, 0.0011920928955078125,
        #            0.46315932273864746, 0.7527892589569092, 2.645094633102417, 0.23529434204101562, 0.8605573177337646,
        #            10.454352855682373, 0.16903018951416016]

        # default_timeout = [2.114644765853882, 0.3178749084472656, 0.8655669689178467, 0.27109265327453613, 1.0132851600646973, 0.3362388610839844, 0.6741001605987549, 0.4631633758544922, 1.3484652042388916, 0.7488498687744141, 0.12991714477539062, 0.9270060062408447, 1.2022361755371094, 0.3823051452636719, 0.7328939437866211, 0.6157047748565674, 1.9892585277557373, 3.471993923187256, 0.4750077724456787, 1.323035717010498, 0.8502225875854492, 0.41719698905944824]

        reward = sum(self.default_default_runtime) / sum(run_time)
        current_time = time.time()
        print("current time:", (current_time - self.start_time))
        self.cr_step += 1
        if self.cr_step == self.horizon:
            self.cr_step = 0
            return next_state, reward, True, {}
        else:
            return next_state, reward, False, {}

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

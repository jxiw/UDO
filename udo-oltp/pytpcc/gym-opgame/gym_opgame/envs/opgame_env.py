import gym

import random
import logging
import numpy as np
import math
from gym import spaces
import permutation
import tpcc
from util import *
import itertools
import time
from . import parameter
from . import index
from tpcc import loader

class OptimizationGameEnv(gym.Env):

    def filterPermutationWithConstraint(self, all_permutation, constraints):
        permutation_with_constraint = []
        for p in all_permutation:
            # check whether this permutation is validate
            flag = True
            for constraint in constraints:
                if constraint[0] < len(p) and constraint[1] < len(p):
                    firstElementPos = p.index(constraint[0])
                    secondElementPos = p.index(constraint[1])
                    if firstElementPos > secondElementPos:
                        flag = False
                        break
            if flag:
                permutation_with_constraint.append(list(p))
        # print "permutation_with_constraint"
        # print permutation_with_constraint
        return permutation_with_constraint

    def check_constraint(self, constraints, prev_unit, next_unit):
        for constraint in constraints:
            if constraint[0] == prev_unit and constraint[1] == next_unit:
                return False
        return True

    def __init__(self):
        # init
        super(OptimizationGameEnv, self).__init__()

        # the reorder unit of each transaction
        self.payment_unit = 7
        self.delivery_unit = 7
        self.new_order_unit = 5
        self.reorder_unit = self.payment_unit + self.delivery_unit + self.new_order_unit

        self.payment_unit_constraint = [(4, 5), (0, 6), (2, 6), (4, 6)]
        self.delivery_unit_constraint = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (2, 6), (5, 6)]
        self.new_order_unit_constraint = [(2, 3), (2, 4), (3, 4)]

        payment_all_permutation = itertools.permutations(range(self.payment_unit))
        self.validate_payment_permutation = self.filterPermutationWithConstraint(payment_all_permutation,
                                                                                 self.payment_unit_constraint)

        self.payment_permutation_to_position = {''.join([str(x) for x in value]): key for key, value in
                                                enumerate(self.validate_payment_permutation)}

        delivery_all_permutation = itertools.permutations(range(0, self.delivery_unit))
        self.validate_delivery_permutation = self.filterPermutationWithConstraint(delivery_all_permutation,
                                                                                  self.delivery_unit_constraint)

        self.delivery_permutation_to_position = {''.join([str(x) for x in value]): key for key, value in
                                                 enumerate(self.validate_delivery_permutation)}

        new_order_all_permutation = itertools.permutations(range(0, self.new_order_unit))
        self.validate_new_order_permutation = self.filterPermutationWithConstraint(new_order_all_permutation,
                                                                                   self.new_order_unit_constraint)

        self.new_order_permutation_to_position = {''.join([str(x) for x in value]): key for key, value in
                                                  enumerate(self.validate_new_order_permutation)}

        # print (self.new_order_permutation_to_position)

        # index action space
        # total number of indices to consider is 20
        self.index_candidate_num = len(index.candidate_indices)

        # parameter action space
        # e.g., the first parameter has 4 choices, the second parameter has 4 choices, and the third and fourth parameter has 4 choices
        # self.parameter_candidate = np.array([5, 4, 4, 4, 4, 4])
        # self.parameter_candidate = np.array([4, 4, 4, 4, 4])

        self.parameter_candidate = [len(specific_parameter) for specific_parameter in
                                   parameter.candidate_dbms_parameter]
        self.parameter_candidate_num = len(self.parameter_candidate)

        # combine the actions from 3 sub actions
        # define action and observation space
        self.nA_reorder_payment = self.payment_unit - 1
        self.nA_reorder_delivery = self.delivery_unit - 1
        self.nA_reorder_new_order = self.new_order_unit - 1
        self.nA_reorder = self.nA_reorder_payment + self.nA_reorder_delivery + self.nA_reorder_new_order
        self.nA_index = self.index_candidate_num
        self.nA_parameter = sum(self.parameter_candidate)
        self.nA = int((self.nA_reorder + self.nA_index + self.nA_parameter))
        print(self.nA)

        self.nS_payment = len(self.validate_payment_permutation)
        self.nS_delivery = len(self.validate_delivery_permutation)
        self.nS_new_order = len(self.validate_new_order_permutation)
        self.nS_reorder = (self.nS_payment * self.nS_delivery * self.nS_new_order)
        self.nS_index = int(math.pow(2, self.index_candidate_num))
        self.nS_parameter = np.prod(self.parameter_candidate)
        self.nS = int(self.nS_reorder * self.nS_index * self.nS_parameter)
        # print (self.nS_payment)
        # print (self.nS_delivery)
        # print (self.nS_new_order)
        # # 3628800
        # print (self.nS_reorder)
        # # 32768
        # print (self.nS_index)
        # # 5120
        # print (self.nS_parameter)

        # action space
        self.action_space = spaces.Discrete(self.nA)
        # observation space
        # self.reorder_observation_space = spaces.Tuple([spaces.MultiDiscrete(np.full(self.delivery_unit, self.delivery_unit)),
        #                                                spaces.MultiDiscrete(np.full(self.delivery_unit, self.delivery_unit)),
        #                                                spaces.MultiDiscrete(np.full(self.new_order_unit, self.new_order_unit))])
        # self.index_observation_space = spaces.MultiBinary(self.index_candidate_num)
        # self.parameter_observation_space = spaces.MultiDiscrete(self.parameter_candidate)
        # self.observation_space = spaces.Tuple([self.reorder_observation_space, self.index_observation_space, self.parameter_observation_space])

        # change the observation space
        observation_space_array = np.concatenate([np.full(self.delivery_unit, self.delivery_unit),
                                                  np.full(self.delivery_unit, self.delivery_unit),
                                                  np.full(self.new_order_unit, self.new_order_unit),
                                                  np.full(self.index_candidate_num, 1),
                                                  self.parameter_candidate])
        # print(observation_space_array)
        self.observation_space = spaces.MultiDiscrete(observation_space_array)

        # our transition matrix is a deterministic matrix
        # self.args = {
        #     'debug': False,
        #     'system': 'mysql',
        #     'ddl': '',
        #     'clients': 32,
        #     'warehouses': 10,
        #     'scalefactor': 10,
        #     'stop_on_error': False,
        #     'duration': 1
        # }

        self.args = {
            'debug': False,
            'system': 'postgres',
            'ddl': '',
            'clients': 32,
            'warehouses': 10,
            'scalefactor': 10,
            'stop_on_error': False,
            'duration': 1
        }

        if self.args['debug']: logging.getLogger().setLevel(logging.DEBUG)

        ## Create a handle to the target client driver
        self.driverClass = tpcc.createDriverClass(self.args['system'])
        self.driver = self.driverClass(self.args['ddl'])
        # add dbms configure
        defaultConfig = self.driver.makeDefaultConfig()
        self.config = dict(map(lambda x: (x, defaultConfig[x][1]), defaultConfig.keys()))
        self.config['reset'] = False
        self.config['load'] = False
        self.config['execute'] = True
        self.driver.loadConfig(self.config)

        self.scaleParameters = scaleparameters.makeWithScaleFactor(self.args['warehouses'], self.args['scalefactor'])
        ## DATA LOADER!!!
        if self.config['load']:
            logging.info("Loading TPC-C benchmark data using %s" % (self.driver))
            tpcc.startLoading(self.driverClass, self.scaleParameters, self.args, self.config)

        self.current_state = None
        self.start_time = time.time()
        self.accumulated_index_time = 0
        self.horizon = 12
        self.cr_step = 0

    def map_number_to_state(self, num):
        reorder_pos = int(num % (self.nS_reorder))
        payment_pos = int(reorder_pos % (self.nS_payment))
        delivery_pos = int((reorder_pos / self.nS_payment) % self.nS_delivery)
        new_order_pos = int((reorder_pos / self.nS_payment) / self.nS_delivery)
        index_pos = int((num / (self.nS_reorder)) % self.nS_index)
        parameter_value = int((num / (self.nS_reorder * self.nS_index)))
        # convert number to a state
        payment_state = self.validate_payment_permutation[payment_pos]
        delivery_state = self.validate_delivery_permutation[delivery_pos]
        new_order_state = self.validate_new_order_permutation[new_order_pos]
        # print payment_pos
        # print delivery_pos
        # print new_order_pos
        # print reorder_pos
        # print index_pos
        # print parameter_value
        index_state_string = np.binary_repr(int(index_pos), width=self.index_candidate_num)[::-1]
        # print index_state_string
        index_state = list(map(int, index_state_string))
        # print index_state
        parameter_pos = [0] * self.parameter_candidate_num
        # np.zeros(self.parameter_candidate_num, dtype=int)
        for i in range(self.parameter_candidate_num):
            parameter_pos[i] = (parameter_value % self.parameter_candidate[i])
            parameter_value = int(parameter_value / self.parameter_candidate[i])
        # print(payment_state)
        # print(index_state)
        # print(parameter_pos)
        return payment_state + delivery_state + new_order_state + index_state + parameter_pos
        # return ((payment_state, delivery_state, new_order_state), index_state, parameter_pos)

    def map_state_to_num(self, state):
        # decompose state
        payment_order_state = state[: self.payment_unit]
        delivery_order_state = state[self.payment_unit: self.payment_unit + self.delivery_unit]
        new_order_state = state[self.payment_unit + self.delivery_unit: self.reorder_unit]
        index_state = state[self.reorder_unit: self.reorder_unit + self.index_candidate_num]
        parameter_state = state[self.reorder_unit + self.index_candidate_num:]
        # print(state)

        # print reorder_state
        payment_pos = self.payment_permutation_to_position[''.join([str(int(x)) for x in payment_order_state])]
        # self.validate_payment_permutation.index(payment_order_state)
        delivery_pos = self.delivery_permutation_to_position[''.join([str(int(x)) for x in delivery_order_state])]
        # self.validate_delivery_permutation.index(delivery_order_state)
        new_order_pos = self.new_order_permutation_to_position[''.join([str(int(x)) for x in new_order_state])]
        # self.validate_new_order_permutation.index(new_order_state)

        reorder_pos = new_order_pos * self.nS_payment * self.nS_delivery + delivery_pos * self.nS_payment + payment_pos
        # print reorder_pos
        # index_pos = 0
        # for bit in reversed(index_state):
        #     index_pos = (index_pos << 1) | bit
        # print index_pos

        index_pos = int("".join([str(int(a)) for a in reversed(index_state)]), 2)

        parameter_pos = 0
        parameter_base = 1
        for i in range(len(self.parameter_candidate)):
            parameter_pos = parameter_pos + parameter_state[i] * parameter_base
            parameter_base = parameter_base * self.parameter_candidate[i]
        # print parameter_pos
        # list can not be used as hash key.
        # print(payment_pos)
        # print(delivery_pos)
        # print(new_order_pos)
        # print(reorder_pos)
        # print(index_pos)
        # print(parameter_pos)
        pos = reorder_pos + index_pos * self.nS_reorder + parameter_pos * self.nS_index * self.nS_reorder
        return int(pos)

    def choose_all_heavy_actions(self, state):
        index_state = state[self.reorder_unit: self.reorder_unit + self.index_candidate_num]
        # check which indices are available or not
        candidate_index_action = [self.nA_reorder + i for i in range(len(index_state)) if index_state[i] == 0]
        return candidate_index_action

    def choose_all_actions(self, state):
        # get all available actions at the current state
        payment_order_state = state[: self.payment_unit]
        delivery_order_state = state[self.payment_unit: self.payment_unit + self.delivery_unit]
        new_order_state = state[self.payment_unit + self.delivery_unit: self.reorder_unit]
        index_state = state[self.reorder_unit: self.reorder_unit + self.index_candidate_num]
        parameter_state = state[self.reorder_unit + self.index_candidate_num:]

        # print(state)
        # check which indices are available or not
        candidate_index_action = [self.nA_reorder + i for i in range(len(index_state)) if index_state[i] == 0]
        # get the validate actions of each reorder state
        candidate_payment_reorder_action = [i for i in range(self.payment_unit - 1) if ((
                                                                                            payment_order_state[i],
                                                                                            payment_order_state[
                                                                                                i + 1]) not in self.payment_unit_constraint) and (
                                                    payment_order_state[i] < payment_order_state[i + 1])]
        candidate_delivery_reorder_action = [self.nA_reorder_payment + i for i in range(self.delivery_unit - 1) if ((
                                                                                                                        delivery_order_state[
                                                                                                                            i],
                                                                                                                        delivery_order_state[
                                                                                                                            i + 1]) not in self.delivery_unit_constraint) and (
                                                     delivery_order_state[i] < delivery_order_state[i + 1])]
        candidate_new_order_reorder_action = [self.nA_reorder_payment + self.nA_reorder_delivery + i for i in
                                              range(self.new_order_unit - 1) if ((
                                                                                     new_order_state[i],
                                                                                     new_order_state[
                                                                                         i + 1]) not in self.new_order_unit_constraint) and (
                                                      new_order_state[i] < new_order_state[i + 1])]

        # only allow to change the non-changed parameter
        candidate_parameter_action = []
        parameter_sum = 0
        for i in range(len(parameter_state)):
            if parameter_state[i] == 0:
                for j in range(1, self.parameter_candidate[i]):
                    candidate_parameter_action.append(self.nA_reorder + self.nA_index + parameter_sum + j)
            parameter_sum += self.parameter_candidate[i]

        # print(candidate_parameter_action)
        all_actions = candidate_payment_reorder_action + candidate_delivery_reorder_action + candidate_new_order_reorder_action + candidate_index_action + candidate_parameter_action
        # # get the parameter actions
        # candidate_parameter_action = range(self.nA_parameter)
        # # notice, here i don't preclude the parameter actions are already created
        # all_actions = [((payment_action, delivery_action, new_order_action), index_action, parameter_action)
        #                for payment_action in candidate_payment_reorder_action for delivery_action in
        #                candidate_delivery_reorder_action
        #                for new_order_action in candidate_new_order_reorder_action for index_action in
        #                candidate_index_action
        #                for parameter_action in candidate_parameter_action]
        return all_actions

    def choose_all_light_actions(self, state):
        # get all available actions at the current state
        payment_order_state = state[: self.payment_unit]
        delivery_order_state = state[self.payment_unit: self.payment_unit + self.delivery_unit]
        new_order_state = state[self.payment_unit + self.delivery_unit: self.reorder_unit]
        parameter_state = state[self.reorder_unit + self.index_candidate_num:]

        # get the validate actions of each reorder state
        candidate_payment_reorder_action = [i for i in range(self.payment_unit - 1) if ((
                                                                                            payment_order_state[i],
                                                                                            payment_order_state[
                                                                                                i + 1]) not in self.payment_unit_constraint) and (
                                                    payment_order_state[i] < payment_order_state[i + 1])]
        candidate_delivery_reorder_action = [self.nA_reorder_payment + i for i in range(self.delivery_unit - 1) if ((
                                                                                                                        delivery_order_state[
                                                                                                                            i],
                                                                                                                        delivery_order_state[
                                                                                                                            i + 1]) not in self.delivery_unit_constraint) and (
                                                     delivery_order_state[i] < delivery_order_state[i + 1])]
        candidate_new_order_reorder_action = [self.nA_reorder_payment + self.nA_reorder_delivery + i for i in
                                              range(self.new_order_unit - 1) if ((
                                                                                     new_order_state[i],
                                                                                     new_order_state[
                                                                                         i + 1]) not in self.new_order_unit_constraint) and (
                                                      new_order_state[i] < new_order_state[i + 1])]

        # only allow to change the non-changed parameter
        candidate_parameter_action = []
        parameter_sum = 0
        for i in range(len(parameter_state)):
            if parameter_state[i] == 0:
                for j in range(1, self.parameter_candidate[i]):
                    candidate_parameter_action.append(self.nA_reorder + self.nA_index + parameter_sum + j)
            parameter_sum += self.parameter_candidate[i]

        all_light_actions = candidate_payment_reorder_action + candidate_delivery_reorder_action + candidate_new_order_reorder_action + candidate_parameter_action
        return all_light_actions

    def obtain_next_state(self, state, action):
        assert action < self.nA
        payment_order = state[: self.payment_unit]
        delivery_order = state[self.payment_unit: self.payment_unit + self.delivery_unit]
        new_order_order = state[self.payment_unit + self.delivery_unit: self.reorder_unit]
        index_state = state[self.reorder_unit: self.reorder_unit + self.index_candidate_num]
        parameter_state = state[self.reorder_unit + self.index_candidate_num:]
        if (action < self.nA_reorder_payment):
            # action is reorder action
            payment_reorder_action = action
            if not (self.check_constraint(self.payment_unit_constraint, payment_order[payment_reorder_action],
                                          payment_order[payment_reorder_action + 1])):
                print("error")
            payment_order[payment_reorder_action], payment_order[payment_reorder_action + 1] = payment_order[
                                                                                                   payment_reorder_action + 1], \
                                                                                               payment_order[
                                                                                                   payment_reorder_action]
        elif (action < self.nA_reorder_payment + self.nA_reorder_delivery):
            # action is delivery action
            delivery_reorder_action = action - self.nA_reorder_payment
            if not (self.check_constraint(self.delivery_unit_constraint, delivery_order[delivery_reorder_action],
                                          delivery_order[delivery_reorder_action + 1])):
                print("error")
            delivery_order[delivery_reorder_action], delivery_order[delivery_reorder_action + 1] = delivery_order[
                                                                                                       delivery_reorder_action + 1], \
                                                                                                   delivery_order[
                                                                                                       delivery_reorder_action]
        elif (action < self.nA_reorder_payment + self.nA_reorder_delivery + self.nA_reorder_new_order):
            # action is new order action
            new_order_reorder_action = action - self.nA_reorder_payment - self.nA_reorder_delivery
            if not (self.check_constraint(self.new_order_unit_constraint, new_order_order[new_order_reorder_action],
                                          new_order_order[new_order_reorder_action + 1])):
                print("error")
            new_order_order[new_order_reorder_action], new_order_order[new_order_reorder_action + 1] = new_order_order[
                                                                                                           new_order_reorder_action + 1], \
                                                                                                       new_order_order[
                                                                                                           new_order_reorder_action]
        elif (action < self.nA_reorder + self.nA_index):
            # action is the index action
            index_action = action - self.nA_reorder
            index_state[index_action] = 1
        else:
            # action is the parameter action
            parameter_action = action - self.nA_reorder - self.nA_index
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
        next_state = payment_order + delivery_order + new_order_order + index_state + parameter_state
        return next_state, self.map_state_to_num(next_state)

    def step_without_evaluation(self, action):
        # print("try action without evaluation")
        # print(action)
        # get current state
        state = self.current_state
        # expand those states
        # reorder_current_state, index_current_state, parameter_current_state = state
        # payment_order, delivery_order, new_order_order = reorder_current_state

        payment_order = state[: self.payment_unit]
        delivery_order = state[self.payment_unit: self.payment_unit + self.delivery_unit]
        new_order_order = state[self.payment_unit + self.delivery_unit: self.reorder_unit]
        index_current_state = state[self.reorder_unit: self.reorder_unit + self.index_candidate_num]
        parameter_current_state = state[self.reorder_unit + self.index_candidate_num:]

        invoke_payment_order = list(payment_order)
        invoke_delivery_order = list(delivery_order)
        invoke_new_order_order = list(new_order_order)

        if (action < self.nA_reorder_payment):
            # the action is payment transaction reorder
            payment_reorder_action = action
            prev_unit = invoke_payment_order[payment_reorder_action]
            next_unit = invoke_payment_order[payment_reorder_action + 1]
            # when reorder does not influence the constraint requirement
            if (self.check_constraint(self.payment_unit_constraint, prev_unit, next_unit)):
                invoke_payment_order[payment_reorder_action], invoke_payment_order[payment_reorder_action + 1] = \
                    invoke_payment_order[payment_reorder_action + 1], invoke_payment_order[payment_reorder_action]
        elif (action < self.nA_reorder_payment + self.nA_reorder_delivery):
            delivery_reorder_action = action - self.nA_reorder_payment
            prev_unit = invoke_delivery_order[delivery_reorder_action]
            next_unit = invoke_delivery_order[delivery_reorder_action + 1]
            if (self.check_constraint(self.delivery_unit_constraint, prev_unit, next_unit)):
                invoke_delivery_order[delivery_reorder_action], invoke_delivery_order[delivery_reorder_action + 1] = \
                    invoke_delivery_order[delivery_reorder_action + 1], invoke_delivery_order[delivery_reorder_action]
        elif (action < self.nA_reorder_payment + self.nA_reorder_delivery + self.nA_reorder_new_order):
            new_order_reorder_action = action - self.nA_reorder_payment - self.nA_reorder_delivery
            prev_unit = invoke_new_order_order[new_order_reorder_action]
            next_unit = invoke_new_order_order[new_order_reorder_action + 1]
            if (self.check_constraint(self.new_order_unit_constraint, prev_unit, next_unit)):
                invoke_new_order_order[new_order_reorder_action], invoke_new_order_order[new_order_reorder_action + 1] = \
                    invoke_new_order_order[new_order_reorder_action + 1], invoke_new_order_order[
                        new_order_reorder_action]
        elif (action < self.nA_reorder + self.nA_index):
            index_action = action - self.nA_reorder
            # get the index change sql, create a new index
            if (index_current_state[index_action] == 1):
                print("index is already created, a redundant action")
                pass
            index_current_state[index_action] = 1
        else:
            assert (action < self.nA_reorder + self.nA_index + self.nA_parameter)
            parameter_action = action - self.nA_reorder - self.nA_index
            # print(parameter_action)
            parameter_value = 0
            for parameter_type in range(len(self.parameter_candidate)):
                parameter_range = self.parameter_candidate[parameter_type]
                if parameter_action < (parameter_value + parameter_range):
                    parameter_value = parameter_action - parameter_value
                    break
                parameter_value = parameter_value + parameter_range
            parameter_current_state[parameter_type] = parameter_value

        next_state = np.concatenate(
            [invoke_payment_order, invoke_delivery_order, invoke_new_order_order, index_current_state,
             parameter_current_state])

        self.current_state = next_state
        return next_state

    def evaluate(self):
        state = self.current_state
        print ("current state:")
        print (state)
        payment_order = state[: self.payment_unit]
        delivery_order = state[self.payment_unit: self.payment_unit + self.delivery_unit]
        new_order_order = state[self.payment_unit + self.delivery_unit: self.reorder_unit]
        index_current_state = state[self.reorder_unit: self.reorder_unit + self.index_candidate_num]
        parameter_current_state = state[self.reorder_unit + self.index_candidate_num:]

        invoke_payment_order = list(payment_order)
        invoke_delivery_order = list(delivery_order)
        invoke_new_order_order = list(new_order_order)

        # map invoke transaction order to procedure indentifier
        invoke_payment_proc = self.payment_permutation_to_position[''.join([str(int(x)) for x in invoke_payment_order])]
        invoke_delivery_proc = self.delivery_permutation_to_position[
            ''.join([str(int(x)) for x in invoke_delivery_order])]
        invoke_new_order_proc = self.new_order_permutation_to_position[
            ''.join([str(int(x)) for x in invoke_new_order_order])]

        # create all indices at the current state
        for i in range(self.index_candidate_num):
            if (index_current_state[i] == 1):
                index_creation_sql = index.candidate_indices[i]
                print(index_creation_sql)
                self.driver.buildIndex(index_creation_sql)

        # change system parameter
        for i in range(self.parameter_candidate_num):
            parameter_choice = int(parameter_current_state[i])
            parameter_change_sql = parameter.candidate_dbms_parameter[i][parameter_choice]
            print(parameter_change_sql)
            self.driver.setSystemParameter(parameter_change_sql)

        # invoke transaction reorder



        # invoke transaction reorder
        tx_results = tpcc.startExecution(self.driverClass, self.scaleParameters, self.args, self.config)

        # obtain results
        print(tx_results.show())
        reward = tx_results.total_rate
        return reward

    def evaluate_without_indices(self):
        state = self.current_state
        print ("current state:")
        print (state)
        payment_order = state[: self.payment_unit]
        delivery_order = state[self.payment_unit: self.payment_unit + self.delivery_unit]
        new_order_order = state[self.payment_unit + self.delivery_unit: self.reorder_unit]
        parameter_current_state = state[self.reorder_unit + self.index_candidate_num:]

        invoke_payment_order = list(payment_order)
        invoke_delivery_order = list(delivery_order)
        invoke_new_order_order = list(new_order_order)

        # map invoke transaction order to procedure indentifier
        invoke_payment_proc = self.payment_permutation_to_position[''.join([str(int(x)) for x in invoke_payment_order])]
        invoke_delivery_proc = self.delivery_permutation_to_position[
            ''.join([str(int(x)) for x in invoke_delivery_order])]
        invoke_new_order_proc = self.new_order_permutation_to_position[
            ''.join([str(int(x)) for x in invoke_new_order_order])]

        # change system parameter
        for i in range(self.parameter_candidate_num):
            parameter_choice = int(parameter_current_state[i])
            parameter_change_sql = parameter.candidate_dbms_parameter[i][parameter_choice]
            print(parameter_change_sql)
            self.driver.setSystemParameter(parameter_change_sql)

        # invoke transaction reorder
        proc_info = {"payment": invoke_payment_proc, "delivery": invoke_delivery_proc,
                     "new_order": invoke_new_order_proc}
        print(proc_info)
        self.scaleParameters.changeInvokeProcedure(proc_info)

        # invoke transaction reorder
        tx_results = tpcc.startExecution(self.driverClass, self.scaleParameters, self.args, self.config)
        # obtain results
        print(tx_results.show())
        reward = tx_results.total_rate
        return reward

    def step(self, action):
        print("try action")
        print(action)
        # get current state
        state = self.current_state
        # expand those states
        # reorder_current_state, index_current_state, parameter_current_state = state
        # payment_order, delivery_order, new_order_order = reorder_current_state

        payment_order = state[: self.payment_unit]
        delivery_order = state[self.payment_unit: self.payment_unit + self.delivery_unit]
        new_order_order = state[self.payment_unit + self.delivery_unit: self.reorder_unit]
        index_current_state = state[self.reorder_unit: self.reorder_unit + self.index_candidate_num]
        parameter_current_state = state[self.reorder_unit + self.index_candidate_num:]

        invoke_payment_order = list(payment_order)
        invoke_delivery_order = list(delivery_order)
        invoke_new_order_order = list(new_order_order)
        # extract the action type and value
        action_type = -1
        if (action < self.nA_reorder_payment):
            print("try payment action")
            # the action is payment transaction reorder
            action_type = 0
            payment_reorder_action = action
            prev_unit = invoke_payment_order[payment_reorder_action]
            next_unit = invoke_payment_order[payment_reorder_action + 1]
            # when reorder does not influence the constraint requirement
            if (self.check_constraint(self.payment_unit_constraint, prev_unit, next_unit)):
                invoke_payment_order[payment_reorder_action], invoke_payment_order[payment_reorder_action + 1] = \
                    invoke_payment_order[payment_reorder_action + 1], invoke_payment_order[payment_reorder_action]
        elif (action < self.nA_reorder_payment + self.nA_reorder_delivery):
            print("try delivery action")
            action_type = 1
            delivery_reorder_action = action - self.nA_reorder_payment
            prev_unit = invoke_delivery_order[delivery_reorder_action]
            next_unit = invoke_delivery_order[delivery_reorder_action + 1]
            if (self.check_constraint(self.delivery_unit_constraint, prev_unit, next_unit)):
                invoke_delivery_order[delivery_reorder_action], invoke_delivery_order[delivery_reorder_action + 1] = \
                    invoke_delivery_order[delivery_reorder_action + 1], invoke_delivery_order[delivery_reorder_action]
        elif (action < self.nA_reorder_payment + self.nA_reorder_delivery + self.nA_reorder_new_order):
            print("try new order action")
            action_type = 2
            new_order_reorder_action = action - self.nA_reorder_payment - self.nA_reorder_delivery
            prev_unit = invoke_new_order_order[new_order_reorder_action]
            next_unit = invoke_new_order_order[new_order_reorder_action + 1]
            if (self.check_constraint(self.new_order_unit_constraint, prev_unit, next_unit)):
                invoke_new_order_order[new_order_reorder_action], invoke_new_order_order[new_order_reorder_action + 1] = \
                    invoke_new_order_order[new_order_reorder_action + 1], invoke_new_order_order[
                        new_order_reorder_action]
        elif (action < self.nA_reorder + self.nA_index):
            print("try indices")
            action_type = 3
            index_action = action - self.nA_reorder
            # get the index change sql, create a new index
            if (index_current_state[index_action] == 1):
                print("index is already created, a redundant action")
            else:
                index_current_state[index_action] = 1
                index_creation_sql = index.candidate_indices[index_action]
                # index_drop_sql = index.candidate_indices_drop[index_action]
                print(index_creation_sql)
                start_time = time.time()
                self.driver.buildIndex(index_creation_sql)
                end_time = time.time()
                index_time = (end_time - start_time)
                self.accumulated_index_time = self.accumulated_index_time + index_time
        else:
            print("try parameter")
            assert (action < self.nA_reorder + self.nA_index + self.nA_parameter)
            action_type = 4
            parameter_action = action - self.nA_reorder - self.nA_index
            # print(parameter_action)
            parameter_value = 0
            for parameter_type in range(len(self.parameter_candidate)):
                parameter_range = self.parameter_candidate[parameter_type]
                if parameter_action < (parameter_value + parameter_range):
                    parameter_value = parameter_action - parameter_value
                    break
                parameter_value = parameter_value + parameter_range
            parameter_current_state[parameter_type] = parameter_value
            parameter_sql = parameter.candidate_dbms_parameter[parameter_type][parameter_value]
            # switch system parameter
            print(parameter_sql)
            # get the parameter change sql, change one parameter
            self.driver.setSystemParameter(parameter_sql)

        print(invoke_payment_order)
        print(invoke_new_order_order)
        print(invoke_delivery_order)

        # map invoke transaction order to procedure indentifier
        invoke_payment_proc = self.payment_permutation_to_position[''.join([str(int(x)) for x in invoke_payment_order])]
        invoke_delivery_proc = self.delivery_permutation_to_position[
            ''.join([str(int(x)) for x in invoke_delivery_order])]
        invoke_new_order_proc = self.new_order_permutation_to_position[
            ''.join([str(int(x)) for x in invoke_new_order_order])]

        # invoke transaction reorder
        proc_info = {"payment": invoke_payment_proc, "delivery": invoke_delivery_proc,
                     "new_order": invoke_new_order_proc}
        print(proc_info)
        self.scaleParameters.changeInvokeProcedure(proc_info)

        # invoke transaction reorder
        tx_results = tpcc.startExecution(self.driverClass, self.scaleParameters, self.args, self.config)

        # obtain results
        print(tx_results.show())
        reward = tx_results.total_commit

        # clean up
        # if action_type == 3:
        #     index_drop_sql = index.candidate_indices_drop[index_action]
        #     self.driver.dropIndex(index_drop_sql)
        # invoke index selection, create indices for the given table copies

        # invoke parameter change
        # switch to new parameter
        next_state = np.concatenate(
            [invoke_payment_order, invoke_delivery_order, invoke_new_order_order, index_current_state,
             parameter_current_state])
        self.current_state = next_state

        print("index time:", self.accumulated_index_time)
        # info = {"reward": reward, "state": state}
        info = {}

        current_time = time.time()
        print("current time:", (current_time - self.start_time))
        self.cr_step += 1
        if self.cr_step == self.horizon:
            self.cr_step = 0
            return next_state, reward, True, {}
        else:
            return next_state, reward, False, {}

    def index_step(self, add_actions, remove_actions):
        # one index build or drop action
        for add_action in add_actions:
            index_to_create = index.candidate_indices[add_action - self.nA_reorder]
            # build index action
            print("create index")
            print(index_to_create)
            self.driver.buildIndex(index_to_create)
        for remove_action in remove_actions:
            index_to_drop = index.candidate_indices[remove_action - self.nA_reorder]
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

    def remove(self, s):
        print("remove")

    def reset(self):
        if self.current_state is not None:
            index_current_state = self.current_state[self.reorder_unit: self.reorder_unit + self.index_candidate_num]
            parameter_current_state = self.current_state[self.reorder_unit + self.index_candidate_num:]
            # drop all indices at the current state
            for i in range(self.index_candidate_num):
                if index_current_state[i] == 1:
                    index_drop_sql = index.candidate_indices[i]
                    self.driver.dropIndex(index_drop_sql)
            # set the parameter to default value
            for i in range(self.parameter_candidate_num):
                parameter_change_sql = parameter.candidate_dbms_parameter[i][0]
                self.driver.setSystemParameter(parameter_change_sql)

        # reset the state to init state
        # self.current_state = [
        #     [np.arange(self.payment_unit), np.arange(self.delivery_unit), np.arange(self.new_order_unit)],
        #     np.zeros(self.index_candidate_num), np.zeros(self.parameter_candidate_num)]

        self.current_state = np.concatenate([np.arange(self.payment_unit),
                                             np.arange(self.delivery_unit),
                                             np.arange(self.new_order_unit),
                                             np.zeros(self.index_candidate_num),
                                             np.zeros(self.parameter_candidate_num)])
        return self.current_state

    def render(self, mode='human', close=False):
        print("render")

    def reset_database(self):
        self.driver.resetDatabase()
        # reset the system parameter
        if self.current_state is not None:
            # set the parameter to default value
            for i in range(self.parameter_candidate_num):
                parameter_change_sql = parameter.candidate_dbms_parameter[i][0]
                self.driver.setSystemParameter(parameter_change_sql)
        self.current_state = np.concatenate([np.arange(self.payment_unit),
                                             np.arange(self.delivery_unit),
                                             np.arange(self.new_order_unit),
                                             np.zeros(self.index_candidate_num),
                                             np.zeros(self.parameter_candidate_num)])



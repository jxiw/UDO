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
import parameter
import index
from tpcc import loader


class OptimizationGameEnv(gym.Env):

    def __init__(self):
        # init
        super(OptimizationGameEnv, self).__init__()

        # the reorder unit of each transaction
        self.payment_unit = 7
        self.delivery_unit = 7
        self.new_order_unit = 5

        self.payment_unit_constraint = [(4, 5), (0, 6), (2, 6), (4, 6)]
        self.delivery_unit_constraint = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (2, 6), (5, 6)]
        self.new_order_unit_constraint = [(2, 3), (2, 4), (3, 4)]

        self.reorder_action_space = spaces.Tuple((spaces.MultiDiscrete(self.payment_unit - 1),
                                                  spaces.MultiDiscrete(self.delivery_unit - 1),
                                                  spaces.MultiDiscrete(self.new_order_unit - 1)))

        # index action space
        self.index_candidate = 10
        self.index_space = spaces.Discrete(self.index_candidate)

        # parameter action space
        # e.g., the first parameter has 4 choices, the second parameter has 4 choices, and the third and fourth parameter has 4 choices
        self.parameter_candidate = [4, 4, 4, 4]
        self.parameter_candidate_num = len(self.parameter_candidate)
        self.parameter_candidate_total_choice = sum(self.parameter_candidate)
        self.parameter_space = spaces.MultiDiscrete([self.parameter_candidate_num, max(self.parameter_candidate)])

        # combine the actions from 3 sub actions
        # define action and observation space
        self.action_space = spaces.Tuple((self.reorder_action_space, self.index_space, self.parameter_space))

        self.reorder_observation_space = spaces.Tuple((spaces.MultiDiscrete(self.payment_unit),
                                                       spaces.MultiDiscrete(self.delivery_unit),
                                                       spaces.MultiDiscrete(self.new_order_unit)))

        self.index_observation_space = spaces.MultiBinary(self.index_candidate)
        self.parameter_observation_space = spaces.MultiDiscrete(self.parameter_candidate)

        self.observation_space = spaces.Tuple(
            (self.reorder_observation_space, self.index_observation_space, self.parameter_observation_space))
        self.args = {
            'debug': True,
            'system': 'mysql',
            'ddl': '',
            'clients': 3,
            'warehouses': 1,
            'scalefactor': 10,
            'stop_on_error': True,
            'duration': 10
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

    def choose_action(self, state):
        # get all available actions at the current state
        reorder_state, index_state, parameter_state = state
        payment_order_state, delivery_order_state, new_order_state = reorder_state
        # check which indices are available or not
        candidate_index = [i for i in range(len(index_state)) if index_state[i] == 0]
        # choose a parameter to switch
        choose_parameter_type = random.randint(0, self.parameter_candidate_num - 1)
        choose_parameter_num = random.randint(0, self.parameter_candidate[choose_parameter_type] - 1)
        # get the validate actions of each reorder state
        candidate_payment_reorder_action = [i for i in range(self.payment_unit - 1) if (
        payment_order_state[i], payment_order_state[i + 1]) not in self.payment_unit_constraint]
        candidate_delivery_reorder_action = [i for i in range(self.delivery_unit - 1) if (
        delivery_order_state[i], delivery_order_state[i + 1]) not in self.delivery_unit_constraint]
        candidate_new_order_reorder_action = [i for i in range(self.new_order_unit - 1) if (
        new_order_state[i], new_order_state[i + 1]) not in self.new_order_unit_constraint]
        print candidate_payment_reorder_action
        print candidate_delivery_reorder_action
        print candidate_new_order_reorder_action
        return ((random.choice(candidate_payment_reorder_action), random.choice(candidate_delivery_reorder_action),
                 random.choice(candidate_new_order_reorder_action)), random.choice(candidate_index), (choose_parameter_type, choose_parameter_num))

    def step(self, action):
        print(action)
        # extract reorder action, index action and parameter action.
        reorder_action, index_action, parameter_action = action
        (payment_reorder_action, delivery_reorder_action, new_order_reorder_action) = reorder_action

        reorder_current_state, index_current_state, parameter_current_state = self.current_state
        payment_order, delivery_order, new_order_order = reorder_current_state

        # swap the order
        payment_order[payment_reorder_action], payment_order[payment_reorder_action + 1] = payment_order[payment_reorder_action + 1], payment_order[payment_reorder_action]
        delivery_order[delivery_reorder_action], delivery_order[delivery_reorder_action + 1] = delivery_order[delivery_reorder_action + 1], delivery_order[delivery_reorder_action]
        new_order_order[new_order_reorder_action], new_order_order[new_order_reorder_action + 1] = new_order_order[new_order_reorder_action + 1], new_order_order[new_order_reorder_action]

        # invoke transaction reorder
        invoke_orders = {"payment_order": payment_order, "delivery_order": delivery_order, "new_order_order": new_order_order}
        self.scaleParameters.changeInvokeOrder(invoke_orders)

        # get the index change sql, create a new index
        index_current_state[index_action] = 1
        index_sql = index.candidate_indices_creation[index_action]

        # get the parameter change sql, change one parameter
        print parameter_action
        parameter_type, parameter_value = parameter_action
        parameter_current_state[parameter_type] = parameter_value
        parameter_sql = parameter.candidate_dbms_parameter[parameter_type][parameter_value]

        # invoke transaction reorder
        results = tpcc.startExecution(self.driverClass, self.scaleParameters, self.args, self.config)
        print(results.show())
        reward = results.total_commit
        # invoke index selection
        # create indices for the given table copies

        # invoke parameter change
        self.current_state = ((payment_order, delivery_order, new_order_order), index_current_state, parameter_current_state)
        return self.current_state, reward, None, None

    def remove(self, s):
        print("remove")

    def reset(self):
        # reset the state to init state
        self.current_state = ((np.arange(self.payment_unit), np.arange(self.delivery_unit), np.arange(self.new_order_unit)),
                np.zeros(self.index_candidate), np.zeros(self.parameter_candidate_num))
        return self.current_state

    def render(self, mode='human', close=False):
        print("render")

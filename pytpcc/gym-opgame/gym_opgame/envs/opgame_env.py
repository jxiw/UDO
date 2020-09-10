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
from tpcc import loader


class OptimizationGameEnv(gym.Env):

    def filterPermutationWithConstraint(self, all_permutation, constraints):
        permutation_with_constraint = []
        for p in all_permutation:
            # check whether this permutation is validate
            flag = True
            for constraint in constraints:
                firstElementPos = p.index(constraint[0])
                secondElementPos = p.index(constraint[1])
                if firstElementPos > secondElementPos:
                    flag = False
                    break
            if flag:
                permutation_with_constraint.append(p)
        return permutation_with_constraint

    def __init__(self):
        # init
        super(OptimizationGameEnv, self).__init__()
        self.payment_unit = 7
        self.delivery_unit = 7
        self.new_order_unit = 5

        # calculate the number of reorder action
        # self.payment_action_space = math.factorial(self.payment_unit)
        # self.delivery_action_space = math.factorial(self.delivery_unit)
        # self.new_order_action_space = math.factorial(self.new_order_unit)

        # permutation with order constraint
        # unit 4 must be ahead of unit 5 ...
        payment_action_constraint = [(4, 5), (0, 6), (2, 6), (4, 6)]
        payment_all_permutation = itertools.permutations(range(0, self.payment_unit))
        self.validate_payment_permutation = self.filterPermutationWithConstraint(payment_all_permutation,
                                                                                 payment_action_constraint)

        delivery_action_constraint = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (2, 6), (5, 6)]
        delivery_all_permutation = itertools.permutations(range(0, self.delivery_unit))
        self.validate_delivery_permutation = self.filterPermutationWithConstraint(delivery_all_permutation,
                                                                                  delivery_action_constraint)

        new_order_action_constraint = [(2, 3), (2, 4), (3, 4)]
        new_order_all_permutation = itertools.permutations(range(0, self.new_order_unit))
        self.validate_new_order_permutation = self.filterPermutationWithConstraint(new_order_all_permutation,
                                                                                   new_order_action_constraint)

        self.payment_action_space = len(self.validate_payment_permutation)
        self.delivery_action_space = len(self.validate_delivery_permutation)
        self.new_order_action_space = len(self.validate_new_order_permutation)

        # reorder action space
        # self.reorder_payment_space = spaces.Discrete(self.payment_num)
        # self.reorder_delivery_space = spaces.Discrete(self.delivery_num)
        # self.reorder_new_order_space = spaces.Discrete(self.reorder_new_order_space)
        self.reorder_candidate = [self.payment_action_space, self.delivery_action_space, self.new_order_action_space]
        self.reorder_space = spaces.MultiDiscrete(self.reorder_candidate)

        # index action space
        self.index_candidate = 10
        self.index_space = spaces.MultiBinary(self.index_candidate)

        # parameter action space
        # e.g., the first parameter has 5 choices, the second parameter has 4 choices, and the third parameter has 6 choices
        self.parameter_candidate = [5, 4, 6]
        self.parameter_space = spaces.MultiDiscrete(self.parameter_candidate)

        # combine the actions from 3 sub actions
        # define action and observation space
        self.action_space = spaces.Tuple((self.reorder_space, self.index_space, self.parameter_space))

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

    def sample(self):
        print("sample")

    def step(self, action):
        print(action)
        # extract reorder action, index action and parameter action.
        reorder_action, index_action, parameter_action = action
        print(reorder_action)
        # map action to reorder unit
        # use the lehmer code to map a given integer to a permutation
        payment_order_num = random.randint(0, self.payment_action_space - 1)
        # reorder_action[0]
        delivery_order_num = random.randint(0, self.delivery_action_space - 1)
        # reorder_action[1]
        new_order_order_num = random.randint(0, self.new_order_action_space - 1)
        # reorder_action[1]

        # Lehmer code: map integer to a permutation array
        # payment_perm = permutation.integerToPerm(self.payment_unit, payment_order_num)
        # delivery_perm = permutation.integerToPerm(self.delivery_unit, delivery_order_num)
        # new_order_perm = permutation.integerToPerm(self.new_order_unit, new_order_order_num)

        # permutation array based on the index
        payment_perm = self.validate_payment_permutation[payment_order_num]
        delivery_perm = self.validate_delivery_permutation[delivery_order_num]
        new_order_perm = self.validate_new_order_permutation[new_order_order_num]
        print payment_perm
        print delivery_perm
        print new_order_perm

        # invoke transaction reorder
        invoke_orders = {"payment_order": payment_perm, "delivery_order": delivery_perm,
                         "new_order_order": new_order_perm}
        self.scaleParameters.changeInvokeOrder(invoke_orders)
        results = tpcc.startExecution(self.driverClass, self.scaleParameters, self.args, self.config)
        print(results.show())
        reward = results.total_commit
        # invoke index selection
        # create indices for the given table copies

        # invoke parameter change

        return None, reward, None, None

    def reset(self):
        print("reset")

    def render(self, mode='human', close=False):
        print("render")

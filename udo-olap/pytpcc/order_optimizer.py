import itertools
import math

from scipy.optimize import minimize
import numpy as np
import gurobipy as gp
from gurobipy import GRB


class OrderOptimizer:
    def __init__(self, index_card_info):
        self.index_card_info = index_card_info

    def index_build_cost(self, current_index_list):
        return sum(self.index_card_info[current_index] for current_index in current_index_list)

    def min_cost_order(self, selected_action_batch):
        # determine the order to evaluate those actions of the given batch
        # dp algorithm
        batch_size = len(selected_action_batch)
        if batch_size < 3:
            return range(batch_size)
        else:
            selected_action_batch_set = [set(batch) for batch in selected_action_batch]
            # take the first
            first_action = selected_action_batch_set[0]
            second_action = selected_action_batch_set[1]
            # cost for the first two elements
            common = first_action.intersection(second_action)
            cost = self.index_build_cost(first_action) + self.index_build_cost(second_action) - self.index_build_cost(
                common)
            order = [0, 1]
            for selected_action_idx in range(2, len(selected_action_batch_set)):
                # obtain select action
                selected_action = selected_action_batch_set[selected_action_idx]
                # consider to insert the new action to the first or last element
                # if insert to first element
                # current_cost1 = cost + len(selected_action) - len(
                #     selected_action.intersection(selected_action_batch_set[order[0]]))
                # current_cost2 = cost + len(selected_action) - len(
                #     selected_action.intersection(selected_action_batch_set[order[-1]]))
                current_cost1 = cost + self.index_build_cost(selected_action) - self.index_build_cost(
                    selected_action.intersection(selected_action_batch_set[order[0]]))
                current_cost2 = cost + self.index_build_cost(selected_action) - self.index_build_cost(
                    selected_action.intersection(selected_action_batch_set[order[-1]]))
                if current_cost2 > current_cost1:
                    min_cost = current_cost1
                    min_pos = -1
                else:
                    min_cost = current_cost2
                    min_pos = len(order) - 1
                # consider to insert the new action to the middle element
                for insert_pos in range(0, len(order) - 1):
                    prev_pos = order[insert_pos]
                    next_pos = order[insert_pos + 1]
                    current_cost = cost + self.index_build_cost(selected_action_batch_set[prev_pos].intersection(
                        selected_action_batch_set[next_pos])) - self.index_build_cost(
                        selected_action.intersection(selected_action_batch_set[prev_pos])) - self.index_build_cost(
                        selected_action.intersection(selected_action_batch_set[next_pos])) + self.index_build_cost(
                        selected_action)
                    if current_cost < min_cost:
                        min_cost = current_cost
                        min_pos = insert_pos
                # update the order
                order.insert(min_pos + 1, selected_action_idx)
                # print("current order")
                # print(order)
            print("min cost order ", order)
            return order

    # def min_cost_order_exp(self, selected_action_batch):
    #     batch_size = len(selected_action_batch)
    #     if batch_size < 3:
    #         return range(batch_size)
    #     else:
    #         selected_action_batch_set = [set(batch) for batch in selected_action_batch]
    #         # hashmap from string to cost
    #         cost = dict()
    #         order = dict()
    #         batch_size = len(selected_action_batch)
    #         for i in range(batch_size):
    #             index_actions = selected_action_batch[i]
    #             cost[str(i)] = self.index_build_cost(index_actions)
    #         print("cost for each index:", cost)
    #         # generate min cost for each subset
    #         consider_reorder = range(batch_size)
    #         all_possible_orders = list(
    #             chain.from_iterable(combinations(consider_reorder, i) for i in range(batch_size + 1)))
    #         # chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))
    #         print("all_possible_subset")
    #         for current_order in all_possible_orders:
    #             if len(current_order) > 1:
    #                 # evaluate the cost of current_order
    #                 min_cost = float("inf")
    #                 min_order = ""
    #                 # test the insertion form each possible position
    #                 for i in range(1, len(current_order)):
    #                     before_order = current_order[:i]
    #                     before_order_str = ','.join(str(unit) for unit in before_order)
    #                     after_order = current_order[i:]
    #                     after_order_str = ','.join(str(unit) for unit in after_order)
    #                     print(before_order_str)
    #                     print(after_order_str)
    #                     current_cost = cost[before_order_str] + cost[after_order_str] - self.index_build_cost(
    #                         selected_action_batch_set[before_order[-1]].intersection(selected_action_batch_set[after_order[0]]))
    #                     if current_cost < min_cost:
    #                         min_cost = current_cost
    #                         min_order = before_order_str + after_order_str
    #                 current_order_str = ','.join(str(unit) for unit in current_order)
    #                 cost[current_order_str] = min_cost
    #                 order[current_order_str] = min_order
    #         print(cost)

    def min_cost_order_exp(self, selected_action_batch):
        batch_size = len(selected_action_batch)
        if batch_size < 3:
            return range(batch_size)
        else:
            batch_size = len(selected_action_batch)
            all_permutations = itertools.permutations(range(batch_size))
            min_cost = float("inf")
            min_order = []
            round = 0
            for permutation in all_permutations:
                # calculate the cost of all permutation
                current_cost = self.index_build_cost(selected_action_batch[permutation[0]])
                for i in range(1, batch_size):
                    build_config = [config for config in selected_action_batch[permutation[i]] if
                                    config not in selected_action_batch[permutation[i - 1]]]
                    current_cost += self.index_build_cost(build_config)
                if current_cost < min_cost:
                    min_cost = current_cost
                    min_order = permutation
                if round % 10000 == 0:
                    print("min_cost", min_cost)
                    print("min_order", min_order)
                round += 1
        print("min_cost", min_cost)
        print("min_order", min_order)
        return min_order

    # def min_cost_order_lp(self, selected_action_batch):
    #     batch_size = len(selected_action_batch)
    #     if batch_size < 3:
    #         return range(batch_size)
    #     else:
    #         def objective(x, costs, reorder_unit):
    #             reorder_unit = int(reorder_unit)
    #             value = 0
    #             for i in range(reorder_unit):
    #                 for j in range(reorder_unit - 1):
    #                     for k in range(reorder_unit):
    #                         value -= x[i * reorder_unit + j] * x[k * reorder_unit + j + 1] * costs[i][k]
    #             large_constant = 1E10
    #             constraint = 0
    #             for i in range(reorder_unit):
    #                 cost_i = 0
    #                 for j in range(reorder_unit):
    #                     cost_i += x[i * reorder_unit + j]
    #                 constraint += large_constant * abs(cost_i - 1)
    #             for j in range(reorder_unit):
    #                 cost_j = 0
    #                 for i in range(reorder_unit):
    #                     cost_j += x[i * reorder_unit + j]
    #                 constraint += large_constant * abs(cost_j - 1)
    #             # integer constraint
    #             for i in range(reorder_unit):
    #                 for j in range(reorder_unit):
    #                     constraint += large_constant * abs(x[i * reorder_unit + j] - math.ceil(x[i * reorder_unit + j]))
    #             return value + constraint
    #
    #         costs = np.zeros((batch_size, batch_size))
    #         for i in range(batch_size - 1):
    #             for j in range(i + 1, batch_size):
    #                 build_config = [config for config in selected_action_batch[i] if
    #                                 config in selected_action_batch[j]]
    #                 current_cost = self.index_build_cost(build_config)
    #                 costs[i][j] = current_cost
    #                 costs[j][i] = current_cost
    #                 # x = [[0] * batch_size] * batch_size
    #         x = np.zeros(batch_size * batch_size)
    #         for i in range(batch_size):
    #             x[i * batch_size + i] = 1
    #         cons = []
    #         l = {'type': 'ineq',
    #              'fun': lambda x, lb=0, i=1: x[i] - lb}
    #         u = {'type': 'ineq',
    #              'fun': lambda x, ub=1, i=1: ub - x[i]}
    #         cons.append(l)
    #         cons.append(u)
    #         # x_star = minimize(objective, x, args=(costs, batch_size), constraints=cons, method='SLSQP')
    #
    #         # sort the batch cost
    #         max_saving_cost = 0
    #         for i in range(batch_size):
    #             max_saving_cost += max(costs[i])
    #         print(max_saving_cost)
    #         # print(np.where(costs == costs.max()))
    #         pos = np.argmax(costs, axis=1)
    #         value = np.max(costs, axis=1)
    #         print("pos", pos)
    #         print("value", value)

    def min_cost_order_lp(self, selected_action_batch):
        # try:

        batch_size = len(selected_action_batch)

        costs = np.zeros((batch_size, batch_size))
        for i in range(batch_size - 1):
            for j in range(i + 1, batch_size):
                build_config = [config for config in selected_action_batch[i] if
                                config in selected_action_batch[j]]
                current_cost = self.index_build_cost(build_config)
                costs[i][j] = current_cost
                costs[j][i] = current_cost

        # Create a new model
        m = gp.Model("Min Order ILP")
        m.setParam('OutputFlag', 0)

        # Create variables
        z = m.addVars(batch_size, batch_size, batch_size, vtype=GRB.BINARY, name="z")
        x = m.addVars(batch_size, batch_size, vtype=GRB.BINARY, name="x")

        # print(costs)
        m.addConstrs((x.sum(i, '*') == 1
                      for i in range(batch_size)), name='R')

        m.addConstrs((x.sum('*', j) == 1
                      for j in range(batch_size)), name='C')

        # fun = sum[z[i][j][k] * self.index_build_cost(intersect_config) for i in range(batch_size) for j in range(batch_size - 1) for k in range(batch_size):
        #             if k != i:
        #                 intersect_config = [config for config in selected_action_batch[i] if
        #                                     config in selected_action_batch[k]]
        # fun += z[i][j][k] * self.index_build_cost(intersect_config)
        # print(str(i) + "," + str(j) + "," + str(k) + ",")
        # m.addConstr(z[i][j][k] - 0.5 * (x[i][j] + x[k][j+1]) <= 0, "1c" + str(i) + "," + str(j) + "," + str(k))

        fun = sum(z[i, j, k] * costs[i][k] for i in
                  range(batch_size) for j in range(batch_size - 1) for k in range(batch_size) if k != i)

        m.addConstrs(
            (z[i, j, k] - 0.5 * (x[i, j] + x[k, j + 1]) <= 0 for i in range(batch_size) for j in range(batch_size - 1)
            for k in range(batch_size)), name='linear')

        # # Create variables
        # x = [[None] * batch_size] * batch_size
        # for i in range(batch_size):
        #     for j in range(batch_size):
        #         x[i][j] = m.addVar(vtype=GRB.BINARY, name="x"+ str(i) + str(j))
        #         print("variable for: x", i, j)
        # z = [[[0] * batch_size] * batch_size] * batch_size
        # for i in range(batch_size):
        #     for j in range(batch_size - 1):
        #         for k in range(batch_size):
        #             current_variable = m.addVar(vtype=GRB.BINARY, name="z"+ str(i) + "," + str(j) + "," + str(k))
        #             z[i][j][k] = current_variable
        #             print("variable for z:", i, j, k)

        # fun = 0
        # for i in range(batch_size):
        #     for j in range(batch_size - 1):
        #         for k in range(batch_size):
        #             if k != i:
        #                 intersect_config = [config for config in selected_action_batch[i] if config in selected_action_batch[k]]
        #                 fun += z[i][j][k] * self.index_build_cost(intersect_config)
        #                 print(str(i) + "," + str(j) + "," + str(k) + ",")
        #                 # m.addConstr(z[i][j][k] - 0.5 * (x[i][j] + x[k][j+1]) <= 0, "1c" + str(i) + "," + str(j) + "," + str(k))
        # for i in range(batch_size):
        #     current_sum = 0
        #     constraint_str = ""
        #     for j in range(batch_size):
        #         current_sum += x[i][j]
        #         constraint_str += str(i) + "," + str(j) + " "
        #     print(constraint_str)
        #     m.addConstr(current_sum == 1, "2c" + str(i))
        # for i in range(batch_size):
        #     current_sum = 0
        #     constraint_str = ""
        #     for j in range(batch_size):
        #         current_sum += x[j][i]
        #         constraint_str += str(j) + "," + str(i) + " "
        #     m.addConstr(current_sum == 1, "3c" + str(i))
        #     print(constraint_str)

        # m.setObjective(x[0][0] + x[0][1], GRB.MAXIMIZE)
        m.setObjective(fun, GRB.MAXIMIZE)

        # Optimize model
        m.optimize()

        solution = m.getAttr('x', x)
        min_order = [0] * batch_size
        for i in range(batch_size):
            for j in range(batch_size):
                if solution[i, j] == 1:
                    min_order[j] = i

        print('Obj: %g' % m.objVal)
        return min_order

    # except gp.GurobiError as e:
    #     print('Error code ' + str(e.errno) + ': ' + str(e))
    #
    # except AttributeError as e:
    #     print('Encountered an attribute error')

    def min_cost_order_lp2(self, selected_action_batch):
        # try:

        batch_size = len(selected_action_batch)

        costs = np.zeros((batch_size, batch_size))
        for i in range(batch_size - 1):
            for j in range(i + 1, batch_size):
                build_config = [config for config in selected_action_batch[i] if
                                config in selected_action_batch[j]]
                current_cost = self.index_build_cost(build_config)
                costs[i][j] = current_cost
                costs[j][i] = current_cost

        # Create a new model
        m = gp.Model("Min Order ILP")
        m.setParam('OutputFlag', 0)

        # Create variables
        x = m.addVars(batch_size, batch_size, vtype=GRB.BINARY, name="x")

        # print(costs)
        m.addConstrs((x.sum(i, '*') == 1
                      for i in range(batch_size)), name='R')

        m.addConstrs((x.sum('*', j) == 1
                      for j in range(batch_size)), name='C')

        fun = sum(x[i, j] * x[k, j + 1] * costs[i][k] for i in
                  range(batch_size) for j in range(batch_size - 1) for k in range(batch_size) if k != i)

        m.setObjective(fun, GRB.MAXIMIZE)

        # Optimize model
        m.optimize()

        # for v in m.getVars():
        #     print('%s %g' % (v.varName, v.x))

        solution = m.getAttr('x', x)
        min_order = [0] * batch_size
        for i in range(batch_size):
            for j in range(batch_size):
                if solution[i, j] == 1:
                    min_order[j] = i

        print('Obj: %g' % m.objVal)
        return min_order


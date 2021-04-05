class OrderOptimizer:
    def __init__(self, index_card_info):
        self.index_card_info = index_card_info

    def index_build_cost(self, current_index_list):
        return sum(self.index_card_info[current_index] for current_index in current_index_list)

    def greedy_min_cost_order(self, selected_action_batch):
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

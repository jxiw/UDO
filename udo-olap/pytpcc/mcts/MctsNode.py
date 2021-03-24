## ==============================================
## Monte Calo Tree Search Class
## ==============================================

from enum import Enum

class SelectionPolicy(Enum):
    UCB1 = 1
    UCBV = 2

class UpdatePolicy(Enum):
    MCTS = 1
    RAVE = 2

class SpaceType(Enum):
    Light = 1
    Heavy = 2
    All = 3

class MctsNode(object):

    def select_action(self):
        """connect to a DBMS"""
        return None

    def playout(self, current_level_action):
        """run queries with specific timeout"""
        return None

    def sample(self, round):
        """run queries without specific timeout"""
        return None

    def opt_policy(self):
        """retrieve the policy of the mcts"""
        return None

## MCTS

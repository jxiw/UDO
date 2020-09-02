import gym
import gym.spaces
import math
import numpy as np
import random

class QueryOptimizationEnv(gym.Env):
  """ RL environment representing query optimization """

  def __init__(self, query_info, cur_lb, cur_ub):
    """ Initializes environment for simulation.
    
    Args:
      query_info: information on query to optimize
      cur_lb: lower cardinality bounds for each relation
      cur_ub: upper cardinality bounds for each relation
    """
    super(QueryOptimizationEnv, self).__init__()
    # Store initialization parameters
    self.query_info = query_info
    self.cur_lb = cur_lb
    self.cur_ub = cur_ub
    # Prepare query optimization
    self.qo = QueryOptimizer(query_info)
    # Actions: which relation to generate next?
    self.action_space = gym.spaces.Discrete(query_info.nr_rels)
    # Observations: cardinality for relation and bound type, unverified flag
    self.observation_space = gym.spaces.Box(
        0, query_info.max_card, shape=(query_info.nr_rels,1), 
        dtype=np.float32)
    # Initialize remaining fields
    self.reset()

  def step(self, action):
    # Update step counter and check timeout
    self.nr_steps = self.nr_steps + 1
    if (self.nr_steps > 100):
      return self.observations, 0, True, {}
    # Find out cardinality of target table
    r = self.query_info.id_to_rel[action]
    rcard = self.sim_card[r]
    # Update simulated cardinality bounds
    self.sim_lb[r] = rcard
    self.sim_ub[r] = rcard
    # Did we analyze a new relation?
    new_rel = self.observations[action][0]
    # Update observations
    self.observations[action][0] = 0
    # Check if (near-)optimal plan was found
    opt_found = self.qo.found_opt(self.sim_lb, self.sim_ub, False)
    # Calculate reward
    reward = new_rel
    if (False and self.nr_steps % 50 == 0):
      print(f"selected action {action}")
      print(f"optimal cost between {cost_lb} and {cost_ub} -> reward {reward}")
      #print(self.observations)
    #done = True if random.randint(0, 10) == 1 else False
    return self.observations, reward, False, {}

  def reset(self):
    """ Initializes simulation for choosing next actions. """
    
    # Initialize counter for timeout
    self.nr_steps = 1;
    # Initialize cardinality values for simulation
    random.seed()
    self.sim_card = {}
    for r in self.query_info.all_rels:
      l = self.cur_lb[r]
      u = self.cur_ub[r]
      c = random.randint(l,u)
      self.sim_card[r] = c
    self.sim_lb = self.cur_lb.copy()
    self.sim_ub = self.cur_ub.copy()
    # Initialize observations
    self.observations = np.zeros((self.query_info.nr_rels,1))
    for rid in range(0, self.query_info.nr_rels):
      r = self.query_info.id_to_rel[rid]
      card = self.sim_card[r]
      l = self.cur_lb[r]
      u = self.cur_ub[r]
      self.observations[rid][0] = 0 if l==u else 1
    return self.observations

  def render(self, mode='human', close=False):
    print("This is the rendering method.")
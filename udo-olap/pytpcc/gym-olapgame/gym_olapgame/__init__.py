from gym.envs.registration import register

register(
    id='olapgame-v0',
    entry_point='gym_olapgame.envs:OLAPOptimizationGameEnv',
)

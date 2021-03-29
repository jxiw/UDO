from gym.envs.registration import register

register(
    id='olapoptimization-v0',
    entry_point='gym_olapoptimization.envs:OLAPOptimizationEnv',
)

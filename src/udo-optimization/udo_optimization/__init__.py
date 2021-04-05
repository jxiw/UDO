from gym.envs.registration import register

register(
    id='udo_optimization-v0',
    entry_point='udo_optimization.envs:OptimizationEnv',
)

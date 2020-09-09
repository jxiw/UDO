from gym.envs.registration import register

register(
    id='opgame-v0',
    entry_point='gym_opgame.envs:OptimizationGameEnv',
)

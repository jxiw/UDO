import numpy as np
import gym
import udo_optimization

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Flatten
from tensorflow.keras.optimizers import Adam

from rl.agents import SARSAAgent
from rl.policy import BoltzmannQPolicy

def run_sarsa_agent(driver, queries, candidate_indices, duration, horizon):

    # Get the environment and extract the number of actions.
    env = gym.make("udo_optimization-v0", driver=driver, queries=queries, candidate_indices=candidate_indices)
    env.horizon = horizon
    nb_actions = env.action_space.n
    print("nr action:", nb_actions)
    print("observation space:", env.observation_space.shape)

    # Next, we build a very simple model.
    model = Sequential()
    model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
    model.add(Dense(52))
    model.add(Activation('relu'))
    model.add(Dense(252))
    model.add(Activation('relu'))
    model.add(Dense(526))
    model.add(Activation('relu'))
    model.add(Dense(252))
    model.add(Activation('relu'))
    model.add(Dense(nb_actions))
    model.add(Activation('linear'))

    print(model.summary())

    # SARSA does not require a memory.
    policy = BoltzmannQPolicy()
    # policy.select_action()
    sarsa = SARSAAgent(model=model, nb_actions=nb_actions, nb_steps_warmup=10, policy=policy)
    sarsa.compile(Adam(lr=1e-3), metrics=['mae'])

    # Okay, now it's time to learn something! We visualize the training here for show, but this
    # slows down training quite a lot. You can always safely abort the training prematurely using
    # Ctrl + C.
    sarsa.fit(env, nb_steps=500, visualize=False, verbose=2)

    # After training is done, we save the final weights.
    # sarsa.save_weights('sarsa_{}_weights.h5f'.format(udo_optimization-v0), overwrite=True)

    # Finally, evaluate our algorithm for 5 episodes.
    sarsa.test(env, nb_episodes=5, visualize=True)
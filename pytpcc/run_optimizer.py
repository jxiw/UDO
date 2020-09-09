import gym
import gym_opgame

env = gym.make('opgame-v0')
episode_count = 100
reward = 0
done = False

for i_episode in range(episode_count):
    observation = env.reset()
    for t in range(100):
        env.render()
        print(observation)
        action = env.action_space.sample()
        observation, reward, done, info = env.step(action)
        if done:
            print("Episode finished after {} timesteps".format(t+1))
            break
env.close()
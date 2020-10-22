import gym
import gym_opgame

env = gym.make('opgame-v0')
episode_count = 100
reward = 0
done = False

print("===")
stn = env.map_state_to_num((([1, 0, 2, 3, 4, 5, 6], [0, 2, 1, 3, 4, 5, 6], [1, 0, 2, 3, 4]), ([1, 0, 0]), ([2, 2, 0, 2])))
print(stn)

# for i in range(env.nS):
# # for i in range(14310, 14311):
#     print "===="
#     print i
#     state = env.map_number_to_state(i)
#     print state
#     num = env.map_state_to_num(state)
#     print num
#     assert i == num

# for i_episode in range(episode_count):
#     observation = env.reset()
#     for t in range(100):
#         env.render()
#         print(observation)
#         action = env.choose_action(observation)
#         observation, reward, done, info = env.step(action)
#         if done:
#             print("Episode finished after {} timesteps".format(t+1))
#             break
# env.close()
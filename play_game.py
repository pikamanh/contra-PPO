from nes_py.nes_env import NESEnv

env = NESEnv("Contra/ROMs/contra.nes")
print(env.action_space)
# observation = env.reset()
# terminated = False
# truncated = False

# while not (terminated or truncated):
#     action = env.action_space.sample()
#     observation, reward, done, info = env.step(action)
#     frame = env.render()

# env.close()
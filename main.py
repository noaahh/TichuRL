from agents.Human import Human
from agents.Random import Random
from tichu.Env import Env

### Set environmets
env = Env(human=0, verbose=1)

### Set parameters
episode_num = 1

### Set up agents
agent_0 = Human()
agent_1 = Random()
agent_2 = Random()
agent_3 = Random()
env.set_agents([agent_0, agent_1, agent_2, agent_3])

### Run
for episode in range(episode_num):
    env.run()

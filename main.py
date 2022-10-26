from agents.Human import Human
from agents.Random import Random
from agents.Priority_min import  Priority_min
from tichu.Env import Env

### Set environmets
env = Env(human=0, verbose=1)

### Set parameters
episode_num = 1

### Set up agents
agent_0 = Priority_min()
agent_1 = Priority_min()
agent_2 = Priority_min()
agent_3 = Priority_min()
env.set_agents([agent_0, agent_1, agent_2, agent_3])

### Run
for episode in range(episode_num):
    env.run()

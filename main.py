from agents.Human import Human
from agents.Random import Random
from agents.Priority_min import  Priority_min
from tichu.Env import Env

env = Env(verbose=False)

agent_0 = Priority_min(position=0)
agent_1 = Priority_min(position=1)
agent_2 = Random(position=2)
agent_3 = Random(position=3)
agents = [agent_0, agent_1, agent_2, agent_3]

env.set_agents(agents)

n = 1

points = []

print(f"Running {n} iterations")
for i in range(n):
    if i % 1000 == 0:
        print(f"Iteration: {i}")

    game_points, accumulated_player_points = env.run()
    print(accumulated_player_points)

print("Done")

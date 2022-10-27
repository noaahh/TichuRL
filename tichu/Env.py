import time

import matplotlib.pyplot as plt
import numpy as np

from tichu.Game import Game
from tichu.Util import reorganize


class Env:

    def __init__(self, human=0, verbose=0):
        self.agents = None
        self.human = human
        self.verbose = verbose
        self.game = Game()
        self.player_num = self.game.get_player_num()
        self.points = np.zeros(4)
        self.state_shape = [1, 40]
        self.action_num = 8192

        self.points_table = []
        self.timestep = 0

    def set_agents(self, agents):
        self.agents = agents

    def next_turn(self, action):
        self.timestep += 1
        next_player, player_id = self.game.next_turn(action)

        return next_player, player_id

    def plot_points(self, agent):
        agent_points = [n[agent.position] for n in self.points_table]
        plt.scatter([i + 1 for i in range(len(agent_points))], agent_points)

        print(f"Avg points agent {agent.position} (type: {agent.strategy}): {sum(agent_points) / len(agent_points)}")

        plt.title(f'Points scored (Agent {agent})')
        plt.xlabel('Iteration')
        plt.ylabel('Points')
        plt.show()

    def run(self):
        trajectories = [[] for _ in range(self.player_num)]
        active_player, player_id = self.init_game()
        return_hand = self.game.get_active_player(0).hand  # for handValue

        if self.verbose:
            print("Your hand (player0) ")
            h_state = self.game.get_active_player(0)
            h_state.hand.show()
            print("First player: " + str(player_id))

        trajectories[player_id].append(active_player)

        # While game is not over continue taking turns.
        while not self.is_over():
            #            if player_id == 0:
            #                for i in active_player['legal_actions']:
            #                    i.show()

            action = self.agents[player_id].play(active_player)
            trajectories[player_id].append(action)

            if self.verbose:
                print("Player" + str(player_id))
                action.show()

            next_player, next_player_id = self.next_turn(action)

            active_player = next_player
            player_id = next_player_id

            if not self.is_over():
                trajectories[player_id].append(active_player)

            if self.human:
                time.sleep(1)

        for player_id in range(self.player_num):
            active_player = self.get_state(player_id)
            trajectories[player_id].append(active_player)

        game_points = self.game.get_points()
        self.points_table.append(game_points)

        if self.verbose:
            print(f"Points: {game_points}")

        trajectories = reorganize(trajectories, game_points)
        return trajectories, game_points

    def is_over(self):
        return self.game.is_over()

    def init_game(self):
        return self.game.init_game()

    def get_points(self):
        self.points += np.array(self.game.get_points())

    def get_state(self, player_id):
        return self.game.get_active_player(player_id)

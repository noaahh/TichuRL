import time

import numpy as np

from tichu.Game import Game


class TichuEnv:

    def __init__(self, verbose=0):
        self.verbose = verbose
        self.game = Game(self)
        self.player_num = self.game.get_player_num()
        self.positional_outcome = {}
        self.points = np.zeros(4)
        self.state_shape = [1, 40]
        self.action_num = 8192
        self.team_names = []

        self.rounds_to_win = None
        self.timestep = 0

    def set_agents(self, agents):
        self.agents = agents

    def next_turn(self, action):
        self.timestep += 1
        next_player, player_id = self.game.next_turn(action)

        return next_player, player_id

    def run(self):
        active_player, player_id = self.init_game()
        return_hand = self.game.get_active_player(0).hand  # for handValue

        if self.verbose:
            print("Your hand (player0) ")
            h_state = self.game.get_active_player(0)
            h_state.hand.show()
            print("First player: " + str(player_id))

        # While game is not over continue taking turns.
        while not self.is_over():
            #            if player_id == 0:
            #                for i in active_player['legal_actions']:
            #                    i.show()

            action = self.agents[player_id].play(active_player)

            if self.verbose:
                print("Player" + str(player_id))
                action.show()

            next_player, next_player_id = self.next_turn(action)

            active_player = next_player
            player_id = next_player_id

        for player_id in range(self.player_num):
            active_player = self.get_state(player_id)

        game_points = self.game.get_points()
        if self.verbose:
            print(f"Points: {game_points}")
            for i in self.game.players:
                print(f"History for {i.player_id}: {i.accumulated_points}")

        return game_points, [p.accumulated_points for p in self.game.players], self.rounds_to_win, self.positional_outcome

    def is_over(self):
        return self.game.is_over()

    def init_game(self):
        return self.game.init_game()

    def get_points(self):
        R = np.array(self.game.get_points())
        self.points += R

    def get_state(self, player_id):
        return self.game.get_active_player(player_id)

    def set_team_names(self, param):
        self.team_names = param

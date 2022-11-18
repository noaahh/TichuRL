from tichu import Player


class Team:
    def __init__(self, player_a, player_b):
        self.player_a = player_a
        self.player_b = player_b
        self.score = 0

    def get_team_id(self):
        players = [self.player_a, self.player_b]
        players.sort(key=lambda x: x.strategy)

        return "_".join([p.strategy for p in players])

    def __str__(self):
        return self.get_team_id()

    def __repr__(self):
        return self.get_team_id()
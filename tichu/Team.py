class Team:
    def __init__(self, player_a, player_b):
        self.player_a = player_a
        self.player_b = player_b

        self.games_played = 0
        self.score = 0
        self.wins = 0

    def get_team_id(self):
        players = [self.player_a, self.player_b]
        players.sort(key=lambda x: x.strategy)

        return "-".join([p.strategy for p in players])

    # Probability of winning a game
    def get_win_probability(self):
        return self.wins / self.games_played

    def __str__(self):
        return self.get_team_id()

    def __repr__(self):
        return self.get_team_id()
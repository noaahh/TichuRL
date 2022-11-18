from tichu.Team import Team
from tichu.TichuEnv import TichuEnv


class Tournament:
    def __init__(self, available_agents):
        self.teams = Tournament.create_all_possible_teams_from_agents(available_agents)
        self.rounds = []
        self.winner = None

    def play(self):
        pairs = Tournament.create_all_possible_pairings(self.teams)
        for pairing in pairs:
            pairing_env = TichuEnv()

            team_a = pairing[0]
            team_b = pairing[1]

            pairing_env.set_agents([team_a.player_a, team_b.player_a, team_a.player_b, team_b.player_b])
            game_points, accumulated_player_points = pairing_env.run()

            points_by_agent = [[accumulated_player_points[0], team_a], [accumulated_player_points[1], team_b],
                               [accumulated_player_points[2], team_a], [accumulated_player_points[3], team_b]]
            points_by_agent.sort(key=lambda x: x[0], reverse=True)

            # Give score based on the official Tichu tournament scoring system
            # https://www.tichu.de/en/tournament-scoring-system/
            points_by_agent[0][1].score += 3
            points_by_agent[1][1].score += 2
            points_by_agent[2][1].score += 1
            points_by_agent[3][1].score += 0

        self.teams.sort(key=lambda x: x.score, reverse=True)

    # Create every possible team matchup from a list of teams
    @staticmethod
    def create_all_possible_pairings(teams):
        pairs = []
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                pairs.append([teams[i], teams[j]])
        return pairs

    # Create all possible combinations of teams given 4 agents
    @staticmethod
    def create_all_possible_teams_from_agents(agents):
        teams = []
        for i in range(len(agents)):
            for j in range(i + 1, len(agents)):
                teams.append(Team(agents[i], agents[j]))

            teams.append(Team(agents[i], agents[i]))

        return teams

    def __str__(self):
        return "vs".join([str(team) for team in self.teams])
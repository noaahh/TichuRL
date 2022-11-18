import math

from plotly.subplots import make_subplots
import plotly.graph_objects as go
from tqdm.notebook import tqdm

from tichu.Team import Team
from tichu.TichuEnv import TichuEnv


def binomial_distribution(n, p, k):
    return (math.factorial(n) / (math.factorial(k) * math.factorial(n - k))) * (p ** k) * ((1 - p) ** (n - k))


class Pairing:
    def __init__(self, teams):
        self.teams = teams
        self.scoring_tables = [{"0": 0, "1": 0, "2": 0, "3": 0}, {"0": 0, "1": 0, "2": 0, "3": 0}]

    def get_pairing_id(self):
        return " vs ".join([team.get_team_id() for team in self.teams])

    def get_count_of_matches_played(self):
        return sum(self.scoring_tables[0].values())

    # Probability of scoring a certain amount of points by team i as a dictionary
    def get_probability_of_scoring(self, i):
        return {k: v / self.get_count_of_matches_played() for k, v in self.scoring_tables[i].items()}

    # Plot probability of scoring a  certain amount of points for every team
    def plot_probability_of_scoring(self):
        fig = make_subplots(rows=1, cols=2, subplot_titles=(
        f"Pairing {self.get_pairing_id()}, Team {self.teams[0].get_team_id()}",
        f"Pairing {self.get_pairing_id()}, Team {self.teams[1].get_team_id()}"), shared_yaxes=True)
        for i, team in enumerate(self.teams):
            x = list(self.get_probability_of_scoring(i).keys())
            y = list(self.get_probability_of_scoring(i).values())
            fig.add_trace(go.Bar(x=x, y=y), row=1, col=i + 1)
        fig.show()

    # Calculcate expected score for team i
    def get_expected_score(self, i):
        return sum([int(k) * v for k, v in self.get_probability_of_scoring(i).items()])

    def plot_bionomial_distributions(self):
        fig = make_subplots(rows=1, cols=2, subplot_titles=(
        f"Pairing {self.get_pairing_id()}, Team {self.teams[0].get_team_id()}",
        f"Pairing {self.get_pairing_id()}, Team {self.teams[1].get_team_id()}"), shared_yaxes=True)
        for i, team in enumerate(self.teams):
            x = list(range(0, self.get_count_of_matches_played() + 1))
            y = [binomial_distribution(self.get_count_of_matches_played(), team.get_win_probability(), k) for k in x]
            fig.add_trace(go.Bar(x=x, y=y), row=1, col=i + 1)
        fig.show()


class Tournament:
    def __init__(self, available_agents, matches_per_pairing=100, verbose=False):
        self.teams = Tournament.create_all_possible_teams_from_agents(available_agents)
        self.pairings = Tournament.create_all_possible_pairings(self.teams)
        self.matches_per_pairing = matches_per_pairing

    def play(self):
        for pairing in tqdm(self.pairings):
            team_a = pairing.teams[0]
            team_b = pairing.teams[1]

            for i in range(self.matches_per_pairing):

                pairing_env = TichuEnv()
                pairing_env.set_agents([team_a.player_a, team_b.player_a, team_a.player_b, team_b.player_b])
                game_points, accumulated_player_points = pairing_env.run()

                points_by_agent = [[game_points[0], team_a], [game_points[1], team_b],
                                   [game_points[2], team_a], [game_points[3], team_b]]

                points_by_agent_copy = points_by_agent.copy()
                points_by_agent_copy.sort(key=lambda x: x[0], reverse=True)

                team_a.games_played += 1
                team_b.games_played += 1

                # Give score based on the official Tichu tournament scoring system
                if points_by_agent_copy[0][1].__str__() == points_by_agent_copy[1][1].__str__():
                    team_index = pairing.teams.index(points_by_agent_copy[0][1])
                    team = pairing.teams[team_index]

                    pairing.scoring_tables[team_index]["3"] += 1
                    pairing.scoring_tables[1 if team_index == 0 else 0]["0"] += 1
                    team.wins += 1

                    team.score += 3
                else:
                    # Total points per team_index
                    team_a_points = points_by_agent[0][0] + points_by_agent[2][0]
                    team_b_points = points_by_agent[1][0] + points_by_agent[3][0]

                    # Win for team_index A or B
                    if team_a_points > team_b_points:
                        pairing.scoring_tables[0]["2"] += 1
                        pairing.scoring_tables[1]["0"] += 1
                        team_a.wins += 1
                        team_a.score += 2
                    elif team_a_points < team_b_points:
                        pairing.scoring_tables[1]["2"] += 1
                        pairing.scoring_tables[0]["0"] += 1
                        team_b.wins += 1
                        team_b.score += 2

                    # Draw
                    elif team_a_points == team_b_points:
                        pairing.scoring_tables[0]["1"] += 1
                        pairing.scoring_tables[1]["1"] += 1

                        team_a.score += 1
                        team_b.score += 1

    # Create every possible team_index matchup from a list of teams
    @staticmethod
    def create_all_possible_pairings(teams):
        pairs = []
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                pairs.append(Pairing([teams[i], teams[j]]))
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

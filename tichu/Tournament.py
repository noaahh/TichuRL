import math

from plotly.subplots import make_subplots
import plotly.graph_objects as go
from tqdm.notebook import tqdm

from tichu.TichuEnv import TichuEnv


def binomial_distribution(n, p, k):
    return (math.factorial(n) / (math.factorial(k) * math.factorial(n - k))) * (p ** k) * ((1 - p) ** (n - k))


def poison_distribution(l, k):
    return (l ** k) * math.exp(-l) / math.factorial(k)


class Team:
    def __init__(self, agents):
        if len(agents) != 2:
            raise ValueError("Team must have 2 agents")

        self.agents = agents
        self.games_played = 0
        self.score = 0
        self.wins = 0

        self.rounds_for_win = {}

    def get_team_id(self):
        agents_copy = self.agents.copy()
        agents_copy.sort(key=lambda x: x.strategy)
        return "-".join([a.strategy for a in agents_copy])

    # Probability of winning a game
    def get_win_probability(self):
        return self.wins / self.games_played

    def __str__(self):
        return self.get_team_id()

    def __repr__(self):
        return self.get_team_id()

    # Add rounds to win in dictionary against a given team
    def add_rounds_for_win(self, rounds, against_team):
        if against_team not in self.rounds_for_win:
            self.rounds_for_win[against_team.get_team_id()] = []

        self.rounds_for_win[against_team.get_team_id()].append(rounds)

    # Plot poisson distribution of rounds to win against each team in one plot as bar plots
    def plot_rounds_for_win(self):
        fig = make_subplots(rows=1, cols=1)

        for team, rounds in self.rounds_for_win.items():
            x = list(range(1, 22))
            y = [poison_distribution(sum(rounds) / len(rounds), k) for k in x]

            fig.add_trace(go.Bar(x=x, y=y, name=team, visible='legendonly'))

        fig.update_layout(title_text="Rounds to win against each team for " + self.get_team_id())
        fig.show()


class Pairing:
    def __init__(self, teams):
        if len(teams) != 2:
            raise ValueError("Pairing must have 2 teams")

        self.teams = teams
        self.scoring_table = {teams[0].__str__(): {"0": 0, "1": 0, "2": 0, "3": 0},
                              teams[1].__str__(): {"0": 0, "1": 0, "2": 0, "3": 0}}

    def get_agent_list(self):
        return [self.teams[0].agents[0], self.teams[1].agents[0],
                self.teams[0].agents[1], self.teams[1].agents[1]]

    def get_pairing_id(self):
        return " vs ".join([team.__str__() for team in self.teams])

    # Calculate the number of matches played
    def get_count_of_matches_played(self):
        if sum(self.scoring_table[self.teams[0].__str__()].values()) != sum(
                self.scoring_table[self.teams[1].__str__()].values()):
            raise ValueError("Number of matches played by both teams must be equal")

        return sum(self.scoring_table[self.teams[0].__str__()].values())

    # Probability of scoring a certain amount of points by team i as a dictionary
    def get_probability_of_scoring(self, team_id):
        return {k: v / self.get_count_of_matches_played() for k, v in self.scoring_table[team_id].items()}

    # Plot probability of scoring a certain amount of points for every team
    def plot_probability_of_scoring(self):
        fig = make_subplots(rows=1, cols=2, subplot_titles=(
            f"Team {self.teams[0].get_team_id()}",
            f"Team {self.teams[1].get_team_id()}"), shared_yaxes=True)
        for i, team in enumerate(self.teams):
            x = list(self.get_probability_of_scoring(team.get_team_id()).keys())
            y = list(self.get_probability_of_scoring(team.get_team_id()).values())
            fig.add_trace(go.Bar(x=x, y=y), row=1, col=i + 1)

        fig.update_layout(
            title_text=f"Probability of scoring amount of points by team | Pairing {self.get_pairing_id()}",
            showlegend=False)
        fig.show()

    # Calculate expected score for team i
    def get_expected_score(self, team_id):
        return sum([int(k) * v for k, v in self.get_probability_of_scoring(team_id).items()])

    def plot_binomial_distributions(self):
        fig = make_subplots(rows=1, cols=2, subplot_titles=(
            f"Team {self.teams[0].get_team_id()}",
            f"Team {self.teams[1].get_team_id()}"), shared_yaxes=True)
        for i, team in enumerate(self.teams):
            x = list(range(0, self.get_count_of_matches_played() + 1))
            y = [binomial_distribution(self.get_count_of_matches_played(), team.get_win_probability(), k) for k in x]
            fig.add_trace(go.Bar(x=x, y=y), row=1, col=i + 1)

        fig.update_layout(
            title_text=f"Binomial Distribution to win by number of rounds | Pairing {self.get_pairing_id()}",
            showlegend=False)
        fig.show()


class Tournament:
    def __init__(self, available_agents, matches_per_pairing=100, verbose=False):
        self.teams = Tournament.create_all_possible_teams_from_agents(available_agents)
        self.pairings = Tournament.create_all_possible_pairings(self.teams)
        self.matches_per_pairing = matches_per_pairing

    def play(self):
        for pairing in tqdm(self.pairings):
            for i in range(self.matches_per_pairing):
                pairing_env = TichuEnv()
                pairing_env.set_agents(pairing.get_agent_list())
                game_points, accumulated_points_per_round, rounds_to_win = pairing_env.run()
                self.update_pairing_stats(pairing, game_points, rounds_to_win)

    @staticmethod
    def update_pairing_stats(pairing, game_points, rounds_to_win):
        team_a = pairing.teams[0]
        team_b = pairing.teams[1]

        team_a.games_played += 1
        team_b.games_played += 1

        points_by_team = [[game_points[0], team_a], [game_points[1], team_b],
                          [game_points[2], team_a], [game_points[3], team_b]]

        points_by_team_copy = points_by_team.copy()
        points_by_team_copy.sort(key=lambda x: x[0], reverse=True)

        # Give score based on the official Tichu tournament scoring system
        if points_by_team_copy[0][1].__str__() == points_by_team_copy[1][1].__str__():
            one_two_team = points_by_team_copy[0][1]

            pairing.scoring_table[one_two_team.__str__()]["3"] += 1
            pairing.scoring_table[points_by_team_copy[-1][1].__str__()]["0"] += 1

            one_two_team.wins += 1
            one_two_team.add_rounds_for_win(rounds_to_win, points_by_team_copy[2][1])

            one_two_team.score += 3
        else:
            # Total points per team_index
            team_a_points = points_by_team[0][0] + points_by_team[2][0]
            team_b_points = points_by_team[1][0] + points_by_team[3][0]

            # Win for team_index A or B
            if team_a_points > team_b_points:
                pairing.scoring_table[team_a.__str__()]["2"] += 1
                pairing.scoring_table[team_b.__str__()]["0"] += 1

                team_a.wins += 1
                team_a.add_rounds_for_win(rounds_to_win, team_b)

                team_a.score += 2
            elif team_a_points < team_b_points:
                pairing.scoring_table[team_b.__str__()]["2"] += 1
                pairing.scoring_table[team_a.__str__()]["0"] += 1

                team_b.wins += 1
                team_b.add_rounds_for_win(rounds_to_win, team_a)

                team_b.score += 2

            # Draw
            elif team_a_points == team_b_points:
                pairing.scoring_table[team_a.__str__()]["1"] += 1
                pairing.scoring_table[team_b.__str__()]["1"] += 1

                team_a.score += 1
                team_b.score += 1

    # Create every possible team_index matchup from a list of teams
    @staticmethod
    def create_all_possible_pairings(teams):
        pairs = []
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                pairs.append(Pairing([teams[i], teams[j]]))

            pairs.append(Pairing([teams[i], teams[i]]))

        return pairs

    # Create all possible combinations of teams given 4 agents
    @staticmethod
    def create_all_possible_teams_from_agents(agents):
        teams = []
        for i in range(len(agents)):
            for j in range(i + 1, len(agents)):
                teams.append(Team([agents[i], agents[j]]))

            teams.append(Team([agents[i], agents[i]]))

        return teams

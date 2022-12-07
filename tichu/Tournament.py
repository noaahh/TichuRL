import math

from plotly.subplots import make_subplots
import plotly.graph_objects as go
from tqdm.notebook import tqdm

from tichu.TichuEnv import TichuEnv


def binomial_distribution(n, p, k):
    return (math.factorial(n) / (math.factorial(k) * math.factorial(n - k))) * (p ** k) * ((1 - p) ** (n - k))


def poison_distribution(l, k):
    return (l ** k) * math.exp(-l) / math.factorial(k)


# Find the Z score for a given confidence level
def get_z_score(confidence_level):
    if confidence_level == 0.90:
        return 1.645
    elif confidence_level == 0.95:
        return 1.96
    elif confidence_level == 0.99:
        return 2.576
    else:
        raise ValueError(f"Confidence level {confidence_level} not supported")


class Team:
    def __init__(self, agents, matches_per_pairing):
        if len(agents) != 2:
            raise ValueError("Team must have 2 agents")

        self.agents = agents
        self.matches_per_pairing = matches_per_pairing

        self.games_played = 0
        self.scores = []
        self.wins = {}
        self.rounds_for_win = {}

    # Get team score
    def get_score(self):
        return sum(self.scores)

    def get_team_id(self):
        agents_copy = self.agents.copy()
        agents_copy.sort(key=lambda x: x.strategy)
        return "-".join([a.strategy for a in agents_copy])

    def __str__(self):
        return self.get_team_id()

    def __repr__(self):
        return self.get_team_id()

    # Add rounds to win in dictionary against a given team
    def add_rounds_for_win(self, rounds, against_team):
        if against_team not in self.rounds_for_win:
            self.rounds_for_win[against_team.get_team_id()] = []

        self.rounds_for_win[against_team.get_team_id()].append(rounds)

    # Add win to dictionary against a given team
    def add_win(self, against_team):
        if against_team.get_team_id() not in self.wins:
            self.wins[against_team.get_team_id()] = 0

        self.wins[against_team.get_team_id()] += 1

    # Get win probability against a given team
    def get_win_probability(self, against_team_id):
        if against_team_id not in self.wins:
            return 0

        return self.wins[against_team_id] / self.matches_per_pairing

    # Get overall win probability
    def get_overall_win_probability(self):
        return sum(self.wins.values()) / (self.matches_per_pairing * len(self.wins))

    # Plot win probability against each team in one plot as bar plots and sort by win probability
    def plot_win_probability_against_teams(self):
        fig = make_subplots(rows=1, cols=1)

        x = list(k for k in self.wins.keys() if k != self.get_team_id())
        y = [self.get_win_probability(team) for team in x]

        # Sort by win probability
        x, y = zip(*sorted(zip(x, y), key=lambda item: item[1], reverse=True))

        fig.add_trace(go.Bar(x=x, y=y, name=self.get_team_id()))
        fig.update_layout(title_text="Win probability against each team for " + self.get_team_id())
        fig.show()

    # Plot poisson distribution of rounds to win against each team in one plot as bar plots
    def plot_rounds_for_win(self, hide_teams=False):
        fig = make_subplots(rows=1, cols=1)

        for team, rounds in self.rounds_for_win.items():
            x = list(range(1, 22))
            y = [poison_distribution(sum(rounds) / len(rounds), k) for k in x]

            fig.add_trace(go.Bar(x=x, y=y, name=team, visible='legendonly' if hide_teams else True))

        fig.update_layout(title_text="Rounds to win against each team for " + self.get_team_id())
        fig.show()

    # Confidence interval as tuple for the win probability against a given team with a given confidence level
    def get_win_confidence_interval(self, against_team_id, confidence_level=.95):
        if against_team_id not in self.wins:
            return 0

        p = self.get_win_probability(against_team_id)
        n = self.matches_per_pairing
        z_score = get_z_score(confidence_level)

        return p - z_score * math.sqrt(p * (1 - p) / n), p + z_score * math.sqrt(p * (1 - p) / n)

    # Confidence interval for the average rounds to win against a given team with a given confidence level
    def get_rounds_for_win_confidence_interval(self, against_team_id, confidence_level=.95):
        if against_team_id not in self.rounds_for_win:
            return 0

        x = sum(self.rounds_for_win[against_team_id]) / len(self.rounds_for_win[against_team_id])
        n = len(self.rounds_for_win[against_team_id])
        z_score = get_z_score(confidence_level)

        return x - z_score * math.sqrt(x / n), x + z_score * math.sqrt(x / n)


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


class Tournament:
    def __init__(self, available_agents, matches_per_pairing=100, verbose=False):
        self.teams = Tournament.create_all_possible_teams_from_agents(available_agents, matches_per_pairing)
        self.pairings = Tournament.create_all_possible_pairings(self.teams)
        self.matches_per_pairing = matches_per_pairing

    # Get winner team of tournament based on score
    def get_winner_team(self):
        return max(self.teams, key=lambda team: team.get_score())

    def play(self):
        for pairing in tqdm(self.pairings):
            for _ in range(self.matches_per_pairing):
                pairing_env = TichuEnv()
                pairing_env.set_agents(pairing.get_agent_list())
                game_points, accumulated_points_per_round, rounds_to_win = pairing_env.run()
                self.update_pairing_stats(pairing, game_points, rounds_to_win)

    # Plot cumulative score over time for each team of the tournament as line plots
    def plot_cumulative_score(self):
        fig = make_subplots(rows=1, cols=1)

        for team in self.teams:
            fig.add_trace(go.Scatter(x=list(range(1, len(team.scores) + 1)),
                                     y=[sum(team.scores[:i]) for i in range(1, len(team.scores) + 1)],
                                     name=team.get_team_id()))

        fig.update_layout(title_text="Cumulative score over time for each team")
        fig.show()

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

        # Give scores based on the official Tichu tournament scoring system
        if points_by_team_copy[0][1].__str__() == points_by_team_copy[1][1].__str__():
            one_two_team = points_by_team_copy[0][1]
            other_team = points_by_team_copy[2][1]

            pairing.scoring_table[one_two_team.__str__()]["3"] += 1
            pairing.scoring_table[points_by_team_copy[-1][1].__str__()]["0"] += 1

            one_two_team.add_win(other_team)
            one_two_team.add_rounds_for_win(rounds_to_win, other_team)

            one_two_team.scores.append(3)
            other_team.scores.append(0)

        else:
            # Total points per team_index
            team_a_points = points_by_team[0][0] + points_by_team[2][0]
            team_b_points = points_by_team[1][0] + points_by_team[3][0]

            # Win for team_index A or B
            if team_a_points > team_b_points:
                pairing.scoring_table[team_a.__str__()]["2"] += 1
                pairing.scoring_table[team_b.__str__()]["0"] += 1

                team_a.add_win(team_b)
                team_a.add_rounds_for_win(rounds_to_win, team_b)

                team_a.scores.append(2)
                team_b.scores.append(0)
            elif team_a_points < team_b_points:
                pairing.scoring_table[team_b.__str__()]["2"] += 1
                pairing.scoring_table[team_a.__str__()]["0"] += 1

                team_b.add_win(team_a)
                team_b.add_rounds_for_win(rounds_to_win, team_a)

                team_b.scores.append(2)
                team_a.scores.append(0)

            # Draw
            elif team_a_points == team_b_points:
                for team in pairing.teams:
                    pairing.scoring_table[team.__str__()]["1"] += 1
                    team.scores.append(1)

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
    def create_all_possible_teams_from_agents(agents, matches_per_pairing):
        teams = []
        for i in range(len(agents)):
            for j in range(i + 1, len(agents)):
                teams.append(Team([agents[i], agents[j]], matches_per_pairing))

            teams.append(Team([agents[i], agents[i]], matches_per_pairing))

        return teams

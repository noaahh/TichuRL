import pickle

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from tqdm.notebook import tqdm

from src.Pairing import Pairing
from src.Team import Team
from tichu.TichuEnv import TichuEnv

class Tournament:
    def __init__(self, available_agents, matches_per_pairing=100, verbose=False):
        self.teams = Tournament.create_all_possible_teams_from_agents(available_agents, matches_per_pairing)
        self.pairings = Tournament.create_all_possible_pairings(self.teams)
        self.matches_per_pairing = matches_per_pairing

    def play(self):
        """
        Play the tournament and update the statistics of each team and pairing
        :return: None
        """

        # Play all pairings
        for pairing in tqdm(self.pairings):
            for _ in range(self.matches_per_pairing):
                # Create the game
                pairing_env = TichuEnv()
                pairing_env.set_agents(pairing.get_agent_list())
                pairing_env.set_team_names([pairing.teams[0].__str__(), pairing.teams[1].__str__()])

                # Play the game
                game_points, accumulated_points_per_round, rounds_to_win, positional_outcome = pairing_env.run()

                # Update the statistics of the teams
                self.update_pairing_stats(pairing, game_points, rounds_to_win, positional_outcome)

    def get_top_three_teams(self):
        """
        Get the top three teams
        :return: top three teams
        """
        return sorted(self.teams, key=lambda team: team.get_score(), reverse=True)[:3]

    def get_team(self, team_id):
        for team in self.teams:
            if team.get_team_id() == team_id:
                return team

    def plot_cumulative_score(self):
        """
        Plot the cumulative score of each team
        :return: None
        """
        fig = make_subplots(rows=1, cols=1)

        for team in self.teams:
            fig.add_trace(go.Scatter(x=list(range(1, len(team.scores) + 1)),
                                     y=[sum(team.scores[:i]) for i in range(1, len(team.scores) + 1)],
                                     name=team.get_team_id()))

        fig.update_layout(title_text="Cumulative score over time for each team")
        fig.update_xaxes(title_text="Number of matches played")
        fig.update_yaxes(title_text="Cumulative score")

        fig.show()

    def plot_total_score(self):
        """
        Plot the total score of each team
        :return: None
        """
        fig = go.Figure(data=[go.Bar(x=[team.get_team_id() for team in self.teams],
                                     y=[team.get_score() for team in self.teams])])

        # Sort bars by total score
        fig.update_layout(title_text="Total score for each team", xaxis={'categoryorder': 'total descending'})

        # Add labels to bars with total score
        fig.update_traces(text=[team.get_score() for team in self.teams], textposition='inside')

        fig.update_xaxes(title_text="Team")
        fig.update_yaxes(title_text="Total score")

        fig.show()

    def get_pairings_for_team(self, team):
        return [p for p in self.pairings if team in p.teams]

    def save(self, file_name):
        try:
            with open(file_name, 'wb') as f:
                pickle.dump(self, f)
                print("Tournament saved to file " + file_name)
        except Exception as e:
            print(e)
            print("Could not save tournament to file")

    @staticmethod
    def load(file_name):
        try:
            with open(file_name, 'rb') as f:
                tournament = pickle.load(f)
                print("Tournament loaded from file " + file_name)
                return tournament
        except Exception as e:
            print(e)
            print("Could not load tournament from file")

        return None

    @staticmethod
    def update_pairing_stats(pairing, game_points, rounds_to_win, positional_outcome):
        """
        Update the statistics of a pairing
        :param pairing: pairing
        :param game_points: points of the game
        :param rounds_to_win: number of rounds to win
        :param positional_outcome: positional outcome
        :return: None
        """

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

            if positional_outcome[one_two_team.__str__()] == 1:
                one_two_team.add_first_to_play(other_team, "win")
                other_team.add_second_to_play(one_two_team, "loss")
            else:
                other_team.add_first_to_play(one_two_team, "loss")
                one_two_team.add_second_to_play(other_team, "win")

            one_two_team.scores.append(3)
            other_team.scores.append(0)

        else:
            # Total points per team_index
            team_a_points = points_by_team[0][0] + points_by_team[2][0]
            team_b_points = points_by_team[1][0] + points_by_team[3][0]

            # Win for team A
            if team_a_points > team_b_points:
                pairing.scoring_table[team_a.__str__()]["2"] += 1
                pairing.scoring_table[team_b.__str__()]["0"] += 1

                team_a.add_win(team_b)
                team_a.add_rounds_for_win(rounds_to_win, team_b)

                team_a.scores.append(2)
                team_b.scores.append(0)

                if positional_outcome[team_a.__str__()] == 1:
                    team_a.add_first_to_play(team_b, "win")
                    team_b.add_second_to_play(team_a, "loss")
                else:
                    team_b.add_first_to_play(team_a, "loss")
                    team_a.add_second_to_play(team_b, "win")

            # Win for team B
            elif team_a_points < team_b_points:
                pairing.scoring_table[team_b.__str__()]["2"] += 1
                pairing.scoring_table[team_a.__str__()]["0"] += 1

                team_b.add_win(team_a)

                team_b.add_rounds_for_win(rounds_to_win, team_a)

                team_b.scores.append(2)
                team_a.scores.append(0)

                if positional_outcome[team_b.__str__()] == 1:
                    team_b.add_first_to_play(team_a, "win")
                    team_a.add_second_to_play(team_b, "loss")
                else:
                    team_a.add_first_to_play(team_b, "loss")
                    team_b.add_second_to_play(team_a, "win")

            # Draw
            elif team_a_points == team_b_points:
                team_b.add_draw(team_a)
                team_a.add_draw(team_b)

                if positional_outcome[team_b.__str__()] == 1:
                    team_b.add_first_to_play(team_a, "draw")
                    team_a.add_second_to_play(team_b, "draw")
                else:
                    team_a.add_first_to_play(team_b, "draw")
                    team_b.add_second_to_play(team_a, "draw")

                for team in pairing.teams:
                    pairing.scoring_table[team.__str__()]["1"] += 1
                    team.scores.append(1)

    @staticmethod
    def create_all_possible_pairings(teams):
        """
        Create all possible pairings of teams
        :param teams: list of teams
        :return: list of pairings
        """
        pairs = []
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                pairs.append(Pairing([teams[i], teams[j]]))

            # pairs.append(Pairing([teams[i], teams[i]]))

        return pairs

    @staticmethod
    def create_all_possible_teams_from_agents(agents, matches_per_pairing):
        """
        Create all possible teams from a list of agents
        :param agents: list of available agents
        :param matches_per_pairing: number of matches per pairing
        :return: list of teams
        """
        teams = []
        for i in range(len(agents)):
            for j in range(i + 1, len(agents)):
                teams.append(Team([agents[i], agents[j]], matches_per_pairing))

            teams.append(Team([agents[i], agents[i]], matches_per_pairing))

        return teams

    def get_rounds_to_win(self, team_a_id, team_b_id):
        """
        Get the number of rounds to win for a given pairing
        :param team_a_id: id of team A
        :param team_b_id: id of team B
        :return: number of rounds to win
        """
        team_a = self.get_team(team_a_id)
        return team_a.rounds_for_win[team_b_id]

from plotly import graph_objects as go
from plotly.subplots import make_subplots

from src.Stats import poison_distribution, \
    get_confidence_interval_probability, get_confidence_interval_expected_value_poisson


class Team:
    def __init__(self, agents, matches_per_pairing):
        if len(agents) != 2:
            raise ValueError("Team must have 2 agents")

        self.agents = agents
        self.matches_per_pairing = matches_per_pairing

        self.games_played = 0
        self.scores = []
        self.wins = {}
        self.draws = {}
        self.first_to_play = {}
        self.second_to_play = {}
        self.rounds_for_win = {}

    def get_total_games_played_first_second(self, against_team_id):
        """
        Get total number of games played when starting first or second against a given team
        :param against_team_id: team id
        :return: total number of games played
        """
        if against_team_id not in self.first_to_play or against_team_id not in self.second_to_play:
            return (0, 0), (0, 0)

        return self.first_to_play[against_team_id]['win'] + self.first_to_play[against_team_id]['loss'] + self.first_to_play[against_team_id]['draw'], \
               self.second_to_play[against_team_id]['win'] + self.second_to_play[against_team_id]['loss'] + self.second_to_play[against_team_id]['draw']

    def get_win_probability_first_second(self, against_team_id):
        """
        Get the win probability when starting first and when starting second against a given team
        :param against_team_id: team id
        :return: win probability when starting first and when starting second
        """
        if against_team_id not in self.wins:
            return 0, 0

        first_to_play = self.first_to_play[against_team_id]
        second_to_play = self.second_to_play[against_team_id]

        n_first, n_second = self.get_total_games_played_first_second(against_team_id)

        return first_to_play["win"] / n_first, second_to_play["win"] / n_second


    def get_draw_probability_first_second(self, against_team_id):
        """
        Get the draw probability when starting first and when starting second against a given team
        :param against_team_id: team id
        :return: draw probability when starting first and when starting second
        """
        if against_team_id not in self.first_to_play or against_team_id not in self.second_to_play:
            return 0, 0

        first_to_play = self.first_to_play[against_team_id]
        second_to_play = self.second_to_play[against_team_id]

        n_first, n_second = self.get_total_games_played_first_second(against_team_id)

        return first_to_play["draw"] / n_first, second_to_play["draw"] / n_second

    def get_win_confidence_interval_first_second(self, against_team_id, confidence_level=.95):
        """
        Get the confidence interval for the win probability when starting first or second against a given team with a given confidence level
        :param against_team_id: team id
        :param confidence_level: confidence level
        :return: confidence interval
        """
        if against_team_id not in self.wins:
            return (0, 0), (0, 0)

        p = self.get_win_probability_first_second(against_team_id)
        n_first, n_second = self.get_total_games_played_first_second(against_team_id)

        # Calculate the confidence interval
        return get_confidence_interval_probability(p[0], n_first, confidence_level), get_confidence_interval_probability(p[1], n_second, confidence_level)

    def get_draw_confidence_interval_first_second(self, against_team_id, confidence_level=.95):
        """
        Get the confidence interval for the draw probability when starting first or second against a given team with a given confidence level
        :param against_team_id: team id
        :param confidence_level: confidence level
        :return: confidence interval
        """
        if against_team_id not in self.draws:
            return (0, 0), (0, 0)

        p = self.get_draw_probability_first_second(against_team_id)
        n_first, n_second = self.get_total_games_played_first_second(against_team_id)

        # Calculate the confidence interval
        return get_confidence_interval_probability(p[0], n_first, confidence_level), get_confidence_interval_probability(p[1], n_second, confidence_level)

    def __str__(self):
        return self.get_team_id()

    def __repr__(self):
        return self.get_team_id()

    def get_score(self):
        return sum(self.scores)

    def get_team_id(self):
        agents_copy = self.agents.copy()
        agents_copy.sort(key=lambda x: x.strategy)
        return " & ".join([a.strategy for a in agents_copy])

    def add_rounds_for_win(self, rounds, against_team):
        """
        Add the number of rounds for a win against a given team
        :param rounds: number of rounds
        :param against_team: team
        :return: None
        """
        if against_team.get_team_id() not in self.rounds_for_win:
            self.rounds_for_win[against_team.get_team_id()] = []

        self.rounds_for_win[against_team.get_team_id()].append(rounds)

    def add_win(self, against_team):
        """
        Add a win against a given team
        :param against_team: team
        :return: None
        """
        if against_team.get_team_id() not in self.wins:
            self.wins[against_team.get_team_id()] = 0

        self.wins[against_team.get_team_id()] += 1

    def add_draw(self, against_team):
        """
        Add a draw against a given team
        :param against_team: team
        :return: None
        """
        if against_team.get_team_id() not in self.draws:
            self.draws[against_team.get_team_id()] = 0

        self.draws[against_team.get_team_id()] += 1

    def add_first_to_play(self, against_team, outcome):
        """
        Add the first to play for a given team
        :param against_team: team
        :param outcome: outcome
        :return: None
        """
        if against_team.get_team_id() not in self.first_to_play:
            self.first_to_play[against_team.get_team_id()] = {"win": 0, "draw": 0, "loss": 0}

        self.first_to_play[against_team.get_team_id()][outcome] += 1

    def add_second_to_play(self, against_team, outcome):
        """
        Add the second to play for a given team
        :param against_team: team
        :param outcome: outcome
        :return: None
        """
        if against_team.get_team_id() not in self.second_to_play:
            self.second_to_play[against_team.get_team_id()] = {"win": 0, "draw": 0, "loss": 0}

        self.second_to_play[against_team.get_team_id()][outcome] += 1

    def get_win_probability(self, against_team_id):
        """
        Get the probability of a win against a given team
        :param against_team_id: team id
        :return: probability of a win
        """
        if against_team_id not in self.wins:
            return 0

        return self.wins[against_team_id] / self.matches_per_pairing

    def get_draw_probability(self, against_team_id):
        """
        Get the probability of a draw against a given team
        :param against_team_id: team id
        :return: probability of a draw
        """
        if against_team_id not in self.draws:
            return 0

        # get difference of the two win probabilities
        return self.draws[against_team_id] / self.matches_per_pairing

    def get_overall_win_probability(self):
        """
        Get the overall win probability
        :return: overall win probability
        """
        return sum(self.wins.values()) / (self.matches_per_pairing * len(self.wins))

    def plot_probabilities_simple(self, against_teams, confidence_level):
        """
        Plot the win and draw probability against a given team with error bars
        :param against_teams: teams
        :param confidence_level: confidence level
        :return: None
        """
        fig = make_subplots(rows=1, cols=1)

        # get win probabilities
        x = list(k.get_team_id() for k in against_teams if k.get_team_id() != self.get_team_id())
        y = [self.get_win_probability(team) for team in x]
        y2 = [self.get_draw_probability(team) for team in x]

        # Sort by win probability
        x, y, y2 = zip(*sorted(zip(x, y, y2), key=lambda item: item[1], reverse=True))

        # Add labels to each bar
        labels = [f"{round(y[i] * 100, 2)}%" for i in range(len(y))]
        labels2 = [f"{round(y2[i] * 100, 2)}%" for i in range(len(y2))]

        # Get error by using confidence interval function and subtracting the win probability
        error_y = [self.get_win_confidence_interval(team, confidence_level)[1] - self.get_win_probability(team) for team
                   in x]
        error_y2 = [self.get_draw_confidence_interval(team, confidence_level)[1] - self.get_draw_probability(team) for
                    team in x]

        # Plot win probability
        fig.add_trace(go.Bar(x=x, y=y, error_y=dict(type="data", array=error_y), text=labels, textposition="auto",
                             name="Win probability"))
        fig.add_trace(go.Bar(x=x, y=y2, error_y=dict(type="data", array=error_y2), text=labels2, textposition="auto",
                             name="Draw probability"))

        fig.update_layout(title_text="Win and draw probability against team for " + self.get_team_id())

        # Add used confidence level to title
        fig.update_layout(title_text=fig.layout.title.text + f" (confidence level: {confidence_level})")

        # Set y axis to start at 0 and end at 1
        fig.update_yaxes(range=[0, 1], title_text="Probability")

        fig.show()

    def plot_probabilities_advanced(self, against_teams, confidence_level=0.95):
        """
        Plot the win and draw probability against a given team with error bars
        :param against_teams: teams to plot against
        :param confidence_level: confidence level
        :return: None
        """
        against_teams_ids = [team.get_team_id() for team in against_teams if team.get_team_id() != self.get_team_id()]

        # get win probabilities
        win_probabilities = [self.get_win_probability(team_id) for team_id in against_teams_ids]
        win_probabilities_first = [self.get_win_probability_first_second(team_id)[0] for team_id in against_teams_ids]
        win_probabilities_second = [self.get_win_probability_first_second(team_id)[1] for team_id in against_teams_ids]

        # get draw probabilities
        draw_probabilities = [self.get_draw_probability(team_id) for team_id in against_teams_ids]
        draw_probabilities_first = [self.get_draw_probability_first_second(team_id)[0] for team_id in against_teams_ids]
        draw_probabilities_second = [self.get_draw_probability_first_second(team_id)[1] for team_id in against_teams_ids]

        # get confidence intervals for win probabilities and draw probabilities
        win_confidence_intervals = [self.get_win_confidence_interval(team_id, confidence_level) for team_id in against_teams_ids]
        draw_confidence_intervals = [self.get_draw_confidence_interval(team_id, confidence_level) for team_id in against_teams_ids]

        # get confidence intervals for win probabilities when starting first and second
        win_confidence_intervals_first = [self.get_win_confidence_interval_first_second(team_id, confidence_level)[0] for team_id in against_teams_ids]
        win_confidence_intervals_second = [self.get_win_confidence_interval_first_second(team_id, confidence_level)[1] for team_id in against_teams_ids]

        # get confidence intervals for draw probabilities when starting first and second
        draw_confidence_intervals_first = [self.get_draw_confidence_interval_first_second(team_id, confidence_level)[0] for team_id in against_teams_ids]
        draw_confidence_intervals_second = [self.get_draw_confidence_interval_first_second(team_id, confidence_level)[1] for team_id in against_teams_ids]

        # plot
        fig = make_subplots(rows=1, cols=3, subplot_titles=("Overall", "Starting first", "Starting second"))

        # Add traces with names and error bars
        fig.add_trace(go.Bar(x=against_teams_ids, y=win_probabilities, error_y=dict(type="data", array=[win_confidence_intervals[i][1] - win_probabilities[i] for i in range(len(win_confidence_intervals))]), name="Win probability"), row=1, col=1)
        fig.add_trace(go.Bar(x=against_teams_ids, y=win_probabilities_first, error_y=dict(type="data", array=[win_confidence_intervals_first[i][1] - win_probabilities_first[i] for i in range(len(win_confidence_intervals_first))]), name="Win probability when starting first"), row=1, col=2)
        fig.add_trace(go.Bar(x=against_teams_ids, y=win_probabilities_second, error_y=dict(type="data", array=[win_confidence_intervals_second[i][1] - win_probabilities_second[i] for i in range(len(win_confidence_intervals_second))]), name="Win probability when starting second"), row=1, col=3)

        # Add draw probabilities
        fig.add_trace(go.Bar(x=against_teams_ids, y=draw_probabilities, error_y=dict(type="data", array=[draw_confidence_intervals[i][1] - draw_probabilities[i] for i in range(len(draw_confidence_intervals))]), name="Draw probability"), row=1, col=1)
        fig.add_trace(go.Bar(x=against_teams_ids, y=draw_probabilities_first, error_y=dict(type="data", array=[draw_confidence_intervals_first[i][1] - draw_probabilities_first[i] for i in range(len(draw_confidence_intervals_first))]), name="Draw probability when starting first"), row=1, col=2)
        fig.add_trace(go.Bar(x=against_teams_ids, y=draw_probabilities_second, error_y=dict(type="data", array=[draw_confidence_intervals_second[i][1] - draw_probabilities_second[i] for i in range(len(draw_confidence_intervals_second))]), name="Draw probability when starting second"), row=1, col=3)

        # Add used confidence level to title
        fig.update_layout(title_text="Win and draw probabilities against team for " + self.get_team_id() + f" (confidence level: {confidence_level})", showlegend=False)

        # Set y-axes limits to 1
        fig.update_yaxes(range=[0, 1], row=1, col=1, title_text="Probability")
        fig.update_yaxes(range=[0, 1], row=1, col=2)
        fig.update_yaxes(range=[0, 1], row=1, col=3)

        # Add labels to all bars. Round to 3 decimals
        fig.update_traces(texttemplate='%{y:.3f}', textposition='outside', row=1, col=1)
        fig.update_traces(texttemplate='%{y:.3f}', textposition='outside', row=1, col=2)
        fig.update_traces(texttemplate='%{y:.3f}', textposition='outside', row=1, col=3)

        fig.show()

    def plot_rounds_for_win(self, against_teams):
        """
        Plot the rounds for win against a given team
        :param against_teams: teams
        :return: None
        """
        fig = make_subplots(rows=1, cols=1)

        for team, rounds in self.rounds_for_win.items():
            if team not in [t.get_team_id() for t in against_teams]:
                continue

            # Get the number of rounds for a win
            x = list(range(1, 22))
            y = [poison_distribution(sum(rounds) / len(rounds), k) for k in x]

            # Add labels to each bar
            labels = [f"{round(y[i] * 100, 2)}%" for i in range(len(y))]
            fig.add_trace(go.Bar(x=x + [0], y=y + [0], text=labels, textposition="auto", name=team))

        fig.update_layout(title_text="Rounds needed against team in case of win for team " + self.get_team_id())

        fig.update_xaxes(title_text="Rounds")
        fig.update_yaxes(title_text="Probability")

        fig.show()

    def get_win_confidence_interval(self, against_team_id, confidence_level=.95):
        """
        Get the confidence interval for the win probability against a given team with a given confidence level
        :param against_team_id: team id
        :param confidence_level: confidence level
        :return: confidence interval
        """
        if against_team_id not in self.wins:
            return 0, 0

        p = self.get_win_probability(against_team_id)
        n = self.matches_per_pairing

        # Calculate the confidence interval
        return get_confidence_interval_probability(p, n, confidence_level)

    def get_draw_confidence_interval(self, against_team_id, confidence_level=.95):
        """
        Get the confidence interval for the draw probability against a given team with a given confidence level
        :param against_team_id: team id
        :param confidence_level: confidence level
        :return: confidence interval
        """
        if against_team_id not in self.draws:
            return 0, 0

        p = self.get_draw_probability(against_team_id)
        n = self.matches_per_pairing

        # Calculate the confidence interval
        return get_confidence_interval_probability(p, n, confidence_level)

    def get_rounds_for_win_confidence_interval(self, against_team_id, confidence_level=.95):
        """
        Get the confidence interval for the average rounds to win against a given team with a given confidence level
        :param against_team_id: team id
        :param confidence_level: confidence level
        :return: confidence interval
        """
        if against_team_id not in self.rounds_for_win:
            return 0, 0

        x = sum(self.rounds_for_win[against_team_id]) / len(self.rounds_for_win[against_team_id])
        n = len(self.rounds_for_win[against_team_id])

        # Calculate the confidence interval
        return get_confidence_interval_expected_value_poisson(x, n, confidence_level)
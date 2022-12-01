import plotly.express as px

from tichu.agents.Max import Max
from tichu.agents.Min import Min
from tichu.agents.MinRisk import MinRisk
from tichu.agents.Priority_min_max import Priority_min_max
from tichu.agents.Random import Random
from tichu.Tournament import Tournament

agents = [Min(), Random(), Max(), MinRisk(), Priority_min_max()]


def show_tournament(tournament):
    wins = {}
    for team in tournament.teams:
        wins.setdefault(team.get_team_id(), 0)
        wins[team.get_team_id()] += team.score

    # Print sorted wins
    for k, v in sorted(wins.items(), key=lambda item: item[1], reverse=True):
        print(f"{k}: {v}")

    # Sort wins
    wins = {k: v for k, v in sorted(wins.items(), key=lambda item: item[1], reverse=True)}

    # Plot wins
    fig = px.bar(x=list(wins.keys()), y=list(wins.values()))
    fig.show()

    # Create plot of probability of winning
    fig = px.bar(x=list(wins.keys()), y=[team.get_win_probability() for team in tournament.teams], range_y=[0, 1])
    fig.show()


if __name__ == "__main__":
    matches_per_pairing = 10
    tournament = Tournament(agents, matches_per_pairing=matches_per_pairing)
    tournament.play()
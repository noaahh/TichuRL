from agents.Priority_max import Priority_max
from agents.Priority_min import Priority_min
from agents.Priority_min_copy import Priority_min_copy
from agents.Random import Random
from tichu.Tournament import Tournament

agents = [Priority_min(position=0), Random(position=3), Priority_max(position=1), Priority_min_copy(position=2)]

wins = {}
for k in range(20):
    tournament = Tournament(agents)
    tournament.play()

    for team in tournament.teams:
        wins.setdefault(team.get_team_id(), 0)
        wins[team.get_team_id()] += team.score

# Print sorted wins
for k, v in sorted(wins.items(), key=lambda item: item[1], reverse=True):
    print(f"{k}: {v}")
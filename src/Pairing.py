class Pairing:
    def __init__(self, teams):
        if len(teams) != 2:
            raise ValueError("Pairing must have 2 against_teams")

        self.teams = teams
        self.scoring_table = {teams[0].__str__(): {"0": 0, "1": 0, "2": 0, "3": 0},
                              teams[1].__str__(): {"0": 0, "1": 0, "2": 0, "3": 0}}

    def get_agent_list(self):
        return [self.teams[0].agents[0], self.teams[1].agents[0],
                self.teams[0].agents[1], self.teams[1].agents[1]]

    def get_pairing_id(self):
        return " vs ".join([team.__str__() for team in self.teams])

    def get_count_of_matches_played(self):
        """
        Get the number of matches played
        :return: number of matches played
        """
        if sum(self.scoring_table[self.teams[0].__str__()].values()) != sum(
                self.scoring_table[self.teams[1].__str__()].values()):
            raise ValueError("Number of matches played by both against_teams must be equal")

        return sum(self.scoring_table[self.teams[0].__str__()].values())

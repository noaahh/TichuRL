import random


class Random:
    def __init__(self, position):
        self.position = position
        self.strategy = "Random"

    def play(self, player):
        return random.choice(player.legal_actions)

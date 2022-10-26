import random


class Random():

    def play(self, player):

        return random.choice(player.legal_actions)

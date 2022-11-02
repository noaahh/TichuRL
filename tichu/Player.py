from tichu.Card import Cards, Card


class Player:

    def __init__(self, player_id=None):
        self.player_id = player_id
        self.hand = Cards()
        self.won_card = Cards()
        self.point = 0
        self.accumulated_points = []

    def show_hand(self):
        if self.hand.size == 0:
            print("No hand!")
        else:
            self.hand.show()

    def play_cards(self, cards, ground, num_out):
        if ground.type != 'none' and cards.type != 'strat_flush' and cards.type != 'four':
            if ground.type != cards.type:
                print(ground.type)
                print(cards.type)
                raise AssertionError

        if cards.type != 'pass':
            self.hand = self.hand - cards
            ground.type = cards.type
            ground.value = cards.value
            ground.cards = ground.cards + cards
            ground.player_id = self.player_id

        is_out = 0
        if self.hand.size == 0:
            is_out = 1

        return is_out

    def win(self, ground):
        self.won_card = self.won_card + ground.cards
        print(ground.cards)
        self.point = self.point + sum(x.point for x in ground.cards.cards)

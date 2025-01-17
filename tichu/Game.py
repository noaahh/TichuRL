from tichu.Card import Card, Deck
from tichu.Player import Player
from tichu.Round import Round
from tichu.Util import Deal


class Game:
    def __init__(self, env, num_players=4):
        self.num_players = num_players
        self.env = env
        self.rounds_played = 1
        self.rounds_played_per_player = {0: 0, 1: 0, 2: 0, 3: 0}

    def init_game(self):
        # Initialize parameters
        self.first_player = 0

        # Initialize deck
        self.deck = Deck()

        # Initialize players
        self.players = list()
        for i in range(self.num_players):
            player = Player(player_id=i)
            if i == 0 or i == 2:
                player.team = self.env.team_names[0]
            else:
                player.team = self.env.team_names[1]
            self.players.append(player)

        # Deal cards
        for i in range(self.num_players):
            self.deck, self.players[i].hand = Deal(self.deck, self.players[i].hand, deck=1, card_num=13)

        ###DEBUG
        #        strat_flush = [Card('2','Spade'), Card('3','Spade'), Card('4','Spade'),Card('5','Spade'),Card('6','Spade')]
        #        self.deck, self.players[0].hand = Deal(self.deck, self.players[0].hand, deck=0, card_deal = strat_flush)
        #        self.deck, self.players[0].hand = Deal(self.deck, self.players[0].hand, deck=1, card_num=8)
        #        for i in range(1,4):
        #            self.deck, self.players[i].hand = Deal(self.deck, self.players[i].hand, deck=1, card_num=13)
        ###

        # Show hands and determine first player
        for i in range(self.num_players):
            if self.players[i].hand.cards.count(Card('2', 'Club')) == 1:
                self.first_player = i
                self.env.positional_outcome[self.players[i].team] = 1
                self.env.positional_outcome[self.players[(i + 1) % 4].team] = 0

        # Initialize round
        self.round = Round(self.num_players, self.first_player, self)

        return self.round.get_state(self.players, self.first_player), self.first_player

    def next_turn(self, action):

        self.round.proceed_round(self.players, action)
        next_player_id = self.round.current_player
        state = self.round.get_state(self.players, next_player_id)

        return state, next_player_id

    def get_active_player(self, player_id):
        return self.round.get_state(self.players, player_id)

    def is_over(self):
        return self.round.get_num_out() > 2

    def get_player_num(self):
        return self.num_players

    def get_points(self):
        points = [0, 0, 0, 0]
        out_players = self.round.get_out_players()
        point = 300

        self.env.rounds_to_win = self.rounds_played_per_player[out_players[0]]

        for i in out_players:
            points[i] = point + self.players[i].point
            self.players[i].accumulated_points.append(points[i])
            point -= 100

        if 0 in points:
            points[points.index(0)] = self.players[points.index(0)].point

        return points

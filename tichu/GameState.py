
# GameState of the game
class GameState:
	# Current hand of the active player
	hand = None

	# Current cards on the ground TODO evaluate the cut
	ground = None

	# All actions of the hand ignoring current ground
	action = None

	# All possible playable options
	legal_actions = None

	# num of cards
	card_num = []

	# All played cards
	played_cards = None

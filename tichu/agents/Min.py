class Min:
    def __init__(self, position):
        self.position = position
        self.strategy = "Min"

    def play(self, player):
        ### First player: Play high priority and min combination
        if player.ground.type == 'none':
            actions = player.action

            idx = 5
            while idx >= 0:
                if len(actions[idx]) > 0:
                    return actions[idx][0]
                idx -= 1

        ### Play min combination
        else:
            actions = player.legal_actions
            try:
                rt = actions[1]
                return rt
            except:
                return actions[0]

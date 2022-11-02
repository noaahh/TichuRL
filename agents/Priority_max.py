class Priority_max:
    def __init__(self, position):
        self.position = position
        self.strategy = "Priority_max"

    def play(self, player):
        ### First player: Play high priority and min combination
        if player.ground.type == 'none':
            actions = player.action

            idx = 0
            while idx < 5:
                if len(actions[idx]) > 0:
                    return actions[idx][0]
                idx += 1

        ### Play min combination
        else:
            actions = player.legal_actions
            try:
                return actions[-1]
            except:
                return actions[0]

class Priority_min():

    def play(self, player):

        ### First player: Play high priority and min combination
        if player.ground.type == 'none':
            actions = player.action
            print(actions)
            for action in actions:
                for card in action:
                    card.show()




        ### Play min combination
        else:
            actions = player.legal_actions
            try:
                rt = actions[1]
                return rt
            except:
                return actions[0]

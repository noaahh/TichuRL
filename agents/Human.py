import sys


class Human():

    def play(self, play):
        print('\n')
        print('*** Card num [player1] ' + str(play.card_num[1]) + ' [player2] ' + str(
            play.card_num[2]) + ' [player3] ' + str(play.card_num[3]))
        print('*** Player hand')
        play.hand.show()
        for i in range(len(play.legal_actions)):
            print('*** (' + str(i) + ') ' + play.legal_actions[i].type)
            play.legal_actions[i].show()
        while True:
            try:
                p_input = input('*** Choose cards :')
                if int(p_input) == 999:
                    # sys.exit()
                    break
                else:
                    for i in range(len(play.legal_actions) * 6 + 6):
                        sys.stdout.write("\033[F")
                        sys.stdout.write("\033[K")
                    return play.legal_actions[int(p_input)]
                break
            except:
                pass

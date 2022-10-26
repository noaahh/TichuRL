import random

import numpy as np

from tichu.Card import Cards


class Ground:

    def __init__(self):
        self.type = 'none'
        self.value = 0
        self.cards = Cards()
        self.player_id = 0


### Deal cards from Cards() to Cards()
def Deal(giver, recver, deck=0, card_num=0, card_deal=None):
    if deck == 1:
        cards = Cards(card_list=random.sample(giver.cards, card_num))
        giver -= cards
        recver += cards
    else:
        cards = Cards(card_deal)
        giver -= cards
        recver += cards
    return giver, recver


### Return legal combination considering ground
### 0: solo, 1: pair, 2: triple, 3: four, 4: full, 5: strat, 6: strat_flush, 7: pair_seq
def get_legal_combination(combinations, ground):
    rt_set = list()
    pass_set = Cards(ctype='pass')
    rt_set.append(pass_set)
    remove_set = list()

    if ground.type == 'none':
        rt_set = combinations[0] + combinations[1] + combinations[2] + combinations[3] + combinations[4] + combinations[
            5] + combinations[6] + combinations[7]
    elif ground.type == 'solo':
        for i in combinations[0]:
            if i.value <= ground.value:
                remove_set.append(i)
        for i in remove_set:
            combinations[0].remove(i)
        rt_set = rt_set + combinations[0] + combinations[3] + combinations[6]
    elif ground.type == 'pair':
        for i in combinations[1]:
            if i.value <= ground.value:
                remove_set.append(i)
        for i in remove_set:
            combinations[1].remove(i)
        rt_set = rt_set + combinations[1] + combinations[3] + combinations[6]
    elif ground.type == 'triple':
        for i in combinations[2]:
            if i.value <= ground.value:
                remove_set.append(i)
        for i in remove_set:
            combinations[2].remove(i)
        rt_set = rt_set + combinations[2] + combinations[3] + combinations[6]
    elif ground.type == 'four':
        for i in combinations[3]:
            if i.value <= ground.value:
                remove_set.append(i)
        for i in remove_set:
            combinations[3].remove(i)
        rt_set = rt_set + combinations[3]
    elif ground.type == 'full':
        for i in combinations[4]:
            if i.value <= ground.value:
                remove_set.append(i)
        for i in remove_set:
            combinations[4].remove(i)
        rt_set = rt_set + combinations[4] + combinations[3] + combinations[6]
    elif ground.type == 'strat':
        for i in combinations[5]:
            if i.value / 100 != ground.value / 100 or i.value % 100 <= ground.value % 100:
                remove_set.append(i)
        for i in remove_set:
            combinations[5].remove(i)
        rt_set = rt_set + combinations[5] + combinations[3] + combinations[6]
    elif ground.type == 'strat_flush':
        for i in combinations[6]:
            if i.value / 100 != ground.value / 100 or i.value % 100 <= ground.value % 100:
                remove_set.append(i)
        for i in remove_set:
            combinations[6].remove(i)
        rt_set = rt_set + combinations[6]
    elif ground.type == 'pair_seq':
        for i in combinations[7]:
            if i.value / 100 != ground.value / 100 or i.value % 100 <= ground.value % 100:
                remove_set.append(i)
        for i in remove_set:
            combinations[7].remove(i)
        rt_set = rt_set + combinations[7] + combinations[3] + combinations[6]
    else:
        raise ValueError("[get_legal_combination] Wrong ground type")

    return rt_set


def reorganize(trajectories, R):
    player_num = len(trajectories)
    new_trajectories = [[] for _ in range(player_num)]

    for player in range(player_num):
        for i in range(0, len(trajectories[player]) - 2, 2):
            if i == len(trajectories[player]) - 3:
                reward = R[player]
                terminal = True
            else:
                min_card = 13
                for j in range(player_num):
                    if j != player:
                        min_card = min(trajectories[player][0].card_num[j], min_card)
                reward = min_card - trajectories[player][0].card_num[player]
                terminal = False
            transition = trajectories[player][i:i + 3].copy()
            transition.insert(2, reward)
            transition.append(terminal)

            new_trajectories[player].append(transition)

    return new_trajectories


def num2action(action_num, hand_list):
    action = Cards()

    for i in range(len(hand_list)):
        if (action_num % (2 ** (i + 1))) // (2 ** i) == 1:
            action.add(hand_list[i])

    action.set_combination()
    return action


def action2num(action, hand):
    action_num = 0

    for i in range(action.size):
        for j in range(hand.size):
            if action.cards[i] == hand.cards[j]:
                action_num += 2 ** j

    return action_num


def get_available_action_array(action_set, hand):
    action_array = np.zeros((8192,), dtype=int)
    for i in action_set:
        action_array[action2num(i, hand)] = 1
    return action_array


def state_parse(state):
    hand = state.hand
    hand_state = np.zeros(26)
    for i in range(hand.size):
        hand_state[2 * i] = hand.cards[i].value
        if hand.cards[i].suit == 'Spade':
            hand_state[2 * i + 1] = 1
        elif hand.cards[i].suit == 'Heart':
            hand_state[2 * i + 1] = 2
        elif hand.cards[i].suit == 'Dia':
            hand_state[2 * i + 1] = 3
        elif hand.cards[i].suit == 'Club':
            hand_state[2 * i + 1] = 4
        else:
            raise ValueError

    ground_state = np.zeros(3)
    ground_type = state.ground.type
    if ground_type == 'none':
        ground_state[0] = 0
    elif ground_type == 'solo':
        ground_state[0] = 1
    elif ground_type == 'pair':
        ground_state[0] = 2
    elif ground_type == 'triple':
        ground_state[0] = 3
    elif ground_type == 'four':
        ground_state[0] = 4
    elif ground_type == 'full':
        ground_state[0] = 5
    elif ground_type == 'strat':
        ground_state[0] = 6
    elif ground_type == 'strat_flush':
        ground_state[0] = 7
    elif ground_type == 'pair_seq':
        ground_state[0] = 8
    else:
        raise ValueError
    ground_state[1] = state.ground.value
    ground_state[2] = state.ground.player_id

    card_state = np.zeros(3)
    card_state[0] = state.card_num[1]
    card_state[1] = state.card_num[2]
    card_state[2] = state.card_num[3]

    used = np.zeros(8)
    state.played_cards.sort()
    size = len(state['played_cards'])
    if size >= 8:
        for i in range(8):
            used[i] = state['played_cards'][size - 1 - i].value

    rt_state = np.concatenate((hand_state, ground_state, card_state, used), axis=None)

    return rt_state

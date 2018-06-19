from deuces import Evaluator
from deuces import Card as deucesCard

CHAR_SUIT = {
    's' : 0, # spades
    'h' : 1, # hearts
    'd' : 2, # diamonds
    'c' : 3 # clubs
}

CHAR_STR = {
    "A": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "T": 10,
    "J": 11,
    "Q": 12,
    "K": 13
}

evaluator = Evaluator()


class Card(object):

    def __init__(self, card):
        self.card = card

    @property
    def serial(self):
        if self.card == '-':
            return -1
        return CHAR_SUIT[self.card[1]] * 13 +  CHAR_STR[self.card[0]]

    @staticmethod
    def get_card_suite(board, hand):
        if not (all(hand) and all(board)):
            return -1
        elif '-' in hand or '-' in board:
            return -1
        board = [deucesCard.new(c) for c in board]
        hand = [deucesCard.new(c) for c in hand]
        return evaluator.evaluate(board, hand)


if __name__ == '__main__':
    print Card('As').serial
    print Card('Kc').serial

    print Card.get_card_suite(["Kh", "Ah", "Th"], ["As", "2c"])

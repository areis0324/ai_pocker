from talker.client import PokerClient
from talker.action import *


class BasicPlayer(PokerClient):
    CLIENT_NAME = "austin"

    def predict(self):
        if self.my_card_ranking == -1:
            return CALL
        elif self.my_card_ranking > 5000:
            return FOLD
        elif self.my_card_ranking > 3000:
            return CALL
        return RAISE




if __name__ == '__main__':
    pc = BasicPlayer()
    pc.doListen()

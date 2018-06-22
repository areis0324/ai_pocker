from talker.client import PokerClient
from talker.action import *




class RNNPlayer(PokerClient):
    CLIENT_NAME = "austin"

    def predict(self):
        return RAISE


if __name__ == '__main__':
    pc = RNNPlayer()
    pc.doListen()

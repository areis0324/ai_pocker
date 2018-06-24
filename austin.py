import traceback
import numpy as np

from talker.client import PokerClient
from talker.action import *
from holdem.card import Card
from trainer import predict


class RNNPlayer(PokerClient):
    CLIENT_NAME = "austin"


    @property
    def fight_weight(self):
        #print "fight: myBet(%s), minBet(%s), totalBet(%s)" % (self.myBet, self.minBet, self.totalBet)

        if not self.minBet:
            return 1

        weight = sum(self.myBet + [self.minBet]) / self.minBet
        if not weight:
            weight = 1
        return np.sqrt(weight)

    @property
    def rnn_feature(self):
        # rnn features:
        # [
        #   round_seq, raiseCount[0], betCount[0],
        #   privateCards[0], privateCards[1],
        #   0, 0, 0, 0, 0, # public card
        #   0, # card ranking
        # ]

        try:
            features = []

            for seq in Round.ALL:
                public_cards = [0, 0, 0, 0, 0]

                for i, pc in enumerate(self.board):
                    # flop(1) 3 cards,
                    # turn(2) 4 cards,
                    # river(3) 5 cards
                    if i > self.roundSeq + 1:
                        continue
                    public_cards[i] = Card(pc).serial

                round_feature = [
                    seq, self.raiseCount[seq], self.betCount[seq],
                    Card(self.cards[0]).serial, Card(self.cards[1]).serial
                ]

                round_feature.extend(public_cards)
                round_feature.append(self.cardRanking[seq])

                features.append(round_feature)

            #print "-->predict features:", features
            return features
        except BaseException as err:
            print err, traceback.print_exc()
            return []

    def ask_rnn(self):
        features = self.rnn_feature
        if not features:
            print "!!! get features faileds"
            return 0
        x_data = np.array(self.rnn_feature, dtype=np.float32)
        s_data = self.roundSeq + 1
        pred = predict(x_data, s_data)
        return pred[0] - pred[1]

    def predict(self):
        pred_rnn = self.ask_rnn()
        print "***rnn predict:", pred_rnn

        act = FOLD

        # Rule base
        if 1 < self.cardRanking[self.roundSeq] < 300:
            act = RAISE
        elif 1 < self.cardRanking[self.roundSeq] < 1000/np.sqrt(self.roundSeq + 1):
            act = CHECK

        # RNN base
        elif pred_rnn > 10 / self.fight_weight:
            act = RAISE
        elif pred_rnn > 5 / self.fight_weight:
            act = CALL
        elif -5 * self.fight_weight < pred_rnn < 0:
            act = CHECK
        elif not self.needBet:
            act = CHECK
        elif pred_rnn < -10 * self.fight_weight:
            act = FOLD

        print "@@@@ My decision is %s with: fight weight(%s), needbet(%s) @@@@@@" % (ACT_STR[act], self.fight_weight, self.needBet)
        return act

if __name__ == '__main__':
    pc = RNNPlayer()
    pc.doListen()

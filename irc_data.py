import os
import numpy as np
from operator import add
from holdem.holdem_calc import holdem_cal
from holdem.card import Card


#pylint:disable=all

# tableNum | unknown | serialNum | numPlayers | preFlopMoneyInPot | flopMoneyInPot | turnMoneyInPot | riverMoneyInPot | publicCards
#798758687   5  9803  9  5/105   4/265   3/445    3/485    Jc 9c 7h Ad Kh
DATA_PATH = "../data/IRCdata/holdem"
TABLE_FILE = "hdb"
PLAYER_FILE = "hroster"
PLAYER_RECORD_FILE = "pdb/pdb.{}"

class Game(object):
    def __init__(self, data_path=None):
        self.table = {}
        self.player = {}
        self.player_records = {}
        self.data_path = data_path

        with open(os.path.join(os.getcwd(), self.data_path, TABLE_FILE), 'r') as fp:
            read_lines = fp.readlines()
            for l in read_lines:
                l = l.split()

                #798758687   5  9803  9  5/105   4/265   3/445    3/485    Jc 9c 7h Ad Kh
                publicCards = l[8:]

                # just only save the completed game
                if len(publicCards) != 5:
                    continue

                self.table[l[0]] = {
                    "tableNo": l[0],
                    "numPlayers": l[3],
                    "publicCards": publicCards,
                    "raiseCount": [],
                    "betCount": [],
                }

        with open(os.path.join(os.getcwd(), self.data_path, PLAYER_FILE), 'r') as fp:
            read_lines = fp.readlines()
            for l in read_lines:
                l = l.split()
                if l[0] not in self.table:
                    continue
                self.table[l[0]]["player"] = {player:None for player in l[2:]}

    def get_game_info(self, table_no):
        if table_no not in self.table:
            return None

        for player in self.table[table_no]["player"]:
            player_rec = self.get_player_records(player)

            if not player_rec:
                continue
            elif table_no not in player_rec:
                continue

            palyer_game = player_rec[table_no]
            self.table[table_no]["player"][player] = palyer_game

            # assign winner
            if palyer_game["win"]:
                self.table[table_no]["winner"] = player

            # count raise
            if not self.table[table_no]["raiseCount"]:
                self.table[table_no]["raiseCount"] = palyer_game["raise"]
            else:
                self.table[table_no]["raiseCount"] = list(map(add, self.table[table_no]["raiseCount"], palyer_game["raise"]))

            # count bet
            if not self.table[table_no]["betCount"]:
                self.table[table_no]["betCount"] = palyer_game["bet"]
            else:
                self.table[table_no]["betCount"] = list(map(add, self.table[table_no]["betCount"], palyer_game["bet"]))

        return self.table[table_no]

    def get_player_records(self, player):
        if player not in self.player_records:

            file_path = os.path.join(os.getcwd(), self.data_path, PLAYER_RECORD_FILE.format(player))
            if not os.path.exists(file_path):
                return None

            self.player_records[player] = {}
            with open(file_path, 'r') as fp:
                read_lines = fp.readlines()
                for l in read_lines:
                    l = l.split()

                    # table no
                    # Quick     798758687  9  2 Bc  bc    kccA  -          120  120    0 Qs Jd
                    # actions
                    # B => small blind/big blind
                    # b => bet
                    # k => check
                    # r => raise
                    # c => call
                    # f => fold
                    # A => all in

                    # only save the player who finish the game
                    if not l[11:]:
                        continue

                    self.player_records[player][l[1]] = {
                            "name": player,
                            "order": l[3],
                            "action": l[4:8],
                            "give": int(l[9]),
                            "get": int(l[10]),
                            "win": 1 if int(l[10]) > int(l[9]) else 0,
                            "privateCards": l[11:] if l[11:] else ['-', '-'],
                            "raise": [act.count('r') for act in l[4:8]],
                            'bet': [act.count('b') for act in l[4:8]],
                    }

        return self.player_records.get(player, None)

    def get_features(self, table_info, round_seq):
        ############################################
        # roundName, raiseCount, betCount,privateCards, publicCards, evaluate,  histogram
        #   0      ,    1      , 2       , 1, 23      , 1, 2, 4, 0,0,  7624, TBD
        #   0.0, 0.0, 0.9130434782608695, 0.0, 0.0, 0.0, 0.08695652173913043, 0.0, 0.0, 0.0, 1, 11, 22, 33, 44, 55
        ##############

        ###### card Histogram
        # High Card :  0.0
        # Pair :  0.0
        # Two Pair :  0.913043478261
        # Three of a Kind :  0.0
        # Straight :  0.0
        # Flush :  0.0
        # Full House :  0.0869565217391
        # Four of a Kind :  0.0
        # Straight Flush :  0.0
        # Royal Flush :  0.0
        #######################

        #numPlayers = table_info["numPlayers"]

        if not table_info:
            return None

        raiseCount = table_info["raiseCount"]
        betCount = table_info["betCount"]
        publicCards = [Card(card).serial for card in table_info["publicCards"]]

        def _extract_features(records):
            # "Deal", "Flop", "Turn", "River": 0, 1, 2, 3
            privateCards = [Card(card).serial for card in records["privateCards"]]

            deal_round = [round_seq, raiseCount[0], betCount[0],
                          privateCards[0], privateCards[1],
                          0, 0, 0, 0, 0, # public card
                          0, # card ranking
                          ]
                          #+ [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # card histogram

            flop_round = [round_seq, raiseCount[1], betCount[1],
                          privateCards[0], privateCards[1],
                          publicCards[0],
                          publicCards[1],
                          publicCards[2],
                          0,
                          0,
                          Card.get_card_suite(table_info["publicCards"][0:3], records["privateCards"])
                          ] \
                          if round_seq >= 1 else \
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]# + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # card histogram
                          #+ holdem_cal(records["privateCards"], table_info["publicCards"][0:3])[0] \

            turn_round = [round_seq, raiseCount[2], betCount[2],
                          privateCards[0], privateCards[1],
                          publicCards[0],
                          publicCards[1],
                          publicCards[2],
                          publicCards[3], 0,
                          Card.get_card_suite(table_info["publicCards"][0:4], records["privateCards"]),
                          ] \
                          if round_seq >= 2 else \
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]# + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # card histogram
                          #+ holdem_cal(records["privateCards"], table_info["publicCards"][0:4])[0] \


            river_round = [round_seq, raiseCount[3], betCount[3],
                          privateCards[0],
                          privateCards[1],
                          publicCards[0],
                          publicCards[1],
                          publicCards[2],
                          publicCards[3],
                          publicCards[4],
                          Card.get_card_suite(table_info["publicCards"][0:5], records["privateCards"]),
                          ] \
                          if round_seq == 3 else \
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]# + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # card histogram
                          #+ holdem_cal(records["privateCards"], table_info["publicCards"][0:5])[0] \

            return [deal_round, flop_round, turn_round, river_round]

        results = []

        # not found the winner in this game, it is possible the winner has no private cards
        if "winner" not in table_info:
            return results

        # add winer into the 1st
        results.append(_extract_features(self.player_records[table_info["winner"]][table_info["tableNo"]]))

        # add the loser
        for player in table_info["player"]:
            if player == table_info["winner"]:
                continue
            elif player not in self.player_records:
                continue
            player_rec = self.player_records[player]
            if table_info["tableNo"] not in player_rec:
                continue
            results.append(_extract_features(self.player_records[player][table_info["tableNo"]]))

        return results

class Provider(object):


    @staticmethod
    def next_batch(batch_size):

        x_data = []
        y_data = []

        # to list the train data folder
        for dir_name in os.listdir(DATA_PATH):
            dir_name = os.path.join(DATA_PATH, dir_name)

            # record the training
            with open("train.log", "w+") as f:
                f.write(dir_name)

            try:
                game = Game(dir_name)

                # to iterate the all game data in YYYY-MM
                for table_no in game.table:
                    try:
                        # get the specified game record
                        table_info = game.get_game_info(table_no)

                        # Extract the 4 rounds data in this game
                        # Train the data step by step
                        # 0:deal, 1:flop, 2:turn, 3:river

                        # skip "Deal" since it has too less features
                        for seq in (1, 2, 3):

                            features = game.get_features(table_info, seq)

                            if not features:
                                continue

                            x_data += features
                            # the 1st player is winner
                            y_data += [1] + [0 for _ in xrange(len(features) - 1)]

                            if len(y_data) > batch_size:
                                y_data = y_data[:batch_size]
                                x_data = x_data[:batch_size]

                                # for RNN seq_length_batch, which step is useful
                                batch_seq = np.full(batch_size, seq + 1, dtype=np.int)

                                # label this instance
                                y_data =[np.array([yi, yi ^ 1]) for yi in y_data]

                                # import pdb
                                # pdb.set_trace()
                                yield np.array(x_data, dtype=np.float32), np.array(y_data, dtype=np.float32), batch_seq
                                y_data = []
                                x_data = []

                    except BaseException as err:
                        raise
            except BaseException as err:
                    raise

        print "===== no training set ===="

if __name__ == '__main__':
    game = Game("../data/IRCdata/holdem/199505/")
    table_info = game.get_game_info('799891180')
    # print table_info
    # i = 0
    # for x, y in Provider.next_batch(1):
    #     i += 1
    #     print x, y
    #     if i > 0:
    #         break

    # print table_info
    # print game.get_features(table_info)
    print holdem_cal(["Ad", "Kd"], ["Kc", "Qs", "2h","Ah"])
    #print holdem_cal(["Ad", "Kd"], [])

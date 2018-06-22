#! /usr/bin/env python
# -*- coding:utf-8 -*-

#pylint: disable=all


import json
import pprint
import traceback
from action import *
from websocket import create_connection

import event as EVNETNAME
import hashlib


ws = create_connection("ws://poker-dev.wrs.club:3001")
RETRY = 3


class PokerClient(object):
    CLIENT_NAME = "player1"

    def __init__(self):
        self._name_hash = None
        self._chips = 0
        self._cards = []
        self._board = []
        self._big_blind = None
        self._small_blind = None

        self.minBet = 0

    @property
    def name_hash(self):
        if not self._name_hash:
            m = hashlib.md5()
            m.update(self.CLIENT_NAME)
            self._name_hash = m.hexdigest()
        return self._name_hash

    @property
    def is_big_blind(self):
        return self._big_blind == self.name_hash

    @property
    def is_small_blind(self):
        return self._small_blind == self.name_hash

    def _send_event(self, event_name, data=None):
        retry = 0
        payload = {"eventName": event_name}
        if data:
            payload["data"] = data

        while 1:
            try:
                ws.send(json.dumps(payload))
                return True
            except BaseException as err:
                print "send event error: %s", err
                if retry < RETRY:
                    continue
                else:
                    return False
            retry += 1

    def search(self, players):
        for p in players:
            if p['playerName'] == self.name_hash:
                return p

    def join(self):
        print "%s tries to join.." % self.CLIENT_NAME
        return self._send_event(EVNETNAME.JOIN, {"playerName": self.CLIENT_NAME})

    def reload(self):
        return self._send_event(EVNETNAME.RELOAD)

    ##### action function ########
    def _act_new_peer(self, action, data):
        print len(data)
        print "Game Stat: {}".format(action)

    def _act_new_round(self, action, data):
        print len(data)
        print "Game Stat: {}".format(action)

        p = self.search(data["players"])
        self.chards = p["cards"]
        self.chips = p["chips"]

        t = data["table"]
        self._small_blind = t["smallBlind"]
        self._big_blind = t["bigBlind"]

    def _act_deal(self, action, data):
        print "Game Stat: {}".format(action)
        t = data["table"]
        self._board = t["board"]

    def _act_action(self, do_act, bet_times=1):

        a = { "action": 'fold', "amount": self.minBet}

        if do_act == FOLD:
            a = { "action": 'fold', "amount": self.minBet}
        elif do_act == CHECK:
            a = { "action": 'check', "amount": self.minBet}
        elif do_act == BET:
            a = { "action": 'bet', "amount": self.minBet % bet_times}
        elif do_act == RAISE:
            a = { "action": 'raise', "amount": self.minBet % bet_times}
        elif do_act == CALL:
            a = { "action": 'call', "amount": self.minBet}
        else:
            a = { "action": 'allin', "amount": self.minBet}

        print "current action is %s !!!" % ACT_STR[do_act]

        return self._send_event(EVNETNAME.ACTION, a)

    #############override#################

    def predict(self):
        """
        the cation must be predicted in this function
        """
        return FOLD

    ##############################

    def takeAction(self, action, data):
        try:
            if action == EVNETNAME.NEW_PEER:
                self._act_new_peer(action, data)
            elif action == EVNETNAME.NEW_ROUNT:
                self._act_new_round(action, data)
            elif action == EVNETNAME.DEAL:
                self._act_deal(action, data)
            elif action in (EVNETNAME.ACTION, EVNETNAME.BET):
                self.minBet = data['self']['minBet']
                action = self.predict()
                return self._act_action(action)

            elif action == EVNETNAME.START_RELOAD:
                p = self.search(data["players"])
                if p["chips"] == 0:
                    self.reload()
            elif action == EVNETNAME.SHOW_ACTION:
                # record behavior
                pass
            elif action == EVNETNAME.ROUND_END:
                print "Game Stat: {}".format(action)
                pass
            elif action == EVNETNAME.GAME_OVER:
                print "Game Stat: {}".format(action)
                #sys.exit(1)
            else:
                print "Not Handle state : {}".format(action)
                pass
        except BaseException as err:
            print "action error: %s, %s" % (err, traceback.print_exc())
            pprint.pprint(
                        {
                            "event": action,
                            "data":data,
                        }
                    )

    def doListen(self):

        try:
            # ws.send(json.dumps({
            #     "eventName": "__join",
            #     "data": {
            #         "playerName": "player1"
            #     }
            # }))

            if self.join():
                print "connected!!"
            else:
                print "connecton fail!!"

            while 1:
                result = ws.recv()
                msg = json.loads(result)
                event_name = msg["eventName"]
                data = msg["data"]

                # pprint.pprint(
                #         {
                #             "event": event_name,
                #             "data":data,
                #         }
                #     )
                self.takeAction(event_name, data)

        except Exception as e:
            print e
            #self.doListen()


if __name__ == '__main__':
    pc = PokerClient()
    pc.doListen()

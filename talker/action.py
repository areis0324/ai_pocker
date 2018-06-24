FOLD = 0
CHECK = 1
BET = 2
RAISE = 3
CALL = 4
ALL_IN = 5


ACT_STR = {
    FOLD: "fold",
    CHECK: "check",
    BET: "bet",
    RAISE: "raise",
    CALL: "call",
    ALL_IN: "all_in",
}


class Round(object):
    DEAL = 0
    FLOP = 1
    TURN = 2
    RIVER = 3
    ALL = [DEAL, FLOP, TURN, RIVER]

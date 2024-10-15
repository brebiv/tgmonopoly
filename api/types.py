from enum import Enum

class GameActionType:
    START_GAME = 'start_game'
    ROLL_DICE = 'roll_dice'
    BUY_PROPERTY = 'buy_property'
    PAY_RENT = 'pay_rent'
    PAY_FOR_PRISON = 'pay_for_prison'

class GameEventType:
    START_GAME = 'start_game'
    ROLL_DICE = 'roll_dice'
    MOVE_PLAYER = 'move_player'
    BUY_PROPERTY = 'buy_property'
    PASSED_START = 'passed_start'
    STEPPED_ON_OWN_PROPERTY = 'stepped_on_own_property'
    PAY_RENT = 'pay_rent'
    GO_TO_PRISON = 'go_to_prison'
    RELEASE_FROM_PRISON = 'release_from_prison'
    PRISON_RELEASE_FAIL = 'prison_release_fail'
    PAY_FOR_PRISON = 'pay_for_prison'

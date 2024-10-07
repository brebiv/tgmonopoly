from enum import Enum

class GameActionType:
    START_GAME = 'start_game'
    ROLL_DICE = 'roll_dice'
    MOVE_PLAYER = 'move_player'
    BUY_PROPERTY = 'buy_property'
    PAY_RENT = 'pay_rent'

class GameEventType:
    START_GAME = 'start_game'
    ROLL_DICE = 'roll_dice'
    MOVE_PLAYER = 'move_player'
    BUY_PROPERTY = 'buy_property'
    PASSED_START = 'passed_start'
    STEPPED_ON_OWN_PROPERTY = 'stepped_on_own_property'
    PAY_RENT = 'pay_rent'

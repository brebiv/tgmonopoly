from django.db import models


class GameEffectTypes(models.TextChoices):
    ROLL_DICE = 'roll_dice', 'Roll Dice'
    ASK_BUY = 'ask_buy', 'Ask Buy'
    PAY_RENT = 'pay_rent', 'Pay Rent'
    PAY_REPAIRS = 'pay_repairs', 'Pay Repairs'
    IN_CASINO = 'in_casino', 'In Casino'
    IN_TRADE = 'in_trade', 'In Trade'
    IN_AUCTION = 'in_auction', 'In Auction'



class AvailableSVGIcons(models.TextChoices):
    WIND_POWER = 'WIND_POWER', 'Wind Power'
    DAM = 'DAM', 'Dam'
    SOLAR_POWER = 'SOLAR_POWER', 'Solar Power'
    NUKE = 'NUKE', 'Nuke'

# Timeouts in seconds
EFFECTS_TIMEOUTS = {
    GameEffectTypes.ROLL_DICE: 20,
    GameEffectTypes.ASK_BUY: 10,
    GameEffectTypes.PAY_RENT: 10,
    GameEffectTypes.PAY_REPAIRS: 10,
    GameEffectTypes.IN_CASINO: 10,
    GameEffectTypes.IN_TRADE: 20,
    GameEffectTypes.IN_AUCTION: 20,
}

DISABLE_AFK = True
MAXIMUM_JAIL_TURNS = 3
PRISON_PAY_AMOUNT = 50
MORTAGE_MAX_TURNS = 15
MORTAGE_INTEREST_RATE = 1.1
MAX_HOUSES = 5
AUCTION_STEP = 10
MAX_TRADE_PROPOSALS = 2
STARTING_CASH = 1500
MAX_DOUBLES = 3
TAX_AMOUNT = 200

# For testing
TEST_DICE_VALUES = [1, 2]
TEST_DICE_DOUBLE = [3, 3]

from django.db import models


class GameEffectTypes(models.TextChoices):
    ROLL_DICE = 'roll_dice', 'Roll Dice'
    ASK_BUY = 'ask_buy', 'Ask Buy'
    PAY_RENT = 'pay_rent', 'Pay Rent'
    PAY_REPAIRS = 'pay_repairs', 'Pay Repairs'



class AvailableSVGIcons(models.TextChoices):
    WIND_POWER = 'WIND_POWER', 'Wind Power'
    DAM = 'DAM', 'Dam'
    SOLAR_POWER = 'SOLAR_POWER', 'Solar Power'
    NUKE = 'NUKE', 'Nuke'

# Timeouts in seconds
EFFECTS_TIMEOUTS = {
    GameEffectTypes.ROLL_DICE: 10,
    GameEffectTypes.ASK_BUY: 10,
    GameEffectTypes.PAY_RENT: 10,
    GameEffectTypes.PAY_REPAIRS: 10,
}

DISABLE_AFK = True
MAXIMUM_JAIL_TURNS = 3
PRISON_PAY_AMOUNT = 50
MORTAGE_MAX_TURNS = 15
MORTAGE_INTEREST_RATE = 1.1
MAX_HOUSES = 5

from .models import GameEffect

# Timeouts in seconds
EFFECTS_TIMEOUTS = {
    GameEffect.ROLL_DICE: 10,
    GameEffect.ASK_BUY: 10,
    GameEffect.PAY_RENT: 10,
}

DISABLE_AFK = True
MAXIMUM_JAIL_TURNS = 3
PRISON_PAY_AMOUNT = 50

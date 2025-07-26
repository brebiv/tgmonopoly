from .base import BaseMonopolyConfig
from game.models import PendingAction


class ClassicMonopolyConfig(BaseMonopolyConfig):
    STARTING_CASH: int = 1000
    MORTGAGE_INTEREST_RATE: float = 1.1
    MAX_DOUBLES: int = 3

    PENDING_ACTION_TIMEOUTS: dict[PendingAction.Types, int] = {
        PendingAction.Types.ROLL_DICE: 10,
        PendingAction.Types.BUY_PROPERTY: 10,
        PendingAction.Types.PAY_RENT: 10,
        PendingAction.Types.PAY_TAX: 10,
        PendingAction.Types.PAY_REPAIRS: 10,
        PendingAction.Types.IN_CASINO: 10,
        PendingAction.Types.IN_AUCTION: 10,
        PendingAction.Types.IN_TRADE: 10,
    }


# MAXIMUM_JAIL_TURNS = 3
# PRISON_PAY_AMOUNT = 50
# MORTAGE_MAX_TURNS = 15
# MAX_HOUSES = 5
# AUCTION_STEP = 10
# MAX_TRADE_PROPOSALS = 2
# STARTING_CASH = 1500
# MAX_DOUBLES = 3
# TAX_AMOUNT = 200
# ENABLE_AUTO_START_ON_JOIN = True
# ALLOW_CREATING_MULTIPLE_GAMES = False

from dataclasses import dataclass
from game.models import Ownership
from game import config

class GameActionType:
    START_GAME = 'start_game'
    ROLL_DICE = 'roll_dice'
    BUY_PROPERTY = 'buy_property'
    PAY_RENT = 'pay_rent'
    PAY_FOR_PRISON = 'pay_for_prison'
    MORTAGE_PROPERTY = 'mortage_property'
    BUYOUT_PROPERTY = 'buyout_property'
    BUY_HOUSE = 'buy_house'
    SELL_HOUSE = 'sell_house'
    PAY = "pay"
    REJECT = "reject"
    ACCEPT = "accept"
    CREATE_TRADE = "create_trade"
    START_AUCTION = "start_auction"

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
    MORTAGE_PROPERTY = 'mortage_property'
    BUYOUT_PROPERTY = 'buyout_property'
    BUY_HOUSE = 'buy_house'
    SELL_HOUSE = 'sell_house'
    CHANCE_CARD = 'chance_card'
    PAY_TO_BANK = 'pay_to_bank'
    GO_TO_CASINO = 'go_to_casino'
    REJECT_CASINO = 'reject_casino'
    WON_CASINO = 'won_casino'
    LOST_CASINO = 'lost_casino'
    TIMEOUT = 'timeout'
    CREATE_TRADE = 'create_trade'
    REJECT_TRADE = 'reject_trade'
    ACCEPT_TRADE = 'accept_trade'
    START_AUCTION = 'start_auction'
    REJECT_AUCTION = 'reject_auction'
    ACCEPT_AUCTION = 'accept_auction'
    WON_AUCTION = 'won_auction'

@dataclass
class TradeData:
    from_player: int
    to_player: int
    cash_given: int
    cash_received: int
    ownerships: list[Ownership]

    def is_valid(self) -> bool:
        try:
            for ownership in self.ownerships:
                Ownership.objects.get(pk=ownership.pk)
        except Ownership.DoesNotExist:
            return False
        
        return self.cash_given > 0 and self.cash_received > 0 or (self.ownerships and len(self.ownerships) > 0)

    @classmethod
    def from_dict(cls, trade_data: dict) -> 'TradeData':
        ownerships = []
        try:
            for ownership_id in trade_data.get('ownerships', []):
                ownership = Ownership.objects.get(pk=ownership_id)
                ownerships.append(ownership)
        except Ownership.DoesNotExist:
            raise Exception({"status": "!ok", "error": "Could not find ownership"}, status=400)

        return cls(
            from_player=trade_data.get('from_player'),
            to_player=trade_data.get('to_player'),
            cash_given=trade_data.get('cash_given', 0),
            cash_received=trade_data.get('cash_received', 0),
            ownerships=ownerships
        )


@dataclass
class AuctionData:
    started_by: int
    current_player_in_auction: int
    players_participating_in_auction: list[int]
    current_auction_price: int
    property: int
    is_bet: bool = False
    resolved: bool = False
    winner: int = None

    @classmethod
    def from_dict(cls, auction_data: dict) -> 'AuctionData':
        return cls(
            started_by=auction_data.get('started_by'),
            current_player_in_auction=auction_data.get('current_player_in_auction'),
            players_participating_in_auction=auction_data.get('players_participating_in_auction'),
            current_auction_price=auction_data.get('current_auction_price'),
            property=auction_data.get('property'),
            is_bet=auction_data.get('is_bet', False)
        )

    def to_dict(self) -> dict:
        return {
            'started_by': self.started_by,
            'current_player_in_auction': self.current_player_in_auction,
            'players_participating_in_auction': self.players_participating_in_auction,
            'current_auction_price': self.current_auction_price,
            'property': self.property,
            'is_bet': self.is_bet
        }
    
    def calculate_next_player_id(self, pop_current_player=False) -> int:
        current_player_in_auction_index = self.players_participating_in_auction.index(self.current_player_in_auction)
        next_index = (current_player_in_auction_index + 1) % len(self.players_participating_in_auction)
        next_player_id = self.players_participating_in_auction[next_index]

        if pop_current_player:
            self.players_participating_in_auction.pop(current_player_in_auction_index)

        return next_player_id

    def reject(self):
        current_player_index = self.players_participating_in_auction.index(self.current_player_in_auction)
        next_player_id = self.calculate_next_player_id(pop_current_player=True)

        self.current_player_in_auction = next_player_id
        
        if len(self.players_participating_in_auction) == 1:
            if self.is_bet:
                self.resolved = True
                self.winner = self.players_participating_in_auction[0]
            else:                
                self.current_player_in_auction = self.players_participating_in_auction[0]
        elif len(self.players_participating_in_auction) == 0:
            self.resolved = True
        else:
            self.current_auction_price += config.AUCTION_STEP

    def accept(self):
        next_player_id = self.calculate_next_player_id()

        # Next player is the same player, no players left
        if next_player_id == self.current_player_in_auction:
            # print("You won the auction")
            self.resolved = True
            self.winner = self.current_player_in_auction
        else:
            self.is_bet = True
            self.current_player_in_auction = next_player_id
            self.current_auction_price += config.AUCTION_STEP

        return self

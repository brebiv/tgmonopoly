from pydantic import BaseModel, NonNegativeInt
from typing import Optional, Literal, List
from game.models import Player
from game.exceptions import GameException


class OfferRequest(BaseModel):
    tile_positions: List[NonNegativeInt]
    cash: NonNegativeInt


class ActionCommand(BaseModel):
    action: str
    bet: Optional[int] = None
    property_pos: Optional[int] = None
    # Trade data
    to_player: Optional[int] = None
    offer: Optional[OfferRequest] = None
    request: Optional[OfferRequest] = None


class PropertyGroup(BaseModel):
    id: int
    name: str
    color: str


class PropertyData(BaseModel):
    id: int
    price: int
    mortgage_value: int
    house_price: int
    rent: int
    rent_with_1_house: int
    rent_with_2_houses: int
    rent_with_3_houses: int
    rent_with_4_houses: int
    rent_with_5_houses: int
    group_id: int
    group_color: str
    icon: str
    buyout_price: int
    svg_icon: str
    group_name: str


class Tile(BaseModel):
    id: int
    position: int
    name: str
    type: Literal["START", "PROPERTY", "CHANCE", "TAX", "UTILITY", "JAIL", "CASINO", "POLICE"]
    propertyData: Optional[PropertyData]


class AuctionData(BaseModel):
    tile_id: int
    current_price: int
    next_price: Optional[int]
    started_by_id: int
    players: List[int]
    is_bet: bool


class PayRentData(BaseModel):
    rent: int


class PayTaxData(BaseModel):
    amount: int


class CasinoData(BaseModel):
    available_bets: List[int]


class RepairsData(BaseModel):
    amount: int
    num_houses: int
    price_per_house: int


class TradeData(BaseModel):
    from_player: int
    to_player: int
    offer: OfferRequest
    request: OfferRequest

    def ensure_owns_all(self, player: Player, tile_ids: list[int], err: str):
        if not tile_ids:
            return
        owned_ids = set(player.ownerships.values_list("tile__position", flat=True))
        missing = set(tile_ids) - owned_ids
        if missing:
            raise GameException(err)

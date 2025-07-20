from pydantic import BaseModel
from typing import Optional, Literal, List


class ActionCommand(BaseModel):
    action: str
    bet: Optional[int] = None
    property_pos: Optional[int] = None


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

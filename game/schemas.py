from pydantic import BaseModel
from typing import Optional, Literal


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
    type: Literal[
        "START", "PROPERTY", "CHANCE", "TAX", "UTILITY", "JAIL", "CASINO", "POLICE"
    ]
    propertyData: Optional[PropertyData]

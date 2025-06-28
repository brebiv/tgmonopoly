from pydantic import BaseModel, ConfigDict


class BaseMonopolyConfig(BaseModel):
    STARTING_CASH: int
    MORTGAGE_INTEREST_RATE: float
    MAX_DOUBLES: int
    MIN_PLAYERS: int = 2
    MAX_PLAYERS: int = 4

    model_config = ConfigDict(frozen=True)

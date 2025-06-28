from abc import ABC, abstractmethod
from django.db import transaction

from bot.models import TelegramUser
from game.models import BoardConfig, Game, Player
from game.game_config import BaseMonopolyConfig, ClassicMonopolyConfig
from game.exceptions import GameException


class BaseMonopolyService(ABC):
    config: BaseMonopolyConfig

    @abstractmethod
    def assemble_game_frame(self, game: Game, events, type: str) -> dict: ...

    @abstractmethod
    def create_game(self, owner: TelegramUser, max_players: int) -> Game: ...


class ClassicMonopolyService(BaseMonopolyService):
    def __init__(self):
        self.config = ClassicMonopolyConfig()

    def assemble_game_frame(self, game: Game, events, type: str) -> dict:
        return {}

    def create_game(self, owner: TelegramUser, max_players: int) -> Game:
        if max_players < self.config.MIN_PLAYERS:
            raise GameException(
                f"max_players should be greater than or equal {self.config.MIN_PLAYERS}"
            )
        if max_players > self.config.MAX_PLAYERS:
            raise GameException(
                f"max_players should be less than or equal {self.config.MAX_PLAYERS}"
            )
        # Check if user already in game
        if Player.objects.filter(
            user=owner, status__in=Player.ACTIVE_STATUSES
        ).exists():
            raise GameException("You can't create new game while being in another game")

        board_config = BoardConfig.objects.get(name=BoardConfig.Names.CLASSIC)

        with transaction.atomic():
            game = Game.objects.create(
                board_config=board_config, max_players=max_players
            )
            Player.objects.create(user=owner, game=game, color=Player.Color.BLUE)

        return game


_SERVICES: dict[str, type[BaseMonopolyService]] = {
    BoardConfig.Names.CLASSIC.value: ClassicMonopolyService,
    # ...
}


def get_monopoly_service(config: str) -> BaseMonopolyService:
    try:
        return _SERVICES[config]()
    except KeyError:
        raise ValueError("Could not find specified game config")

from game.services.base import BaseMonopoly
from game.services.classic import ClassicMonopolyService
from game.models import BoardConfig, Game
from game.exceptions import GameException

_STRATEGIES: dict[str, type[BaseMonopoly]] = {
    BoardConfig.Names.CLASSIC.value: ClassicMonopolyService,
}


def get_service_by_game(game: Game) -> BaseMonopoly:
    try:
        return _STRATEGIES[game.board_config.name]()
    except KeyError:
        raise GameException("There is no such board config")


def get_service_by_name(config_name: str) -> BaseMonopoly:
    try:
        return _STRATEGIES[config_name]()
    except KeyError:
        raise GameException("There is no such board config")

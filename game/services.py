from uuid import UUID
from abc import ABC, abstractmethod
from typing import List, Tuple

from django.db import transaction, IntegrityError

from bot.models import TelegramUser
from game.models import BoardConfig, Game, Player, GameEvent
from game.game_config import BaseMonopolyConfig, ClassicMonopolyConfig
from game.exceptions import GameException
from game.serializers import GameEventSerializer, GameSerializer, PlayerSerializer


class BaseMonopoly(ABC):
    config: BaseMonopolyConfig

    def assemble_game_frame(
        self,
        game: Game,
        events: List[GameEvent],
        game_frame_type: str = "game.event",
    ) -> dict:
        game_event_serailizer = GameEventSerializer(events, many=True)
        game_serializer = GameSerializer(game)
        players = [PlayerSerializer(player).data for player in game.players.all()]

        return {
            # "type": type.value,
            "type": game_frame_type,
            "game": game_serializer.data,
            "players": players,
            "events": game_event_serailizer.data,
        }

    @abstractmethod
    def create_game(self, owner: TelegramUser, max_players: int) -> Game: ...

    @abstractmethod
    def join_game(
        self, game_uuid: UUID, telegram_user: TelegramUser
    ) -> Tuple[Player, list[GameEvent]]: ...

    @abstractmethod
    def leave_game(self, player: Player) -> list[GameEvent]: ...

    @abstractmethod
    def start_game(self, game: Game, player: Player) -> list[GameEvent]: ...


class ClassicMonopolyService(BaseMonopoly):
    def __init__(self):
        self.config = ClassicMonopolyConfig()

    def create_game(self, user: TelegramUser, max_players: int) -> Game:
        if max_players < self.config.MIN_PLAYERS:
            raise GameException(
                f"max_players should be greater than or equal {self.config.MIN_PLAYERS}"
            )
        if max_players > self.config.MAX_PLAYERS:
            raise GameException(
                f"max_players should be less than or equal {self.config.MAX_PLAYERS}"
            )

        with transaction.atomic():
            # Check if user already in game
            if Player.objects.filter(
                user=user, status__in=Player.ACTIVE_STATUSES
            ).exists():
                raise GameException(
                    "You can't create new game while being in another game"
                )

            board_config = BoardConfig.objects.get(name=BoardConfig.Names.CLASSIC)

            game = Game.objects.create(
                board_config=board_config, max_players=max_players
            )
            Player.objects.create(user=user, game=game, color=Player.Color.BLUE)

        return game

    @transaction.atomic
    def join_game(self, game_uuid, telegram_user):
        events = []

        game = (
            Game.objects.select_for_update()
            .prefetch_related("players")
            .get(pk=game_uuid)
        )

        if game.status != game.Status.WAITING:
            raise GameException("Game is not in waiting state")

        if game.max_players == game.players.count():
            raise GameException("Game is full")

        try:
            existing_colors = game.players.values_list("color", flat=True).all()
            available_colors = [
                color for color in Player.Color.values if color not in existing_colors
            ]
            color = available_colors.pop(0)

            player = Player.objects.create(
                user=telegram_user,
                game=game,
                color=color,
            )
        except IntegrityError:
            raise GameException("You are already playing this game")

        game_event = GameEvent.objects.create(
            event_type=GameEvent.Types.PLAYER_JOINED, extra_data={"player": player.pk}
        )

        events.append(game_event)

        if game.max_players == game.players.count() + 1:
            start_game_event = self.start_game(game, player)
            events.extend(start_game_event)

        return player, events

    def leave_game(self, player) -> list[GameEvent]:
        events = []

        with transaction.atomic():
            game = player.game
            player.delete()

            game_event = GameEvent.objects.create(
                event_type=GameEvent.Types.PLAYER_LEAVE,
                extra_data={"player": player.pk},
            )
            events.append(game_event)

            if game.players.count() == 0:
                game.status = Game.Status.ABANDONED
                game.save()
                # events.append()

        return events

    def start_game(self, game, player):
        events = []

        with transaction.atomic():
            game.players.update(status=Player.Status.PLAYING)

            game.turn += 1
            game.current_player = player
            game.status = Game.Status.PLAYING
            game.save()

            game_event = GameEvent.objects.create(
                event_type=GameEvent.Types.GAME_STARTED,
                extra_data={"player": player.pk},
            )

            events.append(game_event)

        return events


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

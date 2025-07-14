from uuid import UUID
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Callable, Any
import random

from django.db import transaction, IntegrityError
from django.utils import timezone

from bot.models import TelegramUser
from game.models import BoardConfig, Game, Player, GameEvent, Property, Ownership, PendingAction
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
        # Check if users are prefetched
        game_event_serializer = GameEventSerializer(events, many=True)
        game_serializer = GameSerializer(game)
        players = [PlayerSerializer(player).data for player in game.players.all()]

        return {
            "type": game_frame_type,
            "game": game_serializer.data,
            "players": players,
            "events": game_event_serializer.data,
        }

    def _roll_dice_values(self, dices_count=2, min_value=1, max_value=6):
        return [2, 1]
        # return [random.randint(min_value, max_value) for _ in range(dices_count)]

    def _create_game_event(self, game: Game, event_type: GameEvent.Types, extra_data: Optional[dict] = None):
        event = GameEvent.objects.create(game=game, event_type=event_type, extra_data=extra_data or {})
        return event

    @abstractmethod
    def create_game(self, owner: TelegramUser, max_players: int) -> Game: ...

    @abstractmethod
    def join_game(self, game_uuid: UUID, telegram_user: TelegramUser) -> Tuple[Player, list[GameEvent]]: ...

    @abstractmethod
    def leave_game(self, player: Player) -> list[GameEvent]: ...

    @abstractmethod
    def start_game(self, game: Game, player: Player) -> list[GameEvent]: ...

    @abstractmethod
    def process_game_action(self, game_uuid: UUID, player_id: int, action: str) -> dict: ...

    def _calculate_next_player(self, game: Game, after_player: Player) -> Player:
        game_players = game.players.filter(status=Player.Status.PLAYING).order_by("created")
        current_player_index = None

        for i, p in enumerate(game_players):
            if p.pk == after_player.pk:
                current_player_index = i

        if current_player_index is None:
            raise GameException("Could not find next player")

        next_player_index = (current_player_index + 1) % game_players.count()
        next_player = game_players[next_player_index]

        return next_player


class ClassicMonopolyService(BaseMonopoly):
    def __init__(self) -> None:
        self.config = ClassicMonopolyConfig()
        self.PENDING_ACTION_COMMAND_HANDLERS: dict[
            PendingAction.Types, dict[str, Callable[[Game, Player], Any]]
        ] = {
            PendingAction.Types.ROLL_DICE: {
                "roll_dice": self._handle_dice_roll,
            },
            PendingAction.Types.BUY_PROPERTY: {
                "accept": self._buy_property,
                "reject": lambda g, p: print(g, p),
            },
        }

    def create_game(self, user: TelegramUser, max_players: int) -> Game:
        if max_players < self.config.MIN_PLAYERS:
            raise GameException(f"max_players should be greater than or equal {self.config.MIN_PLAYERS}")
        if max_players > self.config.MAX_PLAYERS:
            raise GameException(f"max_players should be less than or equal {self.config.MAX_PLAYERS}")

        with transaction.atomic():
            # Check if user already in the game
            if Player.objects.filter(user=user, status__in=Player.ACTIVE_STATUSES).exists():
                raise GameException("You can't create new game while being in another game")

            board_config = BoardConfig.objects.get(name=BoardConfig.Names.CLASSIC)

            game = Game.objects.create(board_config=board_config, max_players=max_players)
            Player.objects.create(user=user, game=game, color=Player.Color.BLUE)

        return game

    @transaction.atomic
    def join_game(self, game_uuid, telegram_user):
        events = []

        game = Game.objects.select_for_update().prefetch_related("players").get(pk=game_uuid)

        if game.status != game.Status.WAITING:
            raise GameException("Game is not in waiting state")

        if game.max_players == game.players.count():
            raise GameException("Game is full")

        try:
            existing_colors = game.players.values_list("color", flat=True).all()
            available_colors = [color for color in Player.Color.values if color not in existing_colors]
            color = available_colors.pop(0)

            player = Player.objects.create(
                user=telegram_user,
                game=game,
                color=color,
            )
        except IntegrityError:
            raise GameException("You are already playing this game")

        game_event = self._create_game_event(
            game=game,
            event_type=GameEvent.Types.PLAYER_JOINED,
            extra_data={"player": player.pk},
        )

        events.append(game_event)

        if game.max_players == game.players.count() + 1:
            first_player = game.players.first()
            start_game_event = self.start_game(game, first_player)
            events.extend(start_game_event)

        return player, events

    def leave_game(self, player) -> list[GameEvent]:
        events = []

        with transaction.atomic():
            game = player.game
            player.delete()

            game_event = GameEvent.objects.create(
                game=game,
                event_type=GameEvent.Types.PLAYER_LEAVE,
                extra_data={"player": player.pk},
            )
            events.append(game_event)

            if game.players.count() == 0:
                game.status = Game.Status.ABANDONED
                game.save()

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
                game=game,
                event_type=GameEvent.Types.GAME_STARTED,
                extra_data={"player": player.pk},
            )

            events.append(game_event)

            pa = PendingAction.objects.create(
                player=player, action_type=PendingAction.Types.ROLL_DICE, expires_at=timezone.now()
            )

        return events

    def _next_turn(self, game: Game, player: Player) -> list[GameEvent]:
        events: list[GameEvent] = []

        if player.rolled_double:
            next_player = player
        else:
            next_player = self._calculate_next_player(game, player)

        game.current_player = next_player
        game.turn += 1
        game.save()

        pa = PendingAction.objects.create(
            player=next_player, action_type=PendingAction.Types.ROLL_DICE, expires_at=timezone.now()
        )

        return events

    def _handle_normal_roll(self, game: Game, player: Player, dice_values: list[int]) -> list[GameEvent]:
        events = []
        dice_sum = sum(dice_values)
        new_position = player.move_forward(dice_sum)

        event = self._create_game_event(
            game,
            GameEvent.Types.PLAYER_MOVE,
            {"player": player.pk, "position": new_position},
        )
        events.append(event)

        tile = game.board_config.tiles.get(position=player.position).downcast()
        if isinstance(tile, Property):
            if tile.check_if_buyable(game):
                pa = PendingAction.objects.create(
                    player=player, action_type=PendingAction.Types.BUY_PROPERTY, expires_at=timezone.now()
                )
            else:
                self._next_turn(game, player)

        player.save()
        game.save()

        return events

    def _handle_dice_roll(self, game: Game, player: Player) -> list[GameEvent]:
        events = []
        dice_values = self._roll_dice_values()

        event = self._create_game_event(
            game,
            GameEvent.Types.PLAYER_ROLL_DICE,
            {"player": player.pk, "dice_values": dice_values},
        )
        events.append(event)

        if player.in_jail:
            pass
        else:
            roll_events = self._handle_normal_roll(game, player, dice_values)
            events.extend(roll_events)

        return events

    def _buy_property(self, game: Game, player: Player) -> list[GameEvent]:
        events: list[GameEvent] = []

        property = Property.objects.get(position=player.position)
        Ownership.objects.create(
            game=game,
            player=player,
            tile=property,
        )

        self._next_turn(game, player)
        return events

    @transaction.atomic
    def process_game_action(self, game_uuid, player_id, action) -> dict:
        print("Processing game action", game_uuid, player_id, action)
        events: list[GameEvent] = []
        player = Player.objects.select_for_update().get(pk=player_id)
        game = Game.objects.select_for_update().get(pk=game_uuid)

        if game.current_player != player:
            print("WTF?. It's not your turn")

        if player.status == player.Status.WAITING:
            print("Whole other deal")
        elif player.status == player.Status.PLAYING:
            prev_pa = player.pending_action
            if prev_pa is None:
                raise GameException("Could not find pending action to resolve")

            prev_pa.resolved_at = timezone.now()
            prev_pa.save()

            handler = self.PENDING_ACTION_COMMAND_HANDLERS.get(prev_pa.action_type, {}).get(action)  # type: ignore[call-overload]
            if not handler:
                print("You are fucked. There is no such action")
                return {"type": "game.error", "msg": "You are fucked. There is no such action"}

            events = handler(game, player)

        return self.assemble_game_frame(game, events)


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

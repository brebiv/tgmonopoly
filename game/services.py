from uuid import UUID
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Callable, Any
import datetime
import random
import logging
import math

from django.db import transaction, IntegrityError
from django.db.models import QuerySet, F
from django.utils import timezone

from bot.models import TelegramUser
from game.models import BoardConfig, Game, Player, GameEvent, Property, Ownership, PendingAction, Jail, Police
from game.game_config import BaseMonopolyConfig, ClassicMonopolyConfig
from game.exceptions import GameException
from game.serializers import GameEventSerializer, GameSerializer, PlayerSerializer


logger = logging.getLogger(__name__)


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
        if dices_count > 2:
            raise NotImplementedError(
                "Current only two dices supported because of dice double calculation logic"
            )
        # return [2, 1]
        return [2, 2]
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
            PendingAction.Types, dict[str, Callable[[Game, Player, Optional[PendingAction]], Any]]
        ] = {
            PendingAction.Types.ROLL_DICE: {
                "roll_dice": self._handle_dice_roll,
            },
            PendingAction.Types.BUY_PROPERTY: {
                "accept": self._handle_buy_property_accept,
                "start_auction": self._start_auction,
            },
            PendingAction.Types.PAY_RENT: {
                "accept": self._pay_rent,
            },
            PendingAction.Types.IN_AUCTION: {
                "accept": self._accept_auction,
                "reject": self._reject_auction,
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
            Player.objects.create(user=user, game=game, color=Player.Color.BLUE, cash=1000)

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
            player.double_count += 1
            player.rolled_double = False
            if player.double_count == 3:
                move_to_jail_events = self._move_player_to_jail(game, player)
                events.extend(move_to_jail_events)
                next_player = self._calculate_next_player(game, player)
            else:
                next_player = player
        else:
            next_player = self._calculate_next_player(game, player)

        game.current_player = next_player
        game.turn += 1
        game.save(update_fields=["turn", "current_player"])
        player.save()

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
                pa = PendingAction.objects.create(
                    # expires_at = timezone.now() + datetime.timedelta(seconds=30)
                    player=player,
                    action_type=PendingAction.Types.PAY_RENT,
                    expires_at=timezone.now(),
                )
        elif isinstance(tile, Police):
            move_to_jail_event = self._move_player_to_jail(game, player)
            events.extend(move_to_jail_event)
            next_turn_events = self._next_turn(game, player)
            events.extend(next_turn_events)
        else:
            self._next_turn(game, player)
            # raise NotImplementedError()

        player.save()
        game.save()

        return events

    def _handle_dice_roll(
        self, game: Game, player: Player, resolved_pa: Optional[PendingAction] = None
    ) -> list[GameEvent]:
        events = []
        dice_values = self._roll_dice_values()

        if dice_values[0] == dice_values[1]:
            player.rolled_double = True

        event = self._create_game_event(
            game,
            GameEvent.Types.PLAYER_ROLL_DICE,
            {"player": player.pk, "dice_values": dice_values},
        )
        events.append(event)

        if player.in_jail:
            raise NotImplementedError()
        else:
            roll_events = self._handle_normal_roll(game, player, dice_values)
            events.extend(roll_events)

        return events

    def _move_player_to_jail(self, game: Game, player: Player) -> list[GameEvent]:
        events: list[GameEvent] = []
        jail_tile = Jail.objects.get(board_config=game.board_config)
        player.in_jail = True
        player.jail_turns = 0
        player.position = jail_tile.position
        player.save()
        return events

    def _buy_property(
        self, game: Game, player: Player, property: Property, override_price: int | None = None
    ) -> list[GameEvent]:
        events: list[GameEvent] = []
        price = override_price or property.price

        if player.cash < price:
            raise GameException("You don't have enough money to buy this property")

        player.cash -= price
        player.save()
        Ownership.objects.create(
            game=game,
            player=player,
            tile=property,
        )

        return events

    def _handle_buy_property_accept(
        self, game: Game, player: Player, resolved_pa: Optional[PendingAction] = None
    ) -> list[GameEvent]:
        events: list[GameEvent] = []

        property = Property.objects.get(position=player.position)
        buy_property_events = self._buy_property(game, player, property)
        next_turn_events = self._next_turn(game, player)
        events.extend([*buy_property_events, *next_turn_events])

        return events

    def _pay_rent(
        self, game: Game, player: Player, resolved_pa: Optional[PendingAction] = None
    ) -> list[GameEvent]:
        events = []

        tile = Property.objects.get(position=player.position)
        ownership = Ownership.objects.select_related("player").get(game=game, tile=tile)
        player.cash -= tile.rent
        owner = ownership.player
        owner.cash += tile.rent
        player.save()
        owner.save()

        next_turn_events = self._next_turn(game, player)
        events.extend(next_turn_events)

        return events

    def _start_auction(
        self, game: Game, player: Player, resolved_pa: Optional[PendingAction] = None
    ) -> list[GameEvent]:
        events: list[GameEvent] = []

        try:
            property = Property.objects.get(position=player.position)
        except Property.DoesNotExist:
            raise GameException("Could not find property for an auction")

        auction_price = math.ceil(property.price * 1.1)
        auction_participants: QuerySet[Player] = (
            game.players.exclude(pk=player.pk).exclude(cash__lt=auction_price).exclude(in_jail=True)
        )

        if auction_participants.count() == 0:
            self._next_turn(game, player)
        else:
            next_player = auction_participants.first()

            if next_player is None:
                raise GameException("Could not find next player for auction")

            game.current_player = next_player
            game.save()

            pa = PendingAction.objects.create(
                player=next_player,
                action_type=PendingAction.Types.IN_AUCTION,
                expires_at=timezone.now(),
                action_data={
                    "property_id": property.pk,
                    "current_price": auction_price,
                    # "next_price": math.ceil(auction_price * 1.1),
                    "next_price": None,
                    "started_by_id": player.pk,
                    "players": [p.pk for p in auction_participants],
                    "is_bet": False,
                },
            )

        return events

    @transaction.atomic
    def _accept_auction(
        self, game: Game, player: Player, resolved_pa: Optional[PendingAction] = None
    ) -> list[GameEvent]:
        events: list[GameEvent] = []

        pa = resolved_pa
        if pa is None:
            raise GameException("Could not find action for auction")

        # Auction data
        property_id = pa.action_data.get("property_id")
        current_price = pa.action_data.get("current_price")
        next_price = pa.action_data.get("next_price")  # could be None if it's the first turn
        started_by_id = pa.action_data.get("started_by_id")
        players_ids: list[int] = pa.action_data.get("players")

        if len(players_ids) == 1:
            property = Property.objects.get(pk=property_id)
            buy_property_events = self._buy_property(game, player, property, current_price)
            events.extend(buy_property_events)

            started_by = Player.objects.get(pk=started_by_id)
            next_turn_events = self._next_turn(game, started_by)
            events.extend(next_turn_events)
        else:
            next_in_auction_id = players_ids[(players_ids.index(player.pk) + 1) % len(players_ids)]

            if next_price:
                new_current_price = next_price
                new_next_price = math.ceil(next_price * 1.1)
            else:
                new_current_price = current_price
                new_next_price = math.ceil(current_price * 1.1)

            game.current_player_id = next_in_auction_id
            game.save()
            pa = PendingAction.objects.create(
                player_id=next_in_auction_id,
                action_type=PendingAction.Types.IN_AUCTION,
                expires_at=timezone.now(),
                action_data={
                    "property_id": property_id,
                    # "current_price": next_price,
                    "current_price": new_current_price,
                    "next_price": new_next_price,
                    "started_by_id": started_by_id,
                    "players": players_ids,
                    "is_bet": True,
                },
            )

        return events

    def _reject_auction(
        self, game: Game, player: Player, resolved_pa: Optional[PendingAction] = None
    ) -> list[GameEvent]:
        events: list[GameEvent] = []

        pa = resolved_pa
        if pa is None:
            raise GameException("Could not find action for auction")

        # Auction data
        property_id = pa.action_data.get("property_id")
        current_price = pa.action_data.get("current_price")
        next_price = pa.action_data.get("next_price")
        started_by_id = pa.action_data.get("started_by_id")
        players_ids: list[int] = pa.action_data.get("players")
        is_bet = pa.action_data.get("is_bet")

        players_ids.remove(player.pk)

        if len(players_ids) == 0:
            property = Property.objects.get(pk=property_id)
            started_by_user = Player.objects.get(pk=started_by_id)
            next_turn_events = self._next_turn(game, started_by_user)
            events.extend(next_turn_events)
        elif len(players_ids) == 1:
            if is_bet:
                property = Property.objects.get(pk=property_id)
                last_player = Player.objects.get(pk=players_ids[0])
                buy_tile_events = self._buy_property(game, last_player, property, current_price)
                events.extend(buy_tile_events)
                started_by_user = Player.objects.get(pk=started_by_id)
                next_turn_events = self._next_turn(game, started_by_user)

                events.extend(next_turn_events)
            else:
                next_in_auction_id = players_ids[0]
                game.current_player_id = next_in_auction_id
                game.save()
                pa = PendingAction.objects.create(
                    player_id=next_in_auction_id,
                    action_type=PendingAction.Types.IN_AUCTION,
                    expires_at=timezone.now(),
                    action_data={
                        "property_id": property_id,
                        # "current_price": next_price,
                        "current_price": current_price,
                        "next_price": next_price,
                        "started_by_id": started_by_id,
                        "players": players_ids,
                        "is_bet": True,
                    },
                )
        else:
            raise NotImplementedError()

        return events

    @transaction.atomic
    def process_game_action(self, game_uuid, player_id, action) -> dict:
        logger.debug("Processing game action", game_uuid, player_id, action)
        events: list[GameEvent] = []
        player = Player.objects.select_for_update().get(pk=player_id)
        game = Game.objects.select_for_update().get(pk=game_uuid)

        if game.current_player != player:
            raise GameException("WTF? It's not your turn")

        if player.status == player.Status.WAITING:
            print("Whole other deal")
        elif player.status == player.Status.PLAYING:
            prev_pa = player.pending_action
            if prev_pa is None:
                raise GameException("Could not find pending action to resolve")

            handler = self.PENDING_ACTION_COMMAND_HANDLERS.get(prev_pa.action_type, {}).get(action)  # type: ignore[call-overload]
            if not handler:
                raise GameException("You are fucked. There is no such action")

            prev_pa.resolved_at = timezone.now()
            prev_pa.save()

            events = handler(game, player, prev_pa)

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

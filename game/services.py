from uuid import UUID
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Callable, cast
from pydantic import ValidationError
import datetime
import random
import logging
import math

from django.db import transaction, IntegrityError
from django.db.models import QuerySet, F, Sum
from django.db.models.functions import Greatest
from django.utils import timezone

from bot.models import TelegramUser
from game.models import (
    BoardConfig,
    Game,
    Player,
    GameEvent,
    Property,
    Ownership,
    PendingAction,
    Jail,
    Police,
    Utility,
    Tile,
    Tax,
    Start,
    Casino,
    Chance,
    ChanceCard,
)
from game.game_config import BaseMonopolyConfig, ClassicMonopolyConfig
from game.exceptions import GameException
from game.serializers import GameEventSerializer, GameSerializer, PlayerSerializer
from game.schemas import (
    AuctionData,
    PayRentData,
    PayTaxData,
    CasinoData,
    ActionCommand,
    RepairsData,
    TradeData,
)


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
        return [19, 1]
        # return [random.randint(min_value, max_value) for _ in range(dices_count)]

    def _flip_coin_value(self) -> bool:
        return random.choice((True, False))

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
    def process_game_action(self, game_uuid: UUID, player_id: int, action: ActionCommand) -> dict: ...

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
            PendingAction.Types,
            dict[str, Callable[[Game, Player, PendingAction, ActionCommand], list[GameEvent]]],
        ] = {
            PendingAction.Types.ROLL_DICE: {
                "roll_dice": self._handle_dice_roll,
                "reject": self._handle_pay_jail,
                "improve": self._handle_improve,
                "degrade": self._handle_degrade,
                "start_trade": self._handle_start_trade,
            },
            PendingAction.Types.BUY_PROPERTY: {
                "accept": self._handle_buy_property_accept,
                "start_auction": self._handle_start_auction,
                # Add ability to degrade or mortgage tile
            },
            PendingAction.Types.PAY_RENT: {
                "accept": self._handle_pay_rent,
                # Add ability to degrade or mortgage tile
            },
            PendingAction.Types.PAY_TAX: {
                "accept": self._handle_pay_tax,
                # Add ability to degrade or mortgage tile
            },
            PendingAction.Types.PAY_REPAIRS: {
                "accept": self._handle_pay_repairs,
                # Add ability to degrade or mortgage tile
            },
            PendingAction.Types.IN_AUCTION: {
                "accept": self._handle_accept_auction,
                "reject": self._handle_reject_auction,
                # Add ability to degrade or mortgage tile
            },
            PendingAction.Types.IN_CASINO: {
                "accept": self._handle_accept_casino,
                "reject": self._handle_reject_casino,
                # Add ability to degrade or mortgage tile
            },
            PendingAction.Types.IN_TRADE: {
                # Add ability to counter propose
                "accept": self._handle_accept_trade,
                "reject": self._handle_reject_trade,
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

    def _get_random_chance_card(self) -> ChanceCard:
        random_card = ChanceCard.objects.order_by("?").first()
        if not random_card:
            raise GameException("Could not load any chance card")
        return random_card

    def _process_land_on_tile(self, game: Game, player: Player, tile: Tile, dice_sum: int) -> list[GameEvent]:
        events = []
        downcasted_tile = tile.downcast()

        if isinstance(downcasted_tile, (Property, Utility)):
            ownership = Ownership.objects.filter(tile=downcasted_tile, game=game).first()
            if not ownership:
                pa = PendingAction.objects.create(
                    player=player, action_type=PendingAction.Types.BUY_PROPERTY, expires_at=timezone.now()
                )
            else:
                if ownership.player != player:
                    rent = ownership.calculate_rent(dice_sum)
                    payrent_data = PayRentData(rent=rent)
                    pa = PendingAction.objects.create(
                        # expires_at = timezone.now() + datetime.timedelta(seconds=30)
                        player=player,
                        action_type=PendingAction.Types.PAY_RENT,
                        expires_at=timezone.now(),
                        action_data=payrent_data.model_dump(),
                    )
                else:
                    events.append(self._create_game_event(game, GameEvent.Types.LANDED_ON_OWN_PROPERTY))
                    self._next_turn(game, player)
        elif isinstance(downcasted_tile, Police):
            move_to_jail_event = self._move_player_to_jail(game, player)
            events.extend(move_to_jail_event)
            next_turn_events = self._next_turn(game, player)
            events.extend(next_turn_events)
        elif isinstance(downcasted_tile, Tax):
            paytax_data = PayTaxData(amount=100)
            pa = PendingAction.objects.create(
                player=player,
                action_type=PendingAction.Types.PAY_TAX,
                expires_at=timezone.now(),
                action_data=paytax_data.model_dump(),
            )
        elif isinstance(downcasted_tile, Start):
            self._next_turn(game, player)
        elif isinstance(downcasted_tile, Casino):
            casino_data = CasinoData(available_bets=[10, 20, 30, 40, 50])

            if player.cash < 10:
                self._next_turn(game, player)
            else:
                pa = PendingAction.objects.create(
                    player=player,
                    action_type=PendingAction.Types.IN_CASINO,
                    expires_at=timezone.now(),
                    action_data=casino_data.model_dump(),
                )
        elif isinstance(downcasted_tile, Chance):
            events = self._process_chance_card(game, player)
            events.extend(events)
        else:
            raise NotImplementedError()
            self._next_turn(game, player)

        return events

    def _collect_from_players(self, game: Game, player: Player, amount: int) -> None:
        others = game.players.select_for_update().exclude(pk=player.pk)

        total_before = others.aggregate(total=Sum("cash"))["total"] or 0
        # others.update(cash=Greatest(F("cash") - amount, Value(0)))
        others.update(cash=Greatest(F("cash") - amount, 0))
        total_after = others.aggregate(total=Sum("cash"))["total"] or 0

        actually_paid = total_before - total_after
        player.cash += actually_paid
        player.save()

    def _apply_repairs_action(self, game: Game, player: Player) -> None:
        num_houses = player.houses_owned
        price_per_house = 50
        amount = num_houses * price_per_house
        extra_data = RepairsData(amount=amount, num_houses=num_houses, price_per_house=price_per_house)

        pa = PendingAction.objects.create(
            player=player,
            action_type=PendingAction.Types.PAY_REPAIRS,
            expires_at=timezone.now(),
            action_data=extra_data.model_dump(),
        )

    def _process_chance_card(self, game: Game, player: Player) -> list[GameEvent]:
        events = []

        chance_card = self._get_random_chance_card()

        events.append(
            self._create_game_event(game, GameEvent.Types.GOT_CHANCE_CARD, extra_data={"player": player.pk})
        )

        if chance_card.action == ChanceCard.Action.MOVE_TO:
            player.position = chance_card.position  # type: ignore[assignment]
            player.save()
            tile = game.board_config.tiles.get(position=player.position)
            self._process_land_on_tile(game, player, tile, 0)
        elif chance_card.action == ChanceCard.Action.MOVE_RELATIVE:
            pos_relative = chance_card.position_relative
            pos_relative = cast(int, pos_relative)

            if pos_relative > 0:
                player.move_forward(pos_relative)
            else:
                player.move_backward(abs(pos_relative))
            player.save()
            tile = game.board_config.tiles.get(position=player.position)
            self._process_land_on_tile(game, player, tile, pos_relative)
        elif chance_card.action == ChanceCard.Action.MOVE_TO_NEXT_UTILITY:
            closest_util = player.get_next_utility()
            if not closest_util:
                raise GameException("Could not find closest utility")

            player.position = closest_util.position
            player.save()
            self._process_land_on_tile(game, player, closest_util, 0)
        elif chance_card.action == ChanceCard.Action.PAY_BANK:
            paytax_data = PayTaxData(amount=cast(int, chance_card.amount))
            pa = PendingAction.objects.create(
                player=player,
                action_type=PendingAction.Types.PAY_TAX,
                expires_at=timezone.now(),
                action_data=paytax_data.model_dump(),
            )
        elif chance_card.action == ChanceCard.Action.COLLECT_BANK:
            player.cash += cast(int, chance_card.amount)
            player.save()
            self._next_turn(game, player)
        elif chance_card.action == ChanceCard.Action.COLLECT_PLAYERS:
            self._collect_from_players(game, player, cast(int, chance_card.amount))
            self._next_turn(game, player)
        elif chance_card.action == ChanceCard.Action.GO_TO_JAIL:
            self._move_player_to_jail(game, player)
            self._next_turn(game, player)
        elif chance_card.action == ChanceCard.Action.REPAIRS:
            self._apply_repairs_action(game, player)
        else:
            raise NotImplementedError()

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

        tile = game.board_config.tiles.get(position=player.position)
        landing_events = self._process_land_on_tile(game, player, tile, dice_sum)
        events.extend(landing_events)

        player.save()
        game.save()

        return events

    def _handle_jail_dice_roll(self, game: Game, player: Player, dice_values: list[int]) -> list[GameEvent]:
        events: list[GameEvent] = []

        if dice_values[0] == dice_values[1]:
            player.in_jail = False
            player.jail_turns = 0
            pa = PendingAction.objects.create(
                # expires_at = timezone.now() + datetime.timedelta(seconds=30)
                player=player,
                action_type=PendingAction.Types.ROLL_DICE,
                expires_at=timezone.now(),
            )
        else:
            player.jail_turns += 1
            if player.jail_turns < 3:
                next_turn_events = self._next_turn(game, player)
                events.extend(next_turn_events)
            else:
                pa = PendingAction.objects.create(
                    player=player,
                    action_type=PendingAction.Types.ROLL_DICE,
                    expires_at=timezone.now(),
                )

        player.save()
        return events

    def _handle_pay_jail(
        self, game: Game, player: Player, resolved_pa: PendingAction, commmand: ActionCommand
    ) -> list[GameEvent]:
        events: list[GameEvent] = []

        JAIL_PAY_PRICE = 100

        if not player.in_jail:
            raise GameException("You can pay for jail only when you are in jail")
        if player.cash < JAIL_PAY_PRICE:
            raise GameException("You don't have enough money to pay for jail")

        player.cash -= JAIL_PAY_PRICE
        player.in_jail = False
        player.jail_turns = 0
        player.save()

        pa = PendingAction.objects.create(
            player=player,
            action_type=PendingAction.Types.ROLL_DICE,
            expires_at=timezone.now(),
        )

        return events

    def _handle_dice_roll(
        self, game: Game, player: Player, resolved_pa: PendingAction, command: ActionCommand
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
            if player.jail_turns >= 3:
                raise GameException("You can't roll dice in jail anymore")
            self._handle_jail_dice_roll(game, player, dice_values)
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

    def _buy_tile(
        self, game: Game, player: Player, tile: Tile, override_price: int | None = None
    ) -> list[GameEvent]:
        events: list[GameEvent] = []

        if not isinstance(tile, (Property, Utility)):
            raise GameException("You can'y buy something other then Property or Utility")

        price = override_price if override_price is not None else tile.price

        if player.cash < price:
            raise GameException("You don't have enough money to buy this tile")

        player.cash -= price
        player.save()
        Ownership.objects.create(
            game=game,
            player=player,
            tile=tile,
        )

        return events

    def _handle_buy_property_accept(
        self, game: Game, player: Player, resolved_pa: PendingAction, command: ActionCommand
    ) -> list[GameEvent]:
        events: list[GameEvent] = []

        tile = Tile.objects.get(board_config=game.board_config, position=player.position)
        downcasted_tile = tile.downcast()

        buy_property_events = self._buy_tile(game, player, downcasted_tile)
        next_turn_events = self._next_turn(game, player)
        events.extend([*buy_property_events, *next_turn_events])

        return events

    def _handle_pay_rent(
        self, game: Game, player: Player, resolved_pa: PendingAction, command: ActionCommand
    ) -> list[GameEvent]:
        events = []

        payrent_data = PayRentData(**resolved_pa.action_data)
        rent = payrent_data.rent

        if player.cash < rent:
            raise GameException("You don't have enough money to pay rent")

        # ownership = Ownership.objects.select_related("player").get(game=game, tile=tile)
        ownership = Ownership.objects.select_related("player").get(game=game, tile__position=player.position)
        player.cash -= rent
        owner = ownership.player
        owner.cash += rent
        player.save()
        owner.save()

        next_turn_events = self._next_turn(game, player)
        events.extend(next_turn_events)

        return events

    def _handle_pay_tax(
        self, game: Game, player: Player, resolved_pa: PendingAction, command: ActionCommand
    ) -> list[GameEvent]:
        events = []

        action_data = PayTaxData(**resolved_pa.action_data)
        amount = action_data.amount

        if player.cash < amount:
            raise GameException("You don't have enough money to pay tax")

        player.cash -= amount
        player.save()

        next_turn_events = self._next_turn(game, player)
        events.extend(next_turn_events)

        return events

    def _handle_pay_repairs(
        self, game: Game, player: Player, resolved_pa: PendingAction, command: ActionCommand
    ) -> list[GameEvent]:
        events = []

        action_data = RepairsData(**resolved_pa.action_data)
        amount = action_data.amount

        if player.cash < amount:
            raise GameException("You don't have enough money to pay tax")

        player.cash -= amount
        player.save()

        next_turn_events = self._next_turn(game, player)
        events.extend(next_turn_events)

        return events

    def _handle_start_auction(
        self, game: Game, player: Player, resolved_pa: PendingAction, command: ActionCommand
    ) -> list[GameEvent]:
        events: list[GameEvent] = []

        try:
            tile = Tile.objects.get(board_config=game.board_config, position=player.position)
            downcasted_tile = tile.downcast()
        except Tile.DoesNotExist:
            raise GameException("Could not find property for an auction")

        if not isinstance(downcasted_tile, (Property, Utility)):
            raise GameException("You can't start auction on tiles other then Property or Utility")

        auction_price = math.ceil(downcasted_tile.price * 1.1)
        auction_participants: QuerySet[Player] = game.players.exclude(pk=player.pk).exclude(
            cash__lt=auction_price
        )

        if auction_participants.count() == 0:
            self._next_turn(game, player)
            events.append(self._create_game_event(game, GameEvent.Types.GAME_AUCTION_FLOP))
        else:
            next_player = auction_participants.first()

            if next_player is None:
                raise GameException("Could not find next player for auction")

            game.current_player = next_player
            game.save()

            auction_data = AuctionData(
                tile_id=tile.pk,
                current_price=auction_price,
                next_price=None,
                started_by_id=player.pk,
                players=[p.pk for p in auction_participants],
                is_bet=False,
            )

            pa = PendingAction.objects.create(
                player=next_player,
                action_type=PendingAction.Types.IN_AUCTION,
                expires_at=timezone.now(),
                action_data=auction_data.model_dump(),
            )

        return events

    @transaction.atomic
    def _handle_accept_auction(
        self, game: Game, player: Player, resolved_pa: PendingAction, command: ActionCommand
    ) -> list[GameEvent]:
        events: list[GameEvent] = []
        # Auction data
        auction_data = AuctionData(**resolved_pa.action_data)
        tile_id = auction_data.tile_id
        current_price = auction_data.current_price
        next_price = auction_data.next_price  # could be None if it's the first turn
        started_by_id = auction_data.started_by_id
        players_ids = auction_data.players

        if len(players_ids) == 1:
            tile = Tile.objects.get(pk=tile_id)
            downcasted_tile = tile.downcast()

            buy_property_events = self._buy_tile(game, player, downcasted_tile, current_price)
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

            auction_data = AuctionData(
                tile_id=tile_id,
                current_price=new_current_price,
                next_price=new_next_price,
                started_by_id=started_by_id,
                players=players_ids,
                is_bet=True,
            )

            pa = PendingAction.objects.create(
                player_id=next_in_auction_id,
                action_type=PendingAction.Types.IN_AUCTION,
                expires_at=timezone.now(),
                action_data=auction_data.model_dump(),
            )

        return events

    def _handle_reject_auction(
        self, game: Game, player: Player, resolved_pa: PendingAction, command: ActionCommand
    ) -> list[GameEvent]:
        events: list[GameEvent] = []
        # Auction data
        auction_data = AuctionData(**resolved_pa.action_data)
        tile_id = auction_data.tile_id
        current_price = auction_data.current_price
        next_price = auction_data.next_price  # could be None if it's the first turn
        started_by_id = auction_data.started_by_id
        players_ids = auction_data.players
        is_bet = auction_data.is_bet

        players_ids.remove(player.pk)

        if len(players_ids) == 0:
            started_by_user = Player.objects.get(pk=started_by_id)
            next_turn_events = self._next_turn(game, started_by_user)
            events.extend(next_turn_events)
        elif len(players_ids) == 1:
            if is_bet:
                tile = Tile.objects.get(pk=tile_id)
                downcasted_tile = tile.downcast()
                last_player = Player.objects.get(pk=players_ids[0])
                buy_tile_events = self._buy_tile(game, last_player, downcasted_tile, current_price)
                events.extend(buy_tile_events)
                started_by_user = Player.objects.get(pk=started_by_id)
                next_turn_events = self._next_turn(game, started_by_user)

                events.extend(next_turn_events)
            else:
                next_in_auction_id = players_ids[0]
                game.current_player_id = next_in_auction_id
                game.save()
                auction_data = AuctionData(
                    tile_id=tile_id,
                    current_price=current_price,
                    next_price=next_price,
                    started_by_id=started_by_id,
                    players=players_ids,
                    is_bet=True,
                )

                pa = PendingAction.objects.create(
                    player_id=next_in_auction_id,
                    action_type=PendingAction.Types.IN_AUCTION,
                    expires_at=timezone.now(),
                    action_data=auction_data.model_dump(),
                )
        else:
            raise NotImplementedError()

        return events

    def _handle_accept_casino(
        self, game: Game, player: Player, resolved_pa: PendingAction, command: ActionCommand
    ) -> list[GameEvent]:
        events: list[GameEvent] = []

        if not command.bet:
            raise GameException("Bet should be specified for accepting casino")

        won_casino = self._flip_coin_value()
        if won_casino:
            player.cash += command.bet
            events.append(
                self._create_game_event(
                    game, GameEvent.Types.PLAYER_WON_CASINO, extra_data={"player": player.pk}
                )
            )
        else:
            player.cash -= command.bet
            events.append(
                self._create_game_event(
                    game, GameEvent.Types.PLAYER_LOST_CASINO, extra_data={"player": player.pk}
                )
            )

        player.save()
        # pa = PendingAction.objects.create(
        #     player=player,
        #     action_type=PendingAction.Types.IN_CASINO,
        #     expires_at=timezone.now(),
        #     action_data=resolved_pa.action_data,
        # )
        self._next_turn(game, player)

        return events

    def _handle_reject_casino(
        self, game: Game, player: Player, resolved_pa: PendingAction, command: ActionCommand
    ) -> list[GameEvent]:
        events: list[GameEvent] = []
        self._next_turn(game, player)
        return events

    def _improve_ownership(
        self, game: Game, player: Player, ownership: Ownership, override_price: int | None = None
    ) -> list[GameEvent]:
        events: list[GameEvent] = []

        downcasted_tile = ownership.tile.downcast()

        if not isinstance(downcasted_tile, (Property)):
            raise GameException("You can't improve non Property tile")

        if player.cash < downcasted_tile.house_price:
            raise GameException("You don't have enough money")

        amount = override_price if override_price is not None else downcasted_tile.house_price
        player.cash -= amount
        player.save()
        ownership.houses += 1
        ownership.save()

        return events

    def _handle_improve(
        self, game: Game, player: Player, resolved_pa: PendingAction, command: ActionCommand
    ) -> list[GameEvent]:
        events: list[GameEvent] = []

        if not command.property_pos:
            raise GameException("Property position should be specified")

        try:
            ownership = Ownership.objects.select_related("tile").get(
                player=player, tile__position=command.property_pos
            )
        except Ownership.DoesNotExist:
            raise GameException("You don't own this tile")

        if not ownership.owns_entire_group():
            raise GameException("You must own entire group")

        if ownership.houses + 1 > 5:
            raise GameException("You can't improve to more then 5")

        if not ownership.check_can_improve():
            raise GameException("You must improve evenly")

        self._improve_ownership(game, player, ownership)

        pa = PendingAction.objects.create(
            player=player,
            action_type=PendingAction.Types.ROLL_DICE,
            expires_at=timezone.now(),
            action_data=resolved_pa.action_data,
        )

        return events

    def _handle_degrade(
        self, game: Game, player: Player, resolved_pa: PendingAction, command: ActionCommand
    ) -> list[GameEvent]:
        events: list[GameEvent] = []

        if not command.property_pos:
            raise GameException("Property position should be specified")

        try:
            ownership = Ownership.objects.select_related("tile").get(
                player=player, tile__position=command.property_pos
            )
        except Ownership.DoesNotExist:
            raise GameException("You don't own this tile")

        if ownership.houses - 1 < 0:
            raise GameException("You can't degrade below 0")

        if not ownership.check_can_degrade():
            raise GameException("You must degrade evenly")

        downcasted_tile = ownership.tile.downcast()

        if not isinstance(downcasted_tile, (Property)):
            raise GameException("You can't improve non Property tile")

        player.cash += downcasted_tile.house_price
        player.save()
        ownership.houses -= 1
        ownership.save()

        pa = PendingAction.objects.create(
            player=player,
            action_type=PendingAction.Types.ROLL_DICE,
            # action_type=resolved_pa.action_type,
            expires_at=timezone.now(),
            action_data=resolved_pa.action_data,
        )

        return events

    def _handle_start_trade(
        self, game: Game, player: Player, resolved_pa: PendingAction, command: ActionCommand
    ) -> list[GameEvent]:
        events: list[GameEvent] = []

        for attr in ("offer", "request", "to_player"):
            if getattr(command, attr, None) is None:
                raise GameException(f"{attr} should be specified for trade")

        try:
            trade_data = TradeData(**command.model_dump(), from_player=player.pk)
        except ValidationError:
            raise GameException("Action data is invalid")

        if trade_data.from_player == trade_data.to_player:
            raise GameException("You can't trade with yourself")

        if (
            len(trade_data.offer.tile_ids) == 0
            and len(trade_data.request.tile_ids) == 0
            and trade_data.offer.cash == 0
            and trade_data.request.cash == 0
        ):
            raise GameException("You can't send an empty trade")

        try:
            from_player: Player = game.players.get(pk=trade_data.from_player)
            to_player: Player = game.players.get(pk=trade_data.to_player)
        except Player.DoesNotExist:
            raise GameException("Could not find player for trade")

        if from_player.cash < trade_data.offer.cash:
            raise GameException("You don't have that much money to offer")
        if to_player.cash < trade_data.request.cash:
            raise GameException("You can't request that much money")

        trade_data.ensure_owns_all(from_player, trade_data.offer.tile_ids, "You don't own this tile to offer")
        trade_data.ensure_owns_all(
            to_player, trade_data.request.tile_ids, "Other player don't own this tiles"
        )

        game.current_player = to_player
        game.save()

        print(f"{trade_data.request=}")

        pa = PendingAction.objects.create(
            player_id=trade_data.to_player,
            action_type=PendingAction.Types.IN_TRADE,
            expires_at=timezone.now(),
            action_data=trade_data.model_dump(),
        )

        return events

    def _handle_reject_trade(
        self, game: Game, player: Player, resolved_pa: PendingAction, command: ActionCommand
    ) -> list[GameEvent]:
        events: list[GameEvent] = []
        action_data = TradeData(**resolved_pa.action_data)

        game.current_player_id = action_data.from_player
        game.save()

        pa = PendingAction.objects.create(
            player_id=action_data.from_player,
            action_type=PendingAction.Types.ROLL_DICE,
            expires_at=timezone.now(),
        )

        return events

    def _handle_accept_trade(
        self, game: Game, player: Player, resolved_pa: PendingAction, command: ActionCommand
    ) -> list[GameEvent]:
        events: list[GameEvent] = []
        action_data = TradeData(**resolved_pa.action_data)

        offered_cash = action_data.offer.cash
        requested_cash = action_data.request.cash
        from_player_id = action_data.from_player
        to_player_id = action_data.to_player

        # Giving tiles
        Ownership.objects.filter(
            game=game, player_id=from_player_id, tile_id__in=action_data.offer.tile_ids
        ).update(player_id=to_player_id)
        # Receiving tiles
        Ownership.objects.filter(
            game=game, player_id=to_player_id, tile_id__in=action_data.request.tile_ids
        ).update(player_id=from_player_id)

        Player.objects.filter(id=from_player_id).update(cash=F("cash") - offered_cash + requested_cash)
        Player.objects.filter(id=to_player_id).update(cash=F("cash") + offered_cash - requested_cash)

        game.current_player_id = from_player_id
        game.save()

        pa = PendingAction.objects.create(
            player_id=action_data.from_player,
            action_type=PendingAction.Types.ROLL_DICE,
            expires_at=timezone.now(),
        )

        return events

    @transaction.atomic
    def process_game_action(self, game_uuid, player_id, action) -> dict:
        logger.debug("Processing game action", game_uuid, player_id, action)
        if isinstance(action, str):
            action = ActionCommand(action=action)

        events: list[GameEvent] = []
        # TODO: Add select/prefetch related
        player = Player.objects.select_for_update().get(pk=player_id)
        game = Game.objects.select_for_update().get(pk=game_uuid)

        if game.current_player != player:
            raise GameException("It's not your turn")

        if player.status == player.Status.WAITING:
            print("Whole other deal")
        elif player.status == player.Status.PLAYING:
            prev_pa = player.pending_action
            if prev_pa is None:
                raise GameException("Could not find pending action to resolve")

            handler = self.PENDING_ACTION_COMMAND_HANDLERS.get(prev_pa.action_type, {}).get(action.action)  # type: ignore[call-overload]
            if not handler:
                raise GameException(f"There is no such action. Action: {action.action}")

            prev_pa.resolved_at = timezone.now()
            prev_pa.save()

            events = handler(game, player, prev_pa, action)

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

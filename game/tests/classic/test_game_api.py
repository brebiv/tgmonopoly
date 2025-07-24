from typing import no_type_check
import pytest
import math
from unittest.mock import patch
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from django.db import IntegrityError
from django.db.models import Count

from . import mock_data
from tgmonopoly.asgi import application
from game.management.commands.populate_database import (
    Command as PopulateDatabaseCommand,
)
from game.models import (
    PendingAction,
    BoardConfig,
    Game,
    Player,
    Property,
    PropertyGroup,
    Jail,
    Police,
    Ownership,
    GameEvent,
    Utility,
    UtilityGroup,
    Tax,
    Casino,
    Chance,
    ChanceCard,
    Start,
)
from game.services import get_service_by_name, ClassicMonopolyService
from game.exceptions import GameException
from game.schemas import ActionCommand
from game import schemas
from .. import BaseApiTestCase


class CreateGameAPITest(BaseApiTestCase):
    def test_create_game(self):
        self._call_create_game(2, auto_join=False)

    def test_create_game_and_join_game(self):
        self._call_create_game(2)

    def test_unique_color_constraint(self):
        board_config = BoardConfig.objects.get(name=BoardConfig.Names.CLASSIC)
        game = Game.objects.create(board_config=board_config, max_players=2)
        Player.objects.create(user=self.tg_user_1, game=game, color=Player.Color.BLUE)
        with self.assertRaises(IntegrityError):
            Player.objects.create(user=self.tg_user_2, game=game, color=Player.Color.BLUE)


class DiceRollAPITest(BaseApiTestCase):
    @patch("game.services.ClassicMonopolyService._roll_dice_values")
    async def test_initial_roll_dice_action(self, mock_dice_values):
        dices_values = [1, 2]
        dice_sum = sum(dices_values)
        mock_dice_values.return_value = dices_values

        await database_sync_to_async(self._call_create_game)(2)

        ws_url = f"/ws/game/{self.game.uuid}/?" + mock_data.TG_INIT_DATA_RAW_LIST[0]
        communicator = WebsocketCommunicator(application, ws_url)
        connected, _ = await communicator.connect()

        self.assertTrue(connected)
        game_frame = await communicator.receive_json_from()

        await self._refresh_game_and_players_async()
        frame_type = game_frame["type"]
        p1 = game_frame["game"]["players"][0]
        p2 = game_frame["game"]["players"][1]
        player_1 = self.players[0]

        self.assertEqual(frame_type, "game.initial")
        self.assertEqual(p1["pending_action"]["action_type"], PendingAction.Types.ROLL_DICE.value)
        self.assertIsNone(p2["pending_action"])
        self.assertEqual(player_1.position, 0)

        await communicator.send_json_to({"action": "roll_dice"})
        game_frame = await communicator.receive_json_from()
        frame_type = game_frame["type"]
        p1 = game_frame["game"]["players"][0]
        p2 = game_frame["game"]["players"][1]
        await self._refresh_game_and_players_async()

        self.assertEqual(frame_type, "game.event")
        self.assertEqual(p1["pending_action"]["action_type"], PendingAction.Types.BUY_PROPERTY.value)
        self.assertIsNone(p2["pending_action"])
        self.assertEqual(player_1.position, dice_sum)

    async def test_not_your_turn(self):
        await database_sync_to_async(self._call_create_game)(2)

        ws_url = f"/ws/game/{self.game.uuid}/?" + mock_data.TG_INIT_DATA_RAW_LIST[1]
        communicator = WebsocketCommunicator(application, ws_url)
        connected, _ = await communicator.connect()

        self.assertTrue(connected)
        game_frame = await communicator.receive_json_from()

        await communicator.send_json_to({"action": "roll_dice"})
        game_frame = await communicator.receive_json_from()
        await self._refresh_game_and_players_async()
        frame_type = game_frame["type"]

        self.assertEqual(frame_type, "game.error")
        self.assertIsNotNone(game_frame.get("msg"))

    @patch("game.services.ClassicMonopolyService._roll_dice_values")
    async def test_go_to_jail_because_of_doubles(self, mock_dice_values):
        dices_values = [20, 20]  # will loop over start tile
        mock_dice_values.return_value = dices_values

        await database_sync_to_async(self._call_create_game)(2)

        ws_url = f"/ws/game/{self.game.uuid}/?" + mock_data.TG_INIT_DATA_RAW_LIST[0]
        communicator = WebsocketCommunicator(application, ws_url)
        connected, _ = await communicator.connect()

        self.assertTrue(connected)
        game_frame = await communicator.receive_json_from()

        await self._refresh_game_and_players_async()
        frame_type = game_frame["type"]
        p1 = game_frame["game"]["players"][0]
        p2 = game_frame["game"]["players"][1]
        player_1 = self.players[0]
        player_1.cash = 1000
        await player_1.asave()

        self.assertEqual(frame_type, "game.initial")
        self.assertEqual(p1["pending_action"]["action_type"], PendingAction.Types.ROLL_DICE.value)
        self.assertIsNone(p2["pending_action"])
        self.assertEqual(player_1.position, 0)

        await communicator.send_json_to({"action": "roll_dice"})

        for _ in range(5):
            game_frame = await communicator.receive_json_from()
            p1 = game_frame["game"]["players"][0]
            if p1["in_jail"]:
                break

            if p1["pending_action"]["action_type"] == PendingAction.Types.ROLL_DICE:
                await communicator.send_json_to({"action": "roll_dice"})
            elif p1["pending_action"]["action_type"] == PendingAction.Types.BUY_PROPERTY:
                await communicator.send_json_to({"action": "accept"})

        await player_1.arefresh_from_db()
        jail_tile = await database_sync_to_async(Jail.objects.get)(board_config_id=self.game.board_config_id)

        self.assertEqual(player_1.in_jail, True)
        self.assertEqual(player_1.position, jail_tile.position)

    @patch("game.services.ClassicMonopolyService._roll_dice_values")
    async def test_go_to_jail_from_police(self, mock_dice_values):
        await database_sync_to_async(self._call_create_game)(2)

        ws_url = f"/ws/game/{self.game.uuid}/?" + mock_data.TG_INIT_DATA_RAW_LIST[0]
        communicator = WebsocketCommunicator(application, ws_url)
        connected, _ = await communicator.connect()

        self.assertTrue(connected)
        game_frame = await communicator.receive_json_from()

        await self._refresh_game_and_players_async()
        frame_type = game_frame["type"]
        p1 = game_frame["game"]["players"][0]
        p2 = game_frame["game"]["players"][1]
        player_1 = self.players[0]
        player_1.cash = 1000
        await player_1.asave()

        self.assertEqual(frame_type, "game.initial")
        self.assertEqual(p1["pending_action"]["action_type"], PendingAction.Types.ROLL_DICE.value)
        self.assertIsNone(p2["pending_action"])
        self.assertEqual(player_1.position, 0)

        police_tile = await database_sync_to_async(Police.objects.get)(
            board_config_id=self.game.board_config_id
        )

        dices_values = [police_tile.position, 0]
        mock_dice_values.return_value = dices_values

        import json

        await communicator.send_to(text_data=json.dumps({"action": "roll_dice"}))

        game_frame = await communicator.receive_json_from()

        await player_1.arefresh_from_db()
        jail_tile = await database_sync_to_async(Jail.objects.get)(board_config_id=self.game.board_config_id)

        self.assertEqual(player_1.in_jail, True)
        self.assertEqual(player_1.position, jail_tile.position)


class TestAuctionLegacy(BaseApiTestCase):
    monopoly_service: ClassicMonopolyService
    player_1: Player
    player_2: Player
    player_3: Player

    def setUp(self):
        PopulateDatabaseCommand().handle()

    def _create_game(self, players: int):
        self.tg_users = mock_data.create_telegram_users(players, synthetic=True)
        self.monopoly_service = get_service_by_name("classic")  # type: ignore[assignment]
        self.game = self.monopoly_service.create_game(self.tg_users[0], players)

        for i in range(1, players):
            player, _ = self.monopoly_service.join_game(self.game.uuid, self.tg_users[i])

        game_players = self.game.players.all()
        self.players = list(game_players)

        self._refresh_game_and_players()

    @patch("game.services.ClassicMonopolyService._roll_dice_values")
    def test_start_auction(self, mock_dice_values):
        dices_value = [1, 2]
        mock_dice_values.return_value = dices_value
        # Make sure player has enough money for buying tile in auction
        self._create_game(2)
        self.player_1 = self.players[0]
        self.player_2 = self.players[1]
        self.player_2.cash = 1000
        self.player_2.save()

        self.assertEqual(self.player_1.pending_action.action_type, PendingAction.Types.ROLL_DICE)

        self.monopoly_service.process_game_action(self.game.uuid, self.player_1.pk, "roll_dice")
        self._refresh_game_and_players()

        self.assertEqual(self.game.current_player, self.player_1)
        self.assertEqual(self.player_1.pending_action.action_type, PendingAction.Types.BUY_PROPERTY)

        self.monopoly_service.process_game_action(self.game.uuid, self.player_1.pk, "start_auction")
        self._refresh_game_and_players()

        property = Property.objects.get(position=self.player_1.position)

        self.assertEqual(self.game.current_player, self.player_2)
        self.assertEqual(self.player_2.pending_action.action_type, PendingAction.Types.IN_AUCTION)
        self.assertEqual(self.player_2.pending_action.action_data.get("tile_id"), property.pk)
        self.assertEqual(self.player_2.pending_action.action_data.get("current_price"), property.price * 1.1)
        self.assertListEqual(
            self.player_2.pending_action.action_data.get("players"),
            [
                self.player_2.pk,
            ],
        )

    @patch("game.services.ClassicMonopolyService._roll_dice_values")
    def test_start_auction_flop(self, mock_dice_values):
        dices_value = [1, 2]
        mock_dice_values.return_value = dices_value
        """When other players don't have enough money for auction"""
        self._create_game(2)
        self.player_1 = self.players[0]
        self.player_2 = self.players[1]
        # Make sure player has not enough money for buying tile in auction
        self.player_2.cash = 5
        self.player_2.save()

        self.assertEqual(self.player_1.pending_action.action_type, PendingAction.Types.ROLL_DICE)
        self.assertEqual(self.game.turn, 1)

        self.monopoly_service.process_game_action(self.game.uuid, self.player_1.pk, "roll_dice")
        self._refresh_game_and_players()

        self.assertEqual(self.game.current_player, self.player_1)
        self.assertEqual(self.player_1.pending_action.action_type, PendingAction.Types.BUY_PROPERTY)

        self.monopoly_service.process_game_action(self.game.uuid, self.player_1.pk, "start_auction")
        self._refresh_game_and_players()

        self.assertEqual(self.game.turn, 2)
        self.assertEqual(self.player_2.pending_action.action_type, PendingAction.Types.ROLL_DICE)

    @patch("game.services.ClassicMonopolyService._roll_dice_values")
    def test_accept_auction_2_players_no_double_dice(self, mock_dice_values):
        dices_value = [1, 2]
        mock_dice_values.return_value = dices_value
        self._create_game(2)
        self.player_1 = self.players[0]
        self.player_2 = self.players[1]
        # Make sure player has enough money for buying tile in auction
        self.player_2.cash = 1000
        self.player_2.save()
        self.assertEqual(self.player_1.pending_action.action_type, PendingAction.Types.ROLL_DICE)

        self.monopoly_service.process_game_action(self.game.uuid, self.player_1.pk, "roll_dice")
        self._refresh_game_and_players()

        self.assertEqual(self.game.current_player, self.player_1)
        self.assertEqual(self.player_1.pending_action.action_type, PendingAction.Types.BUY_PROPERTY)

        self.monopoly_service.process_game_action(self.game.uuid, self.player_1.pk, "start_auction")
        self._refresh_game_and_players()

        property = Property.objects.get(position=self.player_1.position)
        expected_property_price = property.price * 1.1
        player_2_cash_before_accept = self.player_2.cash

        self.assertEqual(self.game.turn, 1)
        self.assertEqual(self.game.current_player, self.player_2)
        self.assertEqual(self.player_2.pending_action.action_type, PendingAction.Types.IN_AUCTION)
        self.assertEqual(self.player_2.pending_action.action_data.get("tile_id"), property.pk)
        self.assertEqual(
            self.player_2.pending_action.action_data.get("current_price"), expected_property_price
        )
        self.assertEqual(self.player_2.pending_action.action_data.get("started_by_id"), self.player_1.pk)
        self.assertListEqual(
            self.player_2.pending_action.action_data.get("players"),
            [
                self.player_2.pk,
            ],
        )

        self.monopoly_service.process_game_action(self.game.uuid, self.player_2.pk, "accept")
        self._refresh_game_and_players()

        self.assertEqual(self.game.turn, 2)
        self.assertEqual(self.game.current_player, self.player_2)
        self.assertEqual(self.player_2.cash, player_2_cash_before_accept - expected_property_price)
        self.assertEqual(self.player_2.ownerships.count(), 1)

    @patch("game.services.ClassicMonopolyService._roll_dice_values")
    def test_reject_auction_2_players_no_double_dice(self, mock_dice_values):
        dices_value = [1, 2]
        mock_dice_values.return_value = dices_value
        self._create_game(2)
        self.player_1 = self.players[0]
        self.player_2 = self.players[1]
        # Make sure player has enough money for buying tile in auction
        self.player_2.cash = 1000
        self.player_2.save()
        self.assertEqual(self.player_1.pending_action.action_type, PendingAction.Types.ROLL_DICE)

        self.monopoly_service.process_game_action(self.game.uuid, self.player_1.pk, "roll_dice")
        self._refresh_game_and_players()

        self.assertEqual(self.game.current_player, self.player_1)
        self.assertEqual(self.player_1.pending_action.action_type, PendingAction.Types.BUY_PROPERTY)

        self.monopoly_service.process_game_action(self.game.uuid, self.player_1.pk, "start_auction")
        self._refresh_game_and_players()

        property = Property.objects.get(position=self.player_1.position)
        expected_property_price = property.price * 1.1
        player_2_cash_before_accept = self.player_2.cash

        self.assertEqual(self.game.turn, 1)
        self.assertEqual(self.game.current_player, self.player_2)
        self.assertEqual(self.player_2.pending_action.action_type, PendingAction.Types.IN_AUCTION)
        self.assertEqual(self.player_2.pending_action.action_data.get("tile_id"), property.pk)
        self.assertEqual(
            self.player_2.pending_action.action_data.get("current_price"), expected_property_price
        )
        self.assertEqual(self.player_2.pending_action.action_data.get("started_by_id"), self.player_1.pk)

        self.monopoly_service.process_game_action(self.game.uuid, self.player_2.pk, "reject")
        self._refresh_game_and_players()

        self.assertEqual(self.game.turn, 2)
        self.assertEqual(self.game.current_player, self.player_2)
        self.assertEqual(self.player_2.pending_action.action_type, PendingAction.Types.ROLL_DICE)
        self.assertEqual(self.player_2.cash, player_2_cash_before_accept)
        self.assertEqual(self.player_2.ownerships.count(), 0)


@pytest.mark.django_db
class TestAuction:
    monopoly_service: ClassicMonopolyService
    player_1: Player
    player_2: Player
    player_3: Player

    def setup_method(self, method):
        PopulateDatabaseCommand().handle()

    def _refresh_game_and_players(self):
        """Refresh game and all players from DB"""
        self.game.refresh_from_db()
        for player in self.players:
            player.refresh_from_db()

    def _create_game(self, players: int):
        self.tg_users = mock_data.create_telegram_users(players, synthetic=True)
        self.monopoly_service = get_service_by_name("classic")  # type: ignore[assignment]
        self.game = self.monopoly_service.create_game(self.tg_users[0], players)

        for i in range(1, players):
            player, _ = self.monopoly_service.join_game(self.game.uuid, self.tg_users[i])

        game_players = self.game.players.all()
        self.players = list(game_players)
        self._refresh_game_and_players()

    @pytest.mark.parametrize(
        ("actions_sequence", "expected_winner_idx", "description"),
        [
            (("accept", "reject"), 1, "Player 2 accepts, player 3 rejects"),
            (("reject", "reject"), None, "Everybody rejects, no winner"),
            (("reject", "accept"), 2, "Player 2 rejects, Player 3 wins"),
            (("accept", "accept", "accept", "accept", "reject"), 2, "4 step auction"),
            ((*("accept",) * 5, "reject"), 1, "5 step auction"),
        ],
    )
    def test_accept_auction_3_players_no_double_dice(
        self, db, actions_sequence, expected_winner_idx, description
    ):
        self._create_game(3)

        self.player_1 = self.players[0]
        self.player_2 = self.players[1]
        self.player_3 = self.players[2]

        self.player_2.cash = 1000
        self.player_3.cash = 1000
        self.player_2.save()
        self.player_3.save()

        players_in_auction = [self.player_2, self.player_3]

        assert self.player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE

        with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=[1, 2]):
            self.monopoly_service.process_game_action(self.game.uuid, self.player_1.pk, "roll_dice")

        self._refresh_game_and_players()

        assert self.game.current_player == self.player_1
        assert self.player_1.pending_action.action_type == PendingAction.Types.BUY_PROPERTY

        self.monopoly_service.process_game_action(self.game.uuid, self.player_1.pk, "start_auction")
        self._refresh_game_and_players()

        property = Property.objects.get(position=self.player_1.position)
        expected_property_price = math.ceil(property.price * 1.1)
        player_2_cash_before_accept = self.player_2.cash

        assert self.game.turn == 1
        assert self.game.current_player == self.player_2
        assert self.player_2.pending_action.action_type == PendingAction.Types.IN_AUCTION
        assert self.player_2.pending_action.action_data.get("tile_id") == property.pk
        assert self.player_2.pending_action.action_data.get("current_price") == expected_property_price

        assert self.player_2.pending_action.action_data.get("next_price") is None
        assert self.player_2.pending_action.action_data.get("started_by_id") == self.player_1.pk
        assert self.player_2.pending_action.action_data.get("players") == [self.player_2.pk, self.player_3.pk]

        for i, action in enumerate(actions_sequence):
            idx = i % len(players_in_auction)
            cur_player = players_in_auction[idx]
            # next_player = players_in_auction[(i + 1) % len(players_in_auction)]

            self.monopoly_service.process_game_action(self.game.uuid, cur_player.pk, action)

        self._refresh_game_and_players()

        assert self.game.turn == 2
        assert self.game.current_player == self.player_2

        if expected_winner_idx:
            expected_winner = self.players[expected_winner_idx]
            assert expected_winner.ownerships.count() == 1
        else:
            assert self.player_2.ownerships.count() == 0
            assert self.player_2.cash == player_2_cash_before_accept


@pytest.mark.django_db
class TestJail:
    monopoly_service: ClassicMonopolyService
    game: Game
    player_1: Player
    player_2: Player
    player_3: Player

    def setup_method(self, method):
        PopulateDatabaseCommand().handle()

    def _refresh_game_and_players(self):
        """Refresh game and all players from DB"""
        self.game.refresh_from_db()
        for player in self.players:
            player.refresh_from_db()

    def _create_game(self, players: int):
        self.tg_users = mock_data.create_telegram_users(players, synthetic=True)
        self.monopoly_service = get_service_by_name("classic")  # type: ignore[assignment]
        self.game = self.monopoly_service.create_game(self.tg_users[0], players)

        for i in range(1, players):
            player, _ = self.monopoly_service.join_game(self.game.uuid, self.tg_users[i])

        game_players = self.game.players.all()
        self.players = list(game_players)
        self._refresh_game_and_players()

    def test_getting_out_of_jail_on_first_attempt(self):
        self._create_game(2)
        self.game.players.update(cash=1000)

        player_1 = self.players[0]

        self.monopoly_service._move_player_to_jail(self.game, player_1)

        assert player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE

        with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=[2, 2]):
            self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "roll_dice")

        self._refresh_game_and_players()

        assert player_1.in_jail is False
        assert player_1.jail_turns == 0
        assert self.game.current_player == player_1
        assert player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE

    def test_getting_out_of_jail_on_second_attempt(self) -> None:
        self._create_game(2)
        self.game.players.update(cash=1000)

        player_1: Player = self.players[0]
        player_2: Player = self.players[1]

        self.monopoly_service._move_player_to_jail(self.game, player_1)

        assert player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE  # type: ignore[union-attr]
        assert player_1.jail_turns == 0

        with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=[2, 1]):
            self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "roll_dice")

        self._refresh_game_and_players()

        assert player_1.in_jail is True
        assert player_1.jail_turns == 1
        assert self.game.current_player == player_2
        assert player_2.pending_action.action_type == PendingAction.Types.ROLL_DICE  # type: ignore[union-attr]

        with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=[39, 1]):
            # Just go ever to start tile
            self.monopoly_service.process_game_action(self.game.uuid, player_2.pk, "roll_dice")

        with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=[2, 2]):
            self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "roll_dice")

        self._refresh_game_and_players()

        assert player_1.in_jail is False
        assert player_1.jail_turns == 0
        assert self.game.current_player == player_1
        assert player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE

    def test_out_of_jail_escape_attempts(self) -> None:
        self._create_game(2)
        self.game.players.update(cash=1000)

        player_1: Player = self.players[0]
        player_2: Player = self.players[1]

        self.monopoly_service._move_player_to_jail(self.game, player_1)

        assert player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE  # type: ignore[union-attr]
        assert player_1.jail_turns == 0

        for i in range(3):
            with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=[1, 2]):
                self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "roll_dice")

            if i < 2:
                with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=[39, 1]):
                    # Just go ever to start tile
                    self.monopoly_service.process_game_action(self.game.uuid, player_2.pk, "roll_dice")

        self._refresh_game_and_players()

        with pytest.raises(GameException):
            with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=[1, 2]):
                self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "roll_dice")

        assert player_1.in_jail is True
        assert player_1.jail_turns == 3
        assert self.game.current_player == player_1
        assert player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE  # type: ignore[union-attr]

    def test_pay_for_jail(self) -> None:
        self._create_game(2)
        self.game.players.update(cash=1000)

        player_1: Player = self.players[0]
        player_2: Player = self.players[1]

        player_1_cash_before = player_1.cash

        self.monopoly_service._move_player_to_jail(self.game, player_1)

        assert player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE  # type: ignore[union-attr]
        assert player_1.jail_turns == 0

        self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "reject")
        self._refresh_game_and_players()

        assert player_1.cash == player_1_cash_before - 100
        assert player_1.in_jail is False
        assert player_1.jail_turns == 0
        assert self.game.current_player == player_1
        assert player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE  # type: ignore[union-attr]

    def test_pay_for_jail_no_money(self) -> None:
        self._create_game(2)
        self.game.players.update(cash=1)

        player_1: Player = self.players[0]
        player_2: Player = self.players[1]

        player_1.cash = 1
        player_1.save()
        player_1_cash_before = player_1.cash

        self.monopoly_service._move_player_to_jail(self.game, player_1)

        assert player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE  # type: ignore[union-attr]
        assert player_1.jail_turns == 0

        with pytest.raises(GameException):
            self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "reject")

        self._refresh_game_and_players()

        assert player_1.in_jail is True
        assert player_1.jail_turns == 0
        assert self.game.current_player == player_1
        assert player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE  # type: ignore[union-attr]

    def test_pay_for_jail_not_in_jail(self) -> None:
        self._create_game(2)
        player_1: Player = self.players[0]

        assert player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE  # type: ignore[union-attr]

        with pytest.raises(GameException):
            self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "reject")


@pytest.mark.django_db
class TestPayRent:
    monopoly_service: ClassicMonopolyService
    game: Game
    player_1: Player
    player_2: Player
    player_3: Player

    def setup_method(self, method):
        PopulateDatabaseCommand().handle()

    def _refresh_game_and_players(self):
        """Refresh game and all players from DB"""
        self.game.refresh_from_db()
        for player in self.players:
            player.refresh_from_db()

    def _create_game(self, players: int):
        self.tg_users = mock_data.create_telegram_users(players, synthetic=True)
        self.monopoly_service = get_service_by_name("classic")  # type: ignore[assignment]
        self.game = self.monopoly_service.create_game(self.tg_users[0], players)

        for i in range(1, players):
            player, _ = self.monopoly_service.join_game(self.game.uuid, self.tg_users[i])

        game_players = self.game.players.all()
        self.players = list(game_players)
        self._refresh_game_and_players()

    def test_pay_rent(self):
        self._create_game(2)
        player_1 = self.players[0]
        player_2 = self.players[1]

        player_2_cash_before = player_2.cash

        assert player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE

        with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=[2, 1]):
            # Roll dice and but property on position 3
            self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "roll_dice")
            self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "accept")

        self._refresh_game_and_players()

        assert player_1.ownerships.count() == 1
        assert self.game.current_player == player_2
        assert player_2.pending_action.action_type == PendingAction.Types.ROLL_DICE

        with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=[2, 1]):
            # Roll dice and but property on position 3
            self.monopoly_service.process_game_action(self.game.uuid, player_2.pk, "roll_dice")

        self._refresh_game_and_players()
        assert self.game.current_player == player_2
        assert player_2.pending_action.action_type == PendingAction.Types.PAY_RENT

        self.monopoly_service.process_game_action(self.game.uuid, player_2.pk, "accept")
        self._refresh_game_and_players()

        property = Property.objects.get(board_config=self.game.board_config, position=3)

        assert player_2.cash == player_2_cash_before - property.rent
        assert self.game.current_player == player_1
        assert player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE

    def test_pay_rent_no_money(self):
        self._create_game(2)
        player_1 = self.players[0]
        player_2 = self.players[1]

        player_2.cash = 1
        player_2.save()
        player_2_cash_before = player_2.cash

        assert player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE

        with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=[2, 1]):
            # Roll dice and but property on position 3
            self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "roll_dice")
            self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "accept")

        self._refresh_game_and_players()

        assert player_1.ownerships.count() == 1
        assert self.game.current_player == player_2
        assert player_2.pending_action.action_type == PendingAction.Types.ROLL_DICE

        with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=[2, 1]):
            # Roll dice and but property on position 3
            self.monopoly_service.process_game_action(self.game.uuid, player_2.pk, "roll_dice")

        self._refresh_game_and_players()
        assert self.game.current_player == player_2
        assert player_2.pending_action.action_type == PendingAction.Types.PAY_RENT

        with pytest.raises(GameException):
            self.monopoly_service.process_game_action(self.game.uuid, player_2.pk, "accept")

        self._refresh_game_and_players()

        assert player_2.cash == player_2_cash_before
        assert self.game.current_player == player_2
        assert player_2.pending_action.action_type == PendingAction.Types.PAY_RENT

    def test_land_on_own_property(self):
        self._create_game(2)
        player_1 = self.players[0]
        player_2 = self.players[1]

        player_2.cash = 1
        property = Property.objects.get(board_config=self.game.board_config, position=3)
        ownership = Ownership.objects.create(
            game=self.game,
            player=player_1,
            tile=property,
        )

        with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=[2, 1]):
            # Roll dice and but property on position 3
            game_frame = self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "roll_dice")

        self._refresh_game_and_players()

        assert self.game.current_player == player_2
        assert (
            next(
                (
                    e
                    for e in game_frame["events"]
                    if e["event_type"] == GameEvent.Types.LANDED_ON_OWN_PROPERTY
                ),
                None,
            )
            is not None
        )


@pytest.mark.django_db
class TestUtility:
    monopoly_service: ClassicMonopolyService
    game: Game
    player_1: Player
    player_2: Player
    player_3: Player

    def setup_method(self, method):
        PopulateDatabaseCommand().handle()

    def _refresh_game_and_players(self):
        """Refresh game and all players from DB"""
        self.game.refresh_from_db()
        for player in self.players:
            player.refresh_from_db()

    def _create_game(self, players: int):
        self.tg_users = mock_data.create_telegram_users(players, synthetic=True)
        self.monopoly_service = get_service_by_name("classic")  # type: ignore[assignment]
        self.game = self.monopoly_service.create_game(self.tg_users[0], players)

        for i in range(1, players):
            player, _ = self.monopoly_service.join_game(self.game.uuid, self.tg_users[i])

        game_players = self.game.players.all()
        self.players = list(game_players)
        self._refresh_game_and_players()

    @pytest.mark.parametrize(
        ("should_roll_double",),
        [
            (False,),
            (True,),
        ],
    )
    @no_type_check
    def test_landing_on_free_utility_buy(self, should_roll_double):
        self._create_game(2)
        player_1: Player = self.players[0]
        player_2: Player = self.players[1]

        utility = Utility.objects.get(board_config=self.game.board_config, position=5)
        dice_values = [utility.position - 1, 1]

        if should_roll_double:
            player_1.position = (player_1.position - utility.position) % self.game.board_config.tiles.count()
            player_1.save()
            dice_values = [utility.position] * 2

        with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=dice_values):
            game_frame = self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "roll_dice")

        self._refresh_game_and_players()

        assert self.game.current_player == player_1
        assert player_1.pending_action.action_type == PendingAction.Types.BUY_PROPERTY

        self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "accept")
        self._refresh_game_and_players()

        if should_roll_double:
            assert self.game.current_player == player_1
            assert player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE
        else:
            assert self.game.current_player == player_2
            assert player_2.pending_action.action_type == PendingAction.Types.ROLL_DICE

    @pytest.mark.parametrize(
        ("should_roll_double", "auction_action", "player_2_expected_ownerships_count"),
        [
            (False, "reject", 0),
            (True, "accept", 1),
        ],
    )
    @no_type_check
    def test_landing_on_free_utility_auction(
        self, should_roll_double, auction_action, player_2_expected_ownerships_count
    ):
        self._create_game(2)
        player_1: Player = self.players[0]
        player_2: Player = self.players[1]

        utility = Utility.objects.get(board_config=self.game.board_config, position=5)
        dice_values = [utility.position - 1, 1]

        if should_roll_double:
            player_1.position = (player_1.position - utility.position) % self.game.board_config.tiles.count()
            player_1.save()
            dice_values = [utility.position] * 2

        with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=dice_values):
            game_frame = self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "roll_dice")

        self._refresh_game_and_players()

        assert self.game.current_player == player_1
        assert player_1.pending_action.action_type == PendingAction.Types.BUY_PROPERTY

        self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "start_auction")
        self._refresh_game_and_players()

        assert self.game.current_player == player_2
        assert player_2.pending_action.action_type == PendingAction.Types.IN_AUCTION

        self.monopoly_service.process_game_action(self.game.uuid, player_2.pk, auction_action)
        self._refresh_game_and_players()

        assert player_2.ownerships.count() == player_2_expected_ownerships_count

        if should_roll_double:
            assert self.game.current_player == player_1
            assert player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE
        else:
            assert self.game.current_player == player_2
            assert player_2.pending_action.action_type == PendingAction.Types.ROLL_DICE

    @pytest.mark.parametrize(
        ("utility_group", "own_entire_group"),
        [
            (UtilityGroup.Types.UTILITY_1, False),
            (UtilityGroup.Types.UTILITY_1, True),
        ],
    )
    @no_type_check
    def test_landing_on_owned_utility_1(self, utility_group, own_entire_group):
        self._create_game(2)
        player_1: Player = self.players[0]
        player_2: Player = self.players[1]
        player_1_cash_before = player_1.cash

        if own_entire_group:
            utilities = list(
                Utility.objects.filter(board_config=self.game.board_config, group__type=utility_group).all()
            )
        else:
            utilities = list(
                Utility.objects.filter(board_config=self.game.board_config, group__type=utility_group)[:1]
            )

        for u in utilities:
            ownership = Ownership.objects.create(
                game=self.game,
                player=player_2,
                tile=u,
            )

        dice_values = [utilities[0].position - 1, 1]

        with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=dice_values):
            game_frame = self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "roll_dice")

        self._refresh_game_and_players()

        expected_rent = utilities[0].rent * len(utilities)

        assert self.game.current_player == player_1
        assert player_1.pending_action.action_type == PendingAction.Types.PAY_RENT  # type: ignore[union-attr]
        assert player_1.pending_action.action_data.get("rent") == expected_rent

        self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "accept")
        self._refresh_game_and_players()

        assert player_1.cash == player_1_cash_before - expected_rent
        assert self.game.current_player == player_2
        assert player_2.pending_action.action_type == PendingAction.Types.ROLL_DICE

    @pytest.mark.parametrize(
        ("utility_group", "own_entire_group"),
        [
            (UtilityGroup.Types.UTILITY_2, False),
            (UtilityGroup.Types.UTILITY_2, True),
        ],
    )
    @no_type_check
    def test_landing_on_owned_utility_2(self, utility_group, own_entire_group):
        self._create_game(2)
        player_1: Player = self.players[0]
        player_2: Player = self.players[1]
        player_1_cash_before = player_1.cash

        if own_entire_group:
            utilities = list(
                Utility.objects.filter(board_config=self.game.board_config, group__type=utility_group).all()
            )
        else:
            utilities = list(
                Utility.objects.filter(board_config=self.game.board_config, group__type=utility_group)[:1]
            )

        for u in utilities:
            ownership = Ownership.objects.create(
                game=self.game,
                player=player_2,
                tile=u,
            )

        dice_values = [utilities[0].position - 1, 1]
        utility_2_multiplier = 10 if own_entire_group else 4

        with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=dice_values):
            game_frame = self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "roll_dice")

        self._refresh_game_and_players()

        expected_rent = sum(dice_values) * utility_2_multiplier

        assert self.game.current_player == player_1
        assert player_1.pending_action.action_type == PendingAction.Types.PAY_RENT  # type: ignore[union-attr]
        assert player_1.pending_action.action_data.get("rent") == expected_rent

        self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "accept")
        self._refresh_game_and_players()

        assert player_1.cash == player_1_cash_before - expected_rent
        assert self.game.current_player == player_2
        assert player_2.pending_action.action_type == PendingAction.Types.ROLL_DICE


@pytest.mark.django_db
class TestTax:
    monopoly_service: ClassicMonopolyService
    game: Game
    player_1: Player
    player_2: Player
    player_3: Player

    def setup_method(self, method):
        PopulateDatabaseCommand().handle()

    def _refresh_game_and_players(self):
        """Refresh game and all players from DB"""
        self.game.refresh_from_db()
        for player in self.players:
            player.refresh_from_db()

    def _create_game(self, players: int):
        self.tg_users = mock_data.create_telegram_users(players, synthetic=True)
        self.monopoly_service = get_service_by_name("classic")  # type: ignore[assignment]
        self.game = self.monopoly_service.create_game(self.tg_users[0], players)

        for i in range(1, players):
            player, _ = self.monopoly_service.join_game(self.game.uuid, self.tg_users[i])

        game_players = self.game.players.all()
        self.players = list(game_players)
        self._refresh_game_and_players()

    @pytest.mark.parametrize(
        ("should_roll_double", "should_have_enough_money"),
        [
            (False, True),
            (True, True),
            (False, True),
            (False, True),
            (False, False),
        ],
        ids=[
            "no_double_enough_money_1",
            "double_enough_money",
            "no_double_enough_money_2",
            "no_double_enough_money_3",
            "no_double_not_enough_money",
        ],
    )
    @no_type_check
    def test_landing_on_tax(self, should_roll_double, should_have_enough_money):
        self._create_game(2)
        player_1: Player = self.players[0]
        player_2: Player = self.players[1]
        player_1_cash_before = player_1.cash

        if not should_have_enough_money:
            player_1.cash = 1
            player_1.save()

        tax = Tax.objects.filter(board_config=self.game.board_config).first()
        dice_values = [tax.position - 1, 1]

        if should_roll_double:
            player_1.position = (player_1.position - tax.position) % self.game.board_config.tiles.count()
            player_1.save()
            dice_values = [tax.position] * 2

        with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=dice_values):
            game_frame = self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "roll_dice")

        self._refresh_game_and_players()

        assert self.game.current_player == player_1
        assert player_1.pending_action.action_type == PendingAction.Types.PAY_TAX

        if not should_have_enough_money:
            with pytest.raises(GameException):
                self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "accept")
        else:
            self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "accept")

        self._refresh_game_and_players()
        if should_have_enough_money:
            assert player_1.cash == player_1_cash_before - 100

        if should_roll_double:
            assert self.game.current_player == player_1
            assert player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE
        else:
            if not should_have_enough_money:
                assert self.game.current_player == player_1
                assert player_1.pending_action.action_type == PendingAction.Types.PAY_TAX
            else:
                assert self.game.current_player == player_2
                assert player_2.pending_action.action_type == PendingAction.Types.ROLL_DICE


@pytest.mark.django_db
class TestCasino:
    monopoly_service: ClassicMonopolyService
    game: Game
    player_1: Player
    player_2: Player
    player_3: Player

    def setup_method(self, method):
        PopulateDatabaseCommand().handle()

    def _refresh_game_and_players(self):
        """Refresh game and all players from DB"""
        self.game.refresh_from_db()
        for player in self.players:
            player.refresh_from_db()

    def _create_game(self, players: int):
        self.tg_users = mock_data.create_telegram_users(players, synthetic=True)
        self.monopoly_service = get_service_by_name("classic")  # type: ignore[assignment]
        self.game = self.monopoly_service.create_game(self.tg_users[0], players)

        for i in range(1, players):
            player, _ = self.monopoly_service.join_game(self.game.uuid, self.tg_users[i])

        game_players = self.game.players.all()
        self.players = list(game_players)
        self._refresh_game_and_players()

    @pytest.mark.parametrize(
        ("should_win", "should_have_enough_money", "should_roll_double"),
        [
            (False, False, False),
            (True, True, False),
            (True, True, True),
            (False, True, False),
            (False, True, True),
        ],
    )
    @no_type_check
    def test_landing_on_casino(self, should_win, should_roll_double, should_have_enough_money):
        self._create_game(2)
        player_1: Player = self.players[0]
        player_2: Player = self.players[1]
        player_1_cash_before = player_1.cash

        if not should_have_enough_money:
            player_1.cash = 1
            player_1.save()

        casino = Casino.objects.filter(board_config=self.game.board_config).first()
        dice_values = [casino.position - 1, 1]

        if should_roll_double:
            player_1.position = (player_1.position - casino.position) % self.game.board_config.tiles.count()
            player_1.save()
            dice_values = [casino.position] * 2

        with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=dice_values):
            game_frame = self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "roll_dice")

        self._refresh_game_and_players()

        if not should_have_enough_money:
            assert player_1.pending_action is None
            assert self.game.current_player == player_2
            return

        assert self.game.current_player == player_1
        assert player_1.pending_action.action_type == PendingAction.Types.IN_CASINO
        assert player_1.pending_action.action_data.get("available_bets") is not None

        with patch("game.services.ClassicMonopolyService._flip_coin_value", return_value=should_win):
            self.monopoly_service.process_game_action(
                self.game.uuid, player_1.pk, ActionCommand(action="accept", bet=10)
            )
        self._refresh_game_and_players()

        if should_win:
            assert player_1.cash == player_1_cash_before + 10
        else:
            assert player_1.cash == player_1_cash_before - 10

        if should_roll_double:
            assert self.game.current_player == player_1
            assert player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE
        else:
            assert self.game.current_player == player_2
            assert player_2.pending_action.action_type == PendingAction.Types.ROLL_DICE

    @pytest.mark.parametrize(("should_roll_double"), [(False,), (True,)])
    @no_type_check
    def test_landing_on_casino_reject(self, should_roll_double):
        self._create_game(2)
        player_1: Player = self.players[0]
        player_2: Player = self.players[1]

        casino = Casino.objects.filter(board_config=self.game.board_config).first()
        dice_values = [casino.position - 1, 1]

        if should_roll_double:
            player_1.position = (player_1.position - casino.position) % self.game.board_config.tiles.count()
            player_1.save()
            dice_values = [casino.position] * 2

        with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=dice_values):
            game_frame = self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "roll_dice")

        self._refresh_game_and_players()

        assert self.game.current_player == player_1
        assert player_1.pending_action.action_type == PendingAction.Types.IN_CASINO
        assert player_1.pending_action.action_data.get("available_bets") is not None

        self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, ActionCommand(action="reject"))
        self._refresh_game_and_players()

        if should_roll_double:
            assert self.game.current_player == player_1
            assert player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE
        else:
            assert self.game.current_player == player_2
            assert player_2.pending_action.action_type == PendingAction.Types.ROLL_DICE


@pytest.mark.django_db
class TestImprovingTiles:
    monopoly_service: ClassicMonopolyService
    game: Game
    player_1: Player
    player_2: Player
    player_3: Player

    def setup_method(self, method):
        PopulateDatabaseCommand().handle()

    def _refresh_game_and_players(self):
        """Refresh game and all players from DB"""
        self.game.refresh_from_db()
        for player in self.players:
            player.refresh_from_db()

    def _create_game(self, players: int):
        self.tg_users = mock_data.create_telegram_users(players, synthetic=True)
        self.monopoly_service = get_service_by_name("classic")  # type: ignore[assignment]
        self.game = self.monopoly_service.create_game(self.tg_users[0], players)

        for i in range(1, players):
            player, _ = self.monopoly_service.join_game(self.game.uuid, self.tg_users[i])

        game_players = self.game.players.all()
        self.players = list(game_players)
        self._refresh_game_and_players()

    @pytest.mark.parametrize(
        ("select_group_with_num_tiles", "properties_lvl", "idx_to_improve", "should_succeed", "enough_money"),
        [
            # Test success with 2 properties
            (2, (0, 0), 1, (True, None), True),
            # Test not enough money
            (2, (0, 0), 1, (False, None), False),
            # Test does not own entire group with 2 properties
            (2, (0,), 0, (False, "You must own entire group"), True),
            # Test does not own entire group with 3 properties
            (3, (0, 0), 0, (False, "You must own entire group"), True),
            # Test success with 3 properties
            (3, (0, 0, 0), 1, (True, None), True),
            # Test if improves unevenly with 3 properties
            (3, (1, 1, 0), 0, (False, "You must improve evenly"), True),
            # Test if improves unevenly with 2 properties
            (2, (1, 0), 0, (False, "You must improve evenly"), True),
            # Test if improves more then 5
            (2, (5, 5), 0, (False, "You can't improve to more then 5"), True),
        ],
    )
    @no_type_check
    def test_improving_property(
        self, select_group_with_num_tiles, properties_lvl, idx_to_improve, should_succeed, enough_money
    ):
        self._create_game(2)
        player_1: Player = self.players[0]
        player_2: Player = self.players[1]

        if not enough_money:
            player_1.cash = 1
            player_1.save()

        player_1_cash_before = player_1.cash

        pg = (
            PropertyGroup.objects.annotate(num_properties=Count("properties"))
            .filter(num_properties=select_group_with_num_tiles)
            .first()
        )

        all_properties = pg.properties.all()
        property_to_improve: Property = all_properties[idx_to_improve]
        ownerships = []

        zipped_properties_and_lvls = zip(all_properties, properties_lvl, strict=False)

        for p, lvl in zipped_properties_and_lvls:
            ownership = Ownership.objects.create(game=self.game, player=player_1, tile=p, houses=lvl)
            ownerships.append(ownership)

        if not enough_money:
            with pytest.raises(GameException, match=r"^You don't have enough money$"):
                game_frame = self.monopoly_service.process_game_action(
                    self.game.uuid,
                    player_1.pk,
                    ActionCommand(action="improve", property_pos=property_to_improve.position),
                )
            assert player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE
            assert self.game.current_player == player_1
            return
        else:
            should_succeed, reason = should_succeed
            if not should_succeed:
                with pytest.raises(GameException, match=rf"^{reason}$"):
                    game_frame = self.monopoly_service.process_game_action(
                        self.game.uuid,
                        player_1.pk,
                        ActionCommand(action="improve", property_pos=property_to_improve.position),
                    )
                return

        game_frame = self.monopoly_service.process_game_action(
            self.game.uuid,
            player_1.pk,
            ActionCommand(action="improve", property_pos=property_to_improve.position),
        )

        self._refresh_game_and_players()
        list(map(lambda o: o.refresh_from_db(), ownerships))

        assert self.game.current_player == player_1
        assert player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE
        assert player_1.cash == player_1_cash_before - property_to_improve.house_price
        assert ownerships[idx_to_improve].houses == properties_lvl[idx_to_improve] + 1
        assert ownerships[idx_to_improve].calculate_rent() == getattr(
            property_to_improve, f"rent_with_{ownerships[idx_to_improve].houses}_houses"
        )

    @pytest.mark.parametrize(
        ("select_group_with_num_tiles", "properties_lvl", "idx_to_degrade", "should_succeed"),
        [
            # Test success with 2 properties
            (2, (1, 1), 1, (True, None)),
            # Test fail with 2 properties lower then 0
            (2, (0, 0), 1, (False, "You can't degrade below 0")),
            # Test fail with 2 properties no tile
            (2, (0,), 1, (False, "You don't own this tile")),
            # Test success with 3 properties
            (3, (1, 1, 1), 1, (True, None)),
            # Test uneven with 3 properties
            (3, (2, 1, 1), 1, (False, "You must degrade evenly")),
        ],
    )
    @no_type_check
    def test_degrade_property(
        self, select_group_with_num_tiles, properties_lvl, idx_to_degrade, should_succeed
    ):
        self._create_game(2)
        player_1: Player = self.players[0]
        player_2: Player = self.players[1]

        player_1_cash_before = player_1.cash

        pg = (
            PropertyGroup.objects.annotate(num_properties=Count("properties"))
            .filter(num_properties=select_group_with_num_tiles)
            .first()
        )

        all_properties = pg.properties.all()
        property_to_degrade: Property = all_properties[idx_to_degrade]
        ownerships = []

        zipped_properties_and_lvls = zip(all_properties, properties_lvl, strict=False)

        for p, lvl in zipped_properties_and_lvls:
            ownership = Ownership.objects.create(game=self.game, player=player_1, tile=p, houses=lvl)
            ownerships.append(ownership)

        should_succeed, reason = should_succeed
        if not should_succeed:
            with pytest.raises(GameException, match=rf"^{reason}$"):
                game_frame = self.monopoly_service.process_game_action(
                    self.game.uuid,
                    player_1.pk,
                    ActionCommand(action="degrade", property_pos=property_to_degrade.position),
                )
            return

        game_frame = self.monopoly_service.process_game_action(
            self.game.uuid,
            player_1.pk,
            ActionCommand(action="degrade", property_pos=property_to_degrade.position),
        )

        self._refresh_game_and_players()
        list(map(lambda o: o.refresh_from_db(), ownerships))

        assert self.game.current_player == player_1
        assert player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE
        assert player_1.cash == player_1_cash_before + property_to_degrade.house_price
        assert ownerships[idx_to_degrade].houses == properties_lvl[idx_to_degrade] - 1
        assert ownerships[idx_to_degrade].calculate_rent() == getattr(
            property_to_degrade,
            f"rent_with_{ownerships[idx_to_degrade].houses}_houses",
            property_to_degrade.rent,
        )


@pytest.mark.django_db
class TestChanceCards:
    monopoly_service: ClassicMonopolyService
    game: Game
    player_1: Player
    player_2: Player
    player_3: Player

    def setup_method(self, method):
        PopulateDatabaseCommand().handle()

    def _refresh_game_and_players(self):
        """Refresh game and all players from DB"""
        self.game.refresh_from_db()
        for player in self.players:
            player.refresh_from_db()

    def _create_game(self, players: int):
        self.tg_users = mock_data.create_telegram_users(players, synthetic=True)
        self.monopoly_service = get_service_by_name("classic")  # type: ignore[assignment]
        self.game = self.monopoly_service.create_game(self.tg_users[0], players)

        for i in range(1, players):
            player, _ = self.monopoly_service.join_game(self.game.uuid, self.tg_users[i])

        game_players = self.game.players.all()
        self.players = list(game_players)
        self._refresh_game_and_players()

    @pytest.mark.parametrize(
        ("card_action", "card_value", "should_be_owned", "num_players"),
        [
            (ChanceCard.Action.MOVE_TO, Start, None, 2),
            (ChanceCard.Action.MOVE_TO, Property, None, 2),
            (ChanceCard.Action.MOVE_TO, Utility, None, 2),
            (ChanceCard.Action.MOVE_RELATIVE, -3, None, 2),
            (ChanceCard.Action.MOVE_RELATIVE, 3, None, 2),
            (ChanceCard.Action.MOVE_TO_NEXT_UTILITY, Utility, True, 2),
            (ChanceCard.Action.MOVE_TO_NEXT_UTILITY, Utility, False, 2),
            (ChanceCard.Action.PAY_BANK, 100, None, 2),
            (ChanceCard.Action.COLLECT_BANK, 100, None, 2),
            (ChanceCard.Action.COLLECT_PLAYERS, 50, None, 3),
            (ChanceCard.Action.GO_TO_JAIL, None, None, 2),
            (ChanceCard.Action.REPAIRS, None, None, 2),
        ],
    )
    @no_type_check
    def test_landing_on_chance_card(self, card_action, card_value, should_be_owned: bool | None, num_players):
        self._create_game(num_players)
        player_1: Player = self.players[0]
        player_2: Player = self.players[1]
        player_1_cash_before = player_1.cash
        player_2_cash_before = player_2.cash

        if num_players == 3:
            player_3: Player = self.players[2]
            # Test with value that is less then chance card amount
            player_3.cash = card_value - 1
            player_3.save()
            player_3_cash_before = player_3.cash

        tile = Chance.objects.filter(board_config=self.game.board_config).first()
        # Dice values to land on Chance field
        dice_values = [tile.position, 0]

        if card_action == ChanceCard.Action.MOVE_TO:
            t = card_value.objects.first()

            forced_card = ChanceCard.objects.create(
                board_config=self.game.board_config,
                description="Temporary created card",
                action=card_action,
                position=t.position,
            )

            with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=dice_values):
                with patch(
                    "game.services.ClassicMonopolyService._get_random_chance_card",
                    return_value=forced_card,
                ):
                    game_frame = self.monopoly_service.process_game_action(
                        self.game.uuid, player_1.pk, "roll_dice"
                    )

            self._refresh_game_and_players()

            assert player_1.position == t.position

            if isinstance(card_value, Start):
                assert player_1.pending_action.action_type is None
            elif isinstance(card_value, (Property, Utility)):
                assert player_1.pending_action.action_type == PendingAction.Types.BUY_PROPERTY
        elif card_action == ChanceCard.Action.MOVE_RELATIVE:
            forced_card = ChanceCard.objects.create(
                board_config=self.game.board_config,
                description="Temporary created card",
                action=card_action,
                position_relative=card_value,
            )

            with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=dice_values):
                with patch(
                    "game.services.ClassicMonopolyService._get_random_chance_card",
                    return_value=forced_card,
                ):
                    game_frame = self.monopoly_service.process_game_action(
                        self.game.uuid, player_1.pk, "roll_dice"
                    )

            self._refresh_game_and_players()
            assert player_1.position == (sum(dice_values) + card_value) % 40
        elif card_action == ChanceCard.Action.MOVE_TO_NEXT_UTILITY:
            next_utility = player_1.get_next_utility()
            if should_be_owned:
                self.monopoly_service._buy_tile(self.game, player_2, next_utility, 0)

            forced_card = ChanceCard.objects.create(
                board_config=self.game.board_config,
                description="Temporary created card",
                action=card_action,
            )

            with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=dice_values):
                with patch(
                    "game.services.ClassicMonopolyService._get_random_chance_card",
                    return_value=forced_card,
                ):
                    game_frame = self.monopoly_service.process_game_action(
                        self.game.uuid, player_1.pk, "roll_dice"
                    )

            self._refresh_game_and_players()
            assert player_1.position == next_utility.position
            if should_be_owned:
                assert player_1.pending_action.action_type == PendingAction.Types.PAY_RENT
            else:
                assert player_1.pending_action.action_type == PendingAction.Types.BUY_PROPERTY
        elif card_action == ChanceCard.Action.PAY_BANK:
            forced_card = ChanceCard.objects.create(
                board_config=self.game.board_config,
                description="Temporary created card",
                action=card_action,
                amount=card_value,
            )

            with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=dice_values):
                with patch(
                    "game.services.ClassicMonopolyService._get_random_chance_card",
                    return_value=forced_card,
                ):
                    self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "roll_dice")

            self._refresh_game_and_players()
            assert player_1.position == sum(dice_values)
            assert player_1.pending_action.action_type == PendingAction.Types.PAY_TAX

            self.monopoly_service.process_game_action(
                self.game.uuid, player_1.pk, ActionCommand(action="accept")
            )
            self._refresh_game_and_players()
            assert player_1.cash == player_1_cash_before - forced_card.amount
            assert player_1.pending_action is None
            assert player_2.pending_action.action_type == PendingAction.Types.ROLL_DICE
        elif card_action == ChanceCard.Action.COLLECT_BANK:
            forced_card = ChanceCard.objects.create(
                board_config=self.game.board_config,
                description="Temporary created card",
                action=card_action,
                amount=card_value,
            )

            with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=dice_values):
                with patch(
                    "game.services.ClassicMonopolyService._get_random_chance_card",
                    return_value=forced_card,
                ):
                    self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "roll_dice")

            self._refresh_game_and_players()
            assert player_1.position == sum(dice_values)
            assert player_1.pending_action is None
            assert player_1.cash == player_1_cash_before + forced_card.amount
            assert player_2.pending_action.action_type == PendingAction.Types.ROLL_DICE
        elif card_action == ChanceCard.Action.COLLECT_PLAYERS:
            forced_card = ChanceCard.objects.create(
                board_config=self.game.board_config,
                description="Temporary created card",
                action=card_action,
                amount=card_value,
            )

            with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=dice_values):
                with patch(
                    "game.services.ClassicMonopolyService._get_random_chance_card",
                    return_value=forced_card,
                ):
                    self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "roll_dice")

            self._refresh_game_and_players()
            assert player_1.position == sum(dice_values)
            assert player_1.pending_action is None
            # assert player_1.cash == player_1_cash_before + forced_card.amount * (num_players - 1)
            assert player_2.cash == player_2_cash_before - forced_card.amount
            assert player_3.cash == 0
            assert player_2.pending_action.action_type == PendingAction.Types.ROLL_DICE
        elif card_action == ChanceCard.Action.GO_TO_JAIL:
            forced_card = ChanceCard.objects.create(
                board_config=self.game.board_config,
                description="Temporary created card",
                action=card_action,
            )

            with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=dice_values):
                with patch(
                    "game.services.ClassicMonopolyService._get_random_chance_card",
                    return_value=forced_card,
                ):
                    self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "roll_dice")

            self._refresh_game_and_players()
            assert player_1.position == Jail.objects.get().position
            assert player_1.in_jail is True
            assert player_1.jail_turns == 0
            assert player_1.pending_action is None
            assert player_2.pending_action.action_type == PendingAction.Types.ROLL_DICE
        elif card_action == ChanceCard.Action.REPAIRS:
            forced_card = ChanceCard.objects.create(
                board_config=self.game.board_config,
                description="Temporary created card",
                action=card_action,
            )

            count_of_houses = 0

            for i in range(2):
                p = Property.objects.all()[i]
                self.monopoly_service._buy_tile(self.game, player_1, p, 0)
                o = Ownership.objects.get(player=player_1, tile=p)
                time_to_improve = 1
                if i == 1:
                    time_to_improve = 2
                for _ in range(time_to_improve):
                    count_of_houses += 1
                    self.monopoly_service._improve_ownership(self.game, player_1, o, 0)

            with patch("game.services.ClassicMonopolyService._roll_dice_values", return_value=dice_values):
                with patch(
                    "game.services.ClassicMonopolyService._get_random_chance_card",
                    return_value=forced_card,
                ):
                    self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "roll_dice")

            self._refresh_game_and_players()
            assert player_1.position == sum(dice_values)
            assert player_1.pending_action.action_type == PendingAction.Types.PAY_REPAIRS
            extra_data = schemas.PayTaxData(**player_1.pending_action.action_data)
            assert extra_data.amount == count_of_houses * 50

            self.monopoly_service.process_game_action(self.game.uuid, player_1.pk, "accept")
            self._refresh_game_and_players()

            assert player_1.cash == player_1_cash_before - extra_data.amount
            assert player_1.pending_action is None
            assert player_2.pending_action.action_type == PendingAction.Types.ROLL_DICE


@pytest.mark.django_db
class TestTrade:
    monopoly_service: ClassicMonopolyService
    game: Game
    player_1: Player
    player_2: Player
    property_1: Property
    property_2: Property

    def setup_method(self, method):
        PopulateDatabaseCommand().handle()
        self._create_game(2)
        self.player_1 = self.players[0]
        self.player_2 = self.players[1]

        self.property_1 = Property.objects.filter(board_config=self.game.board_config)[0]
        self.property_2 = Property.objects.filter(board_config=self.game.board_config)[1]

        self.monopoly_service._buy_tile(self.game, self.player_1, self.property_1, 0)
        self.monopoly_service._buy_tile(self.game, self.player_2, self.property_2, 0)

    def _refresh_game_and_players(self):
        """Refresh game and all players from DB"""
        self.game.refresh_from_db()
        for player in self.players:
            player.refresh_from_db()

    def _create_game(self, players: int):
        self.tg_users = mock_data.create_telegram_users(players, synthetic=True)
        self.monopoly_service = get_service_by_name("classic")  # type: ignore[assignment]
        self.game = self.monopoly_service.create_game(self.tg_users[0], players)

        for i in range(1, players):
            player, _ = self.monopoly_service.join_game(self.game.uuid, self.tg_users[i])

        game_players = self.game.players.all()
        self.players = list(game_players)
        self._refresh_game_and_players()

    @pytest.mark.parametrize(
        ("to_player", "should_accept", "excpected_error_msg"),
        [
            (2, True, None),
            (2, False, None),
            (3, True, "Could not find player for trade"),
        ],
    )
    @no_type_check
    def test_trade_cash_for_property(self, to_player, should_accept, excpected_error_msg):
        player_1_cash_before = self.player_1.cash
        player_2_cash_before = self.player_2.cash
        player_1_ownerships_before = self.player_1.ownerships.count()
        player_2_ownerships_before = self.player_2.ownerships.count()

        offer = {"cash": 400, "tile_ids": []}
        request = {"cash": 0, "tile_ids": [self.property_2.pk]}

        if excpected_error_msg:
            with pytest.raises(GameException, match=rf"^{excpected_error_msg}$"):
                self.monopoly_service.process_game_action(
                    self.game.uuid,
                    self.player_1.pk,
                    ActionCommand(action="start_trade", to_player=to_player, offer=offer, request=request),
                )
            return
        else:
            game_frame = self.monopoly_service.process_game_action(
                self.game.uuid,
                self.player_1.pk,
                ActionCommand(action="start_trade", to_player=to_player, offer=offer, request=request),
            )
        self._refresh_game_and_players()

        assert self.game.turn == 1
        assert self.game.current_player == self.player_2
        assert self.player_2.pending_action.action_type == PendingAction.Types.IN_TRADE
        assert game_frame["game"]["players"][1]["pending_action"]["action_data"]["offer"] == offer
        assert game_frame["game"]["players"][1]["pending_action"]["action_data"]["request"] == request

        if should_accept:
            self.monopoly_service.process_game_action(
                self.game.uuid, self.player_2.pk, ActionCommand(action="accept")
            )
            self._refresh_game_and_players()
            assert self.game.turn == 1
            assert self.game.current_player == self.player_1
            assert self.player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE
            assert self.player_2.pending_action is None
            assert self.player_1.cash == player_1_cash_before + -offer["cash"] + request["cash"]
            assert self.player_2.cash == player_2_cash_before + offer["cash"] - request["cash"]
            assert self.player_1.ownerships.count() == player_1_ownerships_before - len(
                offer["tile_ids"]
            ) + len(request["tile_ids"])
            assert self.player_2.ownerships.count() == player_2_ownerships_before + len(
                offer["tile_ids"]
            ) - len(request["tile_ids"])
        else:
            self.monopoly_service.process_game_action(
                self.game.uuid, self.player_2.pk, ActionCommand(action="reject")
            )
            self._refresh_game_and_players()
            assert self.game.turn == 1
            assert self.game.current_player == self.player_1
            assert self.player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE
            assert self.player_2.pending_action is None
            assert self.player_1.cash == player_1_cash_before
            assert self.player_2.cash == player_2_cash_before
            assert self.player_1.ownerships.count() == player_1_ownerships_before
            assert self.player_2.ownerships.count() == player_2_ownerships_before

    @pytest.mark.parametrize(
        ("to_player", "should_accept"),
        [
            (2, True),
            (2, False),
        ],
    )
    @no_type_check
    def test_trade_property_for_property(self, to_player, should_accept):
        player_1_cash_before = self.player_1.cash
        player_2_cash_before = self.player_2.cash
        player_1_ownerships_before = self.player_1.ownerships.count()
        player_2_ownerships_before = self.player_2.ownerships.count()

        offer = {"cash": 0, "tile_ids": [self.property_1.pk]}
        request = {"cash": 0, "tile_ids": [self.property_2.pk]}

        game_frame = self.monopoly_service.process_game_action(
            self.game.uuid,
            self.player_1.pk,
            ActionCommand(action="start_trade", to_player=to_player, offer=offer, request=request),
        )
        self._refresh_game_and_players()

        assert self.game.turn == 1
        assert self.game.current_player == self.player_2
        assert self.player_2.pending_action.action_type == PendingAction.Types.IN_TRADE
        assert game_frame["game"]["players"][1]["pending_action"]["action_data"]["offer"] == offer
        assert game_frame["game"]["players"][1]["pending_action"]["action_data"]["request"] == request

        if should_accept:
            self.monopoly_service.process_game_action(
                self.game.uuid, self.player_2.pk, ActionCommand(action="accept")
            )
            self._refresh_game_and_players()
            assert self.game.turn == 1
            assert self.game.current_player == self.player_1
            assert self.player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE
            assert self.player_2.pending_action is None
            assert self.player_1.cash == player_1_cash_before + -offer["cash"] + request["cash"]
            assert self.player_2.cash == player_2_cash_before + offer["cash"] - request["cash"]
            assert self.player_1.ownerships.count() == player_1_ownerships_before - len(
                offer["tile_ids"]
            ) + len(request["tile_ids"])
            assert self.player_2.ownerships.count() == player_2_ownerships_before + len(
                offer["tile_ids"]
            ) - len(request["tile_ids"])
        else:
            self.monopoly_service.process_game_action(
                self.game.uuid, self.player_2.pk, ActionCommand(action="reject")
            )
            self._refresh_game_and_players()
            assert self.game.turn == 1
            assert self.game.current_player == self.player_1
            assert self.player_1.pending_action.action_type == PendingAction.Types.ROLL_DICE
            assert self.player_2.pending_action is None
            assert self.player_1.cash == player_1_cash_before
            assert self.player_2.cash == player_2_cash_before
            assert self.player_1.ownerships.count() == player_1_ownerships_before
            assert self.player_2.ownerships.count() == player_2_ownerships_before

    # Errors
    @pytest.mark.parametrize(
        ("excpected_error_msg"),
        [
            ("Could not find player for trade"),
            ("You don't have that much money to offer"),
            ("You can't request that much money"),
            ("You don't own this tile to offer"),
            ("Other player don't own this tiles"),
            ("You can't trade with yourself"),
            ("You can't send an empty trade"),
        ],
    )
    @no_type_check
    def test_errors(self, excpected_error_msg):
        if excpected_error_msg == "You don't have that much money to offer":
            to_player = 2
            offer = {"cash": self.player_1.cash + 1, "tile_ids": []}
            request = {"cash": 0, "tile_ids": [self.property_2.pk]}
        elif excpected_error_msg == "Could not find player for trade":
            to_player = 22
            offer = {"cash": 40, "tile_ids": []}
            request = {"cash": 0, "tile_ids": [self.property_2.pk]}
        elif excpected_error_msg == "You can't request that much money":
            to_player = 2
            offer = {"cash": 0, "tile_ids": []}
            request = {"cash": self.player_2.cash + 1, "tile_ids": [self.property_2.pk]}
        elif excpected_error_msg == "You don't own this tile to offer":
            to_player = 2
            # Property 2 is property owned by player 2
            offer = {"cash": 0, "tile_ids": [self.property_1.pk, self.property_2.pk]}
            request = {"cash": 10, "tile_ids": [self.property_2.pk]}
        elif excpected_error_msg == "Other player don't own this tiles":
            to_player = 2
            offer = {"cash": 0, "tile_ids": [self.property_1.pk]}
            # Property 1 is property owned by player 1
            request = {"cash": 10, "tile_ids": [self.property_2.pk, self.property_1.pk]}
        elif excpected_error_msg == "You can't trade with yourself":
            to_player = 1
            offer = {"cash": 0, "tile_ids": []}
            request = {"cash": 10, "tile_ids": [self.property_1.pk]}
        elif excpected_error_msg == "You can't send an empty trade":
            to_player = 2
            offer = {"cash": 0, "tile_ids": []}
            request = {"cash": 0, "tile_ids": []}

        with pytest.raises(GameException, match=rf"^{excpected_error_msg}$"):
            self.monopoly_service.process_game_action(
                self.game.uuid,
                self.player_1.pk,
                ActionCommand(action="start_trade", to_player=to_player, offer=offer, request=request),
            )
        self._refresh_game_and_players()

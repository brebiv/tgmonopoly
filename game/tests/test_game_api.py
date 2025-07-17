import pytest
import math
from unittest.mock import patch
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from django.db import IntegrityError

from tgmonopoly.asgi import application
from game.management.commands.populate_database import (
    Command as PopulateDatabaseCommand,
)
from game.models import PendingAction, BoardConfig, Game, Player, Property, Jail, Police, Ownership, GameEvent
from game.services import get_service_by_name, ClassicMonopolyService
from game.exceptions import GameException
from . import BaseApiTestCase, test_data


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

        ws_url = f"/ws/game/{self.game.uuid}/?" + test_data.TG_INIT_DATA_RAW_LIST[0]
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

        await communicator.send_to("roll_dice")
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

        ws_url = f"/ws/game/{self.game.uuid}/?" + test_data.TG_INIT_DATA_RAW_LIST[1]
        communicator = WebsocketCommunicator(application, ws_url)
        connected, _ = await communicator.connect()

        self.assertTrue(connected)
        game_frame = await communicator.receive_json_from()

        await communicator.send_to("roll_dice")
        game_frame = await communicator.receive_json_from()
        await self._refresh_game_and_players_async()
        frame_type = game_frame["type"]

        self.assertEqual(frame_type, "game.error")
        self.assertIsNotNone(game_frame.get("msg"))

    @patch("game.services.ClassicMonopolyService._roll_dice_values")
    async def test_go_to_jail_because_of_doubles(self, mock_dice_values):
        dices_values = [2, 2]
        mock_dice_values.return_value = dices_values

        await database_sync_to_async(self._call_create_game)(2)

        ws_url = f"/ws/game/{self.game.uuid}/?" + test_data.TG_INIT_DATA_RAW_LIST[0]
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

        await communicator.send_to("roll_dice")

        for _ in range(4):
            game_frame = await communicator.receive_json_from()
            p1 = game_frame["game"]["players"][0]
            if p1["in_jail"]:
                break

            if p1["pending_action"]["action_type"] == PendingAction.Types.ROLL_DICE:
                await communicator.send_to("roll_dice")
            elif p1["pending_action"]["action_type"] == PendingAction.Types.BUY_PROPERTY:
                await communicator.send_to("accept")

        await player_1.arefresh_from_db()
        jail_tile = await database_sync_to_async(Jail.objects.get)(board_config_id=self.game.board_config_id)

        self.assertEqual(player_1.in_jail, True)
        self.assertEqual(player_1.position, jail_tile.position)

    @patch("game.services.ClassicMonopolyService._roll_dice_values")
    async def test_go_to_jail_from_police(self, mock_dice_values):
        await database_sync_to_async(self._call_create_game)(2)

        ws_url = f"/ws/game/{self.game.uuid}/?" + test_data.TG_INIT_DATA_RAW_LIST[0]
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

        await communicator.send_to("roll_dice")

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
        self.tg_users = test_data.create_telegram_users(players, synthetic=True)
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
        self.assertEqual(self.player_2.pending_action.action_data.get("property_id"), property.pk)
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
        self.assertEqual(self.player_2.pending_action.action_data.get("property_id"), property.pk)
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
        self.assertEqual(self.player_2.pending_action.action_data.get("property_id"), property.pk)
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
        self.tg_users = test_data.create_telegram_users(players, synthetic=True)
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
        assert self.player_2.pending_action.action_data.get("property_id") == property.pk
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
        self.tg_users = test_data.create_telegram_users(players, synthetic=True)
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
        self.tg_users = test_data.create_telegram_users(players, synthetic=True)
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

            with open("events", "w") as f:
                print(str(game_frame["events"]), file=f)

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

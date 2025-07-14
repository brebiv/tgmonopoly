from unittest.mock import patch
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async

from tgmonopoly.asgi import application
from game.models import PendingAction
from . import BaseApiTestCase, test_data


class CreateGameAPITest(BaseApiTestCase):
    def test_create_game(self):
        self._call_create_game(2, auto_join=False)

    def test_create_game_and_join_game(self):
        self._call_create_game(2)


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

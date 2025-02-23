from django.http import HttpResponse
from django.urls import reverse
from unittest.mock import patch
from copy import copy

from game.models import Player, GameEffect, Property, Ownership, PropertyGroup, ChanceCard, Tile
from game import config
from api.types import GameActionType, AuctionData, WSEventType, GameEventType
from api.serializers import PlayerSerializer
from api import services
from .utils import BaseAPITestCase


# Create your tests here.
class AuctionAPITest(BaseAPITestCase):
    def test_create_auction_2_players(self):
        self._create_game(2)
        self._start_game_and_begin_auction_flow()

    def test_create_auction_3_players(self):
        self._create_game(3)
        self._start_game_and_begin_auction_flow()
    
    def test_reject_auction_2_players(self):
        self._create_game(2)
        self._start_game_and_begin_auction_flow()

        self._refresh_game_and_players()
        player_1, player_2 = self.players

        self.assertEqual(player_2, self.game.current_player)

        self._post_game_action(self.client_2, GameActionType.REJECT)

        self._refresh_game_and_players()
        current_effect_2 = player_2.get_current_effect()

        self.assertEqual(self.game.current_player, player_2)
        self.assertEqual(current_effect_2.name, GameEffect.ROLL_DICE)

    def test_reject_auction_3_players(self):
        self._create_game(3)
        self._start_game_and_begin_auction_flow()

        self._refresh_game_and_players()
        player_1, player_2, player_3 = self.players

        self.assertEqual(player_2, self.game.current_player)

        self._post_game_action(self.client_2, GameActionType.REJECT)

        self._refresh_game_and_players()
        current_effect_2 = player_2.get_current_effect()
        current_effect_3 = player_3.get_current_effect()

        self.assertEqual(self.game.current_player.pk, player_3.pk)
        self.assertIsNone(current_effect_2)
        self.assertEqual(current_effect_3.name, GameEffect.IN_AUCTION)

        self._post_game_action(self.client_3, GameActionType.REJECT)

        self._refresh_game_and_players()
        current_effect_2 = player_2.get_current_effect()
        current_effect_3 = player_3.get_current_effect()

        self.assertEqual(self.game.current_player.pk, player_2.pk)
        self.assertEqual(current_effect_2.name, GameEffect.ROLL_DICE)
        self.assertIsNone(current_effect_3)

    def test_auction_2_players(self):
        self._create_game(2)
        self._start_game_and_begin_auction_flow()

        self._refresh_game_and_players()
        player_1, player_2 = self.players

        current_effect_1 = player_1.get_current_effect()
        current_effect_2 = player_2.get_current_effect()

        auction_data_raw = current_effect_2.effect_data
        auction_data = AuctionData.from_dict(auction_data_raw)
        auction_price = auction_data.current_auction_price

        self.assertEqual(auction_price, auction_data_raw['current_auction_price'])

        cash_before_winning = player_2.cash
        game_turn_before_winning = self.game.turn


        self.assertEqual(player_2.owned_properties.count(), 0)
        self.assertEqual(player_2, self.game.current_player)

        self._post_game_action(self.client_2, GameActionType.ACCEPT)

        self._refresh_game_and_players()

        current_effect_1 = player_1.get_current_effect()
        current_effect_2 = player_2.get_current_effect()

        self.assertEqual(self.game.turn, game_turn_before_winning + 1)
        self.assertEqual(self.game.current_player, player_2)
        self.assertIsNone(current_effect_1)
        self.assertEqual(current_effect_2.name, GameEffect.ROLL_DICE)
        self.assertEqual(player_1.owned_properties.count(), 0)
        self.assertEqual(player_2.owned_properties.count(), 1)
        self.assertEqual(player_2.cash, cash_before_winning - auction_price)

    def test_auction_3_players_2_turns(self):
        self._create_game(3)
        self._start_game_and_begin_auction_flow()

        self._refresh_game_and_players()
        player_1, player_2, player_3 = self.players

        current_effect_1 = player_1.get_current_effect()
        current_effect_2 = player_2.get_current_effect()
        current_effect_3 = player_3.get_current_effect()

        auction_data_raw = current_effect_2.effect_data
        auction_data = AuctionData.from_dict(auction_data_raw)
        auction_price_1 = auction_data.current_auction_price

        cash_before_winning = player_3.cash
        game_turn_before_winning = self.game.turn


        self.assertEqual(player_2.owned_properties.count(), 0)
        self.assertEqual(player_2, self.game.current_player)

        self._post_game_action(self.client_2, GameActionType.ACCEPT)

        self._refresh_game_and_players()

        current_effect_1 = player_1.get_current_effect()
        current_effect_2 = player_2.get_current_effect()
        current_effect_3 = player_3.get_current_effect()

        auction_data_raw = current_effect_3.effect_data
        auction_data = AuctionData.from_dict(auction_data_raw)
        auction_price_2 = auction_data.current_auction_price

        self.assertEqual(self.game.current_player, player_3)
        self.assertEqual(self.game.turn, game_turn_before_winning)
        self.assertIsNone(current_effect_1)
        self.assertIsNone(current_effect_2)
        self.assertEqual(current_effect_3.name, GameEffect.IN_AUCTION)
        self.assertEqual(auction_price_2, auction_price_1 + config.AUCTION_STEP)

        # Testing if it's not your turn
        self._post_game_action(self.client_2, GameActionType.ACCEPT, 400, "!ok", "Unknown action or it's not your turn")

        # Continuing
        self._post_game_action(self.client_3, GameActionType.ACCEPT)

        self._refresh_game_and_players()

        current_effect_1 = player_1.get_current_effect()
        current_effect_2 = player_2.get_current_effect()
        current_effect_3 = player_3.get_current_effect()

        auction_data_raw = current_effect_2.effect_data
        auction_data = AuctionData.from_dict(auction_data_raw)
        auction_price_3 = auction_data.current_auction_price

        self.assertEqual(self.game.current_player, player_2)
        self.assertEqual(self.game.turn, game_turn_before_winning)
        self.assertIsNone(current_effect_1)
        self.assertEqual(current_effect_2.name, GameEffect.IN_AUCTION)
        self.assertIsNone(current_effect_3)
        self.assertEqual(auction_price_3, auction_price_2 + config.AUCTION_STEP)

        self._post_game_action(self.client_2, GameActionType.REJECT)

        self._refresh_game_and_players()

        current_effect_1 = player_1.get_current_effect()
        current_effect_2 = player_2.get_current_effect()
        current_effect_3 = player_3.get_current_effect()

        self.assertEqual(self.game.turn, game_turn_before_winning + 1)
        self.assertEqual(self.game.current_player, player_2)
        self.assertIsNone(current_effect_1)
        self.assertIsNone(current_effect_3)
        self.assertEqual(current_effect_2.name, GameEffect.ROLL_DICE)
        self.assertEqual(player_1.owned_properties.count(), 0)
        self.assertEqual(player_2.owned_properties.count(), 0)
        self.assertEqual(player_3.owned_properties.count(), 1)
        self.assertGreaterEqual(player_2.cash, 0)
        self.assertEqual(player_3.cash, cash_before_winning - auction_price_3)

    def test_auction_3_players_3_turns(self):
        self._create_game(3)
        self._start_game_and_begin_auction_flow()

        self.game.refresh_from_db()
        player_1, player_2, player_3 = self.players

        current_effect_1 = player_1.get_current_effect()
        current_effect_2 = player_2.get_current_effect()
        current_effect_3 = player_3.get_current_effect()

        auction_data_raw = current_effect_2.effect_data
        auction_data = AuctionData.from_dict(auction_data_raw)
        auction_price_1 = auction_data.current_auction_price

        cash_before_winning = player_2.cash
        game_turn_before_winning = self.game.turn


        self.assertEqual(player_2.owned_properties.count(), 0)
        self.assertEqual(player_2, self.game.current_player)

        self._post_game_action(self.client_2, GameActionType.ACCEPT)

        self._refresh_game_and_players()

        current_effect_1 = player_1.get_current_effect()
        current_effect_2 = player_2.get_current_effect()
        current_effect_3 = player_3.get_current_effect()

        auction_data_raw = current_effect_3.effect_data
        auction_data = AuctionData.from_dict(auction_data_raw)
        auction_price_2 = auction_data.current_auction_price

        self.assertEqual(self.game.current_player, player_3)
        self.assertEqual(self.game.turn, game_turn_before_winning)
        self.assertIsNone(current_effect_1)
        self.assertIsNone(current_effect_2)
        self.assertEqual(current_effect_3.name, GameEffect.IN_AUCTION)
        self.assertEqual(auction_price_2, auction_price_1 + config.AUCTION_STEP)

        # Testing if it's not your turn
        self._post_game_action(self.client_2, GameActionType.ACCEPT, 400, "!ok", "Unknown action or it's not your turn")

        # Continuing
        self._post_game_action(self.client_3, GameActionType.ACCEPT)

        self._refresh_game_and_players()

        current_effect_1 = player_1.get_current_effect()
        current_effect_2 = player_2.get_current_effect()
        current_effect_3 = player_3.get_current_effect()

        auction_data_raw = current_effect_2.effect_data
        auction_data = AuctionData.from_dict(auction_data_raw)
        auction_price_3 = auction_data.current_auction_price

        self.assertEqual(self.game.current_player, player_2)
        self.assertEqual(self.game.turn, game_turn_before_winning)
        self.assertIsNone(current_effect_1)
        self.assertEqual(current_effect_2.name, GameEffect.IN_AUCTION)
        self.assertIsNone(current_effect_3)
        self.assertEqual(auction_price_3, auction_price_2 + config.AUCTION_STEP)

        self._post_game_action(self.client_2, GameActionType.ACCEPT)

        self._refresh_game_and_players()

        current_effect_1 = player_1.get_current_effect()
        current_effect_2 = player_2.get_current_effect()
        current_effect_3 = player_3.get_current_effect()

        auction_data_raw = current_effect_3.effect_data
        auction_data = AuctionData.from_dict(auction_data_raw)
        auction_price_4 = auction_data.current_auction_price

        self.assertEqual(self.game.turn, game_turn_before_winning)
        self.assertEqual(self.game.current_player, player_3)
        self.assertIsNone(current_effect_1)
        self.assertIsNone(current_effect_2)
        self.assertEqual(current_effect_3.name, GameEffect.IN_AUCTION)
        self.assertEqual(auction_price_4, auction_price_3 + config.AUCTION_STEP)

        # Last turn
        self._post_game_action(self.client_3, GameActionType.REJECT)
        self._refresh_game_and_players()

        current_effect_1 = player_1.get_current_effect()
        current_effect_2 = player_2.get_current_effect()
        current_effect_3 = player_3.get_current_effect()

        self.assertEqual(self.game.turn, game_turn_before_winning + 1)
        self.assertEqual(self.game.current_player, player_2)
        self.assertIsNone(current_effect_1)
        self.assertEqual(current_effect_2.name, GameEffect.ROLL_DICE)
        self.assertIsNone(current_effect_3)
        self.assertEqual(player_1.owned_properties.count(), 0)
        self.assertEqual(player_2.owned_properties.count(), 1)
        self.assertEqual(player_3.owned_properties.count(), 0)
        self.assertGreaterEqual(player_2.cash, 0)
        self.assertEqual(player_2.cash, cash_before_winning - auction_price_4)

    def test_not_enough_money_for_auction(self):
        self._create_game(num_players=2)
        self._start_game_and_begin_auction_flow()

        self._refresh_game_and_players()
        player_1, player_2 = self.players

        player_2.cash = 60
        player_2.save()

        self.assertEqual(player_2.owned_properties.count(), 0)
        self.assertEqual(player_2, self.game.current_player)

        self._post_game_action(self.client_2, GameActionType.ACCEPT, 400, "!ok", "Not enough money to accept auction")

    def test_reject_auction_with_double(self):
        self._create_game(2)
        self._start_game()

        dices_values = config.TEST_DICE_DOUBLE
        with patch('game.services.GameService._roll_dice_values', return_value=dices_values):
            response = self.client_1.post(
                reverse('game_action'),
                data={
                    'action': GameActionType.ROLL_DICE,
                    'game_uuid': self.game.uuid,
                }
            )
            self.assertEqual(response.status_code, 200)

        response = self.client_1.post(
            reverse('game_action'),
            data={
                'action': GameActionType.START_AUCTION,
                'game_uuid': self.game.uuid,
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')

        self._refresh_game_and_players()

        player_1, player_2, *_ = self.players

        # Testing effect data
        current_effect_2 = player_2.get_current_effect()
        effect_data = current_effect_2.effect_data

        started_by = effect_data['started_by']
        current_player_in_auction = effect_data['current_player_in_auction']
        players_participating_in_auction = effect_data['players_participating_in_auction']
        property = Property.objects.get(pk=effect_data['property'])

        self.assertNotEqual(self.game.current_player, player_1)
        self.assertEqual(current_effect_2.name, GameEffect.IN_AUCTION)
        self.assertEqual(started_by, player_1.pk)
        self.assertEqual(current_player_in_auction, player_2.pk)
        self.assertEqual(len(players_participating_in_auction), self.num_players - 1)
        self.assertNotIn(player_1.pk, players_participating_in_auction)
        self.assertEqual(current_effect_2.effect_data['current_auction_price'], property.price + config.AUCTION_STEP)

        resp = self._post_game_action(self.client_2, GameActionType.REJECT)
        self.assertEqual(resp.status_code, 200)

        self._refresh_game_and_players()
        self.assertEqual(self.game.current_player, player_1)


class TradingAPITest(BaseAPITestCase):
    enable_logging: bool

    def setUp(self):
        super().setUp()

        self.enable_logging = False
        self._create_game(2)

        self.player_1_ownership = Ownership.objects.create(
            game=self.game,
            player=self.players[0],
            property=Property.objects.get(board_space__position=1),
        )

        self._start_game()
        self._refresh_game_and_players()

    def _start_trade(
            self,
            from_player: Player,
            to_player: Player,
            cash_given: int = 0,
            cash_received: int = 0,
            ownerships: list[int] = [],
        ) -> HttpResponse:
        
        response = self._post_game_action(
            self.client_1,
            GameActionType.CREATE_TRADE,
            extra_data={
                "from_player": from_player.pk,
                "to_player": to_player.pk,
                "cash_given": cash_given,
                "cash_received": cash_received,
                "ownerships": ownerships
            },
            disable_asserts=True,
            enable_logging=self.enable_logging
        )

        return response

    def _start_trade_and_other_player_rejects(self, disable_assertions: bool = False) -> list[HttpResponse]:
        responses = []
        response = self._start_trade(
            from_player=self.players[0],
            to_player=self.players[1],
            cash_given=200,
            cash_received=100,
            ownerships=[
                self.player_1_ownership.pk
            ]
        )
        responses.append(response)

        self._refresh_game_and_players()
        current_effect_1 = self.players[0].get_current_effect()
        current_effect_2 = self.players[1].get_current_effect()

        if not disable_assertions:
            self.assertEqual(self.game.current_player, self.players[1])
            self.assertIsNone(current_effect_1)
            self.assertEqual(current_effect_2.name, GameEffect.IN_TRADE)

        response = self._post_game_action(self.client_2, GameActionType.REJECT, disable_asserts=disable_assertions)
        responses.append(response)

        self._refresh_game_and_players()
        current_effect_1 = self.players[0].get_current_effect()
        current_effect_2 = self.players[1].get_current_effect()

        if not disable_assertions:
            self.assertEqual(self.game.current_player, self.players[0])
            self.assertEqual(current_effect_1.name, GameEffect.ROLL_DICE)
            self.assertIsNone(current_effect_2)

        return responses

    def test_start_trade_success(self):
        self._start_trade(
            from_player=self.players[0],
            to_player=self.players[1],
            cash_given=200,
            cash_received=100,
            ownerships=[
                self.player_1_ownership.pk
            ]
        )

        self._refresh_game_and_players()
        current_effect_1 = self.players[0].get_current_effect()
        current_effect_2 = self.players[1].get_current_effect()

        self.assertEqual(self.game.current_player, self.players[1])
        self.assertIsNone(current_effect_1)
        self.assertEqual(current_effect_2.name, GameEffect.IN_TRADE)
    
    def test_start_trade_error_dont_have_property(self):
        response = self._start_trade(
            from_player=self.players[0],
            to_player=self.players[1],
            cash_given=200,
            cash_received=100,
            ownerships=[
                2 # Property with id 2 doesn't exist
            ]
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Could not find ownership')

    def test_giving_more_money_than_player_has(self):
        player_1_money = self.players[0].cash

        response = self._start_trade(
            from_player=self.players[0],
            to_player=self.players[1],
            cash_given=player_1_money + 10,
            cash_received=100,
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'You are giving more money than you have')

    def test_asking_more_money_than_player_has(self):
        player_1_money = self.players[0].cash
        player_2_money = self.players[1].cash

        response = self._start_trade(
            from_player=self.players[0],
            to_player=self.players[1],
            cash_given=player_1_money,
            cash_received=player_2_money + 1,
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "Other player doesn't have enough money to send")
    
    def test_reject_trade(self):
        self._start_trade_and_other_player_rejects()
    
    def test_that_just_giving_or_receiving_money_doesnt_work(self):
        cash_given = 200
        cash_received = 0

        response = self._start_trade(
            from_player=self.players[0],
            to_player=self.players[1],
            cash_given=cash_given,
            cash_received=cash_received,
            ownerships=[]
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "Invalid trade data")

        cash_given = 0
        cash_received = 100

        response = self._start_trade(
            from_player=self.players[0],
            to_player=self.players[1],
            cash_given=cash_given,
            cash_received=cash_received,
            ownerships=[]
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "Invalid trade data")

    def test_gifting_property(self):
        response = self._start_trade(
            from_player=self.players[0],
            to_player=self.players[1],
            cash_given=0,
            cash_received=0,
            ownerships=[
                self.player_1_ownership.pk
            ]
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "Invalid trade data")

    def test_accept_trade_with_everything(self):
        cash_given = 200
        cash_received = 100

        self._start_trade(
            from_player=self.players[0],
            to_player=self.players[1],
            cash_given=cash_given,
            cash_received=cash_received,
            ownerships=[
                self.player_1_ownership.pk
            ]
        )

        self._refresh_game_and_players()
        current_effect_1 = self.players[0].get_current_effect()
        current_effect_2 = self.players[1].get_current_effect()
        player_1_cash_before_trade = self.players[0].cash
        player_2_cash_before_trade = self.players[1].cash

        self.assertEqual(self.game.current_player, self.players[1])
        self.assertIsNone(current_effect_1)
        self.assertEqual(current_effect_2.name, GameEffect.IN_TRADE)
        self.assertEqual(self.players[0].owned_properties.count(), 1)

        self._post_game_action(self.client_2, GameActionType.ACCEPT)

        self._refresh_game_and_players()
        current_effect_1 = self.players[0].get_current_effect()
        current_effect_2 = self.players[1].get_current_effect()

        self.assertEqual(self.game.current_player, self.players[0])
        self.assertEqual(current_effect_1.name, GameEffect.ROLL_DICE)
        self.assertEqual(current_effect_1.effect_data['trade_count'], 1)
        self.assertEqual(current_effect_1.effect_data['trade_accepted'], True)
        self.assertIsNone(current_effect_2)
        self.assertEqual(self.players[0].owned_properties.count(), 0)
        self.assertEqual(self.players[1].owned_properties.count(), 1)
        self.assertEqual(self.players[1].owned_properties.first().property.pk, self.player_1_ownership.property.pk)
        self.assertEqual(self.players[0].cash, player_1_cash_before_trade + (cash_received - cash_given))
        self.assertEqual(self.players[1].cash, player_2_cash_before_trade + (cash_given - cash_received))

    def test_creating_more_than_max_trades(self):
        for i in range(config.MAX_TRADE_PROPOSALS + 1):
            responses = self._start_trade_and_other_player_rejects(disable_assertions=True)

            if i < config.MAX_TRADE_PROPOSALS:
                for response in responses:
                    self.assertEqual(response.status_code, 200)
                    current_effect = self.players[0].get_current_effect()
                    self.assertEqual(current_effect.effect_data['trade_count'], i + 1)
                    self.assertEqual(current_effect.effect_data['trade_accepted'], False)
            else:
                create_trade_response = responses[0]
                reject_trade_response = responses[1]

                self.assertEqual(create_trade_response.status_code, 400)
                self.assertEqual(create_trade_response.json()['error'], f"You can't create more than {config.MAX_TRADE_PROPOSALS} trades in one turn")
                self.assertEqual(reject_trade_response.status_code, 400)
                self.assertEqual(reject_trade_response.json()['error'], "Unknown action or it's not your turn")

    def test_if_trade_accepted_then_no_more_trades_in_this_turn(self):
        self.test_accept_trade_with_everything()

        response = self._start_trade(
            from_player=self.players[0],
            to_player=self.players[1],
            cash_given=100,
            cash_received=100,
            ownerships=[
                self.player_1_ownership.pk
            ]
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "You can't create more trades in this turn")
    
    @patch('game.services.GameService._roll_dice_values')
    def test_trade_counter_is_reset_next_turn(self, mock_roll_dice_values):
        dices_values = config.TEST_DICE_VALUES
        mock_roll_dice_values.return_value = dices_values
        self.test_creating_more_than_max_trades()
        resp = self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
        self.assertEqual(resp.status_code, 200)
        self._refresh_game_and_players()

        # Now player is in ask_buy state, testing that he can't send trade while in ask_buy
        responses = self._start_trade_and_other_player_rejects(disable_assertions=True)
        for response in responses:
            self.assertEqual(response.status_code, 400)
        
        # Resolving ask_buy effect
        resp = self._post_game_action(self.client_1, GameActionType.START_AUCTION)
        resp = self._post_game_action(self.client_2, GameActionType.REJECT)
        resp = self._post_game_action(self.client_2, GameActionType.ROLL_DICE)
        self._refresh_game_and_players()

        current_effect_1 = self.players[0].get_current_effect()
        current_effect_2 = self.players[1].get_current_effect()

        self.assertIsNone(current_effect_1)
        self.assertEqual(current_effect_2.name, GameEffect.ASK_BUY)
        self.assertEqual(current_effect_2.effect_data['trade_count'], 0)
        
        self._post_game_action(self.client_2, GameActionType.START_AUCTION)
        self._post_game_action(self.client_1, GameActionType.REJECT)

        self.test_creating_more_than_max_trades()

class DiceRollAPITest(BaseAPITestCase):
    def setUp(self):
        super().setUp()

        self.enable_logging = False
        self._create_game(2)

        self.player_1, self.player_2 = self.players

        self._start_game()
        self._refresh_game_and_players()

    @patch('game.services.GameService._roll_dice_values')
    async def test_first_turn(self, mock_roll_dice_values):
        dices_values = config.TEST_DICE_VALUES
        mock_roll_dice_values.return_value = dices_values

        communicator = self._get_ws_communicator(self.player_1)
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        message = await communicator.receive_json_from()
        self.assertEqual(WSEventType(message['type']), WSEventType.GAME_CONNECTED)

        self.assertEqual(self.game.turn, 1)
        self.assertEqual(self.game.current_player_id, self.player_1.pk)
        current_effect = await services.get_current_effect(self.player_1)
        self.assertEqual(current_effect.name, GameEffect.ROLL_DICE)

        resp = await self._post_game_action_async(self.client_1, GameActionType.ROLL_DICE)
        self.assertEqual(resp.status_code, 200)

        await self._refresh_game_and_players_async()

        message = await communicator.receive_json_from()
        players_data = message['players']

        self.assertEqual(WSEventType(message['type']), WSEventType.GAME_ACTION)
        players = [PlayerSerializer(data=player).initial_data for player in players_data]
        current_player = await services.get_player_by_id(self.game.current_player_id)
        test_dice_sum = sum(dices_values)

        for i, player in enumerate(players):
            self.assertEqual(player['id'], self.players[i].pk)
            self.assertEqual(player['cash'], config.STARTING_CASH)
            self.assertEqual(player['color'], self.players[i].color)
            self.assertEqual(player['in_jail'], False)
            self.assertEqual(player['jail_turns'], 0)
            if player['id'] == current_player.pk:
                self.assertEqual(player['position'], test_dice_sum)
                self.assertEqual(len(player['effects']), 1)
                current_effect = await services.get_current_effect(self.players[i])
                effect_from_gameframe = player['effects'][0]

                self.assertEqual(current_effect.name, GameEffect.ASK_BUY)
                self.assertEqual(effect_from_gameframe['name'], GameEffect.ASK_BUY)
                self.assertEqual(effect_from_gameframe['effect_data']['trade_count'], 0)
                self.assertEqual(effect_from_gameframe['effect_data']['trade_accepted'], False)
            else:
                self.assertEqual(player['position'], 0)
                self.assertEqual(player['effects'], [])
            self.assertEqual(player['status'], Player.PLAYING)
            self.assertEqual(player['move_backwards'], False)

        events = message['events']
        self.assertEqual(len(events), 2)
        self.assertEqual(WSEventType(events[0]['type']), WSEventType.GAME_ACTION)
        self.assertEqual(events[0]['action'], GameEventType.ROLL_DICE)
        self.assertEqual(events[0]['dices'], config.TEST_DICE_VALUES)

        self.assertEqual(WSEventType(events[1]['type']), WSEventType.GAME_ACTION)
        self.assertEqual(events[1]['action'], GameEventType.MOVE_PLAYER)
        self.assertEqual(events[1]['player'], self.player_1.pk)
        self.assertEqual(events[1]['position'], test_dice_sum)

    @patch('game.services.GameService._roll_dice_values')
    async def test_reject_buy_with_double(self, mock_roll_dice_values):
        dices_values = [3, 3]
        mock_roll_dice_values.return_value = dices_values

        communicator = self._get_ws_communicator(self.player_1)
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        message = await communicator.receive_json_from()
        self.assertEqual(WSEventType(message['type']), WSEventType.GAME_CONNECTED)

        self.assertEqual(self.game.turn, 1)
        self.assertEqual(self.game.current_player_id, self.player_1.pk)
        current_effect = await services.get_current_effect(self.player_1)
        self.assertEqual(current_effect.name, GameEffect.ROLL_DICE)

        resp = await self._post_game_action_async(self.client_1, GameActionType.ROLL_DICE)

        await self._refresh_game_and_players_async()

        message = await communicator.receive_json_from()
        players_data = message['players']

        self.assertEqual(WSEventType(message['type']), WSEventType.GAME_ACTION)
        players = [PlayerSerializer(data=player).initial_data for player in players_data]
        current_player = await services.get_player_by_id(self.game.current_player_id)
        test_dice_sum = sum(dices_values)

        for i, player in enumerate(players):
            self.assertEqual(player['id'], self.players[i].pk)
            self.assertEqual(player['cash'], config.STARTING_CASH)
            self.assertEqual(player['color'], self.players[i].color)
            self.assertEqual(player['in_jail'], False)
            self.assertEqual(player['jail_turns'], 0)
            if player['id'] == current_player.pk:
                self.assertEqual(player['position'], test_dice_sum)
                self.assertEqual(len(player['effects']), 1)
                current_effect = await services.get_current_effect(self.players[i])
                effect_from_gameframe = player['effects'][0]

                self.assertEqual(current_effect.name, GameEffect.ASK_BUY)
                self.assertEqual(effect_from_gameframe['name'], GameEffect.ASK_BUY)
                self.assertEqual(effect_from_gameframe['effect_data']['trade_count'], 0)
                self.assertEqual(effect_from_gameframe['effect_data']['trade_accepted'], False)
            else:
                self.assertEqual(player['position'], 0)
                self.assertEqual(player['effects'], [])
            self.assertEqual(player['status'], Player.PLAYING)
            self.assertEqual(player['move_backwards'], False)

        events = message['events']
        self.assertEqual(len(events), 2)
        self.assertEqual(WSEventType(events[0]['type']), WSEventType.GAME_ACTION)
        self.assertEqual(events[0]['action'], GameEventType.ROLL_DICE)
        self.assertEqual(events[0]['dices'], dices_values)

        self.assertEqual(WSEventType(events[1]['type']), WSEventType.GAME_ACTION)
        self.assertEqual(events[1]['action'], GameEventType.MOVE_PLAYER)
        self.assertEqual(events[1]['player'], self.player_1.pk)
        self.assertEqual(events[1]['position'], test_dice_sum)

        await self._post_game_action_async(self.client_1, GameActionType.START_AUCTION)
        await self._post_game_action_async(self.client_2, GameActionType.REJECT)
        await self._refresh_game_and_players_async()

        player_1 = await services.get_player_by_id(self.player_1.pk)
        player_2 = await services.get_player_by_id(self.player_2.pk)

        current_effect_1 = await services.get_current_effect(self.player_1)
        current_effect_2 = await services.get_current_effect(self.player_2)

        self.assertEqual(current_effect_1.name, GameEffect.ROLL_DICE)
        self.assertIsNone(current_effect_2)
    
    @patch('game.services.GameService._roll_dice_values')
    def test_max_doubles(self, mock_roll_dice_values):
        dices_values = [3, 3]
        mock_roll_dice_values.return_value = dices_values

        for i in range(config.MAX_DOUBLES + 1):
            self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
            self._refresh_game_and_players()

            current_effect_1 = self.player_1.get_current_effect()
            current_effect_2 = self.player_2.get_current_effect()

            if i == 0:
                self.assertEqual(current_effect_1.name, GameEffect.ASK_BUY)
            elif i == 1:
                self.assertEqual(current_effect_1.name, GameEffect.ASK_BUY)
            elif i == 2:
                self.assertEqual(current_effect_1.name, GameEffect.ASK_BUY)
            elif i == 3:
                self.assertEqual(self.player_1.in_jail, True)
                self.assertEqual(self.game.current_player, self.player_2)
                self.assertIsNone(current_effect_1)
                self.assertEqual(current_effect_2.name, GameEffect.ROLL_DICE)
                self.assertEqual(self.player_1.dobule_count, 0)

            if current_effect_1:
                if current_effect_1.name == GameEffect.ASK_BUY:
                    self._post_game_action(self.client_1, GameActionType.START_AUCTION)
                    self._post_game_action(self.client_2, GameActionType.REJECT)
                else:
                    raise Exception("Something went wrong with default test flow")
    
    @patch('game.services.GameService._roll_dice_values')
    def test_landing_on_tax(self, mock_roll_dice_values):
        dices_values = [3, 1]
        mock_roll_dice_values.return_value = dices_values

        player_1_cash_before_tax = self.players[0].cash

        self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
        self._refresh_game_and_players()

        current_effect_1 = self.player_1.get_current_effect()
        self.assertEqual(current_effect_1.name, GameEffect.PAY_BANK)
        self.assertEqual(current_effect_1.effect_data.get('amount'), config.TAX_AMOUNT)

        self._post_game_action(self.client_1, GameActionType.PAY)
        self._refresh_game_and_players()

        self.assertEqual(player_1_cash_before_tax - config.TAX_AMOUNT, self.player_1.cash)
        self.assertEqual(self.game.current_player, self.player_2)
        self.assertEqual(self.game.turn, 2)

    @patch('game.services.GameService._roll_dice_values')
    def test_landing_on_tax_not_enough_money(self, mock_roll_dice_values):
        dices_values = [3, 1]
        mock_roll_dice_values.return_value = dices_values

        self.player_1.cash = config.TAX_AMOUNT - 1
        self.player_1.save()

        self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
        self._refresh_game_and_players()

        current_effect_1 = self.player_1.get_current_effect()
        self.assertEqual(current_effect_1.name, GameEffect.PAY_BANK)
        self.assertEqual(current_effect_1.effect_data.get('amount'), config.TAX_AMOUNT)

        self._post_game_action(self.client_1, GameActionType.PAY, 400, "!ok", "You don't have enough cash to pay")
        self._refresh_game_and_players()

        self.assertEqual(self.game.current_player, self.player_1)
        self.assertEqual(self.game.turn, 1)

    @patch('game.services.GameService._roll_dice_values')
    def test_landing_on_tax_with_double(self, mock_roll_dice_values):
        dices_values = [2, 2]
        mock_roll_dice_values.return_value = dices_values

        player_1_cash_before_tax = self.players[0].cash

        self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
        self._refresh_game_and_players()

        current_effect_1 = self.player_1.get_current_effect()
        self.assertEqual(current_effect_1.name, GameEffect.PAY_BANK)
        self.assertEqual(current_effect_1.effect_data.get('amount'), config.TAX_AMOUNT)

        self._post_game_action(self.client_1, GameActionType.PAY)
        self._refresh_game_and_players()

        self.assertEqual(player_1_cash_before_tax - config.TAX_AMOUNT, self.player_1.cash)
        self.assertEqual(self.game.current_player, self.player_1)
        self.assertEqual(self.game.turn, 2)

    @patch('game.services.GameService._roll_dice_values')
    def test_langing_on_single_utility_2(self, mock_roll_dice_values):
        dices_values = [6, 6]
        mock_roll_dice_values.return_value = dices_values

        ownership = Ownership.objects.create(
            game=self.game,
            player=self.player_2,
            property = Property.objects.get(board_space__position=12),
        )

        self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
        self._refresh_game_and_players()

        current_effect_1 = self.player_1.get_current_effect()

        self.assertEqual(current_effect_1.name, GameEffect.PAY_RENT)
        self.assertEqual(current_effect_1.effect_data['rent'], sum(dices_values) * ownership.property.rent)

    @patch('game.services.GameService._roll_dice_values')
    def test_langing_on_monopoly_utility_2(self, mock_roll_dice_values):
        dices_values = [6, 6]
        mock_roll_dice_values.return_value = dices_values

        ownership = Ownership.objects.create(
            game=self.game,
            player=self.player_2,
            property = Property.objects.get(board_space__position=12),
        )

        ownership = Ownership.objects.create(
            game=self.game,
            player=self.player_2,
            property = Property.objects.get(board_space__position=28),
        )

        self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
        self._refresh_game_and_players()

        current_effect_1 = self.player_1.get_current_effect()

        self.assertEqual(current_effect_1.name, GameEffect.PAY_RENT)
        self.assertEqual(current_effect_1.effect_data['rent'], sum(dices_values) * ownership.property.rent * 2)

    @patch('game.services.GameService._roll_dice_values')
    def _test_utility_1_roll(self, num_utilities: int, mock_roll_dice_values):
        dices_values = [3, 2]
        mock_roll_dice_values.return_value = dices_values

        properties_to_buy = Property.objects.filter(group__name=PropertyGroup.UTILITIES_1)[:num_utilities]

        for property in properties_to_buy:
            ownership = Ownership.objects.create(
                game=self.game,
                player=self.player_2,
                property = property,
            )

        self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
        self._refresh_game_and_players()

        current_effect_1 = self.player_1.get_current_effect()

        self.assertEqual(current_effect_1.name, GameEffect.PAY_RENT)
        self.assertEqual(current_effect_1.effect_data['rent'], ownership.property.rent * num_utilities)

    def test_langing_on_single_utility_1(self):
        self._test_utility_1_roll(1)

    def test_langing_on_double_utility_1(self):
        self._test_utility_1_roll(2)

    def test_langing_on_triple_utility_1(self):
        self._test_utility_1_roll(3)

    def test_langing_on_quatro_utility_1(self):
        self._test_utility_1_roll(4)

    @patch('game.services.GameService._roll_dice_values')
    def test_ask_buy(self, mock_roll_dice_values):
        dices_values = [1, 2]
        mock_roll_dice_values.return_value = dices_values

        player_1_money_befor_ask_buy = self.player_1.cash

        self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
        self._refresh_game_and_players()

        current_effect_1 = self.player_1.get_current_effect()

        self.assertEqual(current_effect_1.name, GameEffect.ASK_BUY)

        self._post_game_action(self.client_1, GameActionType.BUY_PROPERTY)
        self._refresh_game_and_players()

        current_effect_1 = self.player_1.get_current_effect()
        current_effect_2 = self.player_2.get_current_effect()

        self.assertIsNone(current_effect_1)
        self.assertEqual(current_effect_2.name, GameEffect.ROLL_DICE)
        self.assertEqual(self.player_1.owned_properties.count(), 1)
        self.assertEqual(self.player_1.cash, player_1_money_befor_ask_buy - self.player_1.owned_properties.first().property.price)


    @patch('game.services.GameService._roll_dice_values')
    def test_ask_buy_not_enough_money(self, mock_roll_dice_values):
        dices_values = [1, 2]
        mock_roll_dice_values.return_value = dices_values

        self.player_1.cash = Property.objects.get(board_space__position=sum(dices_values)).price - 1
        self.player_1.save()

        self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
        self._refresh_game_and_players()

        current_effect_1 = self.player_1.get_current_effect()

        self.assertEqual(current_effect_1.name, GameEffect.ASK_BUY)

        self._post_game_action(self.client_1, GameActionType.BUY_PROPERTY, 400, "!ok", "You don't have enough cash to buy this property")
        self._refresh_game_and_players()

        current_effect_1 = self.player_1.get_current_effect()

        self.assertEqual(current_effect_1.name, GameEffect.ASK_BUY)
        self.assertEqual(self.player_1.owned_properties.count(), 0)

    @patch('game.services.GameService._roll_dice_values')
    def test_ask_buy_with_double(self, mock_roll_dice_values):
        dices_values = [3, 3]
        mock_roll_dice_values.return_value = dices_values

        player_1_money_befor_ask_buy = self.player_1.cash

        self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
        self._refresh_game_and_players()

        current_effect_1 = self.player_1.get_current_effect()

        self.assertEqual(current_effect_1.name, GameEffect.ASK_BUY)

        self._post_game_action(self.client_1, GameActionType.BUY_PROPERTY)
        self._refresh_game_and_players()

        current_effect_1 = self.player_1.get_current_effect()

        self.assertEqual(current_effect_1.name, GameEffect.ROLL_DICE)
        self.assertEqual(self.player_1.owned_properties.count(), 1)
        self.assertEqual(self.player_1.cash, player_1_money_befor_ask_buy - self.player_1.owned_properties.first().property.price)


class CasinoAPITest(BaseAPITestCase):
    def setUp(self):
        super().setUp()

        self.enable_logging = False
        self._create_game(2)

        self.player_1, self.player_2 = self.players

        self._start_game()
        self._refresh_game_and_players()

    @patch('game.services.GameService._roll_dice_values')
    def test_not_enough_money_for_casino(self, mock_roll_dice_values):
        dices_values = [10, 10]
        mock_roll_dice_values.return_value = dices_values

        self.player_1.cash = 1
        self.player_1.save()

        self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
        self._refresh_game_and_players()

        self.assertEqual(self.player_1.get_current_effect().name, GameEffect.IN_CASINO)

        extra_data = {
            'bet_amount': 10
        }
        
        self._post_game_action(self.client_1, GameActionType.ACCEPT, 400, "!ok", "You don't have enough cash", extra_data=extra_data)
        self._refresh_game_and_players()

    @patch('game.services.GameService._roll_dice_values')
    def test_winning_casino(self, mock_roll_dice_values):
        dices_values = [9, 11]
        mock_roll_dice_values.return_value = dices_values

        starting_cash = 50
        bet_amount = 10


        self.player_1.cash = starting_cash
        self.player_1.save()

        self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
        self._refresh_game_and_players()

        self.assertEqual(self.player_1.get_current_effect().name, GameEffect.IN_CASINO)

        extra_data = {
            'bet_amount': bet_amount
        }
        
        with patch('game.services.GameService._flip_coin_value', return_value=True):
            self._post_game_action(self.client_1, GameActionType.ACCEPT, extra_data=extra_data)
        
        self._refresh_game_and_players()

        self.assertEqual(self.player_1.cash, starting_cash + bet_amount)
        self.assertIsNone(self.player_1.get_current_effect())
        self.assertEqual(self.player_2.get_current_effect().name, GameEffect.ROLL_DICE)

    @patch('game.services.GameService._roll_dice_values')
    def test_winning_casino_with_dobule(self, mock_roll_dice_values):
        dices_values = [10, 10]
        mock_roll_dice_values.return_value = dices_values

        starting_cash = 50
        bet_amount = 10

        self.player_1.cash = starting_cash
        self.player_1.save()

        self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
        self._refresh_game_and_players()

        self.assertEqual(self.player_1.get_current_effect().name, GameEffect.IN_CASINO)

        extra_data = {
            'bet_amount': bet_amount
        }
        
        with patch('game.services.GameService._flip_coin_value', return_value=True):
            self._post_game_action(self.client_1, GameActionType.ACCEPT, extra_data=extra_data)
        
        self._refresh_game_and_players()

        self.assertEqual(self.player_1.cash, starting_cash + bet_amount)
        self.assertEqual(self.player_1.get_current_effect().name, GameEffect.ROLL_DICE)

    @patch('game.services.GameService._roll_dice_values')
    def test_losing_casino(self, mock_roll_dice_values):
        dices_values = [9, 11]
        mock_roll_dice_values.return_value = dices_values

        starting_cash = 50
        bet_amount = 10

        self.player_1.cash = starting_cash
        self.player_1.save()

        self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
        self._refresh_game_and_players()

        self.assertEqual(self.player_1.get_current_effect().name, GameEffect.IN_CASINO)

        extra_data = {
            'bet_amount': bet_amount
        }
        
        with patch('game.services.GameService._flip_coin_value', return_value=False):
            self._post_game_action(self.client_1, GameActionType.ACCEPT, extra_data=extra_data)
        
        self._refresh_game_and_players()

        self.assertEqual(self.player_1.cash, starting_cash - bet_amount)
        self.assertIsNone(self.player_1.get_current_effect())
        self.assertEqual(self.player_2.get_current_effect().name, GameEffect.ROLL_DICE)
        
    @patch('game.services.GameService._roll_dice_values')
    def test_losing_casino_with_double(self, mock_roll_dice_values):
        dices_values = [10, 10]
        mock_roll_dice_values.return_value = dices_values

        starting_cash = 50
        bet_amount = 10

        self.player_1.cash = starting_cash
        self.player_1.save()

        self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
        self._refresh_game_and_players()

        self.assertEqual(self.player_1.get_current_effect().name, GameEffect.IN_CASINO)

        extra_data = {
            'bet_amount': bet_amount
        }
        
        with patch('game.services.GameService._flip_coin_value', return_value=False):
            self._post_game_action(self.client_1, GameActionType.ACCEPT, extra_data=extra_data)
        
        self._refresh_game_and_players()

        self.assertEqual(self.player_1.cash, starting_cash - bet_amount)
        self.assertEqual(self.player_1.get_current_effect().name, GameEffect.ROLL_DICE)

    @patch('game.services.GameService._roll_dice_values')
    def test_reject_casino(self, mock_roll_dice_values):
        dices_values = [9, 11]
        mock_roll_dice_values.return_value = dices_values

        starting_cash = 50

        self.player_1.cash = starting_cash
        self.player_1.save()

        self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
        self._refresh_game_and_players()

        self.assertEqual(self.player_1.get_current_effect().name, GameEffect.IN_CASINO)

        
        self._post_game_action(self.client_1, GameActionType.REJECT)
        self._refresh_game_and_players()

        self.assertIsNone(self.player_1.get_current_effect())
        self.assertEqual(self.player_2.get_current_effect().name, GameEffect.ROLL_DICE)

    @patch('game.services.GameService._roll_dice_values')
    def test_reject_casino_with_double(self, mock_roll_dice_values):
        dices_values = [10, 10]
        mock_roll_dice_values.return_value = dices_values

        starting_cash = 50

        self.player_1.cash = starting_cash
        self.player_1.save()

        self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
        self._refresh_game_and_players()

        self.assertEqual(self.player_1.get_current_effect().name, GameEffect.IN_CASINO)
        
        self._post_game_action(self.client_1, GameActionType.REJECT)
        
        self._refresh_game_and_players()

        self.assertEqual(self.player_1.get_current_effect().name, GameEffect.ROLL_DICE)


class JailAPITest(BaseAPITestCase):
    def setUp(self):
        super().setUp()

        self.enable_logging = False
        self._create_game(2)

        self.player_1, self.player_2 = self.players

        self._start_game()
        self._refresh_game_and_players()


        # Getting player 1 into jail
        with patch('game.services.GameService._roll_dice_values', return_value=[9, 1]):
            self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
            self._refresh_game_and_players()

            self.assertEqual(self.player_1.in_jail, True)
            self.assertEqual(self.player_1.jail_turns, 0)
            self.assertEqual(self.player_2.get_current_effect().name, GameEffect.ROLL_DICE)
        
        # Player 2 will just go from start to start
        with patch('game.services.GameService._roll_dice_values', return_value=[39, 1]):
            self._post_game_action(self.client_2, GameActionType.ROLL_DICE)

    @patch('game.services.GameService._roll_dice_values')
    def test_getting_out_by_throwing_dice(self, mock_roll_dice_values):
        dices_values = [10, 10]
        mock_roll_dice_values.return_value = dices_values

        with patch('game.services.GameService._roll_dice_values', return_value=[9, 1]):
            self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
        
        self._refresh_game_and_players()
        self.assertEqual(self.player_1.in_jail, True)
        self.assertEqual(self.player_1.jail_turns, 1)
        
        # Moving player 2 to start
        with patch('game.services.GameService._roll_dice_values', return_value=[39, 1]):
            self._post_game_action(self.client_2, GameActionType.ROLL_DICE)
        
        with patch('game.services.GameService._roll_dice_values', return_value=[2, 2]):
            self._post_game_action(self.client_1, GameActionType.ROLL_DICE)        
            
        self._refresh_game_and_players()
        self.assertEqual(self.player_1.in_jail, False)
        self.assertEqual(self.player_1.jail_turns, 0)
        self.assertEqual(self.player_1.get_current_effect().name, GameEffect.ROLL_DICE)

    @patch('game.services.GameService._roll_dice_values')
    def test_getting_out_by_losing_all_attempts_and_paying_for_jail(self, mock_roll_dice_values):
        dices_values = [10, 10]
        mock_roll_dice_values.return_value = dices_values

        for i in range(config.MAXIMUM_JAIL_TURNS):
            with patch('game.services.GameService._roll_dice_values', return_value=[9, 1]):
                self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
            
            self._refresh_game_and_players()
            self.assertEqual(self.player_1.in_jail, True)
            self.assertEqual(self.player_1.jail_turns, i + 1)
            
            # Moving player 2 to start
            with patch('game.services.GameService._roll_dice_values', return_value=[39, 1]):
                self._post_game_action(self.client_2, GameActionType.ROLL_DICE)
        
        self._post_game_action(self.client_1, GameActionType.ROLL_DICE, 400, "!ok", "You can't roll dice anymore")
        self._post_game_action(self.client_1, GameActionType.PAY_FOR_PRISON)

        self._refresh_game_and_players()
        self.assertEqual(self.player_1.in_jail, False)
        self.assertEqual(self.player_1.jail_turns, 0)
        self.assertEqual(self.player_1.get_current_effect().name, GameEffect.ROLL_DICE)

    @patch('game.services.GameService._roll_dice_values')
    def test_not_enough_money_to_pay_for_jail(self, mock_roll_dice_values):
        dices_values = [10, 10]
        mock_roll_dice_values.return_value = dices_values

        self.player_1.cash = config.PRISON_PAY_AMOUNT - 1
        self.player_1.save()
        
        self._post_game_action(self.client_1, GameActionType.PAY_FOR_PRISON, 400, "!ok", "You don't have enough cash to pay for prison")

        self._refresh_game_and_players()
        self.assertEqual(self.player_1.in_jail, True)

class ChanceCardsAPITest(BaseAPITestCase):
    def setUp(self):
        super().setUp()

        self.enable_logging = False
        self._create_game(2)

        self.player_1, self.player_2 = self.players

        self._start_game()
        self._refresh_game_and_players()

    @patch('game.services.GameService._roll_dice_values')
    def test_move(self, mock_roll_dice_values):
        dices_values = [0, 2]
        mock_roll_dice_values.return_value = dices_values

        target_chance_card = ChanceCard.objects.get(title="Advance to Shell")

        with patch('game.models.ChanceCard.get_random_card', return_value=target_chance_card):
            self._post_game_action(self.client_1, GameActionType.ROLL_DICE)

        self._refresh_game_and_players()

        current_effect_1 = self.player_1.get_current_effect()
        target_tile = Tile.objects.get(position=target_chance_card.details['position'])

        self.assertEqual(current_effect_1.name, GameEffect.ASK_BUY)
        self.assertEqual(self.player_1.position, target_tile.position)

    @patch('game.services.GameService._roll_dice_values')
    def test_move_with_extra_money(self, mock_roll_dice_values):
        dices_values = [0, 2]
        mock_roll_dice_values.return_value = dices_values

        target_chance_card = ChanceCard.objects.get(title="Advance to Go")
        player_1_before = copy(self.player_1)

        with patch('game.models.ChanceCard.get_random_card', return_value=target_chance_card):
            self._post_game_action(self.client_1, GameActionType.ROLL_DICE)

        self._refresh_game_and_players()

        current_effect_1 = self.player_1.get_current_effect()
        target_tile = Tile.objects.get(position=target_chance_card.details['position'])

        self.assertIsNone(current_effect_1)
        self.assertEqual(self.player_1.position, target_tile.position)
        self.assertEqual(self.player_1.cash, player_1_before.cash + target_chance_card.details['amount'])

    @patch('game.services.GameService._roll_dice_values')
    def test_money_gain(self, mock_roll_dice_values):
        dices_values = [0, 2]
        mock_roll_dice_values.return_value = dices_values

        target_chance_card = ChanceCard.objects.get(title="You won beauty contest")
        player_1_before = copy(self.player_1)

        with patch('game.models.ChanceCard.get_random_card', return_value=target_chance_card):
            self._post_game_action(self.client_1, GameActionType.ROLL_DICE)

        self._refresh_game_and_players()

        self.assertIsNone(self.player_1.get_current_effect())
        self.assertEqual(self.player_1.cash, player_1_before.cash + target_chance_card.details['amount'])

    @patch('game.services.GameService._roll_dice_values')
    def test_go_to_jail(self, mock_roll_dice_values):
        dice_values = [0, 2]
        mock_roll_dice_values.return_value = dice_values

        target_chance_card = ChanceCard.objects.get(title="Go to Jail")

        with patch('game.models.ChanceCard.get_random_card', return_value=target_chance_card):
            self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
        
        self._refresh_game_and_players()

        current_effect_1 = self.player_1.get_current_effect()
        self.assertIsNone(current_effect_1)
        self.assertEqual(self.player_1.in_jail, True)
        self.assertEqual(self.player_1.jail_turns, 0)

    @patch('game.services.GameService._roll_dice_values')
    def test_move_backwards(self, mock_roll_dice_values):
        dice_values = [0, 2]
        mock_roll_dice_values.return_value = dice_values

        target_chance_card = ChanceCard.objects.get(title="Move backwards")

        with patch('game.models.ChanceCard.get_random_card', return_value=target_chance_card):
            self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
        
        self._refresh_game_and_players()

        # Moving player 2 to start
        with patch('game.services.GameService._roll_dice_values', return_value=[39, 1]):
            self._post_game_action(self.client_2, GameActionType.ROLL_DICE)
        
        self._refresh_game_and_players()

        player_1_before_move_backwards = copy(self.player_1)
        self.assertEqual(self.player_1.get_current_effect().name, GameEffect.ROLL_DICE)
        self.assertEqual(self.player_1.move_backwards, True)
        self.assertEqual(self.player_1.jail_turns, 0)

        self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
        self._refresh_game_and_players()

        self.assertIsNone(self.player_1.get_current_effect())
        self.assertEqual(self.player_1.move_backwards, False)
        self.assertEqual(self.player_1.position, player_1_before_move_backwards.position - sum(dice_values))

    @patch('game.services.GameService._roll_dice_values')
    def test_repairs(self, mock_roll_dice_values):
        dice_values = [0, 2]
        mock_roll_dice_values.return_value = dice_values

        target_chance_card = ChanceCard.objects.get(card_type=ChanceCard.REPAIRS)
        target_property_group_1 = PropertyGroup.objects.get(name=PropertyGroup.CLOTH)
        ownerships: list[Ownership] = []

        for property in Property.objects.filter(group=target_property_group_1):
            o = Ownership.objects.create(
                game=self.game,
                player=self.player_1,
                property=property,
            )
            ownerships.append(o)

        for i in range(len(ownerships)):
            if i == 0:
                ownerships[i].houses = 2
            else:
                ownerships[i].houses = 1
            ownerships[i].save()

        with patch('game.models.ChanceCard.get_random_card', return_value=target_chance_card):
            self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
        
        self._refresh_game_and_players()

        current_effect_1 = self.player_1.get_current_effect()
        effect_data = current_effect_1.effect_data
        player_1_before_pay = copy(self.player_1)

        self.assertEqual(current_effect_1.name, GameEffect.PAY_REPAIRS)
        self.assertEqual(effect_data['repair_cost'], 3 * target_chance_card.details['house_repair_cost'])
        self.assertEqual(effect_data['number_of_houses'], 3)
        self.assertEqual(effect_data['house_repair_cost'], target_chance_card.details['house_repair_cost'])

        self._post_game_action(self.client_1, GameActionType.PAY)

        self._refresh_game_and_players()
        self.assertEqual(self.player_1.cash, player_1_before_pay.cash - effect_data['repair_cost'])
        self.assertIsNone(self.player_1.get_current_effect())

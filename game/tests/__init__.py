from typing import Literal

from django.test import TestCase, Client
from django.urls import reverse
from channels.db import database_sync_to_async

from game.management.commands.populate_database import (
    Command as PopulateDatabaseCommand,
)
from game.models import Game, BoardConfig, Player, Property, PendingAction
from game.services import ClassicMonopolyService, get_service_by_name
from game.schemas import ActionCommand
from .mixins import TelegramAuthMixin
from .classic import mock_data


class BaseApiTestCase(TestCase, TelegramAuthMixin):
    game: Game
    players: list[Player]

    def setUp(self):
        PopulateDatabaseCommand().populate()

        headers_1 = self.generate_auth_headers(mock_data._TG_INIT_DATA_1)
        headers_2 = self.generate_auth_headers(mock_data._TG_INIT_DATA_2)

        self.client_1 = Client(headers=headers_1)
        self.client_2 = Client(headers=headers_2)

        self.clients = [self.client_1, self.client_2]

        self.tg_users = mock_data.create_telegram_users(2)
        self.tg_user_1 = self.tg_users[0]
        self.tg_user_2 = self.tg_users[1]

    def _refresh_game_and_players(self):
        """Refresh game and all players from DB"""
        self.game.refresh_from_db()
        for player in self.players:
            player.refresh_from_db()

    @database_sync_to_async
    def _refresh_game_and_players_async(self):
        """Refresh game and all players from DB"""
        self.game.refresh_from_db()
        for player in self.players:
            player.refresh_from_db()

    def _call_create_game(
        self,
        num_players: Literal[2, 3],
        config: str = BoardConfig.Names.CLASSIC.value,
        auto_join: bool = True,
    ):
        if num_players != 2 and num_players != 3:
            raise ValueError("num_players must be 2 or 3, because there is no more test users")

        self.num_players = num_players

        response = self.client_1.post(
            reverse("games-list"), data={"max_players": num_players, "config": config}
        )

        self.assertEqual(response.status_code, 201)

        resp_data = response.json()
        game_uuid = resp_data["game_uuid"]

        self.game = Game.objects.get(uuid=game_uuid)
        self.assertEqual(self.game.status, self.game.Status.WAITING)
        self.assertEqual(self.game.max_players, num_players)
        self.assertEqual(self.game.board_config.name, config)
        self.players = []

        if auto_join:
            for i in range(self.num_players - 1):
                response = self.clients[i + 1].post(reverse("games-join", kwargs={"uuid": game_uuid}))

                self.assertEqual(response.status_code, 200)
                self.game.refresh_from_db()
                self.assertEqual(self.game.status, self.game.Status.PLAYING)

        self.players = list(self.game.players.all())


class TestGameMixin:
    monopoly_service: ClassicMonopolyService
    game: Game
    player_1: Player
    player_2: Player
    property_1: Property
    property_2: Property

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

    def _send_game_action(
        self,
        player: Player,
        command: ActionCommand,
        should_resolve: bool,
        pa_type_prior: PendingAction.Types | None = None,
        pa_type_after: PendingAction.Types | None = None,
    ) -> dict:
        if pa_type_prior:
            assert player.pending_action is not None
            assert player.pending_action.action_type == pa_type_prior
            assert player.pending_action.resolved_at is None

        prev_pa = player.pending_action
        game_frame = self.monopoly_service.process_game_action(self.game.uuid, player.pk, command)
        self._refresh_game_and_players()
        prev_pa.refresh_from_db()  # type: ignore[union-attr]
        assert prev_pa.resolved_at is not None if should_resolve else prev_pa.resolved_at is None  # type: ignore[union-attr]

        if pa_type_after:
            assert player.pending_action is not None
            assert pa_type_after == player.pending_action.action_type
        return game_frame

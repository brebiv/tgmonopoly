from typing import Literal

from django.test import TestCase, Client
from django.urls import reverse
from channels.db import database_sync_to_async

from game.management.commands.populate_database import (
    Command as PopulateDatabaseCommand,
)
from game.models import Game, BoardConfig, Player
from .mixins import TelegramAuthMixin
from . import test_data


class BaseApiTestCase(TestCase, TelegramAuthMixin):
    game: Game
    players: list[Player]

    def setUp(self):
        PopulateDatabaseCommand().populate()

        headers_1 = self.generate_auth_headers(test_data._TG_INIT_DATA_1)
        headers_2 = self.generate_auth_headers(test_data._TG_INIT_DATA_2)

        self.client_1 = Client(headers=headers_1)
        self.client_2 = Client(headers=headers_2)

        self.clients = [self.client_1, self.client_2]

        self.tg_users = test_data.create_telegram_users(2)
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

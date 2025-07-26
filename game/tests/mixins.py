from abc import ABC
from django.conf import settings

from game.services.classic import ClassicMonopolyService
from game.services import get_service_by_name
from game.schemas import ActionCommand
from game.models import Game, Player, Property, PendingAction
from .classic import mock_data


class TelegramAuthMixin(ABC):
    AUTH_METHOD_NAME = "TWA"

    def generate_auth_header(self, init_data: str) -> str:
        return f"{self.AUTH_METHOD_NAME} {init_data}"

    def generate_auth_headers(self, init_data: str) -> dict:
        return {"Authorization": self.generate_auth_header(init_data)}


class TestGameMixin(ABC):
    monopoly_service: ClassicMonopolyService
    game: Game
    player_1: Player
    player_2: Player
    property_1: Property
    property_2: Property

    def setup_method(self, method):
        settings.IN_TEST_MODE = True

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

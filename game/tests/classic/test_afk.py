import pytest
from pytest_mock import MockerFixture
from unittest.mock import patch
from typing import no_type_check

from game.management.commands.populate_database import (
    Command as PopulateDatabaseCommand,
)
from game.models import (
    PendingAction,
    Game,
    Player,
    Property,
)
from game.services.classic import ClassicMonopolyService
from game.tests.mixins import TestGameMixin
from game.schemas import ActionCommand
from game.exceptions import GameException
from game.tasks import trigger_afk


@pytest.mark.django_db
class TestCelery(TestGameMixin):
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

    @pytest.mark.parametrize(
        ("action_type"),
        [*PendingAction.Types.values],
    )
    @no_type_check
    def test_afk_success(self, mocker: MockerFixture, action_type):
        if action_type == PendingAction.Types.PAY_RENT:
            self.player_1.cash = 1
            self.player_1.save()
            with patch(
                "game.services.ClassicMonopolyService._roll_dice_values",
                return_value=[self.property_2.position, 0],
            ):
                self._send_game_action(self.player_1, ActionCommand(action="roll_dice"), True)

        pa: PendingAction = self.player_1.pending_action
        p2_cash_before = self.player_2.cash

        assert self.player_1.ownerships.count() == 1

        trigger_afk({"pa_uuid": pa.uuid})
        self._refresh_game_and_players()

        assert self.game.current_player == self.player_2
        assert self.player_1.status == Player.Status.TIMEOUT
        assert self.player_2.pending_action.action_type == PendingAction.Types.ROLL_DICE
        assert self.player_1.ownerships.count() == 0

        if action_type == PendingAction.Types.PAY_RENT:
            assert self.player_2.cash == p2_cash_before + self.player_1.cash

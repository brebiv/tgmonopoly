from uuid import UUID
from typing import List, Tuple, Optional
from abc import ABC, abstractmethod
import random

from bot.models import TelegramUser
from game.serializers import GameEventSerializer, GameSerializer, PlayerSerializer
from game.game_config import BaseMonopolyConfig
from game.exceptions import GameException
from game.schemas import ActionCommand
from game.models import (
    Game,
    Player,
    GameEvent,
    PendingAction,
)


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
        return [2, 1]
        # return [19, 1]
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
    def handle_afk(
        self, game: Game, player: Player, prev_pa: PendingAction, command: ActionCommand | None = None
    ) -> list[GameEvent]: ...

    @abstractmethod
    def process_game_action(self, game_uuid: UUID, player_id: int, action: ActionCommand) -> dict: ...

    def _calculate_next_player(self, game: Game, after_player: Player) -> Player:
        game_players = game.players.filter(status=Player.Status.PLAYING).order_by("created")
        current_player_index = None

        for i, p in enumerate(game_players):
            if p.pk == after_player.pk:
                current_player_index = i

        if current_player_index is None:
            return game_players.first()  # type: ignore[return-value]
            raise GameException("Could not find next player")

        next_player_index = (current_player_index + 1) % game_players.count()
        next_player = game_players[next_player_index]

        return next_player

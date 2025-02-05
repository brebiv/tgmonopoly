from channels.db import database_sync_to_async
from django.db.models import Q
from game.models import Player, Game
from bot.models import TelegramUser


@database_sync_to_async
def get_current_effect(player: Player):
    return player.get_current_effect()

@database_sync_to_async
def get_player_by_id(player_id: int):
    return Player.objects.get(pk=player_id)

def check_user_can_create_game(user: TelegramUser) -> bool:
    return not Player.objects.filter(user=user, game__status=Game.WAITING).exists()

def get_user_current_game(user: TelegramUser) -> Game | None:
    return Game.objects.filter(Q(players__user=user) & ~Q(status=Game.FINISHED) & ~Q(status=Game.ABANDONED)).last()

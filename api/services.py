from channels.db import database_sync_to_async
from game.models import Player


@database_sync_to_async
def get_current_effect(player: Player):
    return player.get_current_effect()

@database_sync_to_async
def get_player_by_id(player_id: int):
    return Player.objects.get(pk=player_id)

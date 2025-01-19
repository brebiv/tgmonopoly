from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from game.models import Game, GameEffect


@shared_task
def handle_game_effect_timeout(effect_id: int):
    from game.services import GameService
    print("Handling game effect timeout")

    effect = GameEffect.objects.get(pk=effect_id)
    game = effect.game
    player = effect.player

    events = GameService.handle_afk(game, player, effect)
    game_frame = GameService.assemble_game_frame(game, events)

    channel_layer = get_channel_layer()
    game_group_name = f"game_{game.uuid}"

    async_to_sync(channel_layer.group_send)(
        game_group_name, game_frame
    )

    return {'status': 'ok'}

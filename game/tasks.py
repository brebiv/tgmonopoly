from pydantic import BaseModel, UUID4
from django.utils.timezone import now
from django.db import transaction
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from celery import shared_task

from game.models import Player, PendingAction
from game.services import get_service_by_game
from game.services.classic import ClassicMonopolyService


class TriggerAfkArgs(BaseModel):
    pa_uuid: UUID4


@shared_task(pydantic=True)
def trigger_afk(arg: TriggerAfkArgs):
    with transaction.atomic():
        pa = PendingAction.objects.select_related("player").get(pk=arg.pa_uuid)

        if pa.resolved_at:
            return

        player = Player.objects.select_related("game").get(pk=pa.player.pk)

        service: ClassicMonopolyService = get_service_by_game(pa.player.game)  # type: ignore[assignment]
        game_frame = service.handle_afk(player.game, player, pa)

        channel_layer = get_channel_layer()
        game_group_name = f"game_{player.game.uuid}"

        async_to_sync(channel_layer.group_send)(game_group_name, game_frame)

from pydantic import BaseModel, UUID4
from django.utils.timezone import now
from django.db import transaction
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
        service.handle_afk(player.game, player, pa)

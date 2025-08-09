from celery import current_app
from tgmonopoly.celery import debug_task
from game.tasks import trigger_afk

# debug_task.apply_async()
# trigger_afk.apply_async(({"pa_uuid": "fe93b37a-3f9c-496f-91a7-62904386f287"},), countdown=3)


# print(dir(current_app)
current_app.send_task(
    "game.tasks.trigger_afk", args=({"pa_uuid": "fe93b37a-3f9c-496f-91a7-62904386f287"},), countdown=3
)

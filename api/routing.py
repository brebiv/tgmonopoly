from django.urls import re_path, path
from . import consumers

websocket_urlpatterns = [
    path('ws/game/<uuid:game_uuid>/', consumers.GameConsumer.as_asgi()),
]
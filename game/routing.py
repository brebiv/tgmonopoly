from django.urls import re_path
from game import consumers

websocket_urlpatterns = [
    re_path(r"ws/game/(?P<game_uuid>[\w-]+)/$", consumers.GameConsumer.as_asgi()),
    re_path(r"ws/games/", consumers.GameListConsumer.as_asgi()),
]

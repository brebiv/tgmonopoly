from django.urls import path

from game.views import api
from game.views import web


urlpatterns = [
    # api
    path("api/me", api.me, name="me"),
    path("api/games", api.games, name="games"),
    # web
    path("", web.home, name="home"),
    path("game/<uuid:game_uuid>", web.game, name="game"),
]

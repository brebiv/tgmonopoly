from django.urls import path, include
from rest_framework.routers import DefaultRouter

from game.views import api
from game.views import web

router = DefaultRouter(use_regex_path=False)
router.register(r"games", api.GameViewSet, "game")

urlpatterns = [
    # api
    path("api/me", api.me, name="me"),
    path("api/", include(router.urls)),
    # web
    path("", web.home, name="home"),
    path("game/<uuid:game_uuid>", web.game, name="game"),
]

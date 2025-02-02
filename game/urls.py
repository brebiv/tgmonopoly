from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('games/', views.home, name='browse_games'),
    path('create_game', views.create_game, name='create_game_page'),
    path('game/<uuid:game_uuid>', views.game, name='game'),
]
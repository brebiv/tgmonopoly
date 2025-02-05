from django.urls import path
from . import views

urlpatterns = [
    path('me/', views.me, name='me'),
    path('create_game/', views.create_game, name='create_game'),
    path('join_game/', views.join_game, name='join_game'),
    path('leave_game/<uuid:game_uuid>/', views.leave_game, name='leave_game'),
    path('game_action/', views.game_action, name='game_action'),
    path('games/', views.game_list, name='game_list'),
]

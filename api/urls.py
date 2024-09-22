from django.urls import path
from . import views

urlpatterns = [
    path('me/', views.me, name='me'),
    path('create_game/', views.create_game, name='create_game'),
]
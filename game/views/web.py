import uuid
from django.shortcuts import render
from django.http import HttpRequest


# Create your views here.
def home(request: HttpRequest):
    return render(request, "game/home.html")


def game(request: HttpRequest, game_uuid: uuid.UUID):
    return render(request, "game/game.html")

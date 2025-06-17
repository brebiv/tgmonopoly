from django.shortcuts import render
from django.http import HttpRequest


# Create your views here.
def game(request: HttpRequest):
    return render(request, "game/game.html")

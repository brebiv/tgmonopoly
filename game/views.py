from django.shortcuts import render
from django.http import HttpRequest
import json

from .models import Tile
from api.serializers import TileSerializer

# Create your views here.
def home(request: HttpRequest):
    return render(request, 'game/home.html')


def create_game(request: HttpRequest):
    return render(request, 'game/create_game.html')


def game(request: HttpRequest, game_id: int):
    tiles = Tile.objects.all()

    context = {
        'tiles': json.dumps(TileSerializer(tiles, many=True).data),
    }

    return render(request, 'game/game.html', context)

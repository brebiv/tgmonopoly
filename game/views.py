from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
import json
import uuid

from .models import Tile, Game, Player
from api.serializers import TileSerializer, GameSerializer, PlayerSerializer

# Create your views here.
def home(request: HttpRequest):
    return render(request, 'game/home.html')


def create_game(request: HttpRequest):
    if request.method == 'GET':
        return render(request, 'game/create_game.html')
    else:
        return HttpResponse(status=405)


def game(request: HttpRequest, game_uuid: uuid.UUID):
    game = Game.objects.get(uuid=game_uuid)
    players = Player.objects.filter(game=game)
    tiles = Tile.objects.all()

    context = {
        'tiles': json.dumps(TileSerializer(tiles, many=True).data),
        'game': json.dumps(GameSerializer(game).data),
        # 'players': json.dumps(PlayerSerializer(players, many=True).data),
    }

    return render(request, 'game/game.html', context)

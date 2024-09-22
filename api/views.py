from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from .serializers import CreateGameSerializer, GameSerializer, PlayerSerializer
from .utils import telegram_auth_required, CustomRequest
from game.models import Player, Game


# Create your views here.
@api_view(['GET',])
@telegram_auth_required
def me(request: CustomRequest):
    me = {
        'id': request.telegram_user.user_id,
        'username': request.telegram_user.username,
        'first_name': request.telegram_user.first_name,
        'last_name': request.telegram_user.last_name,
        'language': request.telegram_user.language,
    }
    return JsonResponse(me)

@api_view(['POST',])
@telegram_auth_required
def create_game(request: CustomRequest):
    if request.method == 'POST':
        serializer = CreateGameSerializer(data=request.data)
        if serializer.is_valid():
            try:
                player = Player.objects.get(user=request.telegram_user, game__status=Game.PLAYING)
                return JsonResponse({'error': 'You are already playing a game'}, status=400)
            except Player.DoesNotExist:
                game = Game.objects.create(
                    max_players=serializer.data['max_players'],
                )
                player = Player.objects.create(
                    user=request.telegram_user,
                    game=game,
                    color="red",
                )
                response_data = {
                    'next_url': f'/game/{game.uuid}',
                    # 'game': GameSerializer(game).data,
                    # 'players': [PlayerSerializer(player).data],
                }
                return JsonResponse(response_data, status=201)
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=405)

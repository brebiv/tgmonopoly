from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .serializers import CreateGameSerializer, GameSerializer, PlayerSerializer, GameActionSerializer, GameEventSerializer
from .utils import telegram_auth_required, CustomRequest
from .types import GameActionType
from game.models import Player, Game, GameEffect
from .services import GameService


# Create your views here.
@api_view(['GET',])
@telegram_auth_required
def me(request: CustomRequest):
    # try:
    #     player = Player.objects.get(user=request.telegram_user)
    # except Player.DoesNotExist:
    #     pass

    me = {
        'id': request.telegram_user.user_id,
        'username': request.telegram_user.username,
        'first_name': request.telegram_user.first_name,
        'last_name': request.telegram_user.last_name,
        'language': request.telegram_user.language,
        # 'player': PlayerSerializer(player).data if player else None,
    }
    return JsonResponse(me)


@api_view(['POST',])
@telegram_auth_required
def create_game(request: CustomRequest):
    if request.method == 'POST':
        serializer = CreateGameSerializer(data=request.data)
        if serializer.is_valid():
            # Delete from here
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
            # To here
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

import random


@api_view(['POST',])
@telegram_auth_required
def game_action(request: CustomRequest):
    if request.method == 'POST':
        game_action_serializer = GameActionSerializer(data=request.data)
        if not game_action_serializer.is_valid():
            return HttpResponse(status=400)

        try:
            game = Game.objects.get(uuid=request.data['game_uuid'])
        except Game.DoesNotExist:
            return HttpResponse(status=400)

        channel_layer = get_channel_layer()
        game_group_name = f"game_{game.uuid}"

        if request.data['action'] == GameActionType.ROLL_DICE:
            dices = [random.randint(1, 6) for _ in range(2)]
            
            response_data = {
                # 'dices': dices,
                "status": "ok",
            }

            game_event = {
                'type': 'game.action',
                'action': GameActionType.ROLL_DICE,
                'game_uuid': game.uuid,
                'dices': dices,
            }
            
            game_event_serializer = GameEventSerializer(data=game_event)
            if not game_event_serializer.is_valid():
                return HttpResponse(status=400)

            async_to_sync(channel_layer.group_send)(
                game_group_name, game_event_serializer.data
            )

            return JsonResponse(response_data, status=201)
        elif request.data['action'] == GameActionType.START_GAME:
            player = Player.objects.get(game=game, user=request.telegram_user)

            events = GameService.start_game(game, player)
            
            game_event_serializer = GameEventSerializer(data=events)

            if not game_event_serializer.is_valid():
                return JsonResponse({"status": "!ok", "error": "Invalid events"}, status=400)

            async_to_sync(channel_layer.group_send)(
                game_group_name, game_event_serializer.data
            )
            return JsonResponse({"status": "ok",}, status=200)
        else:
            return JsonResponse({"status": "!ok", "error": "Unknown action"}, status=400)
    else:
        return HttpResponse(status=405)

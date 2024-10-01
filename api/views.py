from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .serializers import (
    CreateGameSerializer, GameSerializer, PlayerSerializer, 
    GameActionSerializer, GameEventSerializer, JoinGameSerializer
)
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

@api_view(['POST',])
@telegram_auth_required
def join_game(request: CustomRequest):
    if request.method == 'POST':
        game_join_serializer = JoinGameSerializer(data=request.data)
        if not game_join_serializer.is_valid():
            pass
            # return HttpResponse(status=400)
        
        game = Game.objects.last()
        player = Player.objects.create(
            user=request.telegram_user,
            game=game,
            color="green",
        )

        response_data = {
            'status': 'ok',
            'next_url': f'/game/{game.uuid}',
        }
        return JsonResponse(response_data, status=201)

        # try:
        #     game = Game.objects.get(uuid=request.data['game_uuid'])
        # except Game.DoesNotExist:
        #     return HttpResponse(status=400)


@api_view(['POST',])
@telegram_auth_required
def game_action(request: CustomRequest):
    if request.method == 'POST':
        game_action_serializer = GameActionSerializer(data=request.data)
        if not game_action_serializer.is_valid():
            return HttpResponse(status=400)

        try:
            game = Game.objects.get(uuid=request.data['game_uuid'])
            player = Player.objects.get(game=game, user=request.telegram_user)
        except Game.DoesNotExist:
            return HttpResponse(status=400)
        except Player.DoesNotExist:
            return HttpResponse(status=400)

        channel_layer = get_channel_layer()
        game_group_name = f"game_{game.uuid}"

        if request.data['action'] == GameActionType.ROLL_DICE:
            events = GameService.roll_dice(game, player)
            events_serializer = GameEventSerializer(data=events, many=True)
            if not events_serializer.is_valid():
                return HttpResponse(status=400)
            
            game_frame = {
                'type': 'game.action',
                'action': GameActionType.START_GAME,
                'game': GameSerializer(game).data,
                'players': [PlayerSerializer(player).data for player in game.players.all()],
                'events': events_serializer.data,
            }

            async_to_sync(channel_layer.group_send)(
                game_group_name, game_frame
            )

            return JsonResponse({"status": "ok",}, status=201)
        elif request.data['action'] == GameActionType.START_GAME:

            events = GameService.start_game(game, player)
            
            events_serializer = GameEventSerializer(data=events, many=True)

            if not events_serializer.is_valid():
                return JsonResponse({"status": "!ok", "error": "Invalid events"}, status=400)
            
            game_frame = {
                'type': 'game.action',
                'action': GameActionType.START_GAME,
                'game': GameSerializer(game).data,
                'players': [PlayerSerializer(player).data for player in game.players.all()],
                'events': events_serializer.data,
            }

            async_to_sync(channel_layer.group_send)(
                game_group_name, game_frame
            )
            return JsonResponse({"status": "ok",}, status=200)
        else:
            return JsonResponse({"status": "!ok", "error": "Unknown action"}, status=400)
    else:
        return HttpResponse(status=405)

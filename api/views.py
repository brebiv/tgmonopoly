from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .serializers import (
    CreateGameSerializer, GameSerializer, PlayerSerializer, 
    GameActionSerializer, GameEventSerializer, JoinGameSerializer,
    OwnershipSerializer, MortagePropertySerializer
)
from .utils import telegram_auth_required, CustomRequest
from .types import GameActionType
from game.models import Player, Game, GameEffect, Ownership
from game import config
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
            return JsonResponse(response_data, status=200)
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
                return JsonResponse(response_data, status=200)
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
        return JsonResponse(response_data, status=200)

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
        action = request.data['action']
        extra_data = request.data.get('extra_data')

        first_effect: GameEffect = player.effects.first()

        if first_effect:
            if first_effect.name == GameEffect.ROLL_DICE:
                if player.in_jail:
                    if action == GameActionType.ROLL_DICE:
                        if player.jail_turns < config.MAXIMUM_JAIL_TURNS:
                            events = GameService.roll_dice(game, player)
                        else:
                            return JsonResponse({"status": "!ok", "error": "You can't roll dice anymore"}, status=400)
                        
                        game_frame = GameService.assemble_game_frame(game, events)

                        async_to_sync(channel_layer.group_send)(
                            game_group_name, game_frame
                        )
                        return JsonResponse({"status": "ok",}, status=200)
                    elif action == GameActionType.PAY_FOR_PRISON:
                        events = GameService.pay_for_prison(game, player)
                        game_frame = GameService.assemble_game_frame(game, events)

                        async_to_sync(channel_layer.group_send)(
                            game_group_name, game_frame
                        )
                        return JsonResponse({"status": "ok",}, status=200)
                    elif action == GameActionType.MORTAGE_PROPERTY:
                        extra_data_serializer = MortagePropertySerializer(data=extra_data)
                        if not extra_data_serializer.is_valid():
                            return JsonResponse({"status": "!ok", "error": "Invalid extra data"}, status=400)

                        property_id = extra_data_serializer.data['property_id']

                        events = GameService.mortage_property(game, player, property_id)
                        game_frame = GameService.assemble_game_frame(game, events)

                        async_to_sync(channel_layer.group_send)(
                            game_group_name, game_frame
                        )
                        return JsonResponse({"status": "ok",}, status=200)
                    elif action == GameActionType.BUYOUT_PROPERTY:
                        extra_data_serializer = MortagePropertySerializer(data=extra_data)
                        if not extra_data_serializer.is_valid():
                            return JsonResponse({"status": "!ok", "error": "Invalid extra data"}, status=400)

                        property_id = extra_data_serializer.data['property_id']

                        events = GameService.buyouy_property(game, player, property_id)
                        game_frame = GameService.assemble_game_frame(game, events)

                        async_to_sync(channel_layer.group_send)(
                            game_group_name, game_frame
                        )
                        return JsonResponse({"status": "ok",}, status=200)
                    elif action == GameActionType.BUY_HOUSE:
                        extra_data_serializer = MortagePropertySerializer(data=extra_data)
                        if not extra_data_serializer.is_valid():
                            return JsonResponse({"status": "!ok", "error": "Invalid extra data"}, status=400)

                        property_id = extra_data_serializer.data['property_id']

                        events = GameService.buy_house(game, player, property_id)
                        game_frame = GameService.assemble_game_frame(game, events)

                        async_to_sync(channel_layer.group_send)(
                            game_group_name, game_frame
                        )
                        return JsonResponse({"status": "ok",}, status=200)
                    elif action == GameActionType.SELL_HOUSE:
                        extra_data_serializer = MortagePropertySerializer(data=extra_data)
                        if not extra_data_serializer.is_valid():
                            return JsonResponse({"status": "!ok", "error": "Invalid extra data"}, status=400)

                        property_id = extra_data_serializer.data['property_id']

                        events = GameService.sell_house(game, player, property_id)
                        game_frame = GameService.assemble_game_frame(game, events)

                        async_to_sync(channel_layer.group_send)(
                            game_group_name, game_frame
                        )
                        return JsonResponse({"status": "ok",}, status=200)
                    else:
                        return JsonResponse({"status": "!ok", "error": "Unknown action"}, status=400)
                else:
                    if action == GameActionType.ROLL_DICE:
                        events = GameService.roll_dice(game, player)
                        game_frame = GameService.assemble_game_frame(game, events)

                        async_to_sync(channel_layer.group_send)(
                            game_group_name, game_frame
                        )
                        return JsonResponse({"status": "ok",}, status=200)
                    elif action == GameActionType.MORTAGE_PROPERTY:
                        extra_data_serializer = MortagePropertySerializer(data=extra_data)
                        if not extra_data_serializer.is_valid():
                            return JsonResponse({"status": "!ok", "error": "Invalid extra data"}, status=400)

                        property_id = extra_data_serializer.data['property_id']

                        events = GameService.mortage_property(game, player, property_id)
                        game_frame = GameService.assemble_game_frame(game, events)

                        async_to_sync(channel_layer.group_send)(
                            game_group_name, game_frame
                        )
                        return JsonResponse({"status": "ok",}, status=200)
                    elif action == GameActionType.BUYOUT_PROPERTY:
                        extra_data_serializer = MortagePropertySerializer(data=extra_data)
                        if not extra_data_serializer.is_valid():
                            return JsonResponse({"status": "!ok", "error": "Invalid extra data"}, status=400)

                        property_id = extra_data_serializer.data['property_id']

                        events = GameService.buyouy_property(game, player, property_id)
                        game_frame = GameService.assemble_game_frame(game, events)

                        async_to_sync(channel_layer.group_send)(
                            game_group_name, game_frame
                        )
                        return JsonResponse({"status": "ok",}, status=200)
                    elif action == GameActionType.BUY_HOUSE:
                        extra_data_serializer = MortagePropertySerializer(data=extra_data)
                        if not extra_data_serializer.is_valid():
                            return JsonResponse({"status": "!ok", "error": "Invalid extra data"}, status=400)

                        property_id = extra_data_serializer.data['property_id']

                        events = GameService.buy_house(game, player, property_id)
                        game_frame = GameService.assemble_game_frame(game, events)

                        async_to_sync(channel_layer.group_send)(
                            game_group_name, game_frame
                        )
                        return JsonResponse({"status": "ok",}, status=200)
                    elif action == GameActionType.SELL_HOUSE:
                        extra_data_serializer = MortagePropertySerializer(data=extra_data)
                        if not extra_data_serializer.is_valid():
                            return JsonResponse({"status": "!ok", "error": "Invalid extra data"}, status=400)

                        property_id = extra_data_serializer.data['property_id']

                        events = GameService.sell_house(game, player, property_id)
                        game_frame = GameService.assemble_game_frame(game, events)

                        async_to_sync(channel_layer.group_send)(
                            game_group_name, game_frame
                        )
                        return JsonResponse({"status": "ok",}, status=200)
                    else:
                        return JsonResponse({"status": "!ok", "error": "Unknown action"}, status=400)
            elif first_effect.name == GameEffect.ASK_BUY:
                if action == GameActionType.BUY_PROPERTY:
                    events = GameService.buy_property(game, player)
                    game_frame = GameService.assemble_game_frame(game, events)

                    async_to_sync(channel_layer.group_send)(
                        game_group_name, game_frame
                    )
                    return JsonResponse({"status": "ok",}, status=200)
                elif action == GameActionType.MORTAGE_PROPERTY:
                    extra_data_serializer = MortagePropertySerializer(data=extra_data)
                    if not extra_data_serializer.is_valid():
                        return JsonResponse({"status": "!ok", "error": "Invalid extra data"}, status=400)

                    property_id = extra_data_serializer.data['property_id']

                    events = GameService.mortage_property(game, player, property_id)
                    game_frame = GameService.assemble_game_frame(game, events)

                    async_to_sync(channel_layer.group_send)(
                        game_group_name, game_frame
                    )
                    return JsonResponse({"status": "ok",}, status=200)
                elif action == GameActionType.BUYOUT_PROPERTY:
                    extra_data_serializer = MortagePropertySerializer(data=extra_data)
                    if not extra_data_serializer.is_valid():
                        return JsonResponse({"status": "!ok", "error": "Invalid extra data"}, status=400)

                    property_id = extra_data_serializer.data['property_id']

                    events = GameService.buyouy_property(game, player, property_id)
                    game_frame = GameService.assemble_game_frame(game, events)

                    async_to_sync(channel_layer.group_send)(
                        game_group_name, game_frame
                    )
                elif action == GameActionType.SELL_HOUSE:
                    extra_data_serializer = MortagePropertySerializer(data=extra_data)
                    if not extra_data_serializer.is_valid():
                        return JsonResponse({"status": "!ok", "error": "Invalid extra data"}, status=400)

                    property_id = extra_data_serializer.data['property_id']

                    events = GameService.sell_house(game, player, property_id)
                    game_frame = GameService.assemble_game_frame(game, events)

                    async_to_sync(channel_layer.group_send)(
                        game_group_name, game_frame
                    )
                    return JsonResponse({"status": "ok",}, status=200)
                else:
                    return JsonResponse({"status": "!ok", "error": "Unknown action"}, status=400)
            elif first_effect.name == GameEffect.PAY_RENT:
                if action == GameActionType.PAY_RENT:
                    events = GameService.pay_rent(game, player)
                    game_frame = GameService.assemble_game_frame(game, events)

                    async_to_sync(channel_layer.group_send)(
                        game_group_name, game_frame
                    )
                    return JsonResponse({"status": "ok",}, status=200)
                elif action == GameActionType.MORTAGE_PROPERTY:
                    extra_data_serializer = MortagePropertySerializer(data=extra_data)
                    if not extra_data_serializer.is_valid():
                        return JsonResponse({"status": "!ok", "error": "Invalid extra data"}, status=400)

                    property_id = extra_data_serializer.data['property_id']

                    events = GameService.mortage_property(game, player, property_id)
                    game_frame = GameService.assemble_game_frame(game, events)

                    async_to_sync(channel_layer.group_send)(
                        game_group_name, game_frame
                    )
                    return JsonResponse({"status": "ok",}, status=200)
                elif action == GameActionType.BUYOUT_PROPERTY:
                    extra_data_serializer = MortagePropertySerializer(data=extra_data)
                    if not extra_data_serializer.is_valid():
                        return JsonResponse({"status": "!ok", "error": "Invalid extra data"}, status=400)

                    property_id = extra_data_serializer.data['property_id']

                    events = GameService.buyouy_property(game, player, property_id)
                    game_frame = GameService.assemble_game_frame(game, events)

                    async_to_sync(channel_layer.group_send)(
                        game_group_name, game_frame
                    )
                elif action == GameActionType.SELL_HOUSE:
                    extra_data_serializer = MortagePropertySerializer(data=extra_data)
                    if not extra_data_serializer.is_valid():
                        return JsonResponse({"status": "!ok", "error": "Invalid extra data"}, status=400)

                    property_id = extra_data_serializer.data['property_id']

                    events = GameService.sell_house(game, player, property_id)
                    game_frame = GameService.assemble_game_frame(game, events)

                    async_to_sync(channel_layer.group_send)(
                        game_group_name, game_frame
                    )
                    return JsonResponse({"status": "ok",}, status=200)
                else:
                    return JsonResponse({"status": "!ok", "error": "Unknown action"}, status=400)
            else:
                return JsonResponse({"status": "!ok", "error": "Unknown action"}, status=400)
        else:
            if action == GameActionType.START_GAME:
                events = GameService.start_game(game, player)
                game_frame = GameService.assemble_game_frame(game, events)

                async_to_sync(channel_layer.group_send)(
                    game_group_name, game_frame
                )
                return JsonResponse({"status": "ok",}, status=200)
            else:
                return JsonResponse({"status": "!ok", "error": "Unknown action"}, status=400)
    else:
        return HttpResponse(status=405)

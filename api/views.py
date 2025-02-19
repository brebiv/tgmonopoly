from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from urllib.parse import urlencode

from .serializers import (
    CreateGameSerializer, GameSerializer, PlayerSerializer, 
    GameActionSerializer, GameEventSerializer, JoinGameSerializer,
    OwnershipSerializer, MortagePropertySerializer, ExtraDataSerializer,
    TradeDataSerializer
)
from game.models import Player, Game, GameEffect, Ownership
from game import config
from game.services import GameService
from game.exceptions import GameException
from .utils import telegram_auth_required, CustomRequest
from .types import GameActionType, TradeData
from .services import check_user_can_create_game, get_user_current_game


# Create your views here.
@api_view(['GET',])
@telegram_auth_required
def me(request: CustomRequest):
    permissions = {
        "create_game": False
    }

    if check_user_can_create_game(request.telegram_user):
        permissions['create_game'] = True

    current_game = get_user_current_game(request.telegram_user)
    current_game_info = GameSerializer(current_game).data if current_game else None

    me = {
        'id': request.telegram_user.user_id,
        'username': request.telegram_user.username,
        'first_name': request.telegram_user.first_name,
        'last_name': request.telegram_user.last_name,
        'language': request.telegram_user.language,
        'permissions': permissions,
        'current_game_link': f'/game/{current_game.uuid}' if current_game else None,
        'current_game_info': current_game_info,
        # 'player': PlayerSerializer(player).data if player else None,
    }
    return JsonResponse(me)


@api_view(['POST',])
@telegram_auth_required
def create_game(request: CustomRequest):
    if request.method == 'POST':
        serializer = CreateGameSerializer(data=request.data)
        if serializer.is_valid():
            if Player.objects.filter(user=request.telegram_user, game__status__in=[Game.WAITING, Game.PLAYING]).exists():
                if not config.ALLOW_CREATING_MULTIPLE_GAMES:
                    return JsonResponse({'error': 'You are already create a game'}, status=400)

            game = Game.objects.create(
                max_players=serializer.data['max_players'],
            )
            player = Player.objects.create(
                user=request.telegram_user,
                game=game,
                color="red",
            )

            response_data = {
                'status': 'ok',
                'next_url': f'/game/{game.uuid}',
                'game_uuid': game.uuid,
                # 'game': GameSerializer(game).data,
                # 'players': [PlayerSerializer(player).data],
            }
            return JsonResponse(response_data, status=200)
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=405)


@api_view(['GET',])
@telegram_auth_required
def game_list(request: CustomRequest):
    status = request.query_params.get('status')
    if status:
        status = Game.STATUS_CHOICES[int(status)][0]
        games = Game.objects.filter(status=status).order_by('-created')
    else:
        games = Game.objects.filter(status=Game.WAITING).order_by('-created')
    
    paginator = Paginator(games, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    games_data = [GameSerializer(game).data for game in page_obj]

    for game in games_data:
        in_game = Player.objects.filter(game__uuid=game['uuid'], user=request.telegram_user).exists()
        game['in_game'] = in_game
    
    resp_data = {
        'status': 'ok',
        'games': games_data,
    }

    if page_obj.has_next():
        query_params = request.GET.copy()
        query_params['page'] = page_obj.next_page_number()
        resp_data['next_url'] = f'{request.path}?{urlencode(query_params)}'
    
    return JsonResponse(resp_data, status=200)


@api_view(['POST',])
@telegram_auth_required
def join_game(request: CustomRequest):
    if request.method == 'POST':
        game_join_serializer = JoinGameSerializer(data=request.data)
        if not game_join_serializer.is_valid():
            return HttpResponse(status=400)
        
        # game = Game.objects.last()
        game_uuid = request.data.get('game_uuid')
        game = get_object_or_404(Game, uuid=game_uuid)

        channel_layer = get_channel_layer()
        game_group_name = f"game_{game.uuid}"

        try:
            events = GameService.join_game(game, request.telegram_user)
        except GameException as e:
            return JsonResponse({"status": "!ok", "error": str(e)}, status=400)

        response_data = {
            'status': 'ok',
            'next_url': f'/game/{game.uuid}',
        }

        game_frame = GameService.assemble_game_frame(game, events)

        async_to_sync(channel_layer.group_send)(
            game_group_name, game_frame
        )

        return JsonResponse(response_data, status=200)


@api_view(['GET',])
@telegram_auth_required
def leave_game(request: CustomRequest, game_uuid):
    if request.method == 'GET':
        # game = Game.objects.get(uuid=request.data['game_uuid'])
        game = get_object_or_404(Game, uuid=game_uuid)
        player = Player.objects.get(game=game, user=request.telegram_user)

        try:
            events = GameService.leave_game(game, player)
        except GameException as e:
            return JsonResponse({"status": "!ok", "error": str(e)}, status=400)

        game_frame = GameService.assemble_game_frame(game, events)

        channel_layer = get_channel_layer()
        game_group_name = f"game_{game.uuid}"

        async_to_sync(channel_layer.group_send)(
            game_group_name, game_frame
        )

        return JsonResponse({"status": "ok",}, status=200)


@api_view(['GET',])
@telegram_auth_required
def abandon_game(request: CustomRequest, game_uuid):
    if request.method == 'GET':
        game = get_object_or_404(Game, uuid=game_uuid)
        player = Player.objects.get(game=game, user=request.telegram_user)

        try:
            events = GameService.abandon_game(game, player)
        except GameException as e:
            return JsonResponse({"status": "!ok", "error": str(e)}, status=400)

        game_frame = GameService.assemble_game_frame(game, events)

        channel_layer = get_channel_layer()
        game_group_name = f"game_{game.uuid}"

        async_to_sync(channel_layer.group_send)(
            game_group_name, game_frame
        )

        return JsonResponse({"status": "ok",}, status=200)


@api_view(['POST',])
@telegram_auth_required
def game_action(request: CustomRequest):
    if request.method == 'POST':
        game_action_serializer = GameActionSerializer(data=request.data)
        if not game_action_serializer.is_valid():
            return JsonResponse({"status": "!ok", "error": "Invalid game action"}, status=400)

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

        if first_effect and game.current_player == player:
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
                    elif action == GameActionType.CREATE_TRADE:
                        extra_data_serializer = TradeDataSerializer(data=extra_data)
                        if not extra_data_serializer.is_valid():
                            return JsonResponse({"status": "!ok", "error": extra_data_serializer.errors}, status=400)

                        trade_data_raw = extra_data_serializer.validated_data

                        ownerships: list[Ownership] = []
                        if trade_data_raw.get('ownerships'):
                            if not isinstance(trade_data_raw.get('ownerships'), list):
                                return JsonResponse({"status": "!ok", "error": "Invalid ownerships"}, status=400)

                        try:
                            for ownership_id in trade_data_raw.get('ownerships'):
                                ownership = Ownership.objects.get(pk=ownership_id)
                                ownerships.append(ownership)
                        except Ownership.DoesNotExist:
                            return JsonResponse({"status": "!ok", "error": "Could not find ownership"}, status=400)

                        trade_data = TradeData(
                            trade_data_raw.get('from_player'),
                            trade_data_raw.get('to_player'),
                            trade_data_raw.get('cash_given'),
                            trade_data_raw.get('cash_received'),
                            ownerships=ownerships
                        )

                        try:
                            events = GameService.create_trade(game, player, trade_data)
                            game_frame = GameService.assemble_game_frame(game, events)

                            async_to_sync(channel_layer.group_send)(
                                game_group_name, game_frame
                            ) 
                            return JsonResponse({"status": "ok",}, status=200)
                        except GameException as e:
                            return JsonResponse({"status": "!ok", "error": str(e)}, status=400)
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
                elif action == GameActionType.START_AUCTION:
                    events = GameService.start_auction(game, player)
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
            elif first_effect.name == GameEffect.PAY_REPAIRS:
                if action == GameActionType.SELL_HOUSE:
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
                elif action == GameActionType.PAY:
                    amount = first_effect.effect_data.get('repair_cost')
                    events = GameService.pay_to_bank(game, player, amount)
                    game_frame = GameService.assemble_game_frame(game, events)

                    async_to_sync(channel_layer.group_send)(
                        game_group_name, game_frame
                    )
                    return JsonResponse({"status": "ok",}, status=200)
                else:
                    return JsonResponse({"status": "!ok", "error": "Unknown action"}, status=400)
            elif first_effect.name == GameEffect.IN_CASINO:
                if action == GameActionType.REJECT:
                    events = GameService.reject_casino(game, player)
                    game_frame = GameService.assemble_game_frame(game, events)

                    async_to_sync(channel_layer.group_send)(
                        game_group_name, game_frame
                    )
                    return JsonResponse({"status": "ok",}, status=200)
                elif action == GameActionType.ACCEPT:
                    extra_data_serializer = ExtraDataSerializer(data=extra_data)
                    if not extra_data_serializer.is_valid():
                        return JsonResponse({"status": "!ok", "error": "Invalid extra data"}, status=400)
                    
                    bet = extra_data_serializer.data['bet_amount']
    
                    events = GameService.play_casino(game, player, bet)
                    game_frame = GameService.assemble_game_frame(game, events)

                    async_to_sync(channel_layer.group_send)(
                        game_group_name, game_frame
                    )
                    return JsonResponse({"status": "ok",}, status=200)
                else:
                    return JsonResponse({"status": "!ok", "error": "Unknown action"}, status=400)
            elif first_effect.name == GameEffect.IN_TRADE:
                if action == GameActionType.REJECT:
                    events = GameService.reject_trade(game, player)
                    game_frame = GameService.assemble_game_frame(game, events)

                    async_to_sync(channel_layer.group_send)(
                        game_group_name, game_frame
                    )
                    return JsonResponse({"status": "ok",}, status=200)
                elif action == GameActionType.ACCEPT:
                    events = GameService.accept_trade(game, player)
                    game_frame = GameService.assemble_game_frame(game, events)

                    async_to_sync(channel_layer.group_send)(
                        game_group_name, game_frame
                    )
                    return JsonResponse({"status": "ok",}, status=200)
                else:
                    return JsonResponse({"status": "!ok", "error": "Unknown action"}, status=400)
            elif first_effect.name == GameEffect.IN_AUCTION:
                if action == GameActionType.ACCEPT:
                    try:
                        events = GameService.accept_auction(game, player)
                        game_frame = GameService.assemble_game_frame(game, events)

                        async_to_sync(channel_layer.group_send)(
                            game_group_name, game_frame
                        )
                        return JsonResponse({"status": "ok",}, status=200)
                    except GameException as e:
                        return JsonResponse({"status": "!ok", "error": str(e)}, status=400)
                elif action == GameActionType.REJECT:
                    events = GameService.reject_auction(game, player)
                    game_frame = GameService.assemble_game_frame(game, events)

                    async_to_sync(channel_layer.group_send)(
                        game_group_name, game_frame
                    )
                    return JsonResponse({"status": "ok",}, status=200)
                else:
                    return JsonResponse({"status": "!ok", "error": "Unknown action"}, status=400)
            elif first_effect.name == GameEffect.PAY_BANK:
                try:
                    if action == GameActionType.PAY:
                        events = GameService.pay_to_bank(game, player)
                        game_frame = GameService.assemble_game_frame(game, events)

                        async_to_sync(channel_layer.group_send)(
                            game_group_name, game_frame
                        )
                        return JsonResponse({"status": "ok",}, status=200)
                except GameException as e:
                    return JsonResponse({"status": "!ok", "error": str(e)}, status=400)
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
                return JsonResponse({"status": "!ok", "error": "Unknown action or it's not your turn"}, status=400)
    else:
        return HttpResponse(status=405)

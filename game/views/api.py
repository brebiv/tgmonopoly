from uuid import UUID

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
    action,
)
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.shortcuts import get_object_or_404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


from game.auth import (
    CustomRequest,
    TelegramWebAppAuthentication,
    IsTelegramAuthenticated,
)
from game.serializers import (
    TelegramUserSerializer,
    CreateGameInputSerializer,
    GameSerializer,
)
from game.services import get_service_by_game, get_service_by_name
from game.models import Game, Player


@api_view(["GET"])  # type: ignore[arg-type] # I don't want to call request = cast(CustomRequest, request)
@authentication_classes([TelegramWebAppAuthentication])
@permission_classes([IsTelegramAuthenticated])
def me(request: CustomRequest):
    user_data = TelegramUserSerializer(request.telegram_user).data
    current_player = Player.objects.filter(
        user=request.telegram_user, status__in=Player.ACTIVE_STATUSES
    ).first()
    current_game = None
    if current_player:
        current_game = current_player.game

    return Response(
        {
            "user": user_data,
            "current_game": GameSerializer(current_game).data if current_game else None,
        }
    )


class GameViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = (TelegramWebAppAuthentication,)
    # permission_classes = (IsTelegramAuthenticated,)
    queryset = Game.objects.filter(status=Game.Status.WAITING)
    serializer_class = GameSerializer
    lookup_field = "game_uuid"
    lookup_value_converter = "uuid"

    def create(self, request: CustomRequest):
        serializer = CreateGameInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        config_name = serializer.validated_data.get("config")
        max_players = serializer.validated_data.get("max_players")

        monopoly_service = get_service_by_name(config_name)

        assert request.telegram_user
        game = monopoly_service.create_game(request.telegram_user, max_players)

        return Response(
            {"status": "ok", "game_uuid": game.uuid}, status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["post"])
    def join(self, request: CustomRequest, game_uuid: UUID):
        game = get_object_or_404(Game, pk=game_uuid)

        assert request.telegram_user

        monopoly_service = get_service_by_game(game)
        _, events = monopoly_service.join_game(game.uuid, request.telegram_user)

        # because we did not call fetch_related, game.players is going to recalculated
        game_frame = monopoly_service.assemble_game_frame(game, events)

        channel_layer = get_channel_layer()
        game_group_name = f"game_{game.uuid}"
        async_to_sync(channel_layer.group_send)(game_group_name, game_frame)

        return Response(
            {
                "game_uuid": game.uuid,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def leave(self, request: CustomRequest, game_uuid: UUID):
        game = get_object_or_404(Game, pk=game_uuid)
        assert request.telegram_user

        player = game.players.get(user=request.telegram_user)

        monopoly_service = get_service_by_game(game)
        events = monopoly_service.leave_game(player)

        game_frame = monopoly_service.assemble_game_frame(game, events)

        channel_layer = get_channel_layer()
        game_group_name = f"game_{game.uuid}"
        async_to_sync(channel_layer.group_send)(game_group_name, game_frame)

        return Response({"detail": "You left the game"})

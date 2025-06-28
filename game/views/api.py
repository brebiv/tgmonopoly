from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status

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
from game.services import get_monopoly_service
from game.models import Game, Player
from game.exceptions import GameException


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
            "status": "ok",
            "user": user_data,
            "auth": str(request.is_telegram_authenticated),
            "current_game": GameSerializer(current_game).data if current_game else None,
        }
    )


@api_view(["GET", "POST"])  # type: ignore[arg-type]
@authentication_classes([TelegramWebAppAuthentication])
@permission_classes([IsTelegramAuthenticated])
def games(request: CustomRequest):
    if request.method == "GET":
        games = Game.objects.filter(status=Game.Status.WAITING)
        games_serializer = GameSerializer(games, many=True)
        return Response({"status": "ok", "games": games_serializer.data})

    if request.method == "POST":
        serializer = CreateGameInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        assert request.telegram_user  # noqa; for mypy, actual security check happens in DRF auth and perm class

        try:
            monopoly_service = get_monopoly_service(
                serializer.validated_data.get("config")
            )
        except ValueError as err:
            return Response(
                {"status": "!ok", "message": str(err)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            monopoly_service.create_game(
                request.telegram_user, serializer.validated_data.get("max_players")
            )
        except GameException as err:
            raise ValidationError(str(err))

        return Response({"status": "ok"}, status.HTTP_201_CREATED)

from rest_framework import serializers
from django.core.validators import MinValueValidator

from bot.models import TelegramUser
from game.models import Game, Player, GameEvent


class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = ("id", "username", "first_name", "last_name", "photo_url")


class CreateGameInputSerializer(serializers.Serializer):
    max_players = serializers.IntegerField(
        # Just sanity checks, all business logic checks happen in ./services.py
        validators=[
            MinValueValidator(
                1,
                "Max players should be greater than 0",
            ),
        ]
    )
    config = serializers.CharField()


class PlayerSerializer(serializers.ModelSerializer):
    avatar = serializers.URLField(source="user.photo_url")
    name = serializers.CharField(source="user.full_name")

    class Meta:
        model = Player
        fields = (
            "position",
            "cash",
            "color",
            "rolled_double",
            "double_count",
            "in_jail",
            "jail_turns",
            "move_backwards",
            "status",
            "avatar",
            "name",
        )


class GameSerializer(serializers.ModelSerializer):
    board_config = serializers.CharField(source="board_config.name")
    players = PlayerSerializer(many=True)

    class Meta:
        model = Game
        fields = (
            "uuid",
            "board_config",
            "max_players",
            "turn",
            "current_player",
            "status",
            "players",
        )


class GameEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameEvent
        fields = ("event_type", "extra_data")

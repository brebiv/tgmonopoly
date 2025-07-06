from rest_framework import serializers
from django.core.validators import MinValueValidator

from bot.models import TelegramUser
from game.models import (
    Game,
    Player,
    GameEvent,
    BoardConfig,
    PropertyGroup,
    UtilityGroup,
    Property,
    Utility,
)


class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = ("user_id", "username", "first_name", "last_name", "photo_url")


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


class PropertyGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyGroup
        fields = ("id", "name", "color")


class UtilityGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UtilityGroup
        fields = ("type", "name", "color")


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = (
            "price",
            "mortgage_value",
            "house_price",
            "rent",
            "rent_with_1_house",
            "rent_with_2_houses",
            "rent_with_3_houses",
            "rent_with_4_houses",
            "rent_with_5_houses",
            "group",
            "icon",
            "mortgage_buyback_price",
        )


class UtilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Utility
        fields = (
            "price",
            "mortgage_value",
            "group",
            "icon",
        )


class TileSeializer(serializers.Serializer):
    tile_type = serializers.CharField()
    position = serializers.IntegerField()
    name = serializers.CharField()

    TILE_SUBSET_SERIALIZERS = {
        Property.__name__: PropertySerializer,
        Utility.__name__: UtilitySerializer,
    }


class BoardConfigOverviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardConfig
        fields = ("name",)


class BoardConfigDetailSerializer(serializers.ModelSerializer):
    property_groups = PropertyGroupSerializer(many=True)
    utility_groups = UtilityGroupSerializer(many=True)
    tiles = serializers.SerializerMethodField()

    def get_tiles(self, board_config: BoardConfig):
        downcasted_tiles = [tile.downcast() for tile in board_config.tiles.all()]
        tiles = []

        for tile in downcasted_tiles:
            tile_type = tile.__class__.__name__

            tile_data = {
                "name": tile.name,
                "position": tile.position,
                "tile_type": tile_type.lower(),
            }

            extra_data_serializer = TileSeializer.TILE_SUBSET_SERIALIZERS.get(tile_type)
            if extra_data_serializer:
                serializer = extra_data_serializer(tile)
                tile_data = {**tile_data, **serializer.data}

            tiles.append(tile_data)
        return tiles

    class Meta:
        model = BoardConfig
        fields = ("name", "property_groups", "utility_groups", "tiles")

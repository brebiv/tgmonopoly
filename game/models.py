import uuid
from typing import Union

from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from bot.models import TelegramUser
from .utils import validate_color
from .game_config import get_config


class BoardConfig(models.Model):
    class Names(models.TextChoices):
        CLASSIC = "classic"

    name = models.CharField(choices=Names.choices, max_length=32, unique=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)


class PropertyGroup(models.Model):
    board_config = models.ForeignKey(
        BoardConfig, related_name="property_groups", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=32)
    color = models.CharField(max_length=32, validators=[validate_color])

    def __str__(self):
        return self.name


class UtilityGroup(models.Model):
    class Types(models.TextChoices):
        UTILITY_1 = "UTILITY_1"
        UTILITY_2 = "UTILITY_2"

    board_config = models.ForeignKey(
        BoardConfig, related_name="utility_groups", on_delete=models.CASCADE
    )
    type = models.CharField(max_length=32, choices=Types.choices)
    name = models.CharField(max_length=32)
    color = models.CharField(max_length=32, validators=[validate_color])


class Tile(models.Model):
    board_config = models.ForeignKey(
        BoardConfig, related_name="tiles", on_delete=models.CASCADE
    )
    position = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=32)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["board_config", "position"], name="unique_board_config_position"
            )
        ]

    def downcast(self) -> Union["Start", "Tax", "Chance", "Jail"]:
        children_names = [c.__name__.lower() for c in Tile.__subclasses__()]
        for c in children_names:
            try:
                return getattr(self, c)
            except AttributeError:
                continue
        raise Exception("Failed to downcast")


class Start(Tile):
    pass


class Tax(Tile):
    pass


class Chance(Tile):
    pass


class Jail(Tile):
    pass


class Police(Tile):
    pass


class Casino(Tile):
    pass


class Property(Tile):
    price = models.PositiveSmallIntegerField()
    mortgage_value = models.PositiveSmallIntegerField()
    house_price = models.PositiveSmallIntegerField()
    rent = models.PositiveSmallIntegerField()
    rent_with_1_house = models.PositiveSmallIntegerField()
    rent_with_2_houses = models.PositiveSmallIntegerField()
    rent_with_3_houses = models.PositiveSmallIntegerField()
    rent_with_4_houses = models.PositiveSmallIntegerField()
    rent_with_5_houses = models.PositiveSmallIntegerField()
    group = models.ForeignKey(PropertyGroup, on_delete=models.CASCADE)

    icon = models.ImageField(upload_to="properties", null=True, blank=True)

    @property
    def mortgage_buyback_price(self) -> int:
        return int(self.mortgage_value * get_config().MORTGAGE_INTEREST_RATE)


class Utility(Tile):
    price = models.IntegerField()
    mortgage_value = models.IntegerField()
    group = models.ForeignKey(
        UtilityGroup, on_delete=models.CASCADE, null=True, blank=True
    )

    icon = models.ImageField(upload_to="properties", null=True, blank=True)


class Game(models.Model):
    class Status(models.TextChoices):
        WAITING = "WAITING"
        PLAYING = "PLAYING"
        FINISHED = "FINISHED"
        ABANDONED = "ABANDONED"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    board_config = models.ForeignKey(
        to=BoardConfig, related_name="games", on_delete=models.DO_NOTHING
    )

    max_players = models.IntegerField(
        default=2,
        validators=[MinValueValidator(2, "Game should have more than 2 players")],
    )
    turn = models.PositiveSmallIntegerField(default=0)
    current_player = models.ForeignKey(
        "game.Player",
        related_name="current_player",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.WAITING
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(max_players__gte=2), name="max_players_gte_2"
            ),
        ]

    def __str__(self):
        return str(self.uuid)


class Player(models.Model):
    class Color(models.TextChoices):
        BLUE = "blue"
        RED = "red"
        GREEN = "green"
        YELLOW = "yellow"

    class Status(models.TextChoices):
        WAITING = "waiting"
        PLAYING = "playing"
        WON = "won"
        LOST = "lost"
        TIMEOUT = "timeout"

    ACTIVE_STATUSES = (Status.WAITING.value, Status.PLAYING.value)

    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, related_name="players", on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(default=0)
    cash = models.IntegerField(default=get_config().STARTING_CASH)
    color = models.CharField(
        max_length=12, choices=Color.choices, null=True, blank=True
    )
    rolled_double = models.BooleanField(default=False)
    double_count = models.PositiveSmallIntegerField(default=0)
    in_jail = models.BooleanField(default=False)
    jail_turns = models.PositiveSmallIntegerField(default=0)
    move_backwards = models.BooleanField(default=False)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.WAITING
    )

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "game"], name="unique_user_game"),
            models.UniqueConstraint(
                fields=["color", "game"], name="unique_color_per_game"
            ),
        ]

    @property
    def is_active(self):
        return self.status in self.Status.ACTIVE_STATUSES

    def move_forward(self, amount: int) -> int:
        """
        Moves player forward by amount of tiles and returns new position
        """
        self.position = (self.position + amount) % 40
        return self.position

    def move_backward(self, amount: int) -> int:
        """
        Moves player backward by amount of tiles and returns new position
        """
        self.position = (self.position - amount) % 40
        return self.position

    @property
    def exceded_doubles(self) -> bool:
        return self.double_count > get_config().MAX_DOUBLES

    def __str__(self):
        return f"{self.user.user_id} in {self.game.uuid}"


class Ownership(models.Model):
    game = models.ForeignKey(Game, related_name="ownerships", on_delete=models.CASCADE)
    player = models.ForeignKey(
        Player, related_name="owned_properties", on_delete=models.CASCADE
    )
    tile = models.ForeignKey(Tile, on_delete=models.CASCADE)
    houses = models.IntegerField(default=0)
    mortgaged = models.BooleanField(default=False)
    mortage_last_turn = models.IntegerField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["game", "tile"], name="unique_game_tile_in_ownership"
            )
        ]

    def clean(self):
        super().clean()
        if not isinstance(self.tile, (Property, Utility)):
            raise ValidationError(
                {"tile": "Tile for ownership must by either Property or Utility"}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class GameEvent(models.Model):
    class Types(models.TextChoices):
        PLAYER_JOINED = "player.joined"
        PLAYER_ACTION = "player.action"
        PLAYER_LEAVE = "player.leave"

    event_type = models.CharField(max_length=32, choices=Types.choices)
    extra_data = models.JSONField(default=dict)

import uuid
from typing import Union

from django.db import models
from django.db.models import Q, QuerySet, Max, Min, Sum
from django.db import IntegrityError
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from bot.models import TelegramUser
from .utils import validate_color
from .exceptions import GameException


class BoardConfig(models.Model):
    class Names(models.TextChoices):
        CLASSIC = "classic"

    name = models.CharField(choices=Names.choices, max_length=32, unique=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)


class PropertyGroup(models.Model):
    board_config = models.ForeignKey(BoardConfig, related_name="property_groups", on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    color = models.CharField(max_length=32, validators=[validate_color])

    def __str__(self):
        return self.name


class UtilityGroup(models.Model):
    class Types(models.TextChoices):
        UTILITY_1 = "UTILITY_1"
        UTILITY_2 = "UTILITY_2"

    board_config = models.ForeignKey(BoardConfig, related_name="utility_groups", on_delete=models.CASCADE)
    type = models.CharField(max_length=32, choices=Types.choices)
    name = models.CharField(max_length=32)
    color = models.CharField(max_length=32, validators=[validate_color])


class Tile(models.Model):
    board_config = models.ForeignKey(BoardConfig, related_name="tiles", on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=32)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["board_config", "position"], name="unique_board_config_position")
        ]

    def downcast(self) -> Union["Start", "Tax", "Chance", "Jail", "Property", "Utility"]:
        children_names = [c.__name__.lower() for c in Tile.__subclasses__()]
        for c in children_names:
            try:
                return getattr(self, c)
            except AttributeError:
                continue
        raise Exception("Failed to downcast")

    def check_if_buyable(self, game: "Game") -> bool:
        return not self.ownerships.filter(game=game).exists()


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
    rent_with_1_houses = models.PositiveSmallIntegerField()
    rent_with_2_houses = models.PositiveSmallIntegerField()
    rent_with_3_houses = models.PositiveSmallIntegerField()
    rent_with_4_houses = models.PositiveSmallIntegerField()
    rent_with_5_houses = models.PositiveSmallIntegerField()
    group = models.ForeignKey(PropertyGroup, on_delete=models.CASCADE, related_name="properties")

    icon = models.ImageField(upload_to="properties", null=True, blank=True)

    # @property
    # def mortgage_buyback_price(self) -> int:
    #     return int(self.mortgage_value * get_config().MORTGAGE_INTEREST_RATE)


class Utility(Tile):
    price = models.IntegerField()
    mortgage_value = models.IntegerField()
    group = models.ForeignKey(UtilityGroup, on_delete=models.CASCADE)
    rent = models.PositiveIntegerField(default=0)

    icon = models.ImageField(upload_to="properties", null=True, blank=True)


class Game(models.Model):
    class Status(models.TextChoices):
        WAITING = "WAITING"
        PLAYING = "PLAYING"
        FINISHED = "FINISHED"
        ABANDONED = "ABANDONED"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    board_config = models.ForeignKey(to=BoardConfig, related_name="games", on_delete=models.DO_NOTHING)

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

    status = models.CharField(max_length=16, choices=Status.choices, default=Status.WAITING)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(max_players__gte=2), name="max_players_gte_2"),
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
    cash = models.IntegerField()
    color = models.CharField(max_length=12, choices=Color.choices)
    rolled_double = models.BooleanField(default=False)
    double_count = models.PositiveSmallIntegerField(default=0)
    in_jail = models.BooleanField(default=False)
    jail_turns = models.PositiveSmallIntegerField(default=0)
    move_backwards = models.BooleanField(default=False)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.WAITING)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "game"], name="unique_user_game"),
            models.UniqueConstraint(fields=["color", "game"], name="unique_color_per_game"),
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

    def check_exceded_doubles(self, max_doubles: int) -> bool:
        return self.double_count > max_doubles

    @property
    def pending_action(self) -> "PendingAction | None":
        return self.pending_actions.filter(resolved_at__isnull=True).first()

    def get_next_utility(self) -> Utility | None:
        utils = Utility.objects.filter(
            board_config=self.game.board_config, group__type=UtilityGroup.Types.UTILITY_1
        )
        next_util = utils.filter(position__gt=self.position).order_by("position").first()
        return next_util or utils.order_by("position").first()

    @property
    def houses_owned(self) -> int:
        houses_owned = self.ownerships.all().aggregate(Sum("houses"))["houses__sum"]
        return houses_owned

    def __str__(self):
        return f"{self.user.user_id} in {self.game.uuid}"


class Ownership(models.Model):
    game = models.ForeignKey(Game, related_name="ownerships", on_delete=models.CASCADE)
    player = models.ForeignKey(Player, related_name="ownerships", on_delete=models.CASCADE)
    tile = models.ForeignKey(Tile, related_name="ownerships", on_delete=models.CASCADE)
    houses = models.IntegerField(default=0)
    mortgaged = models.BooleanField(default=False)
    mortage_last_turn = models.IntegerField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["game", "tile"], name="unique_game_tile_in_ownership")]

    def clean(self):
        super().clean()
        downcasted_tile = self.tile.downcast()
        if not isinstance(downcasted_tile, (Property, Utility)):
            raise ValidationError({"tile": "Tile for ownership must by either Property or Utility"})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def calculate_rent(self, dice_sum: int | None = None) -> int:
        downcasted_tile = self.tile.downcast()
        if isinstance(downcasted_tile, Utility):
            if downcasted_tile.group.type == UtilityGroup.Types.UTILITY_1:
                multiplier = self.get_ownerships_in_the_group().count()
                return downcasted_tile.rent * multiplier
            elif downcasted_tile.group.type == UtilityGroup.Types.UTILITY_2:
                if dice_sum is None:
                    raise GameException("You have to pass dice_sum for calculating rent on utility type 2")

                if self.owns_entire_group():
                    return dice_sum * 10
                else:
                    return dice_sum * 4
        elif isinstance(downcasted_tile, Property):
            attr = f"rent_with_{self.houses}_houses"
            if self.houses == 0:
                return downcasted_tile.rent

            rent = getattr(downcasted_tile, attr, None)
            if rent is None:
                raise GameException(
                    f"Could not determine rent for property pk:downcasted_tile.pk attr:{attr}"
                )

            return rent

        raise GameException("Can not calculate rent for not buyable tile")

    def get_ownerships_in_the_group(self) -> QuerySet["Ownership"]:
        downcasted_tile = self.tile.downcast()
        if isinstance(downcasted_tile, Property):
            tiles_in_group = Property.objects.filter(group=downcasted_tile.group)
        elif isinstance(downcasted_tile, Utility):
            tiles_in_group = Utility.objects.filter(group=downcasted_tile.group)  # type: ignore[assignment]
        else:
            raise IntegrityError("Ownership on something other then Property or Utility!")

        ownerships = Ownership.objects.filter(
            player=self.player, game=self.game, tile__in=tiles_in_group, mortgaged=False
        )

        return ownerships

    def owns_entire_group(self) -> bool:
        """
        Checks if the player owns every property in the group.
        """
        downcasted_tile = self.tile.downcast()
        if isinstance(downcasted_tile, Property):
            tiles_in_group = Property.objects.filter(group=downcasted_tile.group)
        elif isinstance(downcasted_tile, Utility):
            tiles_in_group = Utility.objects.filter(group=downcasted_tile.group)  # type: ignore[assignment]
        else:
            raise IntegrityError("Ownership on something other then Property or Utility!")

        ownerships = self.get_ownerships_in_the_group()
        return ownerships.count() == tiles_in_group.count()

    def get_group_lvl_max(self) -> int:
        """
        Return maximum houses in group
        """
        downcasted_tile = self.tile.downcast()
        if not isinstance(downcasted_tile, Property):
            raise GameException("You can get group_up lvl only of Property")

        # tiles_in_group = Property.objects.filter(group=downcasted_tile.group)
        ownerships = self.get_ownerships_in_the_group()
        max_houses = ownerships.aggregate(Max("houses"))
        return max_houses["houses__max"]

    def get_group_lvl_min(self) -> int:
        """
        Return maximum houses in group
        """
        downcasted_tile = self.tile.downcast()
        if not isinstance(downcasted_tile, Property):
            raise GameException("You can get group_up lvl only of Property")

        # tiles_in_group = Property.objects.filter(group=downcasted_tile.group)
        ownerships = self.get_ownerships_in_the_group()
        min_houses = ownerships.aggregate(Min("houses"))
        return min_houses["houses__min"]

    def check_can_improve(self) -> bool:
        """Check if player can build house on this ownership"""
        if self.houses + 1 > 5:
            return False

        min_lvl = self.get_group_lvl_min()
        max_lvl = self.get_group_lvl_max()

        if self.houses + 1 > max_lvl:
            max_lvl += 1

        diff = max_lvl - min_lvl
        if diff >= 2:
            return False

        return True

    def check_can_degrade(self) -> bool:
        """Check if player can remove house on this ownership"""
        if self.houses - 1 < 0:
            return False

        min_lvl = self.get_group_lvl_min()
        max_lvl = self.get_group_lvl_max()

        new_level = self.houses - 1
        if new_level < min_lvl:
            min_lvl = new_level

        diff = max_lvl - min_lvl
        if diff >= 2:
            return False

        return True


class GameEvent(models.Model):
    class Types(models.TextChoices):
        PLAYER_JOINED = "player.joined"
        PLAYER_ACTION = "player.action"
        PLAYER_LEAVE = "player.leave"
        PLAYER_ROLL_DICE = "player.roll_dice"
        PLAYER_MOVE = "player.move"
        GAME_STARTED = "game.started"
        GAME_AUCTION_FLOP = "game.auction_flop"
        LANDED_ON_OWN_PROPERTY = "game.landed_on_own_property"
        PLAYER_WON_CASINO = "player.won_casino"
        PLAYER_LOST_CASINO = "player.lost_casino"
        GOT_CHANCE_CARD = "player.got_chance_card"

    game = models.ForeignKey(to=Game, related_name="events", on_delete=models.CASCADE)
    event_type = models.CharField(max_length=32, choices=Types.choices)
    extra_data = models.JSONField(default=dict)


class PendingAction(models.Model):
    class Types(models.TextChoices):
        ROLL_DICE = "roll_dice"
        BUY_PROPERTY = "buy_property"
        PAY_RENT = "pay_rent"
        PAY_TAX = "pay_tax"
        PAY_REPAIRS = "pay_repairs"
        IN_AUCTION = "IN_AUCTION"
        IN_CASINO = "IN_CASINO"
        IN_TRADE = "IN_TRADE"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    # game = models.ForeignKey(to=Game, related_name="pending_actions", on_delete=models.DO_NOTHING)
    player = models.ForeignKey(to=Player, related_name="pending_actions", on_delete=models.CASCADE)
    action_type = models.CharField(max_length=32, choices=Types.choices)

    action_data = models.JSONField(default=dict)

    created = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    resolved_at = models.DateTimeField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["player"],
                condition=Q(resolved_at__isnull=True),
                name="unique_active_pending_action_per_player",
            )
        ]


class ChanceCard(models.Model):
    class Action(models.TextChoices):
        MOVE_TO = "MOVE_TO"
        MOVE_RELATIVE = "MOVE_RELATIVE"
        MOVE_TO_NEXT_UTILITY = "MOVE_TO_NEXT_UTILITY"
        PAY_BANK = "PAY_BANK"
        COLLECT_BANK = "COLLECT_BANK"
        COLLECT_PLAYERS = "COLLECT_PLAYERS"
        GO_TO_JAIL = "GO_TO_JAIL"
        REPAIRS = "REPAIRS"
        # GET_OUT_OF_JAIL = "GET_OUT_OF_JAIL"

    board_config = models.ForeignKey(to=BoardConfig, related_name="chance_cards", on_delete=models.CASCADE)

    description = models.CharField(max_length=128)
    action = models.CharField(max_length=32, choices=Action.choices)
    amount = models.PositiveIntegerField(null=True, blank=True, help_text="Cash value involved (if any)")
    position = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="Board position for MOVE_TO action"
    )
    position_relative = models.SmallIntegerField(
        null=True, blank=True, help_text="Relative move (+/- spaces) for MOVE_RELATIVE"
    )

    def __str__(self):
        return f"Chance: {self.description[:40]}"

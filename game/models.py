from django.db import models
from bot.models import TelegramUser
import uuid

# Create your models here.
class Game(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    max_players = models.IntegerField(default=2)
    turn = models.IntegerField(default=0)

    WAITING = 'WAITING'
    PLAYING = 'PLAYING'
    FINISHED = 'FINISHED'
    STATUS_CHOICES = [
        (WAITING, 'Waiting'),
        (PLAYING, 'Playing'),
        (FINISHED, 'Finished'),
    ]
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=WAITING)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Player(models.Model):
    class Meta:
        unique_together = ('user', 'game')

    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, related_name='players', on_delete=models.CASCADE)

    position = models.IntegerField(default=0)
    cash = models.IntegerField(default=1500)
    color = models.CharField(max_length=10, null=True, blank=True)
    in_jail = models.BooleanField(default=False)
    jail_turns = models.IntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} in {self.game.name}"


class Tile(models.Model):

    POSITION_CHOICES = [(i, i) for i in range(40)]

    START = 'START'
    PROPERTY = 'PROPERTY'
    CHANCE = 'CHANCE'
    TAX = 'TAX'
    UTILITY = 'UTILITY'
    JAIL = 'JAIL'
    CASINO = 'CASINO'
    POLICE = 'POLICE'

    TYPE_CHOICES = [
        (START, 'Start'),
        (PROPERTY, 'Property'),
        (CHANCE, 'Chance'),
        (TAX, 'Tax'),
        (UTILITY, 'Utility'),
        (JAIL, 'Jail'),
        (CASINO, 'Casino'),
        (POLICE, 'Police'),
    ]

    position = models.IntegerField(unique=True, choices=POSITION_CHOICES)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.position})"


class PropertyGroup(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Property(models.Model):
    class Meta:
        unique_together = ('board_space', 'group')

    board_space = models.OneToOneField(Tile, on_delete=models.CASCADE)
    price = models.IntegerField()
    mortgage_value = models.IntegerField()
    house_price = models.IntegerField(null=True, blank=True)
    rent = models.IntegerField()
    rent_with_1_house = models.IntegerField()
    rent_with_2_houses = models.IntegerField()
    rent_with_3_houses = models.IntegerField()
    rent_with_4_houses = models.IntegerField()
    rent_with_5_houses = models.IntegerField()
    group = models.ForeignKey(PropertyGroup, on_delete=models.CASCADE, null=True, blank=True)

    icon = models.ImageField(upload_to='properties', null=True, blank=True)

    def __str__(self):
        return self.board_space.name
    
class Utility(models.Model):

    UTILITY_1 = 'UTILITY_1'
    UTILITY_2 = 'UTILITY_2'

    TYPES = [
        (UTILITY_1, 'Utility 1'),
        (UTILITY_2, 'Utility 2'),
    ]
    class Meta:
        unique_together = ('board_space', 'group')
    
    board_space = models.OneToOneField(Tile, on_delete=models.CASCADE)
    price = models.IntegerField()
    mortgage_value = models.IntegerField()
    type = models.CharField(max_length=20, choices=TYPES)
    group = models.ForeignKey(PropertyGroup, on_delete=models.CASCADE, null=True, blank=True)

    icon = models.ImageField(upload_to='properties', null=True, blank=True)

    def __str__(self):
        return self.board_space.name


class Ownership(models.Model):
    class Meta:
        unique_together = ('player', 'property')

    player = models.ForeignKey(Player, related_name='owned_properties', on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    houses = models.IntegerField(default=0)
    mortgaged = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.property.board_space.name} owned by {self.player.user.username}"


class Card(models.Model):
    CARD_TYPES = [
        ('chance', 'Chance'),
        ('community_chest', 'Community Chest'),
    ]

    type = models.CharField(max_length=20, choices=CARD_TYPES)
    description = models.TextField()
    action = models.CharField(max_length=50)
    value = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_type_display()} Card: {self.description}"


class Transaction(models.Model):
    game = models.ForeignKey(Game, related_name='transactions', on_delete=models.CASCADE)
    from_player = models.ForeignKey(
        Player, related_name='transactions_sent', null=True, blank=True, on_delete=models.SET_NULL
    )
    to_player = models.ForeignKey(
        Player, related_name='transactions_received', null=True, blank=True, on_delete=models.SET_NULL
    )
    amount = models.IntegerField()
    description = models.TextField()

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction in {self.game.name} - {self.description}"


# class Trade(models.Model):
#     TRADE_STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('accepted', 'Accepted'),
#         ('declined', 'Declined'),
#     ]

#     game = models.ForeignKey(Game, related_name='trades', on_delete=models.CASCADE)
#     initiator = models.ForeignKey(Player, related_name='trades_initiated', on_delete=models.CASCADE)
#     recipient = models.ForeignKey(Player, related_name='trades_received', on_delete=models.CASCADE)
#     offered_properties = models.ManyToManyField(Property, related_name='offered_in_trades')
#     requested_properties = models.ManyToManyField(Property, related_name='requested_in_trades')
#     offered_cash = models.IntegerField(default=0)
#     requested_cash = models.IntegerField(default=0)
#     status = models.CharField(max_length=20, choices=TRADE_STATUS_CHOICES, default='pending')
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Trade from {self.initiator.user.username} to {self.recipient.user.username} in {self.game.name}"

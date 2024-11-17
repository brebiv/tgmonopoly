from django.db import models
from bot.models import TelegramUser
import random
import uuid

from . import config

# Create your models here.
class Game(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4)
    max_players = models.IntegerField(default=2)
    turn = models.IntegerField(default=0)
    current_player = models.ForeignKey('game.Player', related_name='current_player', on_delete=models.CASCADE, null=True, blank=True)

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
        return str(self.uuid)


class PropertyGroup(models.Model):

    UTILITIES_1 = 'UTILITIES_1'
    UTILITIES_2 = 'UTILITIES_2'
    TECH = 'TECH'
    FINANCE = 'FINANCE'
    MEDECINE = 'MEDECINE'
    OIL = 'OIL'
    AUTOMOBILE = 'AUTOMOBILE'
    COMMUNICATION = 'COMMUNICATION'
    FOOD = 'FOOD'
    CLOTH = 'CLOTH'

    PROPERTY_GROUP_CHOICES = [
        (UTILITIES_1, 'Utilities 1'),
        (UTILITIES_2, 'Utilities 2'),
        (TECH, 'Tech'),
        (FINANCE, 'Finance'),
        (MEDECINE, 'Medecine'),
        (OIL, 'Oil'),
        (AUTOMOBILE, 'Automobile'),
        (COMMUNICATION, 'Communication'),
        (FOOD, 'Food'),
        (CLOTH, 'Cloth'),
    ]

    name = models.CharField(max_length=50, choices=PROPERTY_GROUP_CHOICES)
    color = models.CharField(max_length=10)

    def __str__(self):
        return self.name


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


class Property(models.Model):
    class Meta:
        unique_together = ('board_space', 'group')

    board_space = models.OneToOneField(Tile, on_delete=models.CASCADE)
    price = models.IntegerField()
    mortgage_value = models.IntegerField()
    house_price = models.IntegerField(null=True, blank=True)
    rent = models.IntegerField()
    rent_with_1_house = models.IntegerField(null=True, blank=True)
    rent_with_2_houses = models.IntegerField(null=True, blank=True)
    rent_with_3_houses = models.IntegerField(null=True, blank=True)
    rent_with_4_houses = models.IntegerField(null=True, blank=True)
    rent_with_5_houses = models.IntegerField(null=True, blank=True)
    group = models.ForeignKey(PropertyGroup, on_delete=models.CASCADE, null=True, blank=True)

    icon = models.ImageField(upload_to='properties', null=True, blank=True)
    svg_icon = models.CharField(max_length=50, choices=config.AvailableSVGIcons, null=True, blank=True)

    @property
    def buyout_price(self) -> int:
        return int(self.mortgage_value * config.MORTAGE_INTEREST_RATE)

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


class Player(models.Model):
    class Meta:
        unique_together = ('user', 'game')

    BLUE = 'blue'
    RED = 'red'
    GREEN = 'green'
    YELLOW = 'yellow'
    
    COLOR_CHOICES = [
        (BLUE, 'Blue'),
        (RED, 'Red'),
        (GREEN, 'Green'),
        (YELLOW, 'Yellow'),
    ]

    WAITING = 'waiting'
    PLAYING = 'playing'
    WON = 'won'
    LOST = 'lost'
    TIMEOUT = 'timeout'

    STATUS_CHOICES = [
        (WAITING, 'Waiting'),
        (PLAYING, 'Playing'),
        (WON, 'Won'),
        (LOST, 'Lost'),
        (TIMEOUT, 'Timeout'),
    ]

    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, related_name='players', on_delete=models.CASCADE)

    position = models.IntegerField(default=0)
    cash = models.IntegerField(default=1500)
    color = models.CharField(max_length=10, choices=COLOR_CHOICES, null=True, blank=True)
    in_jail = models.BooleanField(default=False)
    jail_turns = models.IntegerField(default=0)
    move_backwards = models.BooleanField(default=False)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=WAITING)

    created = models.DateTimeField(auto_now_add=True)

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
    
    def owns_entire_group(self, group: PropertyGroup) -> bool:
        """
        Checks if the player owns every property in the given property group
        """
        total_properties_in_group = Property.objects.filter(group=group).count()

        player_owned_properties_in_group = Ownership.objects.filter(
            player=self,
            game=self.game,
            property__group=group,
            mortgaged=False
        ).count()

        return total_properties_in_group == player_owned_properties_in_group
    
    def houses_owned(self) -> int:
        """
        Returns the number of houses owned by the player.
        """
        ownerships = Ownership.objects.filter(player=self, mortgaged=False)
        amount_of_houses = 0

        for ownership in ownerships:
            amount_of_houses += ownership.houses

        return amount_of_houses

    # def can_build_house(self, property: Property) -> list[bool, str]:
    #     """
    #     Checks if the player can build a house on the given property.
    #     Houses must be built evenly across all properties in the group.
    #     Returns a list (can_build: bool, reason: str).
    #     """
    #     group = property.group

    #     properties_in_group = Property.objects.filter(group=group)

    #     ownerships = Ownership.objects.filter(
    #         player=self,
    #         game=self.game,
    #         property__in=properties_in_group
    #     )

    #     if ownerships.count() != properties_in_group.count():
    #         return False, "You must own all properties in this group to build houses."

    #     if any(ownership.mortgaged for ownership in ownerships):
    #         return False, "You cannot build houses while properties in the group are mortgaged."
        
    #     if self.cash < property.house_price:
    #         return False, "You do not have enough cash to buy a house on this property."

    #     houses_on_properties = {
    #         ownership.property.id: ownership.houses
    #         for ownership in ownerships
    #     }

    #     try:
    #         property_ownership = ownerships.get(property=property)
    #     except Ownership.DoesNotExist:
    #         return False, "You do not own this property."
        

    #     if property_ownership.houses >= config.MAX_HOUSES:
    #         return False, "This property already has the maximum number of houses."

    #     min_houses = min(houses_on_properties.values())

    #     if property_ownership.houses > min_houses:
    #         return False, "You must build houses evenly across the group. Build on properties with fewer houses first."

    #     return True, "You can build a house on this property."


    def __str__(self):
        return f"{self.user.user_id} in {self.game.uuid}"


class Ownership(models.Model):
    class Meta:
        unique_together = ('game', 'property')

    game = models.ForeignKey(Game, related_name='ownerships', on_delete=models.CASCADE)
    player = models.ForeignKey(Player, related_name='owned_properties', on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    houses = models.IntegerField(default=0)
    mortgaged = models.BooleanField(default=False)
    mortage_last_turn = models.IntegerField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)

    def calculate_rent(self, dice_sum=1) -> int:
        if self.property.group.name == PropertyGroup.UTILITIES_1:
            ownerships = Ownership.objects.filter(
                player=self.player,
                game=self.game,
                property__group=self.property.group
            )

            number_of_utilities_owned = ownerships.count()

            return self.property.rent * number_of_utilities_owned
        elif self.property.group.name == PropertyGroup.UTILITIES_2:
            if self.owns_entire_group():
                return self.property.rent * 2 * dice_sum
            else:
                return self.property.rent * dice_sum
        else:
            if self.houses == 0:
                print("Self rent", self.property.rent)
                return self.property.rent
            elif self.houses == 1:
                return self.property.rent_with_1_house
            elif self.houses == 2:
                return self.property.rent_with_2_houses
            elif self.houses == 3:
                return self.property.rent_with_3_houses
            elif self.houses == 4:
                return self.property.rent_with_4_houses
            elif self.houses == 5:
                return self.property.rent_with_5_houses
        
    def can_build_house(self) -> list[bool, str]:
        """
        Checks if the player can build a house on this property.
        Houses must be built evenly across all properties in the group.
        Returns a list (can_build: bool, reason: str).
        """
        if self.property.group.name == PropertyGroup.UTILITIES_1 \
            or self.property.group.name == PropertyGroup.UTILITIES_2:
            return False, "You can't build houses on Utilities"

        group = self.property.group

        properties_in_group = Property.objects.filter(group=group)

        ownerships = Ownership.objects.filter(
            player=self.player,
            game=self.game,
            property__in=properties_in_group
        )

        last_effect = GameEffect.objects.filter(player=self.player).last()

        if last_effect:
            if last_effect.name == GameEffect.ASK_BUY:
                return False, "You can't buy a house during the ask buy effect"
            if last_effect.name == GameEffect.PAY_RENT:
                return False, "You can't buy a house during the pay rent effect"

            if last_effect.effect_data:
                if last_effect.effect_data.get('bought_house', False):
                    return False, "You can't buy a house twice per turn"

        if ownerships.count() != properties_in_group.count():
            return False, "You must own all properties in this group to build houses."

        if any(ownership.mortgaged for ownership in ownerships):
            return False, "You cannot build houses while properties in the group are mortgaged."

        if self.player.cash < self.property.house_price:
            return False, "You do not have enough cash to buy a house on this property."

        houses_on_properties = {
            ownership.property.id: ownership.houses
            for ownership in ownerships
        }

        if self.houses >= config.MAX_HOUSES:
            return False, "This property already has the maximum number of houses."

        min_houses = min(houses_on_properties.values())

        if self.houses > min_houses:
            return False, "You must build houses evenly across the group. Build on properties with fewer houses first."

        return True, "You can build a house on this property."
    
    def can_sell_house(self) -> list[bool, str]:
        """
        Checks if the player can sell a house on this property.
        Houses must be sold evenly across all properties in the group.
        Returns a list (can_sell: bool, reason: str).
        """
        if self.property.group.name == PropertyGroup.UTILITIES_1 \
            or self.property.group.name == PropertyGroup.UTILITIES_2:
            return False, "You can't build houses on Utilities"

        group = self.property.group

        properties_in_group = Property.objects.filter(group=group)

        ownerships = Ownership.objects.filter(
            player=self.player,
            game=self.game,
            property__in=properties_in_group
        )

        if ownerships.count() != properties_in_group.count():
            return False, "You must own all properties in this group to sell houses."

        houses_on_properties = {
            ownership.property.id: ownership.houses
            for ownership in ownerships
        }

        if self.houses == 0:
            return False, "There are no houses on this property to sell."

        max_houses = max(houses_on_properties.values())

        if self.houses < max_houses:
            return False, "You must sell houses evenly across the group. Sell houses from properties with more houses first."

        return True, "You can sell a house on this property."

    def owns_entire_group(self) -> bool:
        """
        Checks if the player owns every property in the group.
        """
        properties_in_group = Property.objects.filter(group=self.property.group)
        ownerships = Ownership.objects.filter(
            player=self.player,
            game=self.game,
            property__in=properties_in_group,
            mortgaged=False
        )

        return ownerships.count() == properties_in_group.count()

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
        return f"Transaction in {self.game.uuid} - {self.description}"


class GameEffect(models.Model):

    ROLL_DICE = 'roll_dice'
    ASK_BUY = 'ask_buy'
    PAY_RENT = 'pay_rent'
    PAY_REPAIRS = 'pay_repairs'
    IN_CASINO = 'in_casino'

    game = models.ForeignKey(Game, related_name='effects', on_delete=models.CASCADE)
    player = models.ForeignKey(Player, related_name='effects', on_delete=models.CASCADE)
    name = models.CharField(max_length=20, choices=config.GameEffectTypes)
    description = models.TextField(null=True, blank=True)
    effect_data = models.JSONField(null=True, blank=True)
    task_id = models.CharField(max_length=255, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"GameEffect in {self.game.uuid} - {self.name}"


# class GameEvent(models.Model):

#     START_GAME = 'start_game'
#     ROLL_DICE = 'roll_dice'
#     MOVE_PLAYER = 'move_player'
#     BUY_PROPERTY = 'buy_property'
#     PASSED_START = 'passed_start'
#     STEPPED_ON_OWN_PROPERTY = 'stepped_on_own_property'
#     PAY_RENT = 'pay_rent'
#     GO_TO_PRISON = 'go_to_prison'
#     RELEASE_FROM_PRISON = 'release_from_prison'
#     PRISON_RELEASE_FAIL = 'prison_release_fail'
#     PAY_FOR_PRISON = 'pay_for_prison'
#     MORTAGE_PROPERTY = 'mortage_property'
#     BUYOUT_PROPERTY = 'buyout_property'
#     BUY_HOUSE = 'buy_house'
#     SELL_HOUSE = 'sell_house'
#     CHANCE_CARD = 'chance_card'
#     PAY_TO_BANK = 'pay_to_bank'
#     GO_TO_CASINO = 'go_to_casino'
#     WON_CASINO = 'won_casino'
#     LOST_CASINO = 'lost_casino'

#     TYPE = [
#         (START_GAME, 'Start Game'),
#         (ROLL_DICE, 'Roll Dice'),
#         (MOVE_PLAYER, 'Move Player'),
#         (BUY_PROPERTY, 'Buy Property'),
#         (PASSED_START, 'Passed Start'),
#         (STEPPED_ON_OWN_PROPERTY, 'Stepped on Own Property'),
#         (PAY_RENT, 'Pay Rent'),
#         (GO_TO_PRISON, 'Go to Prison'),
#         (RELEASE_FROM_PRISON, 'Release from Prison'),
#         (PRISON_RELEASE_FAIL, 'Prison Release Fail'),
#         (PAY_FOR_PRISON, 'Pay for Prison'),
#         (MORTAGE_PROPERTY, 'Mortage Property'),
#         (BUYOUT_PROPERTY, 'Buyout Property'),
#         (BUY_HOUSE, 'Buy House'),
#         (SELL_HOUSE, 'Sell House'),
#         (CHANCE_CARD, 'Chance Card'),
#         (PAY_TO_BANK, 'Pay to Bank'),
#         (GO_TO_CASINO, 'Go to Casino'),
#         (WON_CASINO, 'Won Casino'),
#         (LOST_CASINO, 'Lost Casino'),
#     ]

#     game = models.ForeignKey(Game, related_name='log', on_delete=models.CASCADE)
#     player = models.ForeignKey(Player, related_name='log', on_delete=models.CASCADE)
#     type = models.CharField(max_length=50, choices=TYPE)
#     data = models.JSONField(null=True, blank=True)
#     created = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"GameEvent in {self.game.uuid} - {self.type}"


class ChanceCard(models.Model):

    MOVE = 'MOVE'
    MOVE_BACKWARDS = 'MOVE_BACKWARDS'
    MONEY = 'MONEY'
    MONEY_TO_PLAYER = 'MONEY_TO_PLAYER'
    GO_TO_JAIL = 'GO_TO_JAIL'
    FREE_JAIL = 'FREE_JAIL'
    REPAIRS = 'REPAIRS'
    MISC = 'MISC'

    CARD_TYPE_CHOICES = [
        (MOVE, 'Move'),
        (MOVE_BACKWARDS, 'Move Backwards'),
        (MONEY, 'Money'),
        (MONEY_TO_PLAYER, 'Money to Player'),
        (GO_TO_JAIL, 'Go to Jail'),
        (FREE_JAIL, 'Get Out of Jail Free'),
        (REPAIRS, 'Repairs'),
        (MISC, 'Miscellaneous'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    card_type = models.CharField(max_length=16, choices=CARD_TYPE_CHOICES)
    details = models.JSONField(default=dict, blank=True)

    @staticmethod
    def get_random_card() -> 'ChanceCard':
        cards = ChanceCard.objects.all()
        return random.choice(cards)

    def __str__(self):
        return f"{self.title}"


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

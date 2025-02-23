from django.contrib import admin
from .models import (
    Game, Player, Tile, PropertyGroup, Property, Utility,
    Ownership, Card, Transaction, ChanceCard
)

# Register your models here.
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'max_players', 'turn', 'status', 'created')
    list_filter = ('status',)
    search_fields = ('id',)
    date_hierarchy = 'created'
    ordering = ('-created',)

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'position', 'cash', 'in_jail', 'jail_turns', 'created')
    list_filter = ('game', 'in_jail')
    search_fields = ('user__username', 'game__id')
    ordering = ('-created',)
    raw_id_fields = ('user', 'game')

@admin.register(Tile)
class TileAdmin(admin.ModelAdmin):
    list_display = ('position', 'name', 'type')
    list_filter = ('type',)
    search_fields = ('name',)
    ordering = ('position',)

@admin.register(PropertyGroup)
class PropertyGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    search_fields = ('name',)

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('board_space', 'price', 'mortgage_value', 'house_price',)
    list_filter = ('group',)
    search_fields = ('board_space__name',)
    ordering = ('board_space__position',)
    raw_id_fields = ('board_space',)

@admin.register(Utility)
class UtilityAdmin(admin.ModelAdmin):
    list_display = ('board_space', 'price', 'mortgage_value', 'type')
    search_fields = ('board_space__name',)
    ordering = ('board_space__position',)
    # raw_id_fields = ('board_space', 'group')

@admin.register(Ownership)
class OwnershipAdmin(admin.ModelAdmin):
    list_display = ('player', 'property', 'houses', 'mortgaged', 'created')
    list_filter = ('mortgaged',)
    search_fields = ('player__user__username', 'property__board_space__name')
    ordering = ('-created',)
    raw_id_fields = ('player', 'property')

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('type', 'description', 'action', 'value')
    list_filter = ('type',)
    search_fields = ('description',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('game', 'from_player', 'to_player', 'amount', 'description', 'created')
    list_filter = ('game',)
    search_fields = ('description', 'from_player__user__username', 'to_player__user__username')
    date_hierarchy = 'created'
    raw_id_fields = ('from_player', 'to_player', 'game')
    ordering = ('-created',)


@admin.register(ChanceCard)
class ChanceCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'card_type', 'details', 'active')
    search_fields = ('title', 'details')

# @admin.register(Trade)
# class TradeAdmin(admin.ModelAdmin):
#     list_display = ('game', 'initiator', 'recipient', 'offered_cash', 'requested_cash', 'status', 'created_at')
#     list_filter = ('status', 'game')
#     search_fields = ('initiator__user__username', 'recipient__user__username')
#     raw_id_fields = ('initiator', 'recipient', 'game')
#     ordering = ('-created_at',)

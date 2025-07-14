from django.contrib import admin
from .models import (
    Player,
    Tile,
    Start,
    Tax,
    Chance,
    Jail,
    Police,
    Casino,
    Property,
    Utility,
    PropertyGroup,
    UtilityGroup,
)


# Register your models here.
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("user", "game", "position")
    list_editable = ("position",)

from rest_framework import serializers
from game.models import Tile, Property, Utility, Game, Player
from collections import OrderedDict


class GameEventTypes:
    CONNECTED = 'CONNECTED'


class TileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tile
        fields = ('id', 'position', 'name', 'type', 'propertyData')
    
    propertyData = serializers.SerializerMethodField()
    
    def get_propertyData(self, obj):
        if obj.type == Tile.PROPERTY or obj.type == Tile.UTILITY:
            if obj.type == Tile.PROPERTY:
                try:
                    return PropertySerializer(obj.property).data
                except:
                    return None
            elif obj.type == Tile.UTILITY:
                try:
                    return UtilitySerializer(obj.utility).data
                except:
                    return None
        else:
            return None
        
    def to_representation(self, instance):
        """Removes fields that are null"""
        result = super(TileSerializer, self).to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])



class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = (
            'price', 'mortgage_value', 'house_price', 'rent', 
            'rent_with_1_house', 'rent_with_2_houses', 'rent_with_3_houses', 
            'rent_with_4_houses', 'rent_with_5_houses', 'group_id', 'group_color', 'icon'
        )
    
    group_color = serializers.SerializerMethodField()
    
    def get_group_color(self, obj):
        if obj.group:
            return obj.group.color
        else:
            return None

class UtilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Utility
        fields = (
            'price', 'mortgage_value', 'type', 'group_id', 'group_color', 'icon'
        )
    
    group_color = serializers.SerializerMethodField()
    
    def get_group_color(self, obj):
        if obj.group:
            return obj.group.color
        else:
            return None


class CreateGameSerializer(serializers.Serializer):
    max_players = serializers.IntegerField()


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = (
            'uuid', 'max_players', 'turn', 'status', 'created'
        )

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = (
            'id', 'position', 'cash', 'color', 'in_jail', 'jail_turns'
        )


class GameEventSerializer(serializers.Serializer):
    type = serializers.CharField()

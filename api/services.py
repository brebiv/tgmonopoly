import random

from game.models import Game, Player, GameEffect, Tile, Ownership
from .serializers import GameSerializer, PlayerSerializer
from .types import GameActionType, GameEventType


class GameService:

    @staticmethod
    def _calculate_next_player(game: Game, after_player: Player) -> Player:
        game_players = game.players.all().order_by('created')

        current_index = next((index for index, p in enumerate(game_players) if p == after_player), -1)
        next_index = (current_index + 1) % len(game_players)

        next_player = game_players[next_index]

        # if next_player.state == Player.LOSE or next_player.state == Player.TIMEOUT:
        #     return GameService._calculate_next_player(game, next_player)

        return game_players[next_index]

    @staticmethod
    def start_game(game: Game, player: Player) -> list:
        events = []

        effect = GameEffect.objects.create(
            game=game,
            player=player,
            name=GameEffect.ROLL_DICE,
        )

        game.turn += 1
        game.current_player = player
        game.status = Game.PLAYING
        game.save()

        return [{
            'type': 'game.action',
            'action': GameActionType.START_GAME,
            'player': player.pk,
        },]
    
    @staticmethod
    def roll_dice(game: Game, player: Player) -> list:
        events = []
        dices = [random.randint(1, 6) for _ in range(2)]
        dice_sum = sum(dices)

        events.append({
            'type': 'game.action',
            'action': GameEventType.ROLL_DICE,
            'player': player.pk,
            'dices': dices,
        })

        effect = GameEffect.objects.filter(player=player, name=GameEffect.ROLL_DICE).last()
        effect.delete()

        if player.in_jail:
            pass
        else:
            new_postion = player.move_forward(dice_sum)

            events.append({
                'type': 'game.action',
                'action': GameEventType.MOVE_PLAYER,
                'player': player.pk,
                'position': player.position,
            })

            tile = Tile.objects.get(position=new_postion)
            if tile.type == Tile.PROPERTY:
                try:
                    ownership = Ownership.objects.get(player=player, property=tile.property)
                except Ownership.DoesNotExist:
                    effect = GameEffect.objects.create(
                        game=game,
                        player=player,
                        name=GameEffect.ASK_BUY,
                    )
                else:
                    if ownership.player == player:
                        pass
                    else:
                        effect = GameEffect.objects.create(
                            game=game,
                            player=player,
                            name=GameEffect.PAY_RENT,
                        )
            else:
                effect = GameEffect.objects.create(
                    game=game,
                    player=player,
                    name=GameEffect.ROLL_DICE,
                )

                game.turn += 1
                game.current_player = GameService._calculate_next_player(game, player)

            game.save()
            player.save()

        return events
    
    @staticmethod
    def buy_property(game: Game, player: Player) -> list:
        events = []
        tile = Tile.objects.get(position=player.position)

        if tile.type == Tile.PROPERTY:
            try:
                ownership = Ownership.objects.get(player=player, property=tile.property)
                if ownership.player == player:
                    raise Exception("You already own this property")
                else:
                    raise Exception("You are not the owner of this property")
            except Ownership.DoesNotExist:
                ownership = Ownership.objects.create(
                    game=game,
                    player=player,
                    property=tile.property,
                    houses=tile.property.house_price,
                )
                player.cash -= tile.property.price
                player.save()
                
                tile.property.owner = player
                tile.property.save()

                effect = GameEffect.objects.filter(player=player, name=GameEffect.ASK_BUY).last()
                effect.delete()

                # If double add roll dice effect to current player else to the next one
                # effect = GameEffect.objects.create(
                #     game=game,
                #     player=player,
                #     name=GameEffect.ROLL_DICE,
                # )
                game.turn += 1
                game.current_player = GameService._calculate_next_player(game, player)
                game.save()


                effect = GameEffect.objects.create(
                    game=game,
                    player=game.current_player,
                    name=GameEffect.ROLL_DICE,
                )

                events.append({
                    'type': 'game.action',
                    'action': GameEventType.BUY_PROPERTY,
                    'player': player.pk,
                    'tile': tile.pk,
                })

        return events

import random

from game.models import Game, Player, GameEffect, Tile, Ownership
from .types import GameActionType, GameEventType


class GameService:

    ROUND_TRIP_BONUS = 200

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
            passed_start = player.position + dice_sum >= 40
            new_postion = player.move_forward(dice_sum)

            events.append({
                'type': 'game.action',
                'action': GameEventType.MOVE_PLAYER,
                'player': player.pk,
                'position': player.position,
            })

            if passed_start:
                events.append({
                    'type': 'game.action',
                    'action': GameEventType.PASSED_START,
                    'player': player.pk,
                })
                player.cash += GameService.ROUND_TRIP_BONUS
                player.save()

            tile = Tile.objects.get(position=new_postion)
            if tile.type == Tile.PROPERTY:
                try:
                    ownership = Ownership.objects.get(game=game, property=tile.property)
                except Ownership.DoesNotExist:
                    effect = GameEffect.objects.create(
                        game=game,
                        player=player,
                        name=GameEffect.ASK_BUY,
                        effect_data={
                            'price': tile.property.price,
                        },
                    )
                else:
                    if ownership.player == player:
                        events.append({
                            'type': 'game.action',
                            'action': GameEventType.STEPPED_ON_OWN_PROPERTY,
                            'player': player.pk,
                            'tile': tile.pk,
                        })
                        game.turn += 1
                        game.current_player = GameService._calculate_next_player(game, player)

                        effect = GameEffect.objects.create(
                            game=game,
                            player=game.current_player,
                            name=GameEffect.ROLL_DICE,
                        )
                    else:
                        effect = GameEffect.objects.create(
                            game=game,
                            player=player,
                            name=GameEffect.PAY_RENT,
                            effect_data={
                                'rent': ownership.calculate_rent(),
                            },
                        )
            else:
                game.turn += 1
                game.current_player = GameService._calculate_next_player(game, player)

                effect = GameEffect.objects.create(
                    game=game,
                    player=game.current_player,
                    name=GameEffect.ROLL_DICE,
                )

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
                )
                player.cash -= tile.property.price
                player.save()
                
                tile.property.owner = player
                tile.property.save()

                effect = GameEffect.objects.filter(player=player, name=GameEffect.ASK_BUY).last()
                effect.delete()

                events.append({
                    'type': 'game.action',
                    'action': GameEventType.BUY_PROPERTY,
                    'player': player.pk,
                    'tile': tile.pk,
                })

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
        return events
    
    @staticmethod
    def pay_rent(game: Game, player: Player) -> list:
        events = []
        tile = Tile.objects.get(position=player.position)

        if tile.type != Tile.PROPERTY:
            raise Exception("You can't pay rent on a non-property tile")
        
        ownership = Ownership.objects.get(game=game, property=tile.property)
        rent_price = ownership.calculate_rent()

        if rent_price > player.cash:
            raise Exception("You don't have enough cash to pay rent")

        player.cash -= rent_price
        player.save()
        ownership.player.cash += rent_price
        ownership.player.save()

        effect = GameEffect.objects.filter(player=player, name=GameEffect.PAY_RENT).last()
        effect.delete()

        events.append({
            'type': 'game.action',
            'action': GameEventType.PAY_RENT,
            'player': player.pk,
            'rent_price': rent_price,
        })

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

        return events

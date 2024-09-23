from urllib.parse import parse_qs
import json

from typing import List
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.conf import settings
from django.forms import ValidationError

from .utils import parse_user_from_qs, verify_telegram_init_data
from .serializers import GameSerializer, PlayerSerializer
from game.models import Game, Player
from bot.models import TelegramUser

from pprint import pprint as print


class GameConsumer(WebsocketConsumer):
    def connect(self):
        init_data_raw = self.scope['query_string'].decode()
        
        parsed_qs = {k: v[0] for k, v in parse_qs(init_data_raw).items()}
        game_uuid = self.scope['url_route']['kwargs']['game_uuid']

        try:
            if verify_telegram_init_data(parsed_qs, settings.BOT_TOKEN):
                user = parse_user_from_qs(init_data_raw)

                try:
                    game = Game.objects.get(uuid=game_uuid)
                    player = Player.objects.get(game=game, user=user)
                except Game.DoesNotExist:
                    print("Game.DoesNotExist")
                    self.close()
                    return
                
                self.game_id = game.pk
                self.game_group_name = f"game_{game.uuid}"

                async_to_sync(self.channel_layer.group_add)(
                    self.game_group_name, self.channel_name
                )

                self.scope['telegram_user'] = user
                # self.scope['game_data'] = game_data
                self.accept()

                game_serializer = GameSerializer(game)
                response_data = {
                    'type': 'game.connected',
                    'game': game_serializer.data,
                    'players': [PlayerSerializer(player).data for player in game.players.all()],
                }
                self.send(text_data=json.dumps(response_data))
            else:
                print("Not aue")
        except KeyError:
            print("Nope")
            self.close()

    def disconnect(self, close_code):
        try:
            async_to_sync(self.channel_layer.group_discard)(
                self.game_group_name, self.channel_name
            )
        except AttributeError:
            pass

    def receive(self, text_data: str):
        print(text_data)
        # data: dict = json.loads(text_data)

        # try:
        #     game = Game.objects.get(uuid=self.scope['url_route']['kwargs']['game_uuid'])
        #     player = Player.objects.get(game=game, user=self.scope['telegram_user'])
        # except Game.DoesNotExist:
        #     print("Game.DoesNotExist")
        #     return
        
        # game_serializer = GameSerializer(game)
        # self.send(text_data=json.dumps(game_serializer.data))

        # try:
        #     game = Game.objects.get(pk=self.scope['game_data']['game_id'])
        #     player = Player.objects.get(game=game, user=self.scope['telegram_user'])

        #     serializer = GameSerializer(game)
        #     # self.send(text_data=json.dumps(serializer.data))
        # except Game.DoesNotExist:
        #     print("Game.DoesNotExist")
        #     return
        # except Player.DoesNotExist:
        #     print("Player.DoesNotExist")
        #     return

        # if data['action'] == 'roll_dice':
        #     try:
        #         events = services.roll_dice(player)
        #     except ValidationError as e:
        #         if e.message == "You are not the current player":
        #             serializer = GameSerializer(game)
        #             self.send(text_data=json.dumps({"type": "game.eventt", "action": "forbidden", "game": serializer.data}))
        #     else:
        #         async_to_sync(self.channel_layer.group_send)(
        #             self.game_group_name, {"type": "game.action", "game_id": game.pk, "events": [e.pk for e in events]}
        #         )
        # elif data['action'] == 'ping':
        #     self.send(text_data=json.dumps({"type": "pong"}))
    
    # def game_action(self, event):
    #     game_id: int = event['game_id']
    #     events_ids: List[int] = event['events']

    #     game = Game.objects.get(pk=game_id)
    #     events = [GameEvent.objects.get(pk=e_id) for e_id in events_ids]
    #     player_tiles = PlayerTile.objects.filter(game=game)
        
    #     game_serializer = GameSerializer(game)
    #     events_serializer = GameEventSerializer(events, many=True)
    #     player_tiles_serializer = PlayerTileSerializer(player_tiles, many=True)

    #     self.send(text_data=json.dumps({"type": "game.event", "game": game_serializer.data, "events": events_serializer.data, "player_tiles": player_tiles_serializer.data}))

    # def game_event(self, event):
    #     action = event['action']
    #     if action == 'start_game':
    #         # print("EVENTS",event['events'])

    #         game = Game.objects.get(pk=event['game_id'])

    #         events = [GameEvent.objects.get(pk=e_id) for e_id in event['events']]
    #         game_event = GameEvent.objects.get(pk=event['game_event_id'])

    #         game_serializer = GameSerializer(game)
    #         game_event_serializer = GameEventSerializer(game_event)
    #         events_serializer = GameEventSerializer(events, many=True)

    #         self.send(text_data=json.dumps({"type": "game.event", "action": action, "game": game_serializer.data, "game_event": game_event_serializer.data, "events": events_serializer.data}))
    #     elif action == 'roll_dice': # check values based on model values here 
    #         game = Game.objects.get(pk=event['game_id'])
    #         # game_event = GameEvent.objects.get(pk=event['game_tile_id'])
    #         events = [GameEvent.objects.get(pk=e_id) for e_id in event['events']]

    #         game_serializer = GameSerializer(game)
    #         # game_event_serializer = GameEventSerializer(game_event)
    #         events_serializer = GameEventSerializer(events, many=True)

    #         # self.send(text_data=json.dumps({"type": "game.event", "action": action, "game": game_serializer.data, "game_event": game_event_serializer.data}))
    #         self.send(text_data=json.dumps({"type": "game.event", "action": action, "game": game_serializer.data, "events": events_serializer.data}))
    #     elif action == 'ask_buy':
    #         game = Game.objects.get(pk=event['game_id'])
    #         game_event = GameEvent.objects.get(pk=event['game_tile_id'])

    #         game_serializer = GameSerializer(game)
    #         game_event_serializer = GameEventSerializer(game_event)

    #         self.send(text_data=json.dumps({"type": "game.event", "action": action, "game": game_serializer.data, "game_event": game_event_serializer.data}))
    #     elif action == 'buy':
    #         game = Game.objects.get(pk=event['game_id'])
    #         events = [GameEvent.objects.get(pk=e_id) for e_id in event['events']]

    #         game_serializer = GameSerializer(game)
    #         events_serializer = GameEventSerializer(events, many=True)

    #         self.send(text_data=json.dumps({"type": "game.event", "action": action, "game": game_serializer.data, "events": events_serializer.data}))

    #         # self.send(text_data=json.dumps({"type": "game.event", "action": action, "game": game_serializer.data, "game_event": game_event_serializer.data}))
    #     elif action == 'reject_buy':
    #         game = Game.objects.get(pk=event['game_id'])
    #         events = [GameEvent.objects.get(pk=e_id) for e_id in event['events']]

    #         game_serializer = GameSerializer(game)
    #         events_serializer = GameEventSerializer(events, many=True)

    #         self.send(text_data=json.dumps({"type": "game.event", "action": action, "game": game_serializer.data, "events": events_serializer.data}))
    #     elif action == 'player_join':
    #         game = Game.objects.get(pk=event['game_id'])
    #         events = [GameEvent.objects.get(pk=e_id) for e_id in event['events']]

    #         game_serializer = GameSerializer(game)
    #         events_serializer = GameEventSerializer(events, many=True)

    #         self.send(text_data=json.dumps({"type": "game.event", "action": action, "game": game_serializer.data, "events": events_serializer.data}))

    #         # self.send(text_data=json.dumps({"type": "game.event", "action": action, "game": game_serializer.data, "game_event": game_event_serializer.data}))
    #     elif action == 'user_timeout':
    #         game = Game.objects.get(pk=event['game_id'])
    #         game_event = GameEvent.objects.get(pk=event['tile_id'])

    #         game.next_turn()

    #         game_serializer = GameSerializer(game)
    #         game_event_serializer = GameEventSerializer(game_event)

    #         events = [game_event_serializer,]

    #         self.send(text_data=json.dumps({"type": "game.event", "action": action, "game": game_serializer.data, "events": [e.data for e in events]}))
    #     elif action == 'increase_position':
    #         game = Game.objects.get(pk=event['game_id'])
    #         # game_event = GameEvent.objects.get(pk=event['game_tile_id'])
    #         events = [GameEvent.objects.get(pk=e_id) for e_id in event['events']]

    #         game_serializer = GameSerializer(game)
    #         # game_event_serializer = GameEventSerializer(game_event)
    #         events_serializer = GameEventSerializer(events, many=True)

    #         self.send(text_data=json.dumps({"type": "game.event", "action": action, "game": game_serializer.data, "events": events_serializer.data}))
    #         # self.send(text_data=json.dumps({"type": "game.event", "action": action, "game": event['game']}))
    #     elif action == 'pay_rent':
    #         game = Game.objects.get(pk=event['game_id'])
    #         game_event = GameEvent.objects.get(pk=event['game_tile_id'])

    #         game_serializer = GameSerializer(game)
    #         game_event_serializer = GameEventSerializer(game_event)

    #         self.send(text_data=json.dumps({"type": "game.event", "action": action, "game": game_serializer.data, "game_event": game_event_serializer.data}))
    #     elif action == 'go_to_prison':
    #         game = Game.objects.get(pk=event['game_id'])
    #         game_event = GameEvent.objects.get(pk=event['game_tile_id'])

    #         game_serializer = GameSerializer(game)
    #         game_event_serializer = GameEventSerializer(game_event)

    #         self.send(text_data=json.dumps({"type": "game.event", "action": action, "game": game_serializer.data, "game_event": game_event_serializer.data}))
    #     elif action == 'release_from_prison':
    #         game = Game.objects.get(pk=event['game_id'])
    #         game_event = GameEvent.objects.get(pk=event['game_tile_id'])

    #         game_serializer = GameSerializer(game)
    #         game_event_serializer = GameEventSerializer(game_event)

    #         self.send(text_data=json.dumps({"type": "game.event", "action": action, "game": game_serializer.data, "game_event": game_event_serializer.data}))
    #     elif action == 'prison_buyout':
    #         game = Game.objects.get(pk=event['game_id'])
    #         events = [GameEvent.objects.get(pk=e_id) for e_id in event['events']]

    #         game_serializer = GameSerializer(game)
    #         events_serializer = GameEventSerializer(events, many=True)

    #         self.send(text_data=json.dumps({"type": "game.event", "action": action, "game": game_serializer.data, "events": events_serializer.data}))

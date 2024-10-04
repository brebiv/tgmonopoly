from urllib.parse import parse_qs
import json

from typing import List
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.conf import settings
from django.forms import ValidationError

from .utils import parse_user_from_qs, verify_telegram_init_data
from .serializers import GameSerializer, PlayerSerializer, GameEventSerializer, OwnershipSerializer
from game.models import Game, Player, Ownership
from bot.models import TelegramUser

from pprint import pprint as print


class GameConsumer(WebsocketConsumer):
    def connect(self):
        init_data_raw = self.scope['query_string'].decode()
        
        parsed_qs = {k: v[0] for k, v in parse_qs(init_data_raw).items()}
        game_uuid = self.scope['url_route']['kwargs']['game_uuid']

        try:
            if True or verify_telegram_init_data(parsed_qs, settings.BOT_TOKEN):
                user = parse_user_from_qs(init_data_raw)
                # user = TelegramUser.objects.first()

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

                # Maybe put this thing in the fucking views
                ownerships = Ownership.objects.filter(game=game)
                ownerships_serializer = OwnershipSerializer(ownerships, many=True)

                response_data = {
                    'type': 'game.connected',
                    'game': game_serializer.data,
                    'players': [PlayerSerializer(player).data for player in game.players.all()],
                    'me': PlayerSerializer(player).data,
                    'ownerships': ownerships_serializer.data
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
        return
        # if data['action'] == 'ping':
        #     self.send(text_data=json.dumps({"type": "pong"}))
    
    def game_action(self, event):
        # game_action_serializer = GameEventSerializer(data=event)
        
        # if not game_action_serializer.is_valid():
        #     return
        
        # self.send(text_data=json.dumps(game_action_serializer.data))
        self.send(text_data=json.dumps(event))

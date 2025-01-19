from urllib.parse import parse_qs
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.conf import settings

from game.services import GameService
from game.models import Game, Player
from .utils import parse_user_from_qs, verify_telegram_init_data
from .serializers import PlayerSerializer
from .exceptions import AuthException
from .types import WSEventType

from pprint import pprint as print


class GameConsumer(WebsocketConsumer):
    def connect(self):
        init_data_raw = self.scope['query_string'].decode()

        if not init_data_raw:
            self.close()
            # raise AuthException("No init data")
        
        parsed_qs = {k: v[0] for k, v in parse_qs(init_data_raw).items()}
        game_uuid = self.scope['url_route']['kwargs']['game_uuid']

        try:
            # if True or verify_telegram_init_data(parsed_qs, settings.BOT_TOKEN):
            if verify_telegram_init_data(parsed_qs, settings.BOT_TOKEN):
                user = parse_user_from_qs(init_data_raw)
                # user = TelegramUser.objects.first()

                try:
                    game = Game.objects.get(uuid=game_uuid)
                    player = Player.objects.get(game=game, user=user)
                except Game.DoesNotExist:
                    # print("Game.DoesNotExist")
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

                game_frame = GameService.assemble_game_frame(game, [], WSEventType.GAME_CONNECTED)
                game_frame['me'] = PlayerSerializer(player).data

                self.send(text_data=json.dumps(game_frame))
            else:
                # print("Not aue")
                self.close()
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

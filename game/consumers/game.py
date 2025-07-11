from uuid import UUID

from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync

from game.models import Game, Player
from game.services import get_service_by_game, BaseMonopoly
from .mixinis import AuthMixin


class GameConsumer(JsonWebsocketConsumer, AuthMixin):
    player: Player
    monopoly_service: BaseMonopoly

    def connect(self) -> None:
        self.authenticate()
        tg_user = self.scope.get("telegram_user")

        # Verifying game uuid
        try:
            game_uuid_raw = self.scope["url_route"]["kwargs"]["game_uuid"]
            game_uuid = UUID(game_uuid_raw)
            game = Game.objects.get(uuid=game_uuid)
            player = Player.objects.get(game=game, user=tg_user)
        except KeyError:
            print("something was wrong with self.scope keys")
            self.close()
            return
        except ValueError:
            print(
                f"something was wrong with game_uuid, could't parse it to UUID. uuid={game_uuid}"
            )
            self.close()
            return
        except Game.DoesNotExist:
            print(f"could not find game with uuid={game_uuid}")
            self.close()
            return
        except Player.DoesNotExist:
            print(
                f"could not find player with game_uuid={game.uuid} user_id={tg_user.user_id}"
            )
            self.close()
            return

        self.scope["game_found"] = True

        monopoly_service = get_service_by_game(game)
        game_frame = monopoly_service.assemble_game_frame(game, [], "game.initial")
        game_frame["my_player_id"] = player.pk

        self.game_uuid = game.pk
        self.player = player
        self.monopoly_service = monopoly_service
        self.game_group_name = f"game_{game.uuid}"

        async_to_sync(self.channel_layer.group_add)(
            self.game_group_name, self.channel_name
        )

        self.accept()
        self.send_json(game_frame)

    def disconnect(self, code):
        if self.scope.get("game_found"):
            async_to_sync(self.channel_layer.group_discard)(
                self.game_group_name, self.channel_name
            )

    def receive_json(self, content):
        print("Well, here we are JSON")

    def receive(self, text_data):
        action = text_data
        game_frame = self.monopoly_service.process_game_action(
            self.game_uuid, self.player.pk, action
        )
        async_to_sync(self.channel_layer.group_send)(self.game_group_name, game_frame)

    def game_event(self, event):
        self.send_json(event)

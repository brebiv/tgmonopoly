from uuid import UUID

from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync

from .auth import TelegramWebAppAuthentication
from .utils import update_or_create_telegram_user
from .models import Game, Player


class GameConsumer(JsonWebsocketConsumer):
    def connect(self):
        # Verifying Telegram auth
        init_data_raw = self.scope.get("query_string", None)
        if not init_data_raw:
            self.close()
            return

        init_data = init_data_raw.decode()

        data_is_valid, validated_data = (
            TelegramWebAppAuthentication().verify_telegram_init_data(init_data)
        )

        if not data_is_valid:
            self.close()
            return

        tg_user_data = validated_data.get("user")
        tg_user = update_or_create_telegram_user(tg_user_data)
        self.scope["telegram_user"] = tg_user

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

        self.game_id = game.pk
        self.game_group_name = f"game_{game.uuid}"

        async_to_sync(self.channel_layer.group_add)(
            self.game_group_name, self.channel_name
        )

        self.accept()

        # game_frame = assamble_game_frame()
        # self.send()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.game_group_name, self.channel_name
        )

    def receive(self, text_data):
        print(text_data)

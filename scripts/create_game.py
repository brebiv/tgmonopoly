from django.db import transaction, IntegrityError
from game.models import BoardConfig, Game, Player
from game.tests.classic import mock_data
from game.services import get_service_by_game
from bot.models import TelegramUser


@transaction.atomic
def create_game():
    tg_users = mock_data.create_telegram_users(2, synthetic=False)
    board_config = BoardConfig.objects.get(name=BoardConfig.Names.CLASSIC)
    game = Game.objects.create(
        uuid="3c37e784-8834-41d5-b9e3-7813dd905dd3", max_players=2, board_config=board_config
    )
    monopoly_service = get_service_by_game(game)
    p1 = Player.objects.create(user=tg_users[0], game=game, color=Player.Color.BLUE)
    p2, _ = monopoly_service.join_game(game.uuid, tg_users[1])


@transaction.atomic
def delete_game():
    TelegramUser.objects.all().delete()
    Game.objects.get(uuid="3c37e784-8834-41d5-b9e3-7813dd905dd3").delete()


def run():
    try:
        create_game()
    except IntegrityError:
        delete_game()
        create_game()

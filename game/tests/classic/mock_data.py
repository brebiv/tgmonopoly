from django.db import transaction
from urllib.parse import parse_qs
import json
from faker import Faker
import random

from bot.models import TelegramUser
# from game.models import

fake = Faker()

_TG_INIT_DATA_1 = "query_id=AAHVezADAQAAANV7MAN7NUXU&user=%7B%22id%22%3A2200992725%2C%22first_name%22%3A%22ooooo%22%2C%22last_name%22%3A%22%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Fa-ttgme.stel.com%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2Fkm3Kt2Xui5sV_iITWLc7vA3Cq5svooSqa29PcQpToEfRtOLHVNLZhpmxXBImuJBH.svg%22%7D&auth_date=1751188277&signature=que9f1eIDJ0xsDX6T2ZNDtP9c8_nOtX0l-WuZwVMphNKgoZQZzHVlW5_ojQXg50EWBh5WgmGOFy6S1eph5YoCg&hash=67934f1f638d5c59a72ae983ad7a8f98d5e2e32089d91a7e50ea605967efb1fd"
_TG_INIT_DATA_2 = "query_id=AAFGfTADAQAAAEZ9MAOPyqWt&user=%7B%22id%22%3A2200993094%2C%22first_name%22%3A%22%D0%B0%D0%BD%D1%8F%22%2C%22last_name%22%3A%22%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Fa-ttgme.stel.com%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FnG-zbLjFwgajwIVtHiQjS5YLYmwfOj_MhhQCc2A9s6TulwyGlHs_Wm7tgMDa9f-T.svg%22%7D&auth_date=1751188420&signature=gwpb8PiId9M_e9suoUgZBTXGFPfoyHxeId8bO6kaILNr4AHd9DfZ5Tpyl1IS4ngE9n9KrLv6ckj9Myr8uspbCg&hash=15dc4b711623305ca801eaa62ea5aab2416991e261c83fbd755ed5e2d3e78f62"
_TG_INIT_DATA_3 = "query_id=AAFCHQwqAgAAAEIdDCo_utOP&user=%7B%22id%22%3A5000404290%2C%22first_name%22%3A%22%D0%BB%D0%B5%D0%BD%D1%8F%22%2C%22last_name%22%3A%22%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Fa-ttgme.stel.com%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FRdPsoweldGSkJ4FKidFnAM-bcsUodipbw42FalKjQD7SzrjlBJBhfdEbPfi3iCKW.svg%22%7D&auth_date=1752500280&signature=HNb_RmLK8DVW_takwmq9bhsThx6CHe6yU9FnJoic6LAH_vb7r_MNmzFdwIgpMsOl5noZxTHfK9WypvgAcATTAg&hash=cd9cb384ffe7483ca268f961a9ece3d74447735043c7d65f22b1203d2eea744a"

TG_INIT_DATA_RAW_LIST = [_TG_INIT_DATA_1, _TG_INIT_DATA_2, _TG_INIT_DATA_3]
TG_INIT_DATA_PARSED = [parse_qs(init_data_raw) for init_data_raw in TG_INIT_DATA_RAW_LIST]
TG_INIT_DATA_USER = [json.loads(data["user"][0]) for data in TG_INIT_DATA_PARSED]


def create_telegram_users(limit: int = 3, synthetic=False) -> list[TelegramUser]:
    if synthetic:
        users = []
        for _ in range(limit):
            users.append(create_synthetic_telegram_user())
        return users

    user_limit = len(TG_INIT_DATA_USER)
    if limit > user_limit:
        raise ValueError("Current limit is:", user_limit)
    users = []

    with transaction.atomic():
        for user_data in TG_INIT_DATA_USER[:limit]:
            user_data["user_id"] = user_data["id"]
            tg_user = TelegramUser.objects.create(**user_data)
            users.append(tg_user)

    return users


def _random_tg_user_defaults(**overrides):
    defaults = {
        "user_id": fake.unique.random_int(min=10**8, max=10**12),  # 9-12 digits
        "username": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "language": fake.language_code(),
        "language_code": fake.language_code(),
        "allows_write_to_pm": random.choice([True, False, None]),
        "photo_url": fake.image_url(),
        "ban": False,
    }
    defaults.update(overrides)
    return defaults


def create_synthetic_telegram_user(**overrides) -> TelegramUser:
    return TelegramUser.objects.create(**_random_tg_user_defaults(**overrides))

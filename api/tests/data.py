from random import randint
from datetime import datetime
from urllib.parse import parse_qs
import json

from bot.models import TelegramUser

RANDOM_TG_USER_1_DICT = {
    "user_id": randint(1000000000, 9999999999),
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe",
    "language": TelegramUser.EN,
    "lang_code": "en",
    "ban": False,
    "created": datetime(2024, 1, 1, 12, 0),
}

RANDOM_TG_USER_2_DICT = {
    "user_id": randint(1000000000, 9999999999),
    "username": "anna_r",
    "first_name": "Anna",
    "last_name": "Romanova",
    "language": TelegramUser.RU,
    "lang_code": "ru",
    "ban": True,
    "created": datetime(2024, 1, 2, 15, 30),
}

TELEGRAM_TEST_USER_1_WEBAPP_DATA = 'query_id=AAFCHQwqAgAAAEIdDCoTvNzt&user=%7B%22id%22%3A5000404290%2C%22first_name%22%3A%22%D0%BB%D0%B5%D0%BD%D1%8F%22%2C%22last_name%22%3A%22%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1727969049&hash=e60eb0de21918c27cba44ae5e9a4675c78362b207ed2fb84bd533c98b0a308d4'
TELEGRAM_TEST_USER_2_WEBAPP_DATA = 'query_id=AAHVezADAQAAANV7MAMwW6ed&user=%7B%22id%22%3A2200992725%2C%22first_name%22%3A%22ooooo%22%2C%22last_name%22%3A%22%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Fa-ttgme.stel.com%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2Fkm3Kt2Xui5sV_iITWLc7vA3Cq5svooSqa29PcQpToEfRtOLHVNLZhpmxXBImuJBH.svg%22%7D&auth_date=1734288958&signature=E4YQA6xqEsy_Y7KIRn3LnZXMDT0PEZekMCb_bTIlZphyllz74RLsC-2YdQdXTN_I_3Gkqm_um-TAcuc_2Z-HAw&hash=6cd91acd0203056105667da7a7aea400fb9d6196039ad7d3616c059831aea6c8'

TELEGRAM_TEST_WEBAPP_DATAS = [
    TELEGRAM_TEST_USER_1_WEBAPP_DATA,
    TELEGRAM_TEST_USER_2_WEBAPP_DATA,
]

_parsed_user_from_webapp_data_1 = json.loads(parse_qs(TELEGRAM_TEST_USER_1_WEBAPP_DATA)['user'][0])
_parsed_user_from_webapp_data_2 = json.loads(parse_qs(TELEGRAM_TEST_USER_2_WEBAPP_DATA)['user'][0])

TG_USER_1_DICT = {
    "user_id": _parsed_user_from_webapp_data_1['id'],
    "first_name": _parsed_user_from_webapp_data_1['first_name'],
    "last_name": _parsed_user_from_webapp_data_1['last_name'],
    "language": _parsed_user_from_webapp_data_1['language_code'],
    "lang_code": _parsed_user_from_webapp_data_1['language_code'],
    # "ban": False,
    # "created": datetime(2024, 1, 1, 12, 0),
}
TG_USER_2_DICT = {
    "user_id": _parsed_user_from_webapp_data_2['id'],
    "first_name": _parsed_user_from_webapp_data_2['first_name'],
    "last_name": _parsed_user_from_webapp_data_2['last_name'],
    "language": _parsed_user_from_webapp_data_2['language_code'],
    "lang_code": _parsed_user_from_webapp_data_2['language_code'],
    # "ban": False,
    # "created": datetime(2024, 1, 1, 12, 0),
}

TG_USER_DICTS = [
    TG_USER_1_DICT,
    TG_USER_2_DICT,
]

from random import randint
from datetime import datetime
from urllib.parse import parse_qs
import json
from django.db import transaction

from bot.models import TelegramUser
from game.models import (
    PropertyGroup,
    Tile,
    Property,
    Utility,
    ChanceCard,
)


RANDOM_TG_USER_1_DICT = {
    "user_id": randint(1000000000, 9999999999),
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe",
    "language": TelegramUser.EN,
    "lang_code": "en",
    # "ban": False,
    # "created": datetime(2024, 1, 1, 12, 0),
}

RANDOM_TG_USER_2_DICT = {
    "user_id": randint(1000000000, 9999999999),
    "username": "anna_r",
    "first_name": "Anna",
    "last_name": "Romanova",
    "language": TelegramUser.RU,
    "lang_code": "ru",
    # "ban": True,
    # "created": datetime(2024, 1, 2, 15, 30),
}

TELEGRAM_TEST_USER_1_WEBAPP_DATA = 'query_id=AAFCHQwqAgAAAEIdDCoTvNzt&user=%7B%22id%22%3A5000404290%2C%22first_name%22%3A%22%D0%BB%D0%B5%D0%BD%D1%8F%22%2C%22last_name%22%3A%22%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1727969049&hash=e60eb0de21918c27cba44ae5e9a4675c78362b207ed2fb84bd533c98b0a308d4'
TELEGRAM_TEST_USER_2_WEBAPP_DATA = 'query_id=AAHVezADAQAAANV7MAMwW6ed&user=%7B%22id%22%3A2200992725%2C%22first_name%22%3A%22ooooo%22%2C%22last_name%22%3A%22%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Fa-ttgme.stel.com%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2Fkm3Kt2Xui5sV_iITWLc7vA3Cq5svooSqa29PcQpToEfRtOLHVNLZhpmxXBImuJBH.svg%22%7D&auth_date=1734288958&signature=E4YQA6xqEsy_Y7KIRn3LnZXMDT0PEZekMCb_bTIlZphyllz74RLsC-2YdQdXTN_I_3Gkqm_um-TAcuc_2Z-HAw&hash=6cd91acd0203056105667da7a7aea400fb9d6196039ad7d3616c059831aea6c8'
TELEGRAM_TEST_USER_3_WEBAPP_DATA = 'query_id=AAFGfTADAQAAAEZ9MAMhrCUb&user=%7B%22id%22%3A2200993094%2C%22first_name%22%3A%22%D0%B0%D0%BD%D1%8F%22%2C%22last_name%22%3A%22%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Fa-ttgme.stel.com%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FnG-zbLjFwgajwIVtHiQjS5YLYmwfOj_MhhQCc2A9s6TulwyGlHs_Wm7tgMDa9f-T.svg%22%7D&auth_date=1735505829&signature=YmWXtfewmIhBOotbj3m0-6W_xFZZLxW165AIvFQRk-oJ9NsAmwSkx_Adu79F0b-oc__z0o75wiYDGsTXA6yDBg&hash=4d86d96da969e11594b8e2708a124d292e372774995cff3f883e81fe39ea88de'

TELEGRAM_TEST_WEBAPP_DATAS = [
    TELEGRAM_TEST_USER_1_WEBAPP_DATA,
    TELEGRAM_TEST_USER_2_WEBAPP_DATA,
    TELEGRAM_TEST_USER_3_WEBAPP_DATA,
]

_parsed_user_from_webapp_data_1 = json.loads(parse_qs(TELEGRAM_TEST_USER_1_WEBAPP_DATA)['user'][0])
_parsed_user_from_webapp_data_2 = json.loads(parse_qs(TELEGRAM_TEST_USER_2_WEBAPP_DATA)['user'][0])
_parsed_user_from_webapp_data_3 = json.loads(parse_qs(TELEGRAM_TEST_USER_3_WEBAPP_DATA)['user'][0])

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
TG_USER_3_DICT = {
    "user_id": _parsed_user_from_webapp_data_3['id'],
    "first_name": _parsed_user_from_webapp_data_3['first_name'],
    "last_name": _parsed_user_from_webapp_data_3['last_name'],
    "language": _parsed_user_from_webapp_data_3['language_code'],
    "lang_code": _parsed_user_from_webapp_data_3['language_code'],
    # "ban": False,
    # "created": datetime(2024, 1, 1, 12, 0),
}

TG_USER_DICTS = [
    TG_USER_1_DICT,
    TG_USER_2_DICT,
    TG_USER_3_DICT,
]


def load_property_groups():
    with transaction.atomic():
        PropertyGroup.objects.create(pk=1, name="CLOTH", color="#cc5351")
        PropertyGroup.objects.create(pk=2, name="FOOD", color="#cc8c66")
        PropertyGroup.objects.create(pk=3, name="COMMUNICATION", color="#c6c25f")
        PropertyGroup.objects.create(pk=4, name="AUTOMOBILE", color="#339f7e")
        PropertyGroup.objects.create(pk=5, name="OIL", color="#069aa3")
        PropertyGroup.objects.create(pk=6, name="MEDECINE", color="#4785c2")
        PropertyGroup.objects.create(pk=7, name="FINANCE", color="#796fcf")
        PropertyGroup.objects.create(pk=8, name="TECH", color="#9c63b6")
        PropertyGroup.objects.create(pk=9, name="UTILITIES_1", color="#8f0d0d")
        PropertyGroup.objects.create(pk=10, name="UTILITIES_2", color="#3D36B6")


def load_tiles():
    with transaction.atomic():
        Tile.objects.create(pk=1,  position=0,  name="Go",         type="START")
        Tile.objects.create(pk=2,  position=1,  name="Adidas",     type="PROPERTY")
        Tile.objects.create(pk=3,  position=2,  name="Chance",     type="CHANCE")
        Tile.objects.create(pk=4,  position=3,  name="Nike",       type="PROPERTY")
        Tile.objects.create(pk=5,  position=4,  name="Tax",        type="TAX")
        Tile.objects.create(pk=6,  position=5,  name="Wind",       type="PROPERTY")
        Tile.objects.create(pk=7,  position=6,  name="Pepsi",      type="PROPERTY")
        Tile.objects.create(pk=8,  position=7,  name="Chance",     type="CHANCE")
        Tile.objects.create(pk=9,  position=8,  name="Coca-Cola",  type="PROPERTY")
        Tile.objects.create(pk=10, position=9,  name="Nestle",     type="PROPERTY")
        Tile.objects.create(pk=11, position=10, name="Jail",       type="JAIL")
        Tile.objects.create(pk=12, position=11, name="AT&T",       type="PROPERTY")
        Tile.objects.create(pk=13, position=12, name="NASA",       type="PROPERTY")
        Tile.objects.create(pk=14, position=13, name="Verizon",    type="PROPERTY")
        Tile.objects.create(pk=15, position=14, name="Chine Mobile", type="PROPERTY")
        Tile.objects.create(pk=16, position=15, name="Dam",        type="PROPERTY")
        Tile.objects.create(pk=17, position=16, name="Toyota",     type="PROPERTY")
        Tile.objects.create(pk=18, position=17, name="Chance",     type="CHANCE")
        Tile.objects.create(pk=19, position=18, name="Audi",       type="PROPERTY")
        Tile.objects.create(pk=20, position=19, name="Tesla",      type="PROPERTY")
        Tile.objects.create(pk=21, position=20, name="Casino",     type="CASINO")
        Tile.objects.create(pk=22, position=21, name="BP",         type="PROPERTY")
        Tile.objects.create(pk=23, position=22, name="Chance",     type="CHANCE")
        Tile.objects.create(pk=24, position=23, name="Shell",      type="PROPERTY")
        Tile.objects.create(pk=25, position=24, name="Chevron",    type="PROPERTY")
        Tile.objects.create(pk=26, position=25, name="Solar",      type="PROPERTY")
        Tile.objects.create(pk=27, position=26, name="Moderna",    type="PROPERTY")
        Tile.objects.create(pk=28, position=27, name="Durex",      type="PROPERTY")
        Tile.objects.create(pk=29, position=28, name="SpaceX",     type="PROPERTY")
        Tile.objects.create(pk=30, position=29, name="Pfizer",     type="PROPERTY")
        Tile.objects.create(pk=31, position=30, name="Police",     type="POLICE")
        Tile.objects.create(pk=32, position=31, name="Citigroup",  type="PROPERTY")
        Tile.objects.create(pk=33, position=32, name="Goldman Sachs", type="PROPERTY")
        Tile.objects.create(pk=34, position=33, name="Chance",     type="CHANCE")
        Tile.objects.create(pk=35, position=34, name="JPMorgan Chase", type="PROPERTY")
        Tile.objects.create(pk=36, position=35, name="Nuke",       type="PROPERTY")
        Tile.objects.create(pk=37, position=36, name="Chance",     type="CHANCE")
        Tile.objects.create(pk=38, position=37, name="TikTok",     type="PROPERTY")
        Tile.objects.create(pk=39, position=38, name="Tax",        type="TAX")
        Tile.objects.create(pk=40, position=39, name="Telegram",   type="PROPERTY")


def load_properties():
    with transaction.atomic():
        Property.objects.create(
            pk=1, board_space=Tile.objects.get(pk=2), price=60, mortgage_value=30, house_price=50,
            rent=2, rent_with_1_house=10, rent_with_2_houses=30,
            rent_with_3_houses=90, rent_with_4_houses=160, rent_with_5_houses=250,
            group_id=1, icon="properties/adidas_logo.png", svg_icon=None
        )
        Property.objects.create(
            pk=2, board_space=Tile.objects.get(pk=4), price=60, mortgage_value=30, house_price=50,
            rent=4, rent_with_1_house=20, rent_with_2_houses=60,
            rent_with_3_houses=180, rent_with_4_houses=320, rent_with_5_houses=450,
            group_id=1, icon="properties/nike_icon.png", svg_icon=None
        )
        Property.objects.create(
            pk=3, board_space=Tile.objects.get(pk=7), price=100, mortgage_value=50, house_price=50,
            rent=6, rent_with_1_house=30, rent_with_2_houses=90,
            rent_with_3_houses=270, rent_with_4_houses=400, rent_with_5_houses=550,
            group_id=2, icon="properties/pepsi_logo.png", svg_icon=None
        )
        Property.objects.create(
            pk=4, board_space=Tile.objects.get(pk=9), price=120, mortgage_value=60, house_price=50,
            rent=8, rent_with_1_house=40, rent_with_2_houses=100,
            rent_with_3_houses=300, rent_with_4_houses=450, rent_with_5_houses=600,
            group_id=2, icon="properties/Coca-Cola_logo.png", svg_icon=None
        )
        Property.objects.create(
            pk=5, board_space=Tile.objects.get(pk=10), price=120, mortgage_value=60, house_price=50,
            rent=8, rent_with_1_house=40, rent_with_2_houses=100,
            rent_with_3_houses=300, rent_with_4_houses=450, rent_with_5_houses=600,
            group_id=2, icon="properties/Nestle-Logo_tUC6jj9.png", svg_icon=None
        )
        Property.objects.create(
            pk=6, board_space=Tile.objects.get(pk=12), price=140, mortgage_value=70, house_price=100,
            rent=10, rent_with_1_house=50, rent_with_2_houses=150,
            rent_with_3_houses=450, rent_with_4_houses=625, rent_with_5_houses=750,
            group_id=3, icon="properties/att-logo-transparent.png", svg_icon=None
        )
        Property.objects.create(
            pk=7, board_space=Tile.objects.get(pk=14), price=140, mortgage_value=70, house_price=100,
            rent=10, rent_with_1_house=50, rent_with_2_houses=150,
            rent_with_3_houses=450, rent_with_4_houses=625, rent_with_5_houses=750,
            group_id=3, icon="properties/Verizon-Logo.png", svg_icon=None
        )
        Property.objects.create(
            pk=8, board_space=Tile.objects.get(pk=15), price=160, mortgage_value=80, house_price=100,
            rent=12, rent_with_1_house=60, rent_with_2_houses=180,
            rent_with_3_houses=500, rent_with_4_houses=700, rent_with_5_houses=900,
            group_id=3, icon="properties/chine_mobile_logo.png", svg_icon=None
        )
        Property.objects.create(
            pk=9, board_space=Tile.objects.get(pk=17), price=180, mortgage_value=90, house_price=100,
            rent=14, rent_with_1_house=70, rent_with_2_houses=200,
            rent_with_3_houses=550, rent_with_4_houses=750, rent_with_5_houses=950,
            group_id=4, icon="properties/Toyota-Logo.png", svg_icon=None
        )
        Property.objects.create(
            pk=10, board_space=Tile.objects.get(pk=19), price=180, mortgage_value=90, house_price=100,
            rent=14, rent_with_1_house=70, rent_with_2_houses=200,
            rent_with_3_houses=550, rent_with_4_houses=750, rent_with_5_houses=950,
            group_id=4, icon="properties/Audi-Logo.png", svg_icon=None
        )
        Property.objects.create(
            pk=11, board_space=Tile.objects.get(pk=20), price=200, mortgage_value=100, house_price=100,
            rent=16, rent_with_1_house=80, rent_with_2_houses=220,
            rent_with_3_houses=600, rent_with_4_houses=800, rent_with_5_houses=1000,
            group_id=4, icon="properties/Tesla-Logo.png", svg_icon=None
        )
        Property.objects.create(
            pk=12, board_space=Tile.objects.get(pk=22), price=220, mortgage_value=110, house_price=150,
            rent=18, rent_with_1_house=90, rent_with_2_houses=250,
            rent_with_3_houses=700, rent_with_4_houses=875, rent_with_5_houses=1050,
            group_id=5, icon="properties/bp-logo.png", svg_icon=None
        )
        Property.objects.create(
            pk=13, board_space=Tile.objects.get(pk=24), price=220, mortgage_value=110, house_price=150,
            rent=18, rent_with_1_house=90, rent_with_2_houses=250,
            rent_with_3_houses=700, rent_with_4_houses=875, rent_with_5_houses=1050,
            group_id=5, icon="properties/Shell-Logo.png", svg_icon=None
        )
        Property.objects.create(
            pk=14, board_space=Tile.objects.get(pk=25), price=240, mortgage_value=120, house_price=150,
            rent=20, rent_with_1_house=100, rent_with_2_houses=300,
            rent_with_3_houses=750, rent_with_4_houses=925, rent_with_5_houses=1100,
            group_id=5, icon="properties/Chevron-Logo.png", svg_icon=None
        )
        Property.objects.create(
            pk=15, board_space=Tile.objects.get(pk=27), price=260, mortgage_value=130, house_price=150,
            rent=22, rent_with_1_house=110, rent_with_2_houses=330,
            rent_with_3_houses=800, rent_with_4_houses=975, rent_with_5_houses=1150,
            group_id=6, icon="properties/Moderna_logo.png", svg_icon=None
        )
        Property.objects.create(
            pk=16, board_space=Tile.objects.get(pk=28), price=260, mortgage_value=130, house_price=150,
            rent=22, rent_with_1_house=110, rent_with_2_houses=330,
            rent_with_3_houses=800, rent_with_4_houses=975, rent_with_5_houses=1150,
            group_id=6, icon="properties/Durex-Logo.png", svg_icon=None
        )
        Property.objects.create(
            pk=17, board_space=Tile.objects.get(pk=30), price=280, mortgage_value=140, house_price=150,
            rent=24, rent_with_1_house=120, rent_with_2_houses=360,
            rent_with_3_houses=850, rent_with_4_houses=1025, rent_with_5_houses=1200,
            group_id=6, icon="properties/Pfizer_logo.png", svg_icon=None
        )
        Property.objects.create(
            pk=18, board_space=Tile.objects.get(pk=32), price=300, mortgage_value=150, house_price=200,
            rent=26, rent_with_1_house=130, rent_with_2_houses=390,
            rent_with_3_houses=900, rent_with_4_houses=1100, rent_with_5_houses=1275,
            group_id=7, icon="properties/Citigroup-Logo.png", svg_icon=None
        )
        Property.objects.create(
            pk=19, board_space=Tile.objects.get(pk=33), price=300, mortgage_value=150, house_price=200,
            rent=26, rent_with_1_house=130, rent_with_2_houses=390,
            rent_with_3_houses=900, rent_with_4_houses=1100, rent_with_5_houses=1275,
            group_id=7, icon="properties/Goldman-Sachs-Logo.png", svg_icon=None
        )
        Property.objects.create(
            pk=20, board_space=Tile.objects.get(pk=35), price=320, mortgage_value=160, house_price=200,
            rent=28, rent_with_1_house=150, rent_with_2_houses=450,
            rent_with_3_houses=1000, rent_with_4_houses=1200, rent_with_5_houses=1400,
            group_id=7, icon="properties/JP-Morgan-Chase-Emblem.png", svg_icon=None
        )
        Property.objects.create(
            pk=21, board_space=Tile.objects.get(pk=38), price=350, mortgage_value=175, house_price=200,
            rent=35, rent_with_1_house=175, rent_with_2_houses=500,
            rent_with_3_houses=1100, rent_with_4_houses=1300, rent_with_5_houses=1500,
            group_id=8, icon="properties/tiktok-logo-tiktok-logo-transparent-tiktok-icon-transparent-free-free-png.webp",
            svg_icon=None
        )
        Property.objects.create(
            pk=22, board_space=Tile.objects.get(pk=40), price=400, mortgage_value=200, house_price=200,
            rent=50, rent_with_1_house=200, rent_with_2_houses=600,
            rent_with_3_houses=1400, rent_with_4_houses=1700, rent_with_5_houses=2000,
            group_id=8, icon="properties/Telegram_logo.png", svg_icon=None
        )
        # Below properties have null "house_price" for utilities
        Property.objects.create(
            pk=23, board_space=Tile.objects.get(pk=6), price=200, mortgage_value=100, house_price=None,
            rent=200, rent_with_1_house=None, rent_with_2_houses=None,
            rent_with_3_houses=None, rent_with_4_houses=None, rent_with_5_houses=None,
            group_id=9, icon="", svg_icon="WIND_POWER"
        )
        Property.objects.create(
            pk=24, board_space=Tile.objects.get(pk=13), price=150, mortgage_value=75, house_price=None,
            rent=10, rent_with_1_house=None, rent_with_2_houses=None,
            rent_with_3_houses=None, rent_with_4_houses=None, rent_with_5_houses=None,
            group_id=10, icon="properties/NASA-Logo-Large_lv1zNQ4.png", svg_icon=None
        )
        Property.objects.create(
            pk=25, board_space=Tile.objects.get(pk=16), price=200, mortgage_value=100, house_price=None,
            rent=200, rent_with_1_house=None, rent_with_2_houses=None,
            rent_with_3_houses=None, rent_with_4_houses=None, rent_with_5_houses=None,
            group_id=9, icon="", svg_icon="DAM"
        )
        Property.objects.create(
            pk=26, board_space=Tile.objects.get(pk=26), price=200, mortgage_value=100, house_price=None,
            rent=200, rent_with_1_house=None, rent_with_2_houses=None,
            rent_with_3_houses=None, rent_with_4_houses=None, rent_with_5_houses=None,
            group_id=9, icon="", svg_icon="SOLAR_POWER"
        )
        Property.objects.create(
            pk=27, board_space=Tile.objects.get(pk=29), price=150, mortgage_value=75, house_price=None,
            rent=10, rent_with_1_house=None, rent_with_2_houses=None,
            rent_with_3_houses=None, rent_with_4_houses=None, rent_with_5_houses=None,
            group_id=10, icon="properties/spacex_logo_icon_144865_0eDOETd.webp", svg_icon=None
        )
        Property.objects.create(
            pk=28, board_space=Tile.objects.get(pk=36), price=200, mortgage_value=100, house_price=None,
            rent=200, rent_with_1_house=None, rent_with_2_houses=None,
            rent_with_3_houses=None, rent_with_4_houses=None, rent_with_5_houses=None,
            group_id=9, icon="", svg_icon="NUKE"
        )


def load_utilities():
    with transaction.atomic():
        Utility.objects.create(pk=1, board_space=Tile.objects.get(pk=6),  price=200, mortgage_value=100, type="UTILITY_1", group_id=9, icon="")
        Utility.objects.create(pk=2, board_space=Tile.objects.get(pk=16), price=200, mortgage_value=100, type="UTILITY_1", group_id=9, icon="")
        Utility.objects.create(pk=3, board_space=Tile.objects.get(pk=26), price=200, mortgage_value=100, type="UTILITY_1", group_id=9, icon="")
        Utility.objects.create(pk=4, board_space=Tile.objects.get(pk=36), price=200, mortgage_value=100, type="UTILITY_1", group_id=9, icon="")
        Utility.objects.create(pk=5, board_space=Tile.objects.get(pk=13), price=150, mortgage_value=75,  type="UTILITY_2", group_id=10, icon="properties/NASA-Logo-Large.png")
        Utility.objects.create(pk=6, board_space=Tile.objects.get(pk=29), price=150, mortgage_value=75,  type="UTILITY_2", group_id=10, icon="properties/spacex_logo_icon_144865.webp")

def load_chance_cards():
    with transaction.atomic():
        ChanceCard.objects.create(
            pk=1,
            title="Move backwards",
            description="Next turn you will move backwards",
            card_type="MOVE_BACKWARDS",
            details={}
        )
        ChanceCard.objects.create(
            pk=2,
            title="Go to Jail",
            description="Go to Jail",
            card_type="GO_TO_JAIL",
            details={}
        )
        ChanceCard.objects.create(
            pk=3,
            title="All players share 50 with you",
            description="It's your birthday, all players share 50 with you",
            card_type="MONEY_TO_PLAYER",
            details={"from": "all", "amount": 50}
        )
        ChanceCard.objects.create(
            pk=4,
            title="You won beauty contest",
            description="You won beauty contest",
            card_type="MONEY",
            details={"amount": 100}
        )
        ChanceCard.objects.create(
            pk=5,
            title="You have to repair all you properties",
            description="You have to repair all you properties",
            card_type="REPAIRS",
            details={"house_repair_cost": 25}
        )
        ChanceCard.objects.create(
            pk=6,
            title="Advance to Go",
            description="Move to start and collect $200",
            card_type="MOVE",
            details={"position": 0, "amount": 200}
        )
        ChanceCard.objects.create(
            pk=7,
            title="Advance to Shell",
            description="You have to refill your gas tank",
            card_type="MOVE",
            details={"position": 23}
        )
        ChanceCard.objects.create(
            pk=8,
            title="Advance to AT&T",
            description="Why not to visit AT&T?",
            card_type="MOVE",
            details={"position": 11}
        )

def load_all_data():
    load_property_groups()
    load_tiles()
    load_properties()
    load_utilities()
    load_chance_cards()


TELEGRAM_WEB_URL_FOR_TESTING = 'https://web.telegram.org/a/?test=1'

from django.core.management.base import BaseCommand
from django.db import transaction

from game.models import (
    BoardConfig,
    PropertyGroup,
    UtilityGroup,
    Start,
    Tax,
    Chance,
    Jail,
    Police,
    Casino,
    Property,
    Utility,
)


class Command(BaseCommand):
    help = "Populates database with predefined monopoly config"

    def populate(self):
        # fmt: off
        with transaction.atomic():
            board_config = BoardConfig.objects.create(name=BoardConfig.Names.CLASSIC)
            # Insert property groups
            cloth = PropertyGroup.objects.create(board_config=board_config, name="CLOTH", color="#cc5351")
            food = PropertyGroup.objects.create(board_config=board_config, name="FOOD", color="#cc8c66")
            comm = PropertyGroup.objects.create(board_config=board_config, name="COMMUNICATION", color="#c6c25f")
            auto = PropertyGroup.objects.create(board_config=board_config, name="AUTOMOBILE", color="#339f7e")
            oil = PropertyGroup.objects.create(board_config=board_config, name="OIL", color="#069aa3")
            med = PropertyGroup.objects.create(board_config=board_config, name="MEDECINE", color="#4785c2")
            fin = PropertyGroup.objects.create(board_config=board_config, name="FINANCE", color="#796fcf")
            tech = PropertyGroup.objects.create(board_config=board_config, name="TECH", color="#9c63b6")

            # Insert utility groups
            util1 = UtilityGroup.objects.create(board_config=board_config, type=UtilityGroup.Types.UTILITY_1, name="Utilities", color="#8f0d0d")
            util2 = UtilityGroup.objects.create(board_config=board_config, type=UtilityGroup.Types.UTILITY_2, name="Space", color="#3D36B6")

            # Insert tiles
            Start.objects.create(board_config=board_config, position=0, name="Go")
            Property.objects.create(board_config=board_config, position=1, name="Adidas", price=60, mortgage_value=30, house_price=50, rent=2, rent_with_1_house=10, rent_with_2_houses=30, rent_with_3_houses=90, rent_with_4_houses=160, rent_with_5_houses=250, group=cloth, icon="/media/properties/adidas_logo.png")
            Chance.objects.create(board_config=board_config, position=2, name="Chance")
            Property.objects.create(board_config=board_config, position=3, name="Nike", price=60, mortgage_value=30, house_price=50, rent=4, rent_with_1_house=20, rent_with_2_houses=60, rent_with_3_houses=180, rent_with_4_houses=320, rent_with_5_houses=450, group=cloth, icon="/media/properties/nike_icon.png")
            Tax.objects.create(board_config=board_config, position=4, name="Tax")
            Utility.objects.create(board_config=board_config, position=5, name="Wind", price=200, mortgage_value=100, group=util1, icon="/media/properties/wind_turbine.png")
            Property.objects.create(board_config=board_config, position=6, name="Pepsi", price=100, mortgage_value=50, house_price=50, rent=6, rent_with_1_house=30, rent_with_2_houses=90, rent_with_3_houses=270, rent_with_4_houses=400, rent_with_5_houses=550, group=food, icon="/media/properties/pepsi_logo.png")
            Chance.objects.create(board_config=board_config, position=7, name="Chance")
            Property.objects.create(board_config=board_config, position=8, name="Coca-Cola", price=120, mortgage_value=60, house_price=50, rent=8, rent_with_1_house=40, rent_with_2_houses=100, rent_with_3_houses=300, rent_with_4_houses=450, rent_with_5_houses=600, group=food, icon="/media/properties/Coca-Cola_logo.png")
            Property.objects.create(board_config=board_config, position=9, name="Nestle", price=120, mortgage_value=60, house_price=50, rent=8, rent_with_1_house=40, rent_with_2_houses=100, rent_with_3_houses=300, rent_with_4_houses=450, rent_with_5_houses=600, group=food, icon="/media/properties/Nestle-Logo.png")
            Jail.objects.create(board_config=board_config, position=10, name="Jail")
            Property.objects.create(board_config=board_config, position=11, name="AT&T", price=140, mortgage_value=70, house_price=100, rent=10, rent_with_1_house=50, rent_with_2_houses=150, rent_with_3_houses=450, rent_with_4_houses=625, rent_with_5_houses=750, group=comm, icon="/media/properties/att-logo-transparent.png")
            Utility.objects.create(board_config=board_config, position=12, name="NASA", price=150, mortgage_value=75, group=util2, icon="/media/properties/NASA-Logo-Large.png")
            Property.objects.create(board_config=board_config, position=13, name="Verizon", price=140, mortgage_value=70, house_price=100, rent=10, rent_with_1_house=50, rent_with_2_houses=150, rent_with_3_houses=450, rent_with_4_houses=625, rent_with_5_houses=750, group=comm, icon="/media/properties/Verizon-Logo.png")
            Property.objects.create(board_config=board_config, position=14, name="Chine Mobile", price=160, mortgage_value=80, house_price=100, rent=12, rent_with_1_house=60, rent_with_2_houses=180, rent_with_3_houses=500, rent_with_4_houses=700, rent_with_5_houses=900, group=comm, icon="/media/properties/chine_mobile_logo.png")
            Utility.objects.create(board_config=board_config, position=15, name="Dam", price=200, mortgage_value=100, group=util1, icon="/media/properties/dam.png")
            Property.objects.create(board_config=board_config, position=16, name="Toyota", price=180, mortgage_value=90, house_price=100, rent=14, rent_with_1_house=70, rent_with_2_houses=200, rent_with_3_houses=550, rent_with_4_houses=750, rent_with_5_houses=950, group=auto, icon="/media/properties/Toyota-Logo.png")
            Chance.objects.create(board_config=board_config, position=17, name="Chance")
            Property.objects.create(board_config=board_config, position=18, name="Audi", price=180, mortgage_value=90, house_price=100, rent=14, rent_with_1_house=70, rent_with_2_houses=200, rent_with_3_houses=550, rent_with_4_houses=750, rent_with_5_houses=950, group=auto, icon="/media/properties/Audi-Logo.png")
            Property.objects.create(board_config=board_config, position=19, name="Tesla", price=200, mortgage_value=100, house_price=100, rent=16, rent_with_1_house=80, rent_with_2_houses=220, rent_with_3_houses=600, rent_with_4_houses=800, rent_with_5_houses=1000, group=auto, icon="/media/properties/Tesla-Logo.png")
            Casino.objects.create(board_config=board_config, position=20, name="Casino")
            Property.objects.create(board_config=board_config, position=21, name="BP", price=220, mortgage_value=110, house_price=150, rent=18, rent_with_1_house=90, rent_with_2_houses=250, rent_with_3_houses=700, rent_with_4_houses=875, rent_with_5_houses=1050, group=oil, icon="/media/properties/bp-logo.png")
            Chance.objects.create(board_config=board_config, position=22, name="Chance")
            Property.objects.create(board_config=board_config, position=23, name="Shell", price=220, mortgage_value=110, house_price=150, rent=18, rent_with_1_house=90, rent_with_2_houses=250, rent_with_3_houses=700, rent_with_4_houses=875, rent_with_5_houses=1050, group=oil, icon="/media/properties/Shell-Logo.png")
            Property.objects.create(board_config=board_config, position=24, name="Chevron", price=240, mortgage_value=120, house_price=150, rent=20, rent_with_1_house=100, rent_with_2_houses=300, rent_with_3_houses=750, rent_with_4_houses=925, rent_with_5_houses=1100, group=oil, icon="/media/properties/Chevron-Logo.png")
            Utility.objects.create(board_config=board_config, position=25, name="Solar", price=200, mortgage_value=100, group=util1, icon="/media/properties/solar_power_icon.png")
            Property.objects.create(board_config=board_config, position=26, name="Moderna", price=260, mortgage_value=130, house_price=150, rent=22, rent_with_1_house=110, rent_with_2_houses=330, rent_with_3_houses=800, rent_with_4_houses=975, rent_with_5_houses=1150, group=med, icon="/media/properties/Moderna_logo.png")
            Property.objects.create(board_config=board_config, position=27, name="Durex", price=260, mortgage_value=130, house_price=150, rent=22, rent_with_1_house=110, rent_with_2_houses=330, rent_with_3_houses=800, rent_with_4_houses=975, rent_with_5_houses=1150, group=med, icon="/media/properties/Durex-Logo.png")
            Utility.objects.create(board_config=board_config, position=28, name="SpaceX", price=150, mortgage_value=75, group=util2, icon="/media/properties/spacex_logo_icon.webp")
            Property.objects.create(board_config=board_config, position=29, name="Pfizer", price=280, mortgage_value=140, house_price=150, rent=24, rent_with_1_house=120, rent_with_2_houses=360, rent_with_3_houses=850, rent_with_4_houses=1025, rent_with_5_houses=1200, group=med, icon="/media/properties/Pfizer_logo.png")
            Police.objects.create(board_config=board_config, position=30, name="Police")
            Property.objects.create(board_config=board_config, position=31, name="Citigroup", price=300, mortgage_value=150, house_price=200, rent=26, rent_with_1_house=130, rent_with_2_houses=390, rent_with_3_houses=900, rent_with_4_houses=1100, rent_with_5_houses=1275, group=fin, icon="/media/properties/Citigroup-Logo.png")
            Property.objects.create(board_config=board_config, position=32, name="Goldman Sachs", price=300, mortgage_value=150, house_price=200, rent=26, rent_with_1_house=130, rent_with_2_houses=390, rent_with_3_houses=900, rent_with_4_houses=1100, rent_with_5_houses=1275, group=fin, icon="/media/properties/Goldman-Sachs-Logo.png")
            Chance.objects.create(board_config=board_config, position=33, name="Chance")
            Property.objects.create(board_config=board_config, position=34, name="JPMorgan Chase", price=320, mortgage_value=160, house_price=200, rent=28, rent_with_1_house=150, rent_with_2_houses=450, rent_with_3_houses=1000, rent_with_4_houses=1200, rent_with_5_houses=1400, group=fin, icon="/media/properties/JP-Morgan-Chase-Emblem.png")
            Utility.objects.create(board_config=board_config, position=35, name="Nuke", price=200, mortgage_value=100, group=util1, icon="/media/properties/atom.png")
            Chance.objects.create(board_config=board_config, position=36, name="Chance")
            Property.objects.create(board_config=board_config, position=37, name="TikTok", price=350, mortgage_value=175, house_price=200, rent=35, rent_with_1_house=175, rent_with_2_houses=500, rent_with_3_houses=1100, rent_with_4_houses=1300, rent_with_5_houses=1500, group=tech, icon="/media/properties/tiktok-logo.webp")
            Tax.objects.create(board_config=board_config, position=38, name="Tax")
            Property.objects.create(board_config=board_config, position=39, name="Telegram", price=400, mortgage_value=200, house_price=200, rent=50, rent_with_1_house=200, rent_with_2_houses=600, rent_with_3_houses=1400, rent_with_4_houses=1700, rent_with_5_houses=2000, group=tech, icon="/media/properties/Telegram_logo.png")
        # fmt: on

    def handle(self, *args, **options):
        self.populate()
        self.stdout.write(self.style.SUCCESS("Successfully populated database"))

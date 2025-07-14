from django.test import TestCase, Client

from game.management.commands.populate_database import (
    Command as PopulateDatabaseCommand,
)


class BaseApiTestCase(TestCase):
    def setUp(self):
        PopulateDatabaseCommand().populate()

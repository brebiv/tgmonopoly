from typing import Optional
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from .base import BaseMonopolyConfig
from .classic import ClassicMonopolyConfig


def get_config(config_override: Optional[str] = None) -> BaseMonopolyConfig:
    config_name = config_override or settings.GAME_CONFIG

    if config_name == "classic":
        return ClassicMonopolyConfig()

    if config_override:
        raise ValueError(f"Could not override config with value: {config_override}")
    else:
        raise ImproperlyConfigured("GAME_CONFIG is not configured properly")

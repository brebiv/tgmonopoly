from typing import Optional

from pydantic import (
    BaseModel,
    HttpUrl,
    Field,
    TypeAdapter,
    ValidationError as PydanticValidationError,
)
from pydantic_extra_types.color import Color

from django.core.exceptions import ValidationError as DjangoValidationError
from django.conf import settings

from bot.models import TelegramUser


class TgUserPayload(BaseModel):
    id: int
    first_name: str
    last_name: str = ""
    language_code: str = Field(default="?", alias="language")
    username: Optional[str] = None
    photo_url: Optional[HttpUrl] = None
    allows_write_to_pm: Optional[bool] = None


def update_or_create_telegram_user(raw: dict) -> TelegramUser:
    try:
        payload = TgUserPayload.model_validate(raw)
    except PydanticValidationError as e:
        raise e

    # This check is need in order for sqlite not to be locked in development
    if settings.TG_UPDATE_USER_ON_EACH_REQUEST:
        user, _ = TelegramUser.objects.update_or_create(
            user_id=int(payload.id), defaults=payload.model_dump(by_alias=True)
        )
    else:
        user, _ = TelegramUser.objects.get_or_create(
            user_id=int(payload.id), defaults=payload.model_dump(by_alias=True)
        )

    return user


def validate_color(value: str):
    try:
        TypeAdapter(Color).validate_python(value)
    except PydanticValidationError:
        raise DjangoValidationError(f"'{value}' is not a valid color.")

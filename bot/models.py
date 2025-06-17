from django.db import models


# Create your models here.
class TelegramUser(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    # Telegram info
    user_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=256, blank=True, null=True)
    first_name = models.CharField(max_length=256, blank=True, null=True)
    last_name = models.CharField(max_length=256, blank=True, null=True)
    language = models.CharField(max_length=16, blank=True, null=True)

    lang_code = models.CharField(max_length=8, blank=True, null=True)

    ban = models.BooleanField(default=False)

    @property
    def full_name(self) -> str:
        return " ".join([s for s in [self.first_name, self.last_name] if s])

    def __str__(self):
        return f"{self.user_id} | {self.first_name} | @{self.username}"

from abc import ABC


class TelegramAuthMixin(ABC):
    AUTH_METHOD_NAME = "TWA"

    def generate_auth_header(self, init_data: str) -> str:
        return f"{self.AUTH_METHOD_NAME} {init_data}"

    def generate_auth_headers(self, init_data: str) -> dict:
        return {"Authorization": self.generate_auth_header(init_data)}

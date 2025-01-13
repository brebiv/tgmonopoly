class ApiException(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code

    def __str__(self):
        return f"{self.status_code}: {self.message}"

class GameException(Exception):
    pass

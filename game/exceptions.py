from rest_framework.exceptions import APIException


class GameException(APIException):
    status_code = 400

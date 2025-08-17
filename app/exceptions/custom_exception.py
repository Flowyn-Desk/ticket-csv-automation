from http import HTTPStatus


class CustomException(Exception):
    def __init__(self, message: str, status: HTTPStatus) -> None:
        super().__init__(message)
        self.message = message
        self.status = status

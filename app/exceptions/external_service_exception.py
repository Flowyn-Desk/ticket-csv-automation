from app.exceptions.custom_exception import CustomException
from http import HTTPStatus


class ExternalServiceException(CustomException):
    def __init__(self, message) -> None:
        super().__init__(message, HTTPStatus.EXPECTATION_FAILED)

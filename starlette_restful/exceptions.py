from email import message
from typing import Optional

from starlette import status


class APIException(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = "A server error occurred"

    def __init__(
        self,
        message: Optional[str] = None,
        status_code: Optional[int] = None,
    ):
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code


class AuthenticationFailed(APIException):
    status_code: int = status.HTTP_401_UNAUTHORIZED
    message: str = "Incorrect authentication credentials."


class NotAuthenticated(APIException):
    status_code: int = status.HTTP_401_UNAUTHORIZED
    message: str = "Authentication credentials were not provided."


class PermissionDenied(APIException):
    status_code: int = status.HTTP_403_FORBIDDEN
    message: str = "You do not have permission to perform this action."


class NotFound(APIException):
    status_code: int = status.HTTP_404_NOT_FOUND
    message: str = "Not found."

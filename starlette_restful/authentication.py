import base64
import binascii
from abc import ABC, abstractmethod
from typing import Any, Tuple

from starlette.authentication import SimpleUser

from starlette_restful.exceptions import AuthenticationFailed
from starlette_restful.requests import Request


class BaseAuthentication(ABC):
    @abstractmethod
    async def authenticate(self, request: Request) -> Tuple[Any, Any]:
        pass


class BasicAuthentication(BaseAuthentication):
    async def authenticate(self, request: Request) -> Tuple[SimpleUser, str]:
        auth = request.headers.get("Authorization")
        if auth is None:
            return None
        try:
            scheme, credentials = auth.split(" ")
            if scheme.lower() != "basic":
                return
            decoded = base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
            raise AuthenticationFailed("Invalid basic auth credentials")
        username, _, password = decoded.partition(":")
        return SimpleUser(username), credentials

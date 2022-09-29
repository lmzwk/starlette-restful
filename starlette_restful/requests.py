import typing

import orjson
from starlette.authentication import SimpleUser, UnauthenticatedUser
from starlette.requests import Request as StarletteReq
from starlette.types import Receive, Scope, Send

from starlette_restful.authentication import BaseAuthentication


class Request(StarletteReq):
    def __init__(self, scope: Scope, receive: Receive = ..., send: Send = ...):
        super().__init__(scope, receive, send)
        self.authenticators: typing.List[typing.Type[BaseAuthentication]] = ()
        self.successful_authenticator: typing.Optional[BaseAuthentication] = None

    async def json(self) -> typing.Dict[str, typing.Any]:
        if not hasattr(self, "_json"):
            body = await self.body()
            if body == b"":
                self._json = {}
            else:
                self._json = orjson.loads(body)
        return self._json

    @property
    def user(self) -> typing.Union[SimpleUser, UnauthenticatedUser]:
        return super().user

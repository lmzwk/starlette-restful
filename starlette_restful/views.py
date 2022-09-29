import typing

from starlette._utils import is_async_callable
from starlette.concurrency import run_in_threadpool
from starlette.endpoints import HTTPEndpoint

from starlette_restful import exceptions
from starlette_restful.requests import Request
from starlette_restful.settings import api_settings


class APIView(HTTPEndpoint):
    authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES

    def not_authenticated(self, request: Request):
        if api_settings.UNAUTHENTICATED_USER:
            request.scope["user"] = api_settings.UNAUTHENTICATED_USER()
        else:
            request.scope["user"] = None

        if api_settings.UNAUTHENTICATED_TOKEN:
            request.scope["auth"] = api_settings.UNAUTHENTICATED_TOKEN
        else:
            request.scope["auth"] = None

    def permission_denied(self, request: Request, message: typing.Optional[str] = None):
        if request.authenticators and not request.successful_authenticator:
            raise exceptions.NotAuthenticated()

        raise exceptions.PermissionDenied(message=message)

    def get_authenticators(self):
        return [auth() for auth in self.authentication_classes]

    def get_permissions(self):
        return [permission() for permission in self.permission_classes]

    async def perform_authentication(self, request: Request):
        authenticators = self.get_authenticators()
        request.authenticators = authenticators

        for authenticator in authenticators:
            try:
                user_auth_tuple = await authenticator.authenticate(request)
            except exceptions.APIException:
                self.not_authenticated()
                raise

            if user_auth_tuple is not None:
                request.successful_authenticator = authenticator
                request.scope["user"], request.scope["auth"] = user_auth_tuple
                return

        self.not_authenticated(request)

    async def check_permissions(self, request: Request):
        for permission in self.get_permissions():
            if not await permission.has_permission(request):
                self.permission_denied(
                    request, message=getattr(permission, "message", None)
                )

    def initialize_request(self):
        return Request(self.scope, receive=self.receive)

    async def initial(self, request: Request):
        await self.perform_authentication(request)
        await self.check_permissions(request)

    async def dispatch(self) -> None:
        request = self.initialize_request()
        handler_name = (
            "get"
            if request.method == "HEAD" and not hasattr(self, "head")
            else request.method.lower()
        )

        handler: typing.Callable[[Request], typing.Any] = getattr(
            self, handler_name, self.method_not_allowed
        )
        is_async = is_async_callable(handler)
        if is_async:
            response = await handler(request, **request.path_params)
        else:
            response = await run_in_threadpool(handler, request, **request.path_params)
        await response(self.scope, self.receive, self.send)

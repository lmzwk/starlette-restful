from abc import ABC, abstractmethod

from starlette_restful.requests import Request

SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


class BasePermission(ABC):
    @abstractmethod
    async def has_permission(self, request) -> bool:
        pass


class AllowAny(BasePermission):
    async def has_permission(self, request: Request) -> bool:
        return True


class IsAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """

    async def has_permission(self, request: Request) -> bool:
        return bool(request.user and request.user.is_authenticated)


class IsAuthenticatedOrReadOnly(BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    async def has_permission(self, request: Request) -> bool:
        return bool(
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_authenticated
        )

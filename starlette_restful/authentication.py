from abc import ABC, abstractmethod


class BaseAuthentication(ABC):
    @abstractmethod
    async def authenticate(self, request):
        pass

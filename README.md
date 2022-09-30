# starlette-restful

starlette-restful Inspired by Django RESTframework, All codes are a crude imitation of Django RESTframework, Intended to use Starlette to quickly implement REST APIs



## Example

Just like using Django RESTFramework in Django

**example.py**:

```python
import base64

import uvicorn
from starlette import status
from starlette.applications import Starlette
from starlette.requests import Request as StarletteReq
from starlette.responses import JSONResponse
from starlette.routing import Route

from starlette_restful import authentication, permissions
from starlette_restful.exceptions import APIException
from starlette_restful.requests import Request
from starlette_restful.responses import ORJSONResponse
from starlette_restful.views import APIView

users = {
    "lmzwk": {
        "username": "lmzwk",
        "password": "starlette_restful",
    }
}


class LoginAPIView(APIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    async def post(self, request: Request):
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        user = users.get(username)
        if (user is None) or (user["password"] != password):
            return ORJSONResponse(
                {"error": "user not exists"}, status_code=status.HTTP_404_NOT_FOUND
            )

        token = base64.b64decode(f"{username}:{password}".encode("utf-8"))
        return ORJSONResponse({"token": token})


class UserProfileAPView(APIView):
    authentication_classes = (authentication.BasicAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request: Request):
        return JSONResponse({"msg": f"hello {request.user.username}"})


app = Starlette(
    routes=[
        Route("/login", LoginAPIView),
        Route("/users/profile", UserProfileAPView),
    ]
)


def api_exception_handler(request: StarletteReq, exc: APIException):
    return ORJSONResponse({"error": exc.message}, status_code=exc.status_code)


app.add_exception_handler(APIException, api_exception_handler)

if __name__ == "__main__":
    uvicorn.run(app=app, host="127.0.0.1", port=9999)

```


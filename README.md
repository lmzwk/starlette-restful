# starlette-restful

starlette-restful Inspired by Django RESTframework, All codes are a crude imitation of Django RESTframework, Intended to use Starlette to quickly implement REST APIs



## Example

Just like using Django RESTFramework in Django

**example.py**:

```python
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from starlette_restful.requests import Request
from starlette_restful.views import APIView
import uvicorn

class HomeAPView(APIView):
    def get(self, request: Request):
        return JSONResponse({})


app = Starlette(
    routes=[
        Route("/", HomeAPView),
    ]
)

if __name__ == '__main__':
    uvicorn.run(app=app, host="127.0.0.1", port=9999)
```


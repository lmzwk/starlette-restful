from typing import Any

from starlette.responses import JSONResponse

try:
    import orjson
except ImportError:  # pragma: nocover
    orjson = None  # type: ignore


class ORJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        assert orjson is not None, "orjson must be installed to use ORJSONResponse"
        return orjson.dumps(
            content, option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY
        )

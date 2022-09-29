from typing import TYPE_CHECKING, Any, Dict, List, NoReturn, Optional, Type, Union

from .utils.module_loading import import_string


def import_from_string(val: str, setting_name: str) -> Union[Any, NoReturn]:
    """
    Attempt to import a class from a string representation.
    """
    try:
        return import_string(val)
    except ImportError as e:
        msg = "Could not import '%s' for API setting '%s'. %s: %s." % (
            val,
            setting_name,
            e.__class__.__name__,
            e,
        )
        raise ImportError(msg)


def perform_import(val: str, setting_name: str) -> Union[None, Any, NoReturn]:
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


class BaseAPISettings:
    def __init__(
        self,
        user_settings: Dict[str, Any] = None,
        defaults: Dict[str, Any] = None,
        import_strings: List[str] = None,
    ):
        if user_settings:
            self._user_settings = user_settings

        self.defaults = defaults or {}
        self.import_strings = import_strings or []
        self._cached_attrs = set()

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = {}

        return self._user_settings

    def __getattr__(self, attr: str):
        if attr not in self.defaults:
            raise AttributeError("Invalid API setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if attr in self.import_strings:
            val = perform_import(val, attr)

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def set_settings(self, *args, **kwags):
        self.relaod()
        setattr(
            self,
            "_user_settings",
            {
                key: value
                for key, value in kwags.items()
                if key in self.defaults and value != self.defaults[key]
            },
        )

    def relaod(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")


DEFAULTS = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [
        "starlette_restful.permissions.AllowAny",
    ],
    "UNAUTHENTICATED_USER": "starlette.authentication.UnauthenticatedUser",
    "UNAUTHENTICATED_TOKEN": None,
}

IMPORT_STRINGS = [
    "DEFAULT_AUTHENTICATION_CLASSES",
    "DEFAULT_PERMISSION_CLASSES",
    "UNAUTHENTICATED_USER",
    "UNAUTHENTICATED_TOKEN",
]

if TYPE_CHECKING:
    from starlette.authentication import UnauthenticatedUser

    from .authentication import BaseAuthentication
    from .permissions import BasePermission


class APISettings(BaseAPISettings):
    if TYPE_CHECKING:
        DEFAULT_AUTHENTICATION_CLASSES: List["BaseAuthentication"]
        DEFAULT_PERMISSION_CLASSES: List["BasePermission"]
        UNAUTHENTICATED_USER: Type["UnauthenticatedUser"]
        UNAUTHENTICATED_TOKEN: Optional[Any]

    def set_settings(
        self,
        *,
        DEFAULT_AUTHENTICATION_CLASSES: List[str] = None,
        DEFAULT_PERMISSION_CLASSES: List[str] = None,
        UNAUTHENTICATED_USER: Optional[str] = None,
        UNAUTHENTICATED_TOKEN: Optional[Any] = None,
    ):
        settings = locals()
        settings.pop("self")
        super().set_settings(**settings)


api_settings = APISettings(
    user_settings=None,
    defaults=DEFAULTS,
    import_strings=IMPORT_STRINGS,
)

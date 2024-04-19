"""Types for PyLoadAPI."""

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any, List, Type, TypeVar

T = TypeVar("T")


@dataclass
class Response:
    """Base Response class."""

    @classmethod
    def from_dict(cls: Type[T], d: dict[Any, Any]) -> T:
        """Convert from dict."""
        return cls(**d)

    def to_dict(self) -> dict[str, Any] | Any:
        """Convert to dict."""
        return asdict(self)

    def __getitem__(self, key: str) -> Any:
        """Return an item."""
        return getattr(self, key)


@dataclass
class StatusServerResponse(Response):
    """Dataclass for statusServer response."""

    pause: bool
    active: int
    queue: int
    total: int
    speed: float
    download: bool
    reconnect: bool
    captcha: bool


@dataclass
class LoginResponse(Response):
    """Dataclass for statusServer response."""

    _permanent: bool
    authenticated: bool
    id: int
    name: str
    role: int
    perms: int
    template: str
    _flashes: List[Any]


class PyLoadCommand(StrEnum):
    """Set status commands."""

    STATUS = "statusServer"
    PAUSE = "pauseServer"
    UNPAUSE = "unpauseServer"
    TOGGLE_PAUSE = "togglePause"
    ABORT_ALL = "stopAllDownloads"
    RESTART_FAILED = "restartFailed"
    TOGGLE_RECONNECT = "toggleReconnect"
    DELETE_FINISHED = "deleteFinished"
    RESTART = "restart"
    VERSION = "getServerVersion"
    FREESPACE = "freeSpace"

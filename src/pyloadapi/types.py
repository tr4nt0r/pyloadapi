"""Types for PyLoadAPI.

This module defines the data structures and command enumerations used by the PyLoadAPI.
The classes included in this module represent various responses from the PyLoad server
and enumerate the commands that can be sent to the server.

Classes
-------
Response
    Base class for all response types, providing methods for converting to and from dictionaries.
StatusServerResponse
    Dataclass for status server response, containing various attributes related to server status.
LoginResponse
    Dataclass for login response, containing user information and session details.
PyLoadCommand
    Enumeration of commands that can be sent to the PyLoad server.

Usage
-----
These classes are used to structure the data received from and sent to the PyLoad server.
They facilitate interaction with the PyLoadAPI by providing clear and structured representations
of the server responses and available commands.

"""

from enum import IntEnum, StrEnum
from typing import Any, NotRequired, TypedDict, TypeVar

T = TypeVar("T")


class StatusServerResponse(TypedDict):
    """Dataclass for status server response.

    Attributes
    ----------
    pause : bool
        Indicates if the server is paused. If True, `download` is False.
    active : int
        Number of active downloads.
    queue : int
        Number of downloads in the queue.
    total : int
        Total number of downloads.
    speed : float
        Current download speed of the server.
    download : bool
        Indicates if the server is not paused and will start downloading
        if there are files in the queue. If True, `pause` is False.
    reconnect : bool
        Indicates if auto-reconnect is enabled.
    captcha : bool
        Indicates if a captcha request is active.

    """

    pause: bool
    active: int
    queue: int
    total: int
    speed: float
    download: bool
    reconnect: bool
    captcha: NotRequired[bool]


class LoginResponse(TypedDict):
    """Dataclass for login response.

    Attributes
    ----------
    _permanent : bool
        Indicates if the session is permanent.
    authenticated : bool
        Indicates if the user is authenticated.
    id : int
        The ID of the user.
    name : str
        The name of the user.
    role : int
        The role ID of the user.
    perms : int
        The permissions level of the user.
    template : str
        The template associated with the user.
    _flashes : list of Any
        A list of flash messages.

    """

    _permanent: bool
    authenticated: bool
    id: int
    name: str
    role: int
    perms: int
    template: str
    _flashes: list[Any]


class PyLoadCommand(StrEnum):
    """Set of status commands for the PyLoad server.

    Attributes
    ----------
    STATUS : str
        Command to get the server status.
    PAUSE : str
        Command to pause the server.
    UNPAUSE : str
        Command to unpause the server.
    TOGGLE_PAUSE : str
        Command to toggle the pause state of the server.
    ABORT_ALL : str
        Command to stop all downloads.
    RESTART_FAILED : str
        Command to restart failed downloads.
    TOGGLE_RECONNECT : str
        Command to toggle the reconnect feature.
    DELETE_FINISHED : str
        Command to delete finished downloads.
    RESTART : str
        Command to restart the server.
    VERSION : str
        Command to get the server version.
    FREESPACE : str
        Command to get the free space in the download folder of the server.

    """

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
    ADD_PACKAGE = "addPackage"
    UPLOAD_CONTAINER = "uploadContainer"


class Destination(IntEnum):
    """Destination for new Packages."""

    COLLECTOR = 0
    QUEUE = 1

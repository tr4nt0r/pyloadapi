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
from typing import NotRequired, TypedDict, TypeVar

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

    STATUS = "status_server"
    PAUSE = "pause_server"
    UNPAUSE = "unpause_server"
    TOGGLE_PAUSE = "toggle_pause"
    ABORT_ALL = "stop_all_downloads"
    RESTART_FAILED = "restart_failed"
    TOGGLE_RECONNECT = "toggle_reconnect"
    DELETE_FINISHED = "delete_finished"
    RESTART = "restart"
    VERSION = "get_server_version"
    FREESPACE = "free_space"
    ADD_PACKAGE = "add_package"
    UPLOAD_CONTAINER = "upload_container"


class Destination(IntEnum):
    """Destination for new Packages."""

    COLLECTOR = 0
    QUEUE = 1

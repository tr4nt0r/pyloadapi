"""Simple wrapper for pyLoad's API.

This module provides a simplified interface (PyLoadAPI class) to interact with
pyLoad's API using aiohttp for asynchronous HTTP requests. It handles login
authentication and provides methods to perform various operations such as
pausing downloads, restarting pyLoad, retrieving status information, and more.
"""

from http import HTTPStatus
from json import JSONDecodeError
import logging
import traceback
from typing import Any

import aiohttp

from .exceptions import CannotConnect, InvalidAuth, ParserError
from .types import LoginResponse, PyLoadCommand, StatusServerResponse

_LOGGER = logging.getLogger(__name__)


class PyLoadAPI:
    """Simple wrapper for pyLoad's API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        api_url: str,
        username: str,
        password: str,
    ) -> None:
        """Initialize the PyLoadAPI wrapper.

        Parameters
        ----------
        session : aiohttp.ClientSession
            The aiohttp client session to use for making API requests.
        api_url : str
            The base URL of the pyLoad API.
        username : str
            Username for authenticating to the pyLoad API.
        password : str
            Password for authenticating to the pyLoad API.

        """
        self._session = session
        self.api_url = api_url
        self.username = username
        self.password = password

    async def login(self) -> LoginResponse:
        """Authenticate and login to the pyLoad API.

        Returns
        -------
        LoginResponse
            Object containing authentication response data.

        Raises
        ------
        CannotConnect
            If the login request fails due to a connection issue.
        InvalidAuth
            If authentication credentials are invalid.
        ParserError
            If there's an error parsing the login response.

        """

        user_data = {"username": self.username, "password": self.password}
        url = f"{self.api_url}api/login"
        try:
            async with self._session.post(url, data=user_data) as r:
                _LOGGER.debug("Response from %s [%s]: %s", url, r.status, r.text)

                r.raise_for_status()
                try:
                    data = await r.json()
                    if not data:
                        raise InvalidAuth
                    return LoginResponse.from_dict(data)
                except (JSONDecodeError, TypeError, aiohttp.ContentTypeError) as e:
                    _LOGGER.debug(
                        "Exception: Cannot parse login response:\n %s",
                        traceback.format_exc(),
                    )
                    raise ParserError(
                        "Login failed during parsing of request response."
                    ) from e
        except (TimeoutError, aiohttp.ClientError) as e:
            _LOGGER.debug("Exception: Cannot login:\n %s", traceback.format_exc())
            raise CannotConnect from e

    async def get(
        self, command: PyLoadCommand, params: dict[str, Any] | None = None
    ) -> Any:
        """Execute a pyLoad API command.

        Parameters
        ----------
        command : PyLoadCommand
            The pyLoad command to execute.
        params : Optional[dict[str, Any]], optional
            Optional parameters to include in the request query string, by default None.

        Returns
        -------
        Any
            The response data from the API.

        Raises
        ------
        CannotConnect
            If the request to the API fails due to a connection issue.
        InvalidAuth
            If the request fails due to invalid or expired authentication.
        ParserError
            If there's an error parsing the API response.

        Notes
        -----
        This method sends an asynchronous GET request to the pyLoad API endpoint
        specified by `command`, with optional parameters `params`. It handles
        authentication errors, HTTP status checks, and parses the JSON response.

        Example
        -------
        To retrieve the status of pyLoad, use:
        >>> status = await pyload_api.get(PyLoadCommand.STATUS)

        """
        url = f"{self.api_url}api/{command}"
        try:
            async with self._session.get(url, params=params) as r:
                _LOGGER.debug("Response from %s [%s]: %s", r.url, r.status, r.text)

                if r.status == HTTPStatus.UNAUTHORIZED:
                    raise InvalidAuth(
                        "Request failed due invalid or expired authentication cookie."
                    )
                r.raise_for_status()
                try:
                    data = await r.json()
                except JSONDecodeError as e:
                    _LOGGER.debug(
                        "Exception: Cannot parse response for %s:\n %s",
                        command,
                        traceback.format_exc(),
                    )
                    raise ParserError(
                        "Get {command} failed during parsing of request response."
                    ) from e

                return data

        except (TimeoutError, aiohttp.ClientError) as e:
            _LOGGER.debug(
                "Exception: Cannot execute command %s:\n %s",
                command,
                traceback.format_exc(),
            )
            raise CannotConnect(
                "Executing command {command} failed due to request exception"
            ) from e

    async def get_status(self) -> StatusServerResponse:
        """Get general status information of pyLoad.

        Returns
        -------
        StatusServerResponse
            Status information of pyLoad.

        Raises
        ------
        CannotConnect
            If the request to retrieve status information fails due to a connection issue.
        InvalidAuth
            If the request fails due to invalid or expired authentication.
        ParserError
            If there's an issue parsing the response from the server.

        Notes
        -----
        This method sends an asynchronous request to the pyLoad API to fetch
        general status information. It internally calls `get` with the command
        `PyLoadCommand.STATUS` and parses the JSON response into a
        `StatusServerResponse` object.

        Example
        -------
        To get the current status of pyLoad, use:
        >>> status = await pyload_api.get_status()

        """
        try:
            r = await self.get(PyLoadCommand.STATUS)
            return StatusServerResponse.from_dict(r)
        except CannotConnect as e:
            raise CannotConnect("Get status failed due to request exception") from e

    async def pause(self) -> None:
        """Pause the download queue in pyLoad.

        Raises
        ------
        CannotConnect
            If the request to pause the download queue fails due to a connection issue.
        InvalidAuth
            If the request fails due to invalid or expired authentication.
        ParserError
            If there's an issue parsing the response from the server.

        Notes
        -----
        This method sends an asynchronous request to the pyLoad API to pause the download queue.
        It internally calls `get` with the command `PyLoadCommand.PAUSE`.

        Example
        -------
        To pause the download queue, use:
        >>> await pyload_api.pause()

        """
        try:
            await self.get(PyLoadCommand.PAUSE)
        except CannotConnect as e:
            raise CannotConnect(
                "Pausing download queue failed due to request exception"
            ) from e

    async def unpause(self) -> None:
        """Unpause the download queue in pyLoad.

        Raises
        ------
        CannotConnect
            If the request to unpause the download queue fails due to a connection issue.
        InvalidAuth
            If the request fails due to invalid or expired authentication.
        ParserError
            If there's an issue parsing the response from the server.

        Notes
        -----
        This method sends an asynchronous request to the pyLoad API to unpause the download queue.
        It internally calls `get` with the command `PyLoadCommand.UNPAUSE`.

        Example
        -------
        To unpause the download queue, use:
        >>> await pyload_api.unpause()

        """
        try:
            await self.get(PyLoadCommand.UNPAUSE)
        except CannotConnect as e:
            raise CannotConnect(
                "Unpausing download queue failed due to request exception"
            ) from e

    async def toggle_pause(self) -> None:
        """Toggle the pause state of the download queue in pyLoad.

        Raises
        ------
        CannotConnect
            If the request to toggle the pause state of the download queue fails due to a connection issue.
        InvalidAuth
            If the request fails due to invalid or expired authentication.
        ParserError
            If there's an issue parsing the response from the server.

        Notes
        -----
        This method sends an asynchronous request to the pyLoad API to toggle the pause state of the download queue.
        It internally calls `get` with the command `PyLoadCommand.TOGGLE_PAUSE`.

        Example
        -------
        To toggle the pause state of the download queue, use:
        >>> await pyload_api.toggle_pause()

        """
        try:
            await self.get(PyLoadCommand.TOGGLE_PAUSE)
        except CannotConnect as e:
            raise CannotConnect(
                "Toggling pause download queue failed due to request exception"
            ) from e

    async def stop_all_downloads(self) -> None:
        """Abort all running downloads in pyLoad.

        Raises
        ------
        CannotConnect
            If the request to abort all running downloads fails due to a connection issue.
        InvalidAuth
            If the request fails due to invalid or expired authentication.
        ParserError
            If there's an issue parsing the response from the server.

        Notes
        -----
        This method sends an asynchronous request to the pyLoad API to abort all running downloads.
        It internally calls `get` with the command `PyLoadCommand.ABORT_ALL`.

        Example
        -------
        To abort all running downloads, use:
        >>> await pyload_api.stop_all_downloads()

        """
        try:
            await self.get(PyLoadCommand.ABORT_ALL)
        except CannotConnect as e:
            raise CannotConnect(
                "Aborting all running downlods failed due to request exception"
            ) from e

    async def restart_failed(self) -> None:
        """Restart all failed downloads in pyLoad.

        Raises
        ------
        CannotConnect
            If the request to restart all failed downloads fails due to a connection issue.
        InvalidAuth
            If the request fails due to invalid or expired authentication.
        ParserError
            If there's an issue parsing the response from the server.

        Notes
        -----
        This method sends an asynchronous request to the pyLoad API to restart all failed downloads.
        It internally calls `get` with the command `PyLoadCommand.RESTART_FAILED`.

        Example
        -------
        To restart all failed downloads, use:
        >>> await pyload_api.restart_failed()

        """
        try:
            await self.get(PyLoadCommand.RESTART_FAILED)
        except CannotConnect as e:
            raise CannotConnect(
                "Restarting all failed files failed due to request exception"
            ) from e

    async def toggle_reconnect(self) -> None:
        """Toggle reconnect activation in pyLoad.

        Raises
        ------
        CannotConnect
            If the request to toggle reconnect activation fails due to a connection issue.
        InvalidAuth
            If the request fails due to invalid or expired authentication.
        ParserError
            If there's an issue parsing the response from the server.

        Notes
        -----
        This method sends an asynchronous request to the pyLoad API to toggle the reconnect activation.
        It internally calls `get` with the command `PyLoadCommand.TOGGLE_RECONNECT`.

        Example
        -------
        To toggle reconnect activation, use:
        >>> await pyload_api.toggle_reconnect()

        """
        await self.get(PyLoadCommand.TOGGLE_RECONNECT)

    async def delete_finished(self) -> None:
        """Delete all finished files and completely finished packages in pyLoad.

        Raises
        ------
        CannotConnect
            If the request to delete finished files and packages fails due to a connection issue.
        InvalidAuth
            If the request fails due to invalid or expired authentication.
        ParserError
            If there's an issue parsing the response from the server.

        Notes
        -----
        This method sends an asynchronous request to the pyLoad API to delete all finished files and packages.
        It internally calls `get` with the command `PyLoadCommand.DELETE_FINISHED`.

        Example
        -------
        To delete all finished files and packages, use:
        >>> await pyload_api.delete_finished()

        """
        try:
            await self.get(PyLoadCommand.DELETE_FINISHED)
        except CannotConnect as e:
            raise CannotConnect(
                "Deleting all finished files failed due to request exception"
            ) from e

    async def restart(self) -> None:
        """Restart the pyLoad core.

        Raises
        ------
        CannotConnect
            If the request to restart the pyLoad core fails due to a connection issue.
        InvalidAuth
            If the request fails due to invalid or expired authentication.
        ParserError
            If there's an issue parsing the response from the server.

        Notes
        -----
        This method sends an asynchronous request to the pyLoad API to restart its core functionality.
        It internally calls `get` with the command `PyLoadCommand.RESTART`.

        Example
        -------
        To restart the pyLoad core, use:
        >>> await pyload_api.restart()

        """
        try:
            await self.get(PyLoadCommand.RESTART)
        except CannotConnect as e:
            raise CannotConnect(
                "Restarting pyLoad core failed due to request exception"
            ) from e

    async def version(self) -> str:
        """Get the version of pyLoad.

        Returns
        -------
        str
            The version of pyLoad as a string.

        Raises
        ------
        CannotConnect
            If the request to get the pyLoad version fails due to a connection issue.
        InvalidAuth
            If the request fails due to invalid or expired authentication.
        ParserError
            If there's an issue parsing the response from the server.

        Notes
        -----
        This method sends an asynchronous request to the pyLoad API to retrieve its version.
        It internally calls `get` with the command `PyLoadCommand.VERSION`.

        Example
        -------
        To fetch the version of pyLoad, use:
        >>> version = await pyload_api.version()

        """
        try:
            r = await self.get(PyLoadCommand.VERSION)
            return str(r)
        except CannotConnect as e:
            raise CannotConnect("Get version failed due to request exception") from e

    async def free_space(self) -> int:
        """Get the available free space at the download directory in bytes.

        Returns
        -------
        int
            The amount of free space available at the download directory in bytes.

        Raises
        ------
        CannotConnect
            If the request to get the free space information fails due to a connection issue.
        InvalidAuth
            If the request fails due to invalid or expired authentication.
        ParserError
            If there's an issue parsing the response from the server.

        Notes
        -----
        This method sends an asynchronous request to the pyLoad API to retrieve the available
        free space at the download directory. It internally calls `get` with the command
        `PyLoadCommand.FREESPACE`.

        Example
        -------
        To fetch the available free space at the download directory, use:
        >>> free_space = await pyload_api.free_space()

        """
        try:
            r = await self.get(PyLoadCommand.FREESPACE)
            return int(r)
        except CannotConnect as e:
            raise CannotConnect("Get free space failed due to request exception") from e

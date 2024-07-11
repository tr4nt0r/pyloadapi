"""Simple wrapper for pyLoad's API.

This module provides a simplified interface (PyLoadAPI class) to interact with
pyLoad's API using aiohttp for asynchronous HTTP requests. It handles login
authentication and provides methods to perform various operations such as
pausing downloads, restarting pyLoad, retrieving status information, and more.
"""

from http import HTTPStatus
import json
from json import JSONDecodeError
import logging
import traceback
from typing import Any

import aiohttp

from .exceptions import CannotConnect, InvalidAuth, ParserError
from .types import Destination, LoginResponse, PyLoadCommand, StatusServerResponse

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
                    data: LoginResponse = await r.json()
                except (JSONDecodeError, TypeError, aiohttp.ContentTypeError) as e:
                    _LOGGER.debug(
                        "Exception: Cannot parse login response:\n %s",
                        traceback.format_exc(),
                    )
                    raise ParserError(
                        "Login failed during parsing of request response."
                    ) from e
                else:
                    if not data:
                        raise InvalidAuth
                    return data
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
        ```python
        status = await pyload_api.get(PyLoadCommand.STATUS)
        ```

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

    async def post(
        self,
        command: PyLoadCommand,
        data: dict[str, Any],
    ) -> Any:
        """Execute a pyLoad API command using a POST request.

        Parameters
        ----------
        command : PyLoadCommand
            The pyLoad command to execute.
        data : dict[str, Any]
            Data to include in the request body. The values in the dictionary
            will be JSON encoded.

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
        This method sends an asynchronous POST request to the pyLoad API endpoint
        specified by `command`, with the provided `data` dictionary. It handles
        authentication errors, HTTP status checks, and parses the JSON response.


        Example
        -------
        To add a new package to pyLoad, use:
        ```python
        status = await pyload_api.post(PyLoadCommand.ADD_PACKAGE, data={...}
        ```

        """
        url = f"{self.api_url}api/{command}"
        data = {
            k: str(v) if isinstance(v, bytes) else json.dumps(v)
            for k, v in data.items()
        }

        try:
            async with self._session.post(url, data=data) as r:
                _LOGGER.debug(
                    "Response from %s [%s]: %s", r.url, r.status, await r.text()
                )

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
                        f"Get {command} failed during parsing of request response."
                    ) from e

                return data

        except (TimeoutError, aiohttp.ClientError) as e:
            _LOGGER.debug(
                "Exception: Cannot execute command %s:\n %s",
                command,
                traceback.format_exc(),
            )
            raise CannotConnect(
                f"Executing command {command} failed due to request exception"
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
        ```python
        status = await pyload_api.get_status()
        ```

        """
        try:
            data: StatusServerResponse = await self.get(PyLoadCommand.STATUS)
        except CannotConnect as e:
            raise CannotConnect("Get status failed due to request exception") from e
        else:
            return data

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
        ```python
        await pyload_api.pause()
        ```

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
        ```python
        await pyload_api.unpause()
        ```

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
        ```python
        await pyload_api.toggle_pause()
        ```

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
        ```python
        await pyload_api.stop_all_downloads()
        ```

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
        ```python
        await pyload_api.restart_failed()
        ```

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
        ```python
        await pyload_api.toggle_reconnect()
        ```

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
        ```python
        await pyload_api.delete_finished()
        ```

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
        ```python
        await pyload_api.restart()
        ```

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
        ```python
        version = await pyload_api.version()
        ```

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
        ```python
        free_space = await pyload_api.free_space()
        ```

        """
        try:
            r = await self.get(PyLoadCommand.FREESPACE)
            return int(r)
        except CannotConnect as e:
            raise CannotConnect("Get free space failed due to request exception") from e

    async def add_package(
        self,
        name: str,
        links: list[str],
        destination: Destination = Destination.COLLECTOR,
    ) -> int:
        """Add a new package to pyLoad from a list of links.

        Parameters
        ----------
        name : str
            The name of the package to be added.
        links : list[str]
            A list of download links to be included in the package.
        destination : Destination, optional
            The destination where the package should be stored, by default Destination.COLLECTOR.

        Returns
        -------
        int
            The ID of the newly created package.

        Raises
        ------
        CannotConnect
            If the request to add the package fails due to a connection issue.
        InvalidAuth
            If the request fails due to invalid or expired authentication.
        ParserError
            If there's an issue parsing the response from the server.

        Example
        -------
        To add a new package with a couple of links to the pyLoad collector:
        ```python
        package_id = await pyload_api.add_package(
            "test_package",
            [
                "https://example.com/file1.zip",
                "https://example.com/file2.iso",
            ]
        )
        ```
        """

        try:
            r = await self.post(
                PyLoadCommand.ADD_PACKAGE,
                data={
                    "name": name,
                    "links": links,
                    "dest": destination,
                },
            )
            return int(r)
        except CannotConnect as e:
            raise CannotConnect("Adding package failed due to request exception") from e

    async def upload_container(
        self,
        filename: str,
        binary_data: bytes,
    ) -> None:
        """Upload a container file to pyLoad.

        Parameters
        ----------
        filename : str
            The name of the file to be uploaded.
        binary_data : bytes
            The binary content of the file.

        Returns
        -------
        None

        Raises
        ------
        CannotConnect
            If the request to upload the container fails due to a connection issue.
        InvalidAuth
            If the request fails due to invalid or expired authentication.

        Example
        -------
        To upload a container file to pyLoad:
        ```python
        await pyload_api.upload_container(
            "example_container.dlc",
            b"binary data of the file"
        )
        ```
        """
        try:
            await self.post(
                PyLoadCommand.UPLOAD_CONTAINER,
                data={"filename": filename, "data": binary_data},
            )

        except CannotConnect as e:
            raise CannotConnect(
                "Uploading container to pyLoad failed due to request exception"
            ) from e

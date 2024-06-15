"""Simple wrapper for pyLoad's API."""

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
        """Initialize pyLoad API."""
        self._session = session
        self.api_url = api_url
        self.username = username
        self.password = password

    async def login(self) -> LoginResponse:
        """Login to pyLoad API."""

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
        """Execute a pyLoad command."""
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
                Status information of pyLoad

        Raises
        ------
            CannotConnect:
                if request fails

        """
        try:
            r = await self.get(PyLoadCommand.STATUS)
            return StatusServerResponse.from_dict(r)
        except CannotConnect as e:
            raise CannotConnect("Get status failed due to request exception") from e

    async def pause(self) -> None:
        """Pause download queue.

        Raises
        ------
            CannotConnect:
                if request fails

        """
        try:
            await self.get(PyLoadCommand.PAUSE)
        except CannotConnect as e:
            raise CannotConnect(
                "Pausing download queue failed due to request exception"
            ) from e

    async def unpause(self) -> None:
        """Unpause download queue.

        Raises
        ------
            CannotConnect:
                if request fails

        """
        try:
            await self.get(PyLoadCommand.UNPAUSE)
        except CannotConnect as e:
            raise CannotConnect(
                "Unpausing download queue failed due to request exception"
            ) from e

    async def toggle_pause(self) -> None:
        """Toggle pause download queue.

        Raises
        ------
            CannotConnect:
                if request fails

        """
        try:
            await self.get(PyLoadCommand.TOGGLE_PAUSE)
        except CannotConnect as e:
            raise CannotConnect(
                "Toggling pause download queue failed due to request exception"
            ) from e

    async def stop_all_downloads(self) -> None:
        """Abort all running downloads.

        Raises
        ------
            CannotConnect:
                if request fails

        """
        try:
            await self.get(PyLoadCommand.ABORT_ALL)
        except CannotConnect as e:
            raise CannotConnect(
                "Aborting all running downlods failed due to request exception"
            ) from e

    async def restart_failed(self) -> None:
        """Restart all failed files.

        Raises
        ------
            CannotConnect:
                if request fails

        """
        try:
            await self.get(PyLoadCommand.RESTART_FAILED)
        except CannotConnect as e:
            raise CannotConnect(
                "Restarting all failed files failed due to request exception"
            ) from e

    async def toggle_reconnect(self) -> None:
        """Toggle reconnect activation.

        Raises
        ------
            CannotConnect:
                if request fails

        """
        await self.get(PyLoadCommand.TOGGLE_RECONNECT)

    async def delete_finished(self) -> None:
        """Delete all finished files and completly finished packages.

        Raises
        ------
            CannotConnect:
                if request fails

        """
        try:
            await self.get(PyLoadCommand.DELETE_FINISHED)
        except CannotConnect as e:
            raise CannotConnect(
                "Deleting all finished files failed due to request exception"
            ) from e

    async def restart(self) -> None:
        """Restart pyload core.

        Raises
        ------
            CannotConnect:
                if request fails

        """
        try:
            await self.get(PyLoadCommand.RESTART)
        except CannotConnect as e:
            raise CannotConnect(
                "Restarting pyLoad core failed due to request exception"
            ) from e

    async def version(self) -> str:
        """Get version of pyLoad.

        Returns
        -------
            str:
                pyLoad Version

        Raises
        ------
            CannotConnect:
                if request fails

        """
        try:
            r = await self.get(PyLoadCommand.VERSION)
            return str(r)
        except CannotConnect as e:
            raise CannotConnect("Get version failed due to request exception") from e

    async def free_space(self) -> int:
        """Get available free space at download directory in bytes.

        Returns
        -------
            int:
                free space at download directory in bytes

        Raises
        ------
            CannotConnect:
                if request fails

        """
        try:
            r = await self.get(PyLoadCommand.FREESPACE)
            return int(r)
        except CannotConnect as e:
            raise CannotConnect("Get free space failed due to request exception") from e

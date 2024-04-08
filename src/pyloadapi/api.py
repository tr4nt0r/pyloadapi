"""Simple wrapper for pyLoad's API."""

from http import HTTPStatus
from json import JSONDecodeError
import logging
import traceback
from typing import Optional

import aiohttp

from .exceptions import CannotConnect, InvalidAuth, ParserError
from .types import LoginResponse, StatusServerResponse

_LOGGER = logging.getLogger(__name__)


class PyLoadAPI:
    """Simple wrapper for pyLoad's API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        api_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """Initialize pyLoad API."""
        self._session = session
        self.api_url = api_url
        self.status = None
        self.username = username
        self.password = password

    async def login(self) -> LoginResponse:
        """Login to pyLoad API."""

        user_data = {"username": self.username, "password": self.password}
        url = f"{self.api_url}api/login"
        try:
            async with self._session.post(url, data=user_data) as r:
                _LOGGER.debug(
                    "Response from %s [%s]: %s", url, r.status, (await r.text())
                )
                r.raise_for_status()
                try:
                    data = await r.json()
                    if not r:
                        raise InvalidAuth
                    return LoginResponse.from_dict(data)
                except JSONDecodeError as e:
                    _LOGGER.error(
                        "Exception: Cannot parse login response:\n %s",
                        traceback.format_exc(),
                    )
                    raise ParserError(
                        "Login failed during parsing of request response."
                    ) from e
        except (TimeoutError, aiohttp.ClientError) as e:
            _LOGGER.error("Exception: Cannot login:\n %s", traceback.format_exc())
            raise CannotConnect from e

    async def get_status(self) -> StatusServerResponse:
        """Get general status information of pyLoad."""
        url = f"{self.api_url}api/statusServer"
        try:
            async with self._session.get(url) as r:
                _LOGGER.debug(
                    "Response from %s [%s]: %s", url, r.status, (await r.text())
                )
                r.raise_for_status()
                if r.status == HTTPStatus.UNAUTHORIZED:
                    raise InvalidAuth
                try:
                    data = await r.json()
                    return StatusServerResponse.from_dict(data)
                except JSONDecodeError as e:
                    _LOGGER.error(
                        "Exception: Cannot parse status response:\n %s",
                        traceback.format_exc(),
                    )
                    raise ParserError(
                        "Get status failed during parsing of request response."
                    ) from e

        except (TimeoutError, aiohttp.ClientError) as e:
            _LOGGER.error("Exception: Cannot get status:\n %s", traceback.format_exc())
            raise CannotConnect("Get status failed due to request exception") from e

    async def version(self) -> str:
        """Get version of pyLoad."""
        url = f"{self.api_url}api/getServerVersion"
        try:
            async with self._session.get(url) as r:
                _LOGGER.debug(
                    "Response from %s [%s]: %s", url, r.status, (await r.text())
                )
                if r.status == HTTPStatus.UNAUTHORIZED:
                    raise InvalidAuth
                r.raise_for_status()
                try:
                    data = await r.json()
                    return str(data)
                except JSONDecodeError as e:
                    _LOGGER.error(
                        "Exception: Cannot parse status response:\n %s",
                        traceback.format_exc(),
                    )
                    raise ParserError(
                        "Get version failed during parsing of request response."
                    ) from e
        except (TimeoutError, aiohttp.ClientError) as e:
            _LOGGER.error("Exception: Cannot get version:\n %s", traceback.format_exc())
            raise CannotConnect("Get version failed due to request exception") from e

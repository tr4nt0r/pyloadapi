"""Tests for PyLoadAPI."""

import asyncio
from http import HTTPStatus
from json import JSONDecodeError
import re
from typing import Any

import aiohttp
from aioresponses import aioresponses
from dotenv import load_dotenv
import pytest

from pyloadapi.api import PyLoadAPI
from pyloadapi.exceptions import CannotConnect, InvalidAuth, ParserError

from .conftest import TEST_API_URL, TEST_LOGIN_RESPONSE

load_dotenv()


async def test_login(pyload: PyLoadAPI, mocked_aiohttp: aioresponses) -> None:
    """Test login."""
    mocked_aiohttp.post(
        f"{TEST_API_URL}api/login", status=HTTPStatus.OK, payload=TEST_LOGIN_RESPONSE
    )

    result = await pyload.login()
    assert result.to_dict() == TEST_LOGIN_RESPONSE


async def test_login_invalidauth(
    pyload: PyLoadAPI, mocked_aiohttp: aioresponses
) -> None:
    """Test login."""
    mocked_aiohttp.post(f"{TEST_API_URL}api/login", status=HTTPStatus.OK)

    with pytest.raises(InvalidAuth):
        await pyload.login()


@pytest.mark.parametrize(
    "method",
    [
        "version",
        "get_status",
        "pause",
        "unpause",
        "toggle_pause",
        "stop_all_downloads",
        "restart_failed",
        "toggle_reconnect",
        "delete_finished",
        "restart",
        "free_space",
    ],
)
async def test_invalidauth(
    pyload: PyLoadAPI, mocked_aiohttp: aioresponses, method: str
) -> None:
    """Test login."""

    mocked_aiohttp.get(re.compile(r".*"), status=HTTPStatus.UNAUTHORIZED)

    with pytest.raises(InvalidAuth):
        await getattr(pyload, method)()


@pytest.mark.parametrize(
    "exception",
    [asyncio.TimeoutError, aiohttp.ClientError],
)
@pytest.mark.parametrize(
    "method",
    [
        "login",
        "version",
        "get_status",
        "pause",
        "unpause",
        "toggle_pause",
        "stop_all_downloads",
        "restart_failed",
        "toggle_reconnect",
        "delete_finished",
        "restart",
        "free_space",
    ],
)
async def test_request_exceptions(
    pyload: PyLoadAPI,
    mocked_aiohttp: aioresponses,
    exception: Exception,
    method: str,
) -> None:
    """Test login request exception."""

    mocked_aiohttp.get(re.compile(r".*"), exception=exception)
    mocked_aiohttp.post(re.compile(r".*"), exception=exception)

    with pytest.raises(expected_exception=CannotConnect):
        await getattr(pyload, method)()


@pytest.mark.parametrize(
    "method",
    ["login", "version", "get_status"],
)
async def test_parse_exceptions(
    pyload: PyLoadAPI,
    mocked_aiohttp: aioresponses,
    monkeypatch: pytest.MonkeyPatch,
    method: str,
) -> None:
    """Test login."""
    mocked_aiohttp.get(re.compile(r".*"), status=HTTPStatus.OK)
    mocked_aiohttp.post(re.compile(r".*"), status=HTTPStatus.OK)

    async def json(*args: Any) -> None:
        raise JSONDecodeError("", "", 0)

    monkeypatch.setattr(aiohttp.ClientResponse, "json", json)

    with pytest.raises(expected_exception=ParserError):
        await getattr(pyload, method)()

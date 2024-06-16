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

from pyloadapi import (
    CannotConnect,
    InvalidAuth,
    ParserError,
    PyLoadAPI,
    StatusServerResponse,
)
from pyloadapi.types import LoginResponse

from .conftest import TEST_API_URL, TEST_LOGIN_RESPONSE, TEST_STATUS_RESPONSE

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
    ("method", "result"),
    [
        ("version", "0.5.0"),
        ("get_status", StatusServerResponse.from_dict(TEST_STATUS_RESPONSE)),
        ("pause", None),
        ("unpause", None),
        ("toggle_pause", None),
        ("stop_all_downloads", None),
        ("restart_failed", None),
        ("toggle_reconnect", None),
        ("delete_finished", None),
        ("restart", None),
        ("free_space", 100000),
    ],
)
async def test_api_methods(
    pyload: PyLoadAPI, mocked_aiohttp: aioresponses, method: str, result: Any
) -> None:
    """Test login."""

    mocked_aiohttp.get(
        f"{TEST_API_URL}api/getServerVersion",
        payload="0.5.0",
    )
    mocked_aiohttp.get(
        f"{TEST_API_URL}api/statusServer",
        payload=TEST_STATUS_RESPONSE,
    )
    mocked_aiohttp.get(f"{TEST_API_URL}api/freeSpace", payload=100000)
    mocked_aiohttp.get(re.compile(r".*"))

    assert await getattr(pyload, method)() == result


def test_dataclass() -> None:
    """Test methods of Response dataclass."""
    result = LoginResponse.from_dict(TEST_LOGIN_RESPONSE)

    assert result.to_dict() == TEST_LOGIN_RESPONSE
    assert result["name"] == "test-username"


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

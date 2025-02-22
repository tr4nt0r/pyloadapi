"""Tests for PyLoadAPI."""

import asyncio
from http import HTTPStatus
from json import JSONDecodeError
import re
from typing import Any

import aiohttp
from aioresponses import aioresponses
import pytest

from pyloadapi import CannotConnect, InvalidAuth, ParserError, PyLoadAPI
from pyloadapi.types import Destination

from .conftest import (
    BYTE_DATA,
    TEST_API_URL,
    TEST_LOGIN_RESPONSE,
    TEST_STATUS_RESPONSE,
    TEST_STATUS_RESPONSE_NO_CAPTCHA,
)


async def test_login(pyload: PyLoadAPI, mocked_aiohttp: aioresponses) -> None:
    """Test login."""
    mocked_aiohttp.post(
        f"{TEST_API_URL}api/login", status=HTTPStatus.OK, payload=TEST_LOGIN_RESPONSE
    )

    result = await pyload.login()
    assert result == TEST_LOGIN_RESPONSE


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
        ("get_status", TEST_STATUS_RESPONSE),
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
    """Test API methods."""

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


async def test_status_no_captcha(
    pyload: PyLoadAPI, mocked_aiohttp: aioresponses
) -> None:
    """Test status for pre 0.5.0 pyLoad response."""

    mocked_aiohttp.get(
        f"{TEST_API_URL}api/statusServer",
        payload=TEST_STATUS_RESPONSE_NO_CAPTCHA,
    )

    assert await pyload.get_status() == TEST_STATUS_RESPONSE_NO_CAPTCHA


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


async def test_upload_container(
    pyload: PyLoadAPI, mocked_aiohttp: aioresponses
) -> None:
    """Test upload_container method."""

    mocked_aiohttp.post(
        f"{TEST_API_URL}api/uploadContainer",
    )

    await pyload.upload_container("filename.dlc", BYTE_DATA)
    mocked_aiohttp.assert_called_once_with(
        f"{TEST_API_URL}api/uploadContainer",
        method="POST",
        data={"filename": '"filename.dlc"', "data": "b'BYTE_DATA'"},
    )


async def test_upload_container_exception(
    pyload: PyLoadAPI, mocked_aiohttp: aioresponses
) -> None:
    """Test upload_container exception."""

    mocked_aiohttp.post(
        f"{TEST_API_URL}api/uploadContainer", exception=aiohttp.ClientError
    )

    with pytest.raises(expected_exception=CannotConnect):
        await pyload.upload_container("filename.dlc", BYTE_DATA)


async def test_upload_container_unauthorized(
    pyload: PyLoadAPI, mocked_aiohttp: aioresponses
) -> None:
    """Test upload_container authentication error."""

    mocked_aiohttp.post(
        f"{TEST_API_URL}api/uploadContainer", status=HTTPStatus.UNAUTHORIZED
    )

    with pytest.raises(expected_exception=InvalidAuth):
        await pyload.upload_container("filename.dlc", BYTE_DATA)


async def test_upload_container_parse_exception(
    pyload: PyLoadAPI,
    mocked_aiohttp: aioresponses,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test upload_container parser error."""

    mocked_aiohttp.post(re.compile(r".*"), status=HTTPStatus.OK)

    async def json(*args: Any) -> None:
        raise JSONDecodeError("", "", 0)

    monkeypatch.setattr(aiohttp.ClientResponse, "json", json)

    with pytest.raises(expected_exception=ParserError):
        await pyload.upload_container("filename.dlc", BYTE_DATA)


async def test_add_package(pyload: PyLoadAPI, mocked_aiohttp: aioresponses) -> None:
    """Test add_package method."""

    mocked_aiohttp.post(
        f"{TEST_API_URL}api/addPackage",
        payload=1,
    )

    await pyload.add_package(
        name="Package Name",
        links=[
            "https://example.com/file1.zip",
            "https://example.com/file2.iso",
        ],
        destination=Destination.COLLECTOR,
    )
    mocked_aiohttp.assert_called_once_with(
        f"{TEST_API_URL}api/addPackage",
        method="POST",
        data={
            "name": '"Package Name"',
            "links": '["https://example.com/file1.zip", "https://example.com/file2.iso"]',
            "dest": "0",
        },
    )


async def test_add_package_exception(
    pyload: PyLoadAPI, mocked_aiohttp: aioresponses
) -> None:
    """Test add_package with exception."""

    mocked_aiohttp.post(
        f"{TEST_API_URL}api/addPackage", payload=1, exception=aiohttp.ClientError
    )
    with pytest.raises(expected_exception=CannotConnect):
        await pyload.add_package(
            name="Package Name",
            links=[
                "https://example.com/file1.zip",
                "https://example.com/file2.iso",
            ],
            destination=Destination.COLLECTOR,
        )


async def test_add_package_unauthorized(
    pyload: PyLoadAPI, mocked_aiohttp: aioresponses
) -> None:
    """Test add_package authentication error."""

    mocked_aiohttp.post(
        f"{TEST_API_URL}api/addPackage", payload=1, status=HTTPStatus.UNAUTHORIZED
    )
    with pytest.raises(expected_exception=InvalidAuth):
        await pyload.add_package(
            name="Package Name",
            links=[
                "https://example.com/file1.zip",
                "https://example.com/file2.iso",
            ],
            destination=Destination.COLLECTOR,
        )


async def test_add_package_parse_exception(
    pyload: PyLoadAPI,
    mocked_aiohttp: aioresponses,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test add_package parser error."""

    mocked_aiohttp.post(re.compile(r".*"), status=HTTPStatus.OK)

    async def json(*args: Any) -> None:
        raise JSONDecodeError("", "", 0)

    monkeypatch.setattr(aiohttp.ClientResponse, "json", json)

    with pytest.raises(expected_exception=ParserError):
        await pyload.add_package(
            name="Package Name",
            links=[
                "https://example.com/file1.zip",
                "https://example.com/file2.iso",
            ],
            destination=Destination.COLLECTOR,
        )

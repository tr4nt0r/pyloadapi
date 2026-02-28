"""Tests for PyLoadAPI."""

import asyncio
from http import HTTPStatus
from json import JSONDecodeError
from typing import Any
from unittest.mock import AsyncMock

import aiohttp
import pytest
from yarl import URL

from pyloadapi import CannotConnect, InvalidAuth, ParserError, PyLoadAPI
from pyloadapi.types import Destination

from .conftest import BYTE_DATA, TEST_STATUS_RESPONSE, TEST_STATUS_RESPONSE_NO_CAPTCHA


@pytest.mark.parametrize(
    ("method", "result", "response"),
    [
        ("version", "0.5.0", "0.5.0"),
        ("get_status", TEST_STATUS_RESPONSE, TEST_STATUS_RESPONSE),
        ("pause", None, ""),
        ("unpause", None, ""),
        ("toggle_pause", None, ""),
        ("stop_all_downloads", None, ""),
        ("restart_failed", None, ""),
        ("toggle_reconnect", None, ""),
        ("delete_finished", None, ""),
        ("restart", None, ""),
        ("free_space", 100000, "100000"),
    ],
)
async def test_api_methods(
    pyload: PyLoadAPI,
    session: AsyncMock,
    method: str,
    result: Any,
    response: str,
) -> None:
    """Test API methods."""

    session.request.return_value.__aenter__.return_value.json.return_value = response

    assert await getattr(pyload, method)() == result


async def test_status_no_captcha(
    pyload: PyLoadAPI,
    session: AsyncMock,
) -> None:
    """Test status for pre 0.5.0 pyLoad response."""
    session.request.return_value.__aenter__.return_value.json.return_value = (
        TEST_STATUS_RESPONSE_NO_CAPTCHA
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
    pyload: PyLoadAPI,
    session: AsyncMock,
    method: str,
) -> None:
    """Test login."""
    session.request.return_value.__aenter__.return_value.status = (
        HTTPStatus.UNAUTHORIZED
    )

    with pytest.raises(InvalidAuth):
        await getattr(pyload, method)()


@pytest.mark.parametrize(
    "exception",
    [asyncio.TimeoutError, aiohttp.ClientError],
)
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
async def test_request_exceptions(
    pyload: PyLoadAPI,
    exception: Exception,
    session: AsyncMock,
    method: str,
) -> None:
    """Test login request exception."""
    session.get.return_value.__aenter__.side_effect = exception
    session.post.return_value.__aenter__.side_effect = exception

    with pytest.raises(expected_exception=CannotConnect):
        await getattr(pyload, method)()


@pytest.mark.parametrize(
    "method",
    ["version", "get_status"],
)
async def test_parse_exceptions(
    pyload: PyLoadAPI,
    session: AsyncMock,
    method: str,
) -> None:
    """Test login."""
    session.request.return_value.__aenter__.return_value.json.side_effect = (
        JSONDecodeError("", "", 0)
    )

    with pytest.raises(expected_exception=ParserError):
        await getattr(pyload, method)()


async def test_upload_container(
    pyload: PyLoadAPI,
    session: AsyncMock,
) -> None:
    """Test upload_container method."""

    await pyload.upload_container("filename.dlc", BYTE_DATA)

    session.post.assert_called_once_with(
        URL("https://example.com:8000/api/upload_container"),
        data={"filename": '"filename.dlc"', "data": "b'BYTE_DATA'"},
        auth=aiohttp.BasicAuth(
            login="test-username",
            password="test-password",  # noqa: S106
            encoding="latin1",
        ),
    )


async def test_upload_container_exception(
    pyload: PyLoadAPI,
    session: AsyncMock,
) -> None:
    """Test upload_container exception."""

    session.post.return_value.__aenter__.side_effect = aiohttp.ClientError

    with pytest.raises(expected_exception=CannotConnect):
        await pyload.upload_container("filename.dlc", BYTE_DATA)


async def test_upload_container_unauthorized(
    pyload: PyLoadAPI,
    session: AsyncMock,
) -> None:
    """Test upload_container authentication error."""

    session.post.return_value.__aenter__.return_value.status = HTTPStatus.UNAUTHORIZED

    with pytest.raises(expected_exception=InvalidAuth):
        await pyload.upload_container("filename.dlc", BYTE_DATA)


async def test_upload_container_parse_exception(
    pyload: PyLoadAPI,
    session: AsyncMock,
) -> None:
    """Test upload_container parser error."""

    session.request.return_value.__aenter__.return_value.json.side_effect = (
        JSONDecodeError("", "", 0)
    )

    with pytest.raises(expected_exception=ParserError):
        await pyload.upload_container("filename.dlc", BYTE_DATA)


async def test_add_package(
    pyload: PyLoadAPI,
    session: AsyncMock,
) -> None:
    """Test add_package method."""

    await pyload.add_package(
        name="Package Name",
        links=[
            "https://example.com/file1.zip",
            "https://example.com/file2.iso",
        ],
        destination=Destination.COLLECTOR,
    )

    session.post.assert_called_once_with(
        URL("https://example.com:8000/api/add_package"),
        data={
            "name": '"Package Name"',
            "links": '["https://example.com/file1.zip", "https://example.com/file2.iso"]',
            "dest": "0",
        },
        auth=aiohttp.BasicAuth(
            login="test-username",
            password="test-password",  # noqa: S106
            encoding="latin1",
        ),
    )


async def test_add_package_exception(
    pyload: PyLoadAPI,
    session: AsyncMock,
) -> None:
    """Test add_package with exception."""

    session.post.return_value.__aenter__.side_effect = aiohttp.ClientError

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
    pyload: PyLoadAPI,
    session: AsyncMock,
) -> None:
    """Test add_package authentication error."""

    session.post.return_value.__aenter__.return_value.status = HTTPStatus.UNAUTHORIZED

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
    session: AsyncMock,
) -> None:
    """Test add_package parser error."""

    session.request.return_value.__aenter__.return_value.json.side_effect = (
        JSONDecodeError("", "", 0)
    )
    with pytest.raises(expected_exception=ParserError):
        await pyload.add_package(
            name="Package Name",
            links=[
                "https://example.com/file1.zip",
                "https://example.com/file2.iso",
            ],
            destination=Destination.COLLECTOR,
        )

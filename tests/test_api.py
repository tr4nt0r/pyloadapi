"""Tests for PyLoadAPI."""

import asyncio

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
        f"{TEST_API_URL}api/login", status=200, payload=TEST_LOGIN_RESPONSE
    )

    result = await pyload.login()
    assert result.to_dict() == TEST_LOGIN_RESPONSE


async def test_login_invalidauth(
    pyload: PyLoadAPI, mocked_aiohttp: aioresponses
) -> None:
    """Test login."""
    mocked_aiohttp.post(f"{TEST_API_URL}api/login", status=200)

    with pytest.raises(InvalidAuth):
        await pyload.login()


@pytest.mark.parametrize(
    ("exception"),
    [
        asyncio.TimeoutError,
        aiohttp.ClientError,
    ],
)
async def test_login_request_exceptions(
    pyload: PyLoadAPI,
    mocked_aiohttp: aioresponses,
    exception: Exception,
) -> None:
    """Test login."""
    mocked_aiohttp.post(f"{TEST_API_URL}api/login", exception=exception)

    with pytest.raises(expected_exception=CannotConnect):
        await pyload.login()


async def test_login_parse_exceptions(
    pyload: PyLoadAPI, mocked_aiohttp: aioresponses
) -> None:
    """Test login."""
    mocked_aiohttp.post(
        f"{TEST_API_URL}api/login",
        status=200,
        body="not json",
        content_type="application/json",
    )

    with pytest.raises(expected_exception=ParserError):
        await pyload.login()

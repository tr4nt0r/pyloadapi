"""Fixtures for PyLoadAPI Tests."""

from collections.abc import AsyncGenerator, Generator
from typing import Any
from unittest.mock import MagicMock, patch

import aiohttp
from aioresponses import aioresponses
from dotenv import load_dotenv
import pytest

from pyloadapi import PyLoadAPI, StatusServerResponse

load_dotenv()


TEST_API_URL = "https://example.com:8000/"
TEST_USERNAME = "test-username"
TEST_PASSWORD = "test-password"
TEST_LOGIN_RESPONSE = {
    "_permanent": True,
    "authenticated": True,
    "id": 2,
    "name": "test-username",
    "role": 0,
    "perms": 0,
    "template": "default",
    "_flashes": [["message", "Logged in successfully"]],
}

TEST_STATUS_RESPONSE: StatusServerResponse = {
    "pause": False,
    "active": 10,
    "queue": 5,
    "total": 15,
    "speed": 9999999.0,
    "download": True,
    "reconnect": False,
    "captcha": False,
}
TEST_STATUS_RESPONSE_NO_CAPTCHA: StatusServerResponse = {
    "pause": False,
    "active": 10,
    "queue": 5,
    "total": 15,
    "speed": 9999999.0,
    "download": True,
    "reconnect": False,
}


@pytest.fixture(name="session")
async def aiohttp_client_session() -> AsyncGenerator[aiohttp.ClientSession, Any]:
    """Create a client session."""
    async with aiohttp.ClientSession() as session:
        yield session


@pytest.fixture(name="pyload")
async def pyloadapi_client(session: aiohttp.ClientSession) -> PyLoadAPI:
    """Create pyLoad instance."""
    pyload = PyLoadAPI(
        session,
        TEST_API_URL,
        TEST_USERNAME,
        TEST_PASSWORD,
    )
    return pyload


@pytest.fixture(name="mocked_aiohttp")
def aioclient_mock() -> Generator[aioresponses, Any, None]:
    """Mock Aiohttp client requests."""
    with aioresponses() as m:
        yield m


@pytest.fixture
def mock_pyloadapi() -> Generator[MagicMock, None, None]:
    """Mock pyloadapi."""

    with patch("pyloadapi.cli.PyLoadAPI", autospec=True) as mock_client:
        client = mock_client.return_value
        client.get_status.return_value = TEST_STATUS_RESPONSE
        client.free_space.return_value = 107374182400
        yield client

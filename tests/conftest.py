"""Fixtures for PyLoadAPI Tests."""

from typing import Any, AsyncGenerator, Generator

import aiohttp
from aioresponses import aioresponses
from dotenv import load_dotenv
import pytest

from pyloadapi.api import PyLoadAPI

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


@pytest.fixture(name="session")
async def aiohttp_client_session() -> AsyncGenerator[aiohttp.ClientSession, Any]:
    """Create  a client session."""
    async with aiohttp.ClientSession() as session:
        yield session


@pytest.fixture(name="pyload")
async def mocked_pyloadapi_client(session: aiohttp.ClientSession) -> PyLoadAPI:
    """Create Bring instance."""
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

"""Fixtures for PyLoadAPI Tests."""

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from pyloadapi import PyLoadAPI, StatusServerResponse

TEST_API_URL = "https://example.com:8000/"
TEST_USERNAME = "test-username"
TEST_PASSWORD = "test-password"

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

BYTE_DATA = b"BYTE_DATA"


@pytest.fixture(name="session")
async def aiohttp_client_session() -> Generator[AsyncMock]:
    """Create a client session."""
    mock_session = AsyncMock(spec=aiohttp.ClientSession)
    mock_response = AsyncMock(spec=aiohttp.ClientResponse, status=200)

    mock_session.request.return_value.__aenter__.return_value = mock_response
    mock_session.get.return_value.__aenter__.return_value = mock_response
    mock_session.post.return_value.__aenter__.return_value = mock_response
    return mock_session


@pytest.fixture(name="pyload")
async def pyloadapi_client(session: aiohttp.ClientSession) -> PyLoadAPI:
    """Create pyLoad instance."""
    return PyLoadAPI(
        session,
        TEST_API_URL,
        TEST_USERNAME,
        TEST_PASSWORD,
    )


# @pytest.fixture(name="mocked_aiohttp")
# def aioclient_mock() -> Generator[aioresponses, Any, None]:
#     """Mock Aiohttp client requests."""
#     with aioresponses() as m:
#         yield m


@pytest.fixture
def mock_pyloadapi() -> Generator[MagicMock, None, None]:
    """Mock pyloadapi."""

    with patch("pyloadapi.cli.PyLoadAPI", autospec=True) as mock_client:
        client = mock_client.return_value
        client.get_status.return_value = TEST_STATUS_RESPONSE
        client.free_space.return_value = 107374182400
        yield client

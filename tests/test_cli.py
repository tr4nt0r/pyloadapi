"""Tests for pyloadapi CLI."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner
import pytest

from pyloadapi import CannotConnect, InvalidAuth, ParserError
from pyloadapi.cli import cli

from .conftest import TEST_API_URL, TEST_PASSWORD, TEST_USERNAME


@pytest.mark.usefixtures("mock_pyloadapi")
def test_status() -> None:
    """Test status."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            args=f"--username {TEST_USERNAME} --password {TEST_PASSWORD} --api-url {TEST_API_URL} status",
        )
        assert result.exit_code == 0
        assert result.output == (
            "Status:\n"
            "  - Active Downloads: 10\n"
            "  - Items in Queue: 5\n"
            "  - Finished Downloads: 15\n"
            "  - Download Speed: 80.0 Mbit/s\n"
            "  - Free space: 100.0 GiB\n"
            "  - Reconnect: Disabled\n"
            "  - Queue : Running\n\n"
        )


@pytest.mark.usefixtures("mock_pyloadapi")
def test_missing_credentials(tmp_path: Path) -> None:
    """Test status."""
    p = tmp_path / ".pyload_config.json"
    with patch("pyloadapi.cli.CONFIG_FILE_PATH", p) as mock_path:
        assert p == mock_path
        runner = CliRunner()

        result = runner.invoke(
            cli,
            args="status",
        )
        assert result.exit_code == 1
        assert (
            result.output
            == "Error: URL, username, and password must be provided either via command line or config file.\n"
        )


@pytest.mark.parametrize(
    ("command", "msg"),
    (
        ("queue", "Resumed download queue.\n"),
        ("stop-all", "Aborted all running downloads.\n"),
        ("retry", "Retrying failed downloads.\n"),
        ("delete-finished", "Deleted finished files and packages.\n"),
        ("restart", "Restarting pyLoad...\n"),
        ("toggle-reconnect", "Disabled auto-reconnect\n"),
    ),
)
@pytest.mark.usefixtures("mock_pyloadapi")
def test_all_commands(
    msg: str,
    command: str,
) -> None:
    """Test status."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            args=f"--username {TEST_USERNAME} --password {TEST_PASSWORD} --api-url {TEST_API_URL} {command}",
        )
        assert result.exit_code == 0
        assert result.output == msg


@pytest.mark.parametrize(
    ("command", "pause", "msg"),
    [
        ("queue -p", True, "Paused download queue.\n"),
        ("queue --pause", True, "Paused download queue.\n"),
        ("queue -r", False, "Resumed download queue.\n"),
        ("queue --resume", False, "Resumed download queue.\n"),
    ],
)
def test_queue_with_options(
    mock_pyloadapi: MagicMock, msg: str, command: str, pause: bool
) -> None:
    """Test status."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        mock_pyloadapi.get_status.return_value = {"pause": pause}
        result = runner.invoke(
            cli,
            args=f"--username {TEST_USERNAME} --password {TEST_PASSWORD} --api-url {TEST_API_URL} {command}",
        )
        assert result.exit_code == 0
        assert result.output == msg


@pytest.mark.parametrize(
    ("exception", "msg"),
    [
        (CannotConnect, "Error: Unable to connect to pyLoad\n"),
        (InvalidAuth, "Error: Authentication failed, verify username and password\n"),
        (ParserError, "Error: Unable to parse response from pyLoad\n"),
    ],
)
@pytest.mark.parametrize(
    ("command"),
    (
        "status",
        "queue",
        "queue -p",
        "queue -r",
        "stop-all",
        "retry",
        "delete-finished",
        "restart",
        "toggle-reconnect",
    ),
)
def test_exceptions(
    mock_pyloadapi: MagicMock,
    exception: Exception,
    msg: str,
    command: str,
) -> None:
    """Test status."""

    runner = CliRunner()
    with runner.isolated_filesystem():
        mock_pyloadapi.get_status.side_effect = exception
        mock_pyloadapi.unpause.side_effect = exception
        mock_pyloadapi.pause.side_effect = exception
        mock_pyloadapi.toggle_pause.side_effect = exception
        mock_pyloadapi.stop_all_downloads.side_effect = exception
        mock_pyloadapi.restart_failed.side_effect = exception
        mock_pyloadapi.toggle_reconnect.side_effect = exception
        mock_pyloadapi.delete_finished.side_effect = exception
        mock_pyloadapi.restart.side_effect = exception
        mock_pyloadapi.free_space.side_effect = exception

        result = runner.invoke(
            cli,
            args=f"--username {TEST_USERNAME} --password {TEST_PASSWORD} --api-url {TEST_API_URL} {command}",
        )
        assert result.exit_code == 1
        assert result.output == msg

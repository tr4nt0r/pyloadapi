"""Tests for pyloadapi CLI."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner
import pytest

from pyloadapi import CannotConnect, InvalidAuth, ParserError
from pyloadapi.cli import cli

from .conftest import BYTE_DATA, TEST_API_URL, TEST_PASSWORD, TEST_USERNAME


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
            "  - Active downloads: 10\n"
            "  - Items in queue: 5\n"
            "  - Total downloads: 15\n"
            "  - Download speed: 80.0 Mbit/s\n"
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
    tmp_path: Path,
) -> None:
    """Test status."""

    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
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


@pytest.mark.usefixtures("mock_pyloadapi")
def test_upload_container(
    tmp_path: Path,
) -> None:
    """Test status."""

    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path) as tmp:
        dlc = Path(tmp, "container.dlc")
        with open(dlc, "wb") as f:
            f.write(BYTE_DATA)

        result = runner.invoke(
            cli,
            args=f"--username {TEST_USERNAME} --password {TEST_PASSWORD} --api-url {TEST_API_URL} upload-container {dlc.as_posix()}",
        )
        assert result.exit_code == 0


@pytest.mark.parametrize(
    ("exception", "msg"),
    [
        (CannotConnect, "Error: Unable to connect to pyLoad\n"),
        (InvalidAuth, "Error: Authentication failed, verify username and password\n"),
        (ParserError, "Error: Unable to parse response from pyLoad\n"),
    ],
)
def test_upload_container_exceptions(
    mock_pyloadapi: MagicMock,
    exception: Exception,
    msg: str,
    tmp_path: Path,
) -> None:
    """Test status."""

    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path) as tmp:
        dlc = Path(tmp, "container.dlc")
        with open(dlc, "wb") as f:
            f.write(BYTE_DATA)

        mock_pyloadapi.upload_container.side_effect = exception

        result = runner.invoke(
            cli,
            args=f"--username {TEST_USERNAME} --password {TEST_PASSWORD} --api-url {TEST_API_URL} upload-container {dlc.as_posix()}",
        )
        assert result.exit_code == 1
        assert result.output == msg


@pytest.mark.usefixtures("mock_pyloadapi")
def test_add_package(tmp_path: Path) -> None:
    """Test add-package."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(
            cli,
            args=f"--username {TEST_USERNAME} --password {TEST_PASSWORD} --api-url {TEST_API_URL} add-package Test-Package",
            input=("http://example.com/file1.zip\n" "http://example.com/file2.iso\n\n"),
        )
        assert result.exit_code == 0
        assert result.output == (
            "Please enter a link: http://example.com/file1.zip\n"
            "Please enter a link: http://example.com/file2.iso\n"
            "Please enter a link: \n"
        )


@pytest.mark.usefixtures("mock_pyloadapi")
def test_add_package_no_links(tmp_path: Path) -> None:
    """Test add-package aborts if no links provided."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(
            cli,
            args=f"--username {TEST_USERNAME} --password {TEST_PASSWORD} --api-url {TEST_API_URL} add-package Test-Package",
            input="\n",
        )
        assert result.exit_code == 1
        assert result.output == "Please enter a link: \nError: No links entered\n"


@pytest.mark.parametrize(
    ("exception", "msg"),
    [
        (CannotConnect, "Error: Unable to connect to pyLoad\n"),
        (InvalidAuth, "Error: Authentication failed, verify username and password\n"),
        (ParserError, "Error: Unable to parse response from pyLoad\n"),
    ],
)
def test_add_package_exceptions(
    mock_pyloadapi: MagicMock,
    tmp_path: Path,
    exception: Exception,
    msg: str,
) -> None:
    """Test add-package aborts if no links provided."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        mock_pyloadapi.add_package.side_effect = exception
        result = runner.invoke(
            cli,
            args=f"--username {TEST_USERNAME} --password {TEST_PASSWORD} --api-url {TEST_API_URL} add-package Test-Package",
            input=("http://example.com/file1.zip\n" "http://example.com/file2.iso\n\n"),
        )
        assert result.exit_code == 1
        assert msg in result.output


@pytest.mark.usefixtures("mock_pyloadapi")
def test_get_help() -> None:
    """Test that invoking cli without commands and params returns help."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
        )
        assert result.exit_code == 0
        assert "Usage: cli [OPTIONS] COMMAND [ARGS]..." in result.output

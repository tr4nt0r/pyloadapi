"""Commandline interface for pyloadapi."""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

import aiohttp
import click

from pyloadapi import CannotConnect, InvalidAuth, ParserError, PyLoadAPI
from pyloadapi.types import Destination

_LOGGER = logging.getLogger(__name__)

CONFIG_FILE_PATH = Path("~/.config/pyloadapi/.pyload_config.json").expanduser()


def load_config() -> Any:
    """Load the configuration from a JSON file."""
    if not CONFIG_FILE_PATH.is_file():
        return {}

    with CONFIG_FILE_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def save_config(config: dict[str, Any]) -> None:
    """Save the configuration to a JSON file."""
    CONFIG_FILE_PATH.parent.mkdir(exist_ok=True, parents=True)
    with CONFIG_FILE_PATH.open("w", encoding="utf-8") as file:
        json.dump(config, file, indent=4)


async def init_api(
    session: aiohttp.ClientSession, api_url: str, username: str, password: str
) -> PyLoadAPI:
    """Initialize the PyLoadAPI."""

    api = PyLoadAPI(
        session=session, api_url=api_url, username=username, password=password
    )
    await api.login()

    return api


@click.group(invoke_without_command=True)
@click.option("--api-url", help="Base URL of pyLoad")
@click.option("--username", help="Username for pyLoad")
@click.option("--password", help="Password for pyLoad")
@click.pass_context
def cli(
    ctx: click.Context,
    api_url: str | None = None,
    username: str | None = None,
    password: str | None = None,
) -> None:
    """CLI for interacting with pyLoad."""

    if not any([api_url, username, password, ctx.invoked_subcommand]):
        click.echo(ctx.get_help())

    config = load_config()

    if api_url:
        config["api_url"] = api_url

    if username:
        config["username"] = username

    if password:
        config["password"] = password

    save_config(config)

    ctx.ensure_object(dict)
    ctx.obj["api_url"] = config.get("api_url")
    ctx.obj["username"] = config.get("username")
    ctx.obj["password"] = config.get("password")

    if not all([ctx.obj["api_url"], ctx.obj["username"], ctx.obj["password"]]):
        raise click.ClickException(
            "URL, username, and password must be provided either via command line or config file."
        )


@cli.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Display the general status information of pyLoad."""

    async def _status() -> None:
        try:
            async with aiohttp.ClientSession() as session:
                api = await init_api(
                    session,
                    ctx.obj["api_url"],
                    ctx.obj["username"],
                    ctx.obj["password"],
                )
                stat = await api.get_status()
                free_space = await api.free_space()
            click.echo(
                f"Status:\n"
                f"  - Active downloads: {stat['active']}\n"
                f"  - Items in queue: {stat['queue']}\n"
                f"  - Total downloads: {stat['total']}\n"
                f"  - Download speed: {round((stat['speed'] * 8) / 1000000, 2) } Mbit/s\n"
                f"  - Free space: {round(free_space / (1024 ** 3), 2)} GiB\n"
                f"  - Reconnect: {'Enabled' if stat['reconnect'] else 'Disabled'}\n"
                f"  - Queue : {'Paused' if stat['pause'] else 'Running'}\n"
            )
        except CannotConnect as e:
            raise click.ClickException("Unable to connect to pyLoad") from e
        except InvalidAuth as e:
            raise click.ClickException(
                "Authentication failed, verify username and password"
            ) from e
        except ParserError as e:
            raise click.ClickException("Unable to parse response from pyLoad") from e

    asyncio.run(_status())


@cli.command()
@click.option("-p", "--pause", is_flag=True, help="Pause pyLoads download queue")
@click.option("-r", "--resume", is_flag=True, help="Resume pyLoads download queue")
@click.pass_context
def queue(ctx: click.Context, pause: bool, resume: bool) -> None:
    """Toggle, pause or resume the download queue in pyLoad."""

    async def _queue(pause: bool, resume: bool) -> None:
        try:
            async with aiohttp.ClientSession() as session:
                api = await init_api(
                    session,
                    ctx.obj["api_url"],
                    ctx.obj["username"],
                    ctx.obj["password"],
                )
                if pause:
                    await api.pause()
                elif resume:
                    await api.unpause()
                else:
                    await api.toggle_pause()

                s = await api.get_status()
                click.echo(
                    f"{"Paused" if s.get("pause") else "Resumed"} download queue."
                )

        except CannotConnect as e:
            raise click.ClickException("Unable to connect to pyLoad") from e
        except InvalidAuth as e:
            raise click.ClickException(
                "Authentication failed, verify username and password"
            ) from e
        except ParserError as e:
            raise click.ClickException("Unable to parse response from pyLoad") from e

    asyncio.run(_queue(pause, resume))


@cli.command()
@click.pass_context
def stop_all(ctx: click.Context) -> None:
    """Abort all currently running downloads in pyLoad."""

    async def _stop_all() -> None:
        try:
            async with aiohttp.ClientSession() as session:
                api = await init_api(
                    session,
                    ctx.obj["api_url"],
                    ctx.obj["username"],
                    ctx.obj["password"],
                )

                await api.stop_all_downloads()
                click.echo("Aborted all running downloads.")
        except CannotConnect as e:
            raise click.ClickException("Unable to connect to pyLoad") from e
        except InvalidAuth as e:
            raise click.ClickException(
                "Authentication failed, verify username and password"
            ) from e
        except ParserError as e:
            raise click.ClickException("Unable to parse response from pyLoad") from e

    asyncio.run(_stop_all())


@cli.command()
@click.pass_context
def retry(ctx: click.Context) -> None:
    """Retry all failed downloads in pyLoad."""

    async def _retry() -> None:
        try:
            async with aiohttp.ClientSession() as session:
                api = await init_api(
                    session,
                    ctx.obj["api_url"],
                    ctx.obj["username"],
                    ctx.obj["password"],
                )

                await api.restart_failed()
                click.echo("Retrying failed downloads.")
        except CannotConnect as e:
            raise click.ClickException("Unable to connect to pyLoad") from e
        except InvalidAuth as e:
            raise click.ClickException(
                "Authentication failed, verify username and password"
            ) from e
        except ParserError as e:
            raise click.ClickException("Unable to parse response from pyLoad") from e

    asyncio.run(_retry())


@cli.command()
@click.pass_context
def delete_finished(ctx: click.Context) -> None:
    """Delete all finished files and packages from pyLoad."""

    async def _delete_finished() -> None:
        try:
            async with aiohttp.ClientSession() as session:
                api = await init_api(
                    session,
                    ctx.obj["api_url"],
                    ctx.obj["username"],
                    ctx.obj["password"],
                )

                await api.delete_finished()
                click.echo("Deleted finished files and packages.")
        except CannotConnect as e:
            raise click.ClickException("Unable to connect to pyLoad") from e
        except InvalidAuth as e:
            raise click.ClickException(
                "Authentication failed, verify username and password"
            ) from e
        except ParserError as e:
            raise click.ClickException("Unable to parse response from pyLoad") from e

    asyncio.run(_delete_finished())


@cli.command()
@click.pass_context
def restart(ctx: click.Context) -> None:
    """Restart the pyLoad service."""

    async def _restart() -> None:
        try:
            async with aiohttp.ClientSession() as session:
                api = await init_api(
                    session,
                    ctx.obj["api_url"],
                    ctx.obj["username"],
                    ctx.obj["password"],
                )

                await api.restart()
                click.echo("Restarting pyLoad...")
        except CannotConnect as e:
            raise click.ClickException("Unable to connect to pyLoad") from e
        except InvalidAuth as e:
            raise click.ClickException(
                "Authentication failed, verify username and password"
            ) from e
        except ParserError as e:
            raise click.ClickException("Unable to parse response from pyLoad") from e

    asyncio.run(_restart())


@cli.command()
@click.pass_context
def toggle_reconnect(ctx: click.Context) -> None:
    """Toggle the state of the auto-reconnect function of pyLoad."""

    async def _toggle_reconnect() -> None:
        try:
            async with aiohttp.ClientSession() as session:
                api = await init_api(
                    session,
                    ctx.obj["api_url"],
                    ctx.obj["username"],
                    ctx.obj["password"],
                )

                await api.toggle_reconnect()
                s = await api.get_status()
                click.echo(
                    f"{"Enabled" if s.get("reconnect") else "Disabled"} auto-reconnect"
                )
        except CannotConnect as e:
            raise click.ClickException("Unable to connect to pyLoad") from e
        except InvalidAuth as e:
            raise click.ClickException(
                "Authentication failed, verify username and password"
            ) from e
        except ParserError as e:
            raise click.ClickException("Unable to parse response from pyLoad") from e

    asyncio.run(_toggle_reconnect())


@cli.command()
@click.pass_context
@click.argument(
    "container",
    type=click.Path(
        exists=True,
        readable=True,
        path_type=Path,
    ),
)
def upload_container(ctx: click.Context, container: Path) -> None:
    """Upload a container file to pyLoad."""

    with open(container, "rb") as f:
        binary_data = f.read()

    async def _upload_container() -> None:
        try:
            async with aiohttp.ClientSession() as session:
                api = await init_api(
                    session,
                    ctx.obj["api_url"],
                    ctx.obj["username"],
                    ctx.obj["password"],
                )

                await api.upload_container(
                    filename=click.format_filename(container, shorten=True),
                    binary_data=binary_data,
                )

        except CannotConnect as e:
            raise click.ClickException("Unable to connect to pyLoad") from e
        except InvalidAuth as e:
            raise click.ClickException(
                "Authentication failed, verify username and password"
            ) from e
        except ParserError as e:
            raise click.ClickException("Unable to parse response from pyLoad") from e

    asyncio.run(_upload_container())


@cli.command()
@click.pass_context
@click.argument("package_name")
@click.option(
    "--queue/--collector",
    default=True,
    help="Add package to queue or collector. Defaults to queue",
)
def add_package(ctx: click.Context, package_name: str, queue: bool) -> None:
    """Add a package to pyLoad."""

    links = []

    while value := click.prompt(
        "Please enter a link", type=str, default="", show_default=False
    ):
        links.append(value)

    if not links:
        raise click.ClickException("No links entered")

    async def _add_package() -> None:
        try:
            async with aiohttp.ClientSession() as session:
                api = await init_api(
                    session,
                    ctx.obj["api_url"],
                    ctx.obj["username"],
                    ctx.obj["password"],
                )

                await api.add_package(
                    name=package_name,
                    links=links,
                    destination=Destination.QUEUE if queue else Destination.COLLECTOR,
                )

        except CannotConnect as e:
            raise click.ClickException("Unable to connect to pyLoad") from e
        except InvalidAuth as e:
            raise click.ClickException(
                "Authentication failed, verify username and password"
            ) from e
        except ParserError as e:
            raise click.ClickException("Unable to parse response from pyLoad") from e

    asyncio.run(_add_package())

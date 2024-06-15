# Usage


### Importing the Module

First, import the necessary modules and classes:

```python
from aiohttp import ClientSession
from pyloadapi import PyLoadAPI, CannotConnect, InvalidAuth, ParserError
import asyncio
import logging
```

### Setting Logging Configuration

Configure logging to debug mode to capture detailed information:

```python
logging.basicConfig(level=logging.DEBUG)
```

### Creating a PyLoadAPI Instance

To start using the `PyLoadAPI`, create an instance by providing the necessary parameters:

```python
async def main():
    api_url = 'http://your-pyload-server/'
    username = 'your_username'
    password = 'your_password'
    async with aiohttp.ClientSession() as session:
        pyload = PyLoadAPI(session, api_url, username, password)
        try:
            await pyload.login()
            print("Login successful!")
        except (CannotConnect, InvalidAuth, ParserError) as e:
            print(f"Failed to login: {e}")

asyncio.run(main())
```

### Performing Operations

Once logged in, you can perform various operations provided by the `PyLoadAPI` class:

#### Get Status

```python
try:
    status = await pyload.get_status()
    print(f"pyLoad Status: {status}")
except (CannotConnect, InvalidAuth, ParserError) as e:
    print(f"Failed to get status: {e}")
```

#### Pause Download Queue

```python
try:
    await pyload.pause()
    print("Download queue paused.")
except (CannotConnect, InvalidAuth, ParserError) as e:
    print(f"Failed to pause download queue: {e}")
```

#### Unpause Download Queue

```python
try:
    await pyload.unpause()
    print("Download queue unpaused.")
except (CannotConnect, InvalidAuth, ParserError) as e:
    print(f"Failed to unpause download queue: {e}")
```

#### Toggle Pause Download Queue

```python
try:
    await pyload.toggle_pause()
    print("Download queue pause toggled.")
except (CannotConnect, InvalidAuth, ParserError) as e:
    print(f"Failed to toggle pause download queue: {e}")
```

#### Stop All Downloads

```python
try:
    await pyload.stop_all_downloads()
    print("All downloads stopped.")
except (CannotConnect, InvalidAuth, ParserError) as e:
    print(f"Failed to stop all downloads: {e}")
```

#### Restart Failed Downloads

```python
try:
    await pyload.restart_failed()
    print("Failed downloads restarted.")
except (CannotConnect, InvalidAuth, ParserError) as e:
    print(f"Failed to restart failed downloads: {e}")
```

#### Toggle Reconnect

```python
try:
    await pyload.toggle_reconnect()
    print("Reconnect toggled.")
except (CannotConnect, InvalidAuth, ParserError) as e:
    print(f"Failed to toggle reconnect: {e}")
```

#### Delete Finished Files

```python
try:
    await pyload.delete_finished()
    print("Finished files deleted.")
except (CannotConnect, InvalidAuth, ParserError) as e:
    print(f"Failed to delete finished files: {e}")
```

#### Restart PyLoad Core

```python
try:
    await pyload.restart()
    print("PyLoad core restarted.")
except (CannotConnect, InvalidAuth, ParserError) as e:
    print(f"Failed to restart PyLoad core: {e}")
```

#### Get PyLoad Version

```python
try:
    version = await pyload.version()
    print(f"PyLoad version: {version}")
except (CannotConnect, InvalidAuth, ParserError) as e:
    print(f"Failed to get PyLoad version: {e}")
```

#### Get Free Space

```python
try:
    free_space = await pyload.free_space()
    print(f"Free space available: {free_space} bytes")
except (CannotConnect, InvalidAuth, ParserError) as e:
    print(f"Failed to get free space: {e}")
```

### Exception Handling

All methods in PyLoadAPI may raise the following exceptions:

- **CannotConnect**: Raised if there is an issue with the request to the pyLoad server.
- **InvalidAuth**: Raised if the authentication credentials are invalid or the authentication cookie is invalid or expired.
- **ParserError**: Raised if there is an issue parsing the response from the server.

```python
try:
    await pyload.some_method()
except (CannotConnect, InvalidAuth, ParserError) as e:
    print(f"Operation failed: {e}")
```

### Conclusion

This documentation provides an overview of how to use the PyLoadAPI class to interact with a pyLoad server. By following the examples and guidelines, you can effectively manage downloads and retrieve information from pyLoad using Python.

# PyLoadAPI

 *Simple wrapper for pyLoad's API.*

This module provides a simplified interface (PyLoadAPI class) to interact with
pyLoad's API using aiohttp for asynchronous HTTP requests. It handles login
authentication and provides methods to perform various operations such as
pausing downloads, restarting pyLoad, retrieving status information, and more.

[![build](https://github.com/tr4nt0r/pyloadapi/workflows/Build/badge.svg)](https://github.com/tr4nt0r/pyloadapi/actions)
[![codecov](https://codecov.io/gh/tr4nt0r/pyloadapi/graph/badge.svg?token=SZDBSZGZE7)](https://codecov.io/gh/tr4nt0r/pyloadapi)
[![PyPI version](https://badge.fury.io/py/PyLoadAPI.svg)](https://badge.fury.io/py/PyLoadAPI)
[!["Buy Me A Coffee"](https://img.shields.io/badge/-buy_me_a%C2%A0coffee-gray?logo=buy-me-a-coffee)](https://www.buymeacoffee.com/tr4nt0r)
[![GitHub Sponsor](https://img.shields.io/badge/GitHub-Sponsor-blue?logo=github)](https://github.com/sponsors/tr4nt0r)

---

## 📖 Documentation

- **Full Documentation**: [https://tr4nt0r.github.io/pyloadapi](https://tr4nt0r.github.io/pyloadapi)
- **Source Code**: [https://github.com/tr4nt0r/pyloadapi](https://github.com/tr4nt0r/pyloadapi)

---

## 📦 Installation

You can install PyLoadAPI via pip:

```sh
pip install PyLoadAPI
```

---

## 🚀 Usage

### Basic Example

```python
import asyncio
from pyloadapi import PyLoadAPI

async def main():
    async with PyLoadAPI("http://localhost:8000", "username", "password") as api:
        status = await api.status()
        print(status)

asyncio.run(main())
```

### More Examples

<details>

<summary>Pause Downloads</summary>

```python
await api.pause(True)  # Pause all downloads
```

</details>

<details>

<summary>Resume Downloads</summary>

```python
await api.pause(False)  # Resume all downloads
```

</details>

<details>

<summary>Restart pyLoad</summary>

```python
await api.restart()
```

</details>

For more advanced usage, refer to the [documentation](https://tr4nt0r.github.io/pyloadapi).

---

## 🛠 Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch.
3. Make your changes and commit them.
4. Submit a pull request.

Make sure to follow the [contributing guidelines](CONTRIBUTING.md).

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ❤️ Support

If you find this project useful, consider [buying me a coffee ☕](https://www.buymeacoffee.com/tr4nt0r) or [sponsoring me on GitHub](https://github.com/sponsors/tr4nt0r)!

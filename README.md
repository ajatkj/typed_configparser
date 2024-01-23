<p align="center">
  <img src="./assets/logo.png" alt="Description of the image">
</p>
<p align="center">
<a href="https://github.com/ajatkj/typed_configparser/actions?query=workflow%3ATest+event%3Apush+branch%3Amain" target="_blank">
    <img src="https://img.shields.io/github/actions/workflow/status/ajatkj/typed_configparser/tests.yml?branch=main&event=push&style=flat-square&label=test" alt="Test">
</a>
  <a href="https://pypi.org/project/fastapi" target="_blank">
      <img src="https://img.shields.io/pypi/v/typed-configparser?color=%2334D058&label=pypi%20package&style=flat-square" alt="Package version">
  </a>
  <a href="https://pypi.org/project/fastapi" target="_blank">
      <img src="https://img.shields.io/pypi/pyversions/typed-config-parser?color=%2334D058&style=flat-square" alt="Supported Python versions">
  </a>
</p>

# typed-configparser

typed-configparser is an extension of the standard configparser module with support for typed configurations using dataclasses.
It leverages Python's type hints and dataclasses to provide a convenient way of parsing and validating configuration files.

## Features

✓ Fully typed.<br />
✓ Use dataclasses to parse the configuration file.<br />
✓ Support for almost all python built-in data types - `int`, `float`, `str`, `list`, `tuple`, `dict` and complex data types using `Union` and `Optional`.<br />
✓ Built on top of `configparser`, hence retains all functionalities of `configparser`.<br />
✓ Support for optional values (optional values are automatically set to `None` if not provided).<br />
✓ Smarter defaults (see below).

## Installation

You can install `typed_configparser` using `pip`:

```sh
pip install typed_configparser
```

## Usage

`basic_example.py`

```py3
import dataclasses
from typed_configparser import ConfigParser

@dataclasses.dataclass
class AppConfig:
    host: str
    port: int
    debug: bool

# Create an instance of Typed ConfigParser
config_parser = ConfigParser()
config_parser.read("conf.ini")

app_config = config_parser.parse_section(AppConfig, section_name='AppSection')

print(f"Host: {app_config.host}")
print(f"Port: {app_config.port}")
print(f"Debug Mode: {app_config.debug}")
```

`conf.ini`

```ini
[AppSection]
host = localhost
port = 8080
debug = True
```

`optional_example.py`

```py3
import typing
import dataclasses
from typed_configparser import ConfigParser

@dataclasses.dataclass
class AppConfig:
    host: str
    port: int
    debug: typing.Optional[bool]

config_parser = ConfigParser()
app_config = config_parser.parse_section(AppConfig, section_name='AppSection')

```

Check `example` directory for more examples.

## Defaults

- `configparser` includes sensible defaults options which allows you to declare a `[DEFAULT]` section in the config file for fallback values.
- `typed_configparser` goes a step further and allows you to set a final level of defaults at dataclass level.

# License

[MIT License](./LICENSE)

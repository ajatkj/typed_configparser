# TypedConfigparser

Typed ConfigParser is an extension of the standard configparser module with support for typed configurations using dataclasses. 
It leverages Python's type hints and dataclasses to provide a convenient way of parsing and validating configuration files.

## Features
- Fully typed.
- Use dataclasses to parse the configuration file.
- Support for almost all python built-in data types - `int`, `float`, `str`, `list`, `tuple`, `dict` and complex data types using `Union` and `Optional`.
- Built on top of `configparser`, hence retains all functionalities of `configparser`.
- Support for optional values (optional values are automatically set to `None` if not provided).
- Smarter defaults (see below).

## Installation
You can install Typed ConfigParser using pip:
```sh
pip install typed-configparser
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
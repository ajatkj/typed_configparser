<p align="center">
  <img src="https://raw.githubusercontent.com/ajatkj/typed_configparser/main/assets/logo.png" alt="Description of the image">
</p>
<p align="center">
<a href="https://github.com/ajatkj/typed_configparser/actions?query=workflow%3ATest+event%3Apush+branch%3Amain" target="_blank">
    <img src="https://img.shields.io/github/actions/workflow/status/ajatkj/typed_configparser/tests.yml?branch=main&event=push&style=flat-square&label=test&color=%2334D058" alt="Test">
</a>
  <a href="https://pypi.org/project/typed-configparser" target="_blank">
      <img src="https://img.shields.io/pypi/v/typed-configparser?color=%2334D058&label=pypi%20package&style=flat-square" alt="Package version">
  </a>
  <a href="https://pypi.org/project/typed-configparser" target="_blank">
      <img src="https://img.shields.io/pypi/pyversions/typed-configparser?color=%2334D058&style=flat-square" alt="Supported Python versions">
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
pip install typed-configparser
```

## Usage

`examples/basic.py`

```py3
# This is a complete example and should work as is

from typing import List
from typed_configparser import ConfigParser
from dataclasses import dataclass


@dataclass
class BASIC:
    option1: int
    option2: str
    option3: float
    option4: List[str]


config = """
[BASIC]
option1 = 10
option2 = value2
option3 = 5.2
option4 = [foo,bar]
"""

parser = ConfigParser()
parser.read_string(config)
section = parser.parse_section(using_dataclass=BASIC)

print(section)
```

```py3
BASIC(option1=10, option2=value2, option3=5.2, option4=['foo', 'bar'])
```

`examples/unions_and_optionals.py`

```py3
# This is a complete example and should work as is

from typing import List, Union, Optional, Dict, Tuple
from typed_configparser import ConfigParser
from dataclasses import dataclass, field


@dataclass
class DEFAULT_EXAMPLE:
    option1: int
    option2: Union[List[Tuple[str, str]], List[int]]
    option3: Dict[str, str] = field(default_factory=lambda: {"default_key": "default_value"})
    option4: Optional[float] = None


config = """
[DEFAULT]
option1 = 20
option2 = default_value2

[MY_SECTION_1]
option2 = [10,20]
option4 = 5.2

[MY_SECTION_2]
option2 = [(value2a, value2b), (value2c, value2b), (value2c, value2d)]
option3 = {key: value}
option4 = none
"""

parser = ConfigParser()
parser.read_string(config)
my_section_1 = parser.parse_section(using_dataclass=DEFAULT_EXAMPLE, section_name="MY_SECTION_1")
my_section_2 = parser.parse_section(using_dataclass=DEFAULT_EXAMPLE, section_name="MY_SECTION_2")

print(my_section_1)
print(my_section_2)
```

```py3
DEFAULT_EXAMPLE(option1=20, option2=[10, 20], option3={'default_key': 'default_value'}, option4=5.2)
DEFAULT_EXAMPLE(option1=20, option2=[('value2a', 'value2b'), ('value2c', 'value2b'), ('value2c', 'value2d')], option3={'key': 'value'}, option4=None)
```

Check `example` directory for more examples.

## Defaults

- `configparser` includes sensible defaults options which allows you to declare a `[DEFAULT]` section in the config file for fallback values.
- `typed_configparser` goes a step further and allows you to set a final (last) level of defaults at dataclass level.

# License

[MIT License](./LICENSE)

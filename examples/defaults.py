# This is a complete example and should work as is

from typing import List
from typed_configparser import ConfigParser
from dataclasses import dataclass, field


@dataclass
class DEFAULT_EXAMPLE:
    option1: int
    option2: str = "class_default2"
    option3: float = 0.0
    option4: List[str] = field(default_factory=lambda: ["hello", "world"])


config = """
[DEFAULT]
option1 = 20
option2 = default_value2

[MY_SECTION]
option2 = value2
option3 = 5.2
"""

parser = ConfigParser()
parser.read_string(config)
section = parser.parse_section(using_dataclass=DEFAULT_EXAMPLE, section_name="MY_SECTION")

print(section)

# Output:
#   DEFAULT_EXAMPLE(option1=20, option2=value2, option3=5.2, option4=['hello', 'world'])
#

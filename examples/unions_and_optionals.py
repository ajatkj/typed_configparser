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

# Output:
#   DEFAULT_EXAMPLE(option1=20, option2=10, option3={'default_key': 'default_value'}, option4=5.2)
#   DEFAULT_EXAMPLE(option1=20, option2=['value2a', 'value2b', 'value2c'], option3={'key': 'value'}, option4=None)
#

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
option4 = foo,bar
"""

parser = ConfigParser()
parser.read_string(config)
section = parser.parse_section(using_dataclass=BASIC)

print(section)

# Output:
#   BASIC(option1=10, option2=value2, option3=5.2, option4=['foo', 'bar'])
#

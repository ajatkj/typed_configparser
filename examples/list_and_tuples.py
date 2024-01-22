# This is a complete example and should work as is

from typing import List, Union, Tuple
from typed_configparser import ConfigParser
from dataclasses import dataclass


@dataclass
class SECTION:
    option1: List[int]
    option2: List[List[str]]
    option3: List[Union[int, str]]
    option4: Tuple[int, str]
    option5: List[Tuple[str, str]]


config = """
[SECTION]
option1 = [10,20]
option2 = [[foo, bar, baz, hello world]]
option3 = [10, foo, bar]
option4 = (10, foo)
option5 = [(foo, bar), (bar, baz), (baz, qux), (qux, foo)]
"""

parser = ConfigParser()
parser.read_string(config)
my_section_1 = parser.parse_section(using_dataclass=SECTION)

print(my_section_1)

# Output:
#   SECTION(option1=[10, 20], option2=[['foo', 'bar', 'baz', 'hello world']], option3=[10, 'foo', 'bar'], option4=(10, 'foo'), option5=[('foo', 'bar'), ('bar', 'baz'), ('baz', 'qux'), ('qux', 'foo')])
#

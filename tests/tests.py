import dataclasses
from pathlib import Path, PosixPath
import typing
import unittest

from typed_configparser.exceptions import ParseError
from typed_configparser.parser import ConfigParser

_SECTION_ = "test_section"


class TestConfigParser(unittest.TestCase):
    def setUp(self) -> None:
        self.config_parser = ConfigParser()

    def test_parse_section_check_datatypes(self) -> None:
        @dataclasses.dataclass
        class TestDataclass:
            option1: int
            option2: str
            option3: float
            option4: bool
            option5: None

        self.config_parser.add_section(_SECTION_)
        self.config_parser.set(_SECTION_, "option1", "42")
        self.config_parser.set(_SECTION_, "option2", "value")
        self.config_parser.set(_SECTION_, "option3", "10.5")
        self.config_parser.set(_SECTION_, "option4", "True")
        self.config_parser.set(_SECTION_, "option5", "None")

        result = self.config_parser.parse_section(TestDataclass, _SECTION_)

        self.assertIsInstance(result, TestDataclass)
        self.assertEqual(result.option1, 42)
        self.assertIsInstance(result.option1, int)
        self.assertEqual(result.option2, "value")
        self.assertIsInstance(result.option2, str)
        self.assertEqual(result.option3, 10.5)
        self.assertIsInstance(result.option3, float)
        self.assertEqual(result.option4, True)
        self.assertIsInstance(result.option4, bool)
        self.assertEqual(result.option5, None)
        self.assertIsInstance(result.option5, type(None))

    def test_parse_section_invalid_dataclass(self) -> None:
        class NotADataclass:
            pass

        self.config_parser.add_section(_SECTION_)

        with self.assertRaisesRegex(ParseError, f"ParseError in section '{_SECTION_}'"):
            self.config_parser.parse_section(NotADataclass, _SECTION_)  # type: ignore

    def test_parse_section_dataclass_init_false(self) -> None:
        @dataclasses.dataclass(init=False)
        class TestDataclass:
            option1: int

        self.config_parser.add_section(_SECTION_)

        with self.assertRaisesRegex(TypeError, "init flag must be True for dataclass 'TestDataclass'"):
            self.config_parser.parse_section(TestDataclass, _SECTION_)

    def test_parse_section_extra_fields_allow(self) -> None:
        @dataclasses.dataclass
        class TestDataclass:
            option1: int
            option2: str

        self.config_parser.add_section(_SECTION_)
        self.config_parser.set(_SECTION_, "option1", "42")
        self.config_parser.set(_SECTION_, "option2", "value")
        self.config_parser.set(_SECTION_, "extra_option", "extra_value")

        result = self.config_parser.parse_section(TestDataclass, _SECTION_, extra="allow")

        self.assertIsInstance(result, TestDataclass)
        self.assertEqual(result.option1, 42)
        self.assertEqual(result.option2, "value")
        self.assertEqual(getattr(result, "extra_option", None), "extra_value")

    def test_parse_section_extra_fields_error(self) -> None:
        @dataclasses.dataclass
        class TestDataclass:
            option1: int
            option2: str

        self.config_parser.add_section(_SECTION_)
        self.config_parser.set(_SECTION_, "option1", "42")
        self.config_parser.set(_SECTION_, "option2", "value")
        self.config_parser.set(_SECTION_, "extra_option", "extra_value")

        with self.assertRaises(ParseError):
            self.config_parser.parse_section(TestDataclass, _SECTION_, extra="error")

    def test_parse_section_extra_fields_ignore(self) -> None:
        @dataclasses.dataclass
        class TestDataclass:
            option1: int
            option2: str

        self.config_parser.add_section(_SECTION_)
        self.config_parser.set(_SECTION_, "option1", "42")
        self.config_parser.set(_SECTION_, "option2", "value")
        self.config_parser.set(_SECTION_, "extra_option", "extra_value")

        result = self.config_parser.parse_section(TestDataclass, _SECTION_, extra="ignore")

        self.assertIsInstance(result, TestDataclass)
        self.assertEqual(result.option1, 42)
        self.assertEqual(result.option2, "value")
        self.assertFalse(hasattr(result, "extra_option"))

    def test_parse_section_list_fields(self) -> None:
        @dataclasses.dataclass
        class TestDataclass:
            option1: typing.Union[typing.List[int], int]
            option2: typing.Union[typing.List[int], int]

        self.config_parser.add_section(_SECTION_)
        self.config_parser.set(_SECTION_, "option1", "42")
        self.config_parser.set(_SECTION_, "option2", "[42,43]")

        result = self.config_parser.parse_section(TestDataclass, _SECTION_)

        self.assertIsInstance(result, TestDataclass)
        self.assertEqual(result.option1, 42)
        self.assertIsInstance(result.option1, int)
        self.assertEqual(result.option2, [42, 43])
        self.assertIsInstance(result.option2, typing.List)

    def test_parse_section_tuple_fields(self) -> None:
        @dataclasses.dataclass
        class TestDataclass:
            option1: typing.Tuple[int, str]
            option2: typing.List[typing.Tuple[str, str]]

        self.config_parser.add_section(_SECTION_)
        self.config_parser.set(_SECTION_, "option1", "(10, foo)")
        self.config_parser.set(_SECTION_, "option2", "[(foo, bar), (bar, baz), (baz, qux), (qux, foo)]")
        result = self.config_parser.parse_section(TestDataclass, _SECTION_)

        self.assertIsInstance(result, TestDataclass)
        self.assertEqual(result.option1, (10, "foo"))
        self.assertIsInstance(result.option1, tuple)
        self.assertIsInstance(result.option1[0], int)
        self.assertIsInstance(result.option1[1], str)
        self.assertEqual(result.option2, [("foo", "bar"), ("bar", "baz"), ("baz", "qux"), ("qux", "foo")])
        self.assertIsInstance(result.option2, typing.List)
        self.assertIsInstance(result.option2[0], tuple)
        self.assertIsInstance(result.option2[0][0], str)
        self.assertIsInstance(result.option2[0][1], str)

    def test_parse_section_optional_fields(self) -> None:
        @dataclasses.dataclass
        class TestDataclass:
            option1: typing.Optional[typing.List[str]]

        self.config_parser.add_section(_SECTION_)

        result = self.config_parser.parse_section(TestDataclass, _SECTION_)

        self.assertIsInstance(result, TestDataclass)
        self.assertEqual(getattr(result, "option1", None), None)

    def test_parse_section_defaults(self) -> None:
        @dataclasses.dataclass
        class TestDataclass:
            option1: typing.Optional[str]
            option2: str
            option3: typing.Optional[int] = 0
            option4: typing.Optional[float] = 10.2

        self.config_parser.set("DEFAULT", "option1", "default_value1")
        self.config_parser.set("DEFAULT", "option2", "default_value2")
        self.config_parser.add_section(_SECTION_)
        self.config_parser.set(_SECTION_, "option1", "test_value1")
        self.config_parser.set(_SECTION_, "option4", "11.2")

        result = self.config_parser.parse_section(TestDataclass, _SECTION_)
        self.assertIsInstance(result, TestDataclass)
        self.assertEqual(result.option1, "test_value1")
        self.assertIsInstance(result.option1, str)
        self.assertEqual(result.option2, "default_value2")
        self.assertIsInstance(result.option2, str)
        self.assertEqual(result.option3, 0)
        self.assertIsInstance(result.option3, int)
        self.assertEqual(result.option4, 11.2)
        self.assertIsInstance(result.option4, float)

    def test_parse_section_arbitrary_types(self) -> None:
        @dataclasses.dataclass
        class TestDataclass:
            option1: Path
            option2: typing.Dict[str, str]
            option3: typing.Tuple[str, typing.Dict[str, str]]

        self.config_parser.add_section(_SECTION_)
        self.config_parser.set(_SECTION_, "option1", "./home")
        self.config_parser.set(_SECTION_, "option2", "{key1: value1, key2: 10, key3: value3}")
        self.config_parser.set(_SECTION_, "option3", "(foo, {key: value})")

        result = self.config_parser.parse_section(TestDataclass, _SECTION_)

        self.assertIsInstance(result, TestDataclass)
        self.assertEqual(result.option1, Path("./home"))
        self.assertIsInstance(result.option1, PosixPath)
        self.assertEqual(result.option2, {"key1": "value1", "key2": "10", "key3": "value3"})
        self.assertIsInstance(result.option2, typing.Dict)
        self.assertEqual(result.option3, ("foo", {"key": "value"}))
        self.assertIsInstance(result.option3, tuple)

    def test_parse_section_extra_fields_dataclass(self) -> None:
        @dataclasses.dataclass
        class TestDataclass:
            option1: Path

        self.config_parser.add_section(_SECTION_)

        with self.assertRaisesRegex(ParseError, f"ParseError in section '{_SECTION_}' for option 'option1'"):
            self.config_parser.parse_section(TestDataclass, _SECTION_)

    def test_parse_section_invalid_boolean(self) -> None:
        @dataclasses.dataclass
        class TestDataclass:
            option1: bool

        self.config_parser.add_section(_SECTION_)
        self.config_parser.set(_SECTION_, "option1", "foo")

        with self.assertRaisesRegex(
            ParseError, f"ParseError in section '{_SECTION_}' for option 'option1': Cannot cast value 'foo' to 'boolean'"
        ):
            self.config_parser.parse_section(TestDataclass, _SECTION_)

    def test_parse_section_invalid_int(self) -> None:
        @dataclasses.dataclass
        class TestDataclass:
            option1: int

        self.config_parser.add_section(_SECTION_)
        self.config_parser.set(_SECTION_, "option1", "foo")

        with self.assertRaisesRegex(
            ParseError, f"ParseError in section '{_SECTION_}' for option 'option1': Cannot cast value 'foo' to 'int'"
        ):
            self.config_parser.parse_section(TestDataclass, _SECTION_)

    def test_parse_section_invalid_float(self) -> None:
        @dataclasses.dataclass
        class TestDataclass:
            option1: float

        self.config_parser.add_section(_SECTION_)
        self.config_parser.set(_SECTION_, "option1", "foo")

        with self.assertRaisesRegex(
            ParseError, f"ParseError in section '{_SECTION_}' for option 'option1': Cannot cast value 'foo' to 'float'"
        ):
            self.config_parser.parse_section(TestDataclass, _SECTION_)

    def test_parse_section_invalid_str(self) -> None:
        @dataclasses.dataclass
        class TestDataclass:
            option1: str

        self.config_parser.add_section(_SECTION_)
        self.config_parser.set(_SECTION_, "option1", '["foo", "bar"]')

        with self.assertRaisesRegex(
            ParseError,
            f"ParseError in section '{_SECTION_}' for option 'option1': Cannot cast value '"
            + '\\["foo", "bar"\\]'
            + "' to 'str'",
        ):
            self.config_parser.parse_section(TestDataclass, _SECTION_)

    def test_parse_section_invalid_none(self) -> None:
        @dataclasses.dataclass
        class TestDataclass:
            option1: None

        self.config_parser.add_section(_SECTION_)
        self.config_parser.set(_SECTION_, "option1", "foo")

        with self.assertRaisesRegex(
            ParseError, f"ParseError in section '{_SECTION_}' for option 'option1': Cannot cast value 'foo' to 'None'"
        ):
            self.config_parser.parse_section(TestDataclass, _SECTION_)

    def test_parse_section_invalid_union(self) -> None:
        @dataclasses.dataclass
        class TestDataclass:
            option1: typing.Union[int, float]

        self.config_parser.add_section(_SECTION_)
        self.config_parser.set(_SECTION_, "option1", "foo")

        with self.assertRaisesRegex(
            ParseError,
            f"ParseError in section '{_SECTION_}' for option 'option1': Cannot cast value 'foo' to '\(int|float\)' type",
        ):
            self.config_parser.parse_section(TestDataclass, _SECTION_)

    def test_parse_section_invalid_list(self) -> None:
        @dataclasses.dataclass
        class TestDataclass:
            option1: typing.List[int]

        self.config_parser.add_section(_SECTION_)
        self.config_parser.set(_SECTION_, "option1", "12")

        with self.assertRaisesRegex(
            ParseError, f"ParseError in section '{_SECTION_}' for option 'option1': Cannot cast value '12' to 'list'"
        ):
            self.config_parser.parse_section(TestDataclass, _SECTION_)

    def test_parse_section_invalid_tuple(self) -> None:
        @dataclasses.dataclass
        class TestDataclass:
            option1: typing.Tuple[str, int]

        self.config_parser.add_section(_SECTION_)
        self.config_parser.set(_SECTION_, "option1", "12")

        with self.assertRaisesRegex(
            ParseError, f"ParseError in section '{_SECTION_}' for option 'option1': Cannot cast value '12' to 'tuple'"
        ):
            self.config_parser.parse_section(TestDataclass, _SECTION_)

    def test_parse_section_invalid_dict(self) -> None:
        @dataclasses.dataclass
        class TestDataclass:
            option1: typing.Dict[str, int]

        self.config_parser.add_section(_SECTION_)
        self.config_parser.set(_SECTION_, "option1", "foo")

        with self.assertRaisesRegex(
            ParseError, f"ParseError in section '{_SECTION_}' for option 'option1': Cannot cast value 'foo' to 'dict'"
        ):
            self.config_parser.parse_section(TestDataclass, _SECTION_)

    def test_parse_section_invalid_any(self) -> None:
        class CustomType:
            def __init__(self) -> None:
                pass

        @dataclasses.dataclass
        class TestDataclass:
            option1: CustomType

        self.config_parser.add_section(_SECTION_)
        self.config_parser.set(_SECTION_, "option1", "foo")

        with self.assertRaisesRegex(
            ParseError,
            f"ParseError in section '{_SECTION_}' for option 'option1': Cannot cast value 'foo' to 'CustomType'",
        ):
            self.config_parser.parse_section(TestDataclass, _SECTION_)

    def test_parse_section_default_factory(self) -> None:
        @dataclasses.dataclass
        class TestDataclass:
            option1: typing.List[str] = dataclasses.field(default_factory=lambda: ["foo", "bar", "baz"])

        self.config_parser.add_section(_SECTION_)
        result = self.config_parser.parse_section(TestDataclass, _SECTION_)

        self.assertIsInstance(result, TestDataclass)
        self.assertEqual(result.option1, ["foo", "bar", "baz"])
        self.assertIsInstance(result.option1, typing.List)

    def test_parse_section_field_level_init_flag(self) -> None:
        @dataclasses.dataclass
        class TestDataclass:
            option1: int
            option2: float = dataclasses.field(init=False)

        self.config_parser.add_section(_SECTION_)
        self.config_parser.set(_SECTION_, "option1", "10")
        result = self.config_parser.parse_section(TestDataclass, _SECTION_)

        self.assertIsInstance(result, TestDataclass)
        self.assertEqual(result.option1, 10)
        self.assertFalse(hasattr(result, "option2"))

    def test_parse_section_post_init_method(self) -> None:
        @dataclasses.dataclass
        class TestDataclass:
            option1: int
            option2: float = dataclasses.field(init=False)

            def __post_init__(self) -> None:
                self.option2 = self.option1 + 20.2

        self.config_parser.add_section(_SECTION_)
        self.config_parser.set(_SECTION_, "option1", "10")
        result = self.config_parser.parse_section(TestDataclass, _SECTION_)

        self.assertIsInstance(result, TestDataclass)
        self.assertIsInstance(result.option1, int)
        self.assertEqual(result.option1, 10)
        self.assertIsInstance(result.option2, float)
        self.assertEqual(result.option2, 30.2)

    def test_parse_section_initvars(self) -> None:
        @dataclasses.dataclass
        class TestDataclass:
            option1: int
            option2: dataclasses.InitVar[typing.Optional[str]] = None
            option3: typing.Optional[str] = None
            option4: dataclasses.InitVar[typing.Optional[str]] = None

            def __post_init__(self, option2: typing.Optional[str], option4: typing.Optional[str]) -> None:
                self.option3 = option2

        self.config_parser.add_section(_SECTION_)
        self.config_parser.set(_SECTION_, "option1", "10")
        result = self.config_parser.parse_section(TestDataclass, _SECTION_, init_vars={"option2": "foo"})

        self.assertIsInstance(result, TestDataclass)
        self.assertEqual(result.option1, 10)
        self.assertEqual(result.option3, "foo")


def start_test() -> None:
    unittest.main()


if __name__ == "__main__":
    start_test()

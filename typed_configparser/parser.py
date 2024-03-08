import configparser
import dataclasses
import re
import sys
import types
import typing

import typing_extensions

from typed_configparser.exceptions import ParseError

if typing.TYPE_CHECKING:
    from _typeshed import DataclassInstance

T = typing.TypeVar("T", bound="DataclassInstance")

# This is a hack to make sure get_type_hints work correctly for InitVar
# when __future__ annotations is turned on
dataclasses.InitVar.__call__ = lambda *args: None  # type: ignore[method-assign]

BOOLEAN_STATES = {
    "1": True,
    "yes": True,
    "true": True,
    "on": True,
    "0": False,
    "no": False,
    "false": False,
    "off": False,
}

NONE_VALUES = {"none", "null"}

_ORIGIN_KEY_ = "origin"
_ARGS_KEY_ = "args"
_REGEX_ = r",(?![^\[\(\{]*[\]\)\}])"

LIST_TYPE = (list, typing.List)
DICT_TYPE = (dict, typing.Dict)
TUPLE_TYPE = (tuple, typing.Tuple)

if sys.version_info >= (3, 10):  # pragma: no cover
    UNION_TYPE = (types.UnionType, typing.Union)
    NONE_TYPE = (types.NoneType, type(None))
else:  # pragma: no cover
    UNION_TYPE = (typing.Union,)
    NONE_TYPE = (type(None),)


def _CUSTOM_REPR_METHOD(self: T) -> str:
    fields_str = ", ".join(f"{field.name}={getattr(self, field.name)}" for field in self.__dataclass_fields__.values())
    return f"{self.__class__.__name__}({fields_str})"


def _CUSTOM_STR_METHOD(self: T) -> str:
    fields_str = ", ".join(f"{field.name}={getattr(self, field.name)}" for field in self.__dataclass_fields__.values())
    return f"{self.__class__.__name__}({fields_str})"


def get_types(typ: typing.Type[typing.Any]) -> typing.Any:
    """
    Recursively get the types information for a given type.

    Args:
        typ (Type): The type for which to retrieve information.

    Returns:
        Any: A dictionary containing information about the type, including its origin and arguments.

    """
    origin = typing_extensions.get_origin(typ)
    args = typing_extensions.get_args(typ)
    if origin is None:
        return typ
    result = {_ORIGIN_KEY_: origin, _ARGS_KEY_: []}
    for arg in args:
        result[_ARGS_KEY_].append(get_types(arg))
    return result


def cast_bool(section: str, option: str, value: str) -> bool:
    if value.lower() not in BOOLEAN_STATES:
        raise ParseError(f"Cannot cast value '{value}' to 'boolean'", section, option=option)
    return BOOLEAN_STATES[value.lower()]


def cast_none(section: str, option: str, value: str) -> None:
    if value and value.lower() in NONE_VALUES:
        return None

    raise ParseError(f"Cannot cast value '{value}' to 'None'", section, option=option)


def cast_any(section: str, option: str, value: str, target_type: typing.Any) -> typing.Any:
    try:
        return target_type(value)
    except Exception:
        raise ParseError(f"Cannot cast value '{value}' to '{target_type.__name__}'", section, option=option)


def cast_int(section: str, option: str, value: str) -> typing.Any:
    try:
        return int(value)
    except Exception:
        raise ParseError(f"Cannot cast value '{value}' to 'int'", section, option=option)


def cast_float(section: str, option: str, value: str) -> typing.Any:
    try:
        return float(value)
    except Exception:
        raise ParseError(f"Cannot cast value '{value}' to 'float'", section, option=option)


def cast_str(section: str, option: str, value: str) -> typing.Any:
    if is_list(value) or is_tuple(value) or is_dict(value):
        raise ParseError(f"Cannot cast value '{value}' to 'str'", section, option=option)

    try:
        return str(value)
    except Exception:  # pragma: no cover
        raise ParseError(f"Cannot cast value '{value}' to 'str'", section, option=option)


def get_name(args: typing.List[type]) -> str:
    return "|".join([getattr(arg, "__name__", repr(arg)) for arg in args])


def cast_value_wrapper(section: str, option: str, value: str, target_type: typing.Any) -> typing.Any:
    def cast_value(value: str, target_type: typing.Any) -> typing.Any:
        """
        Cast a string value to the specified target type.
        Types are traversed recursively to match the first matching type.

        Lists are special. For list, the string should be separated by LIST_DELIMITED
        which is defaulted to a ",".

        Args:
            value (str): The string value to be cast.
            target_type (Any): The target type to which the value should be cast.

        Returns:
            Any: The casted value of the specified type.

        Raises:
            ParseError: If the value cannot be cast to any of the given types.

        """
        if isinstance(target_type, DICT_TYPE):
            origin = target_type[_ORIGIN_KEY_]
            args = target_type[_ARGS_KEY_]
            if origin in UNION_TYPE:
                for arg in args:
                    try:
                        return cast_value(value, arg)
                    except Exception:
                        continue

                raise ParseError(
                    f"Cannot cast value '{value}' to '({get_name(args)})' type",
                    section,
                    option=option,
                )
            elif origin in LIST_TYPE:
                if is_list(value):
                    values = re.split(_REGEX_, strip(value, "[", "]"))
                    return [cast_value(item.strip(), args) for item in values]
                else:
                    raise ParseError(f"Cannot cast value '{value}' to 'list'", section, option=option)
            elif origin in TUPLE_TYPE:
                if is_tuple(value):
                    values = re.split(_REGEX_, strip(value, "(", ")"))
                    return tuple([cast_value(item.strip(), arg) for item, arg in zip(values, args)])
                else:
                    raise ParseError(f"Cannot cast value '{value}' to 'tuple'", section, option=option)
            elif origin in DICT_TYPE:
                if is_dict(value):
                    values = re.split(_REGEX_, strip(value, "{", "}"))
                    return {
                        cast_value(k.strip(), args[0]): cast_value(v.strip(), args[1])
                        for k, _, v in (val.partition(":") for val in values)
                    }
                else:
                    raise ParseError(f"Cannot cast value '{value}' to 'dict'", section, option=option)
        elif isinstance(target_type, LIST_TYPE):
            for arg in target_type:
                return cast_value(value, arg)
        elif target_type == int:
            return cast_int(section, option, value)
        elif target_type == float:
            return cast_float(section, option, value)
        elif target_type == str:
            return cast_str(section, option, value)
        elif target_type == bool:
            return cast_bool(section, option, value)
        elif target_type in NONE_TYPE:
            return cast_none(section, option, value)
        else:
            return cast_any(section, option, value, target_type)

    return cast_value(value, target_type)


def is_field_optional(typ: typing.Type[T]) -> bool:
    """Check whether type contains any None type variable"""
    typs = get_types(typ)
    if isinstance(typs, DICT_TYPE):
        return any(N_ in typs.get(_ARGS_KEY_, ()) for N_ in NONE_TYPE)
    else:
        return typs in NONE_TYPE


def is_field_default(field: typing.Any) -> bool:
    assert isinstance(field, dataclasses.Field)
    return field.default != dataclasses.MISSING or field.default_factory != dataclasses.MISSING or field.init is False


def is_list(value: str) -> bool:
    """Check whether string value qualifies as a list"""
    if value.startswith("[") and value.endswith("]"):
        return True
    return False


def is_tuple(value: str) -> bool:
    """Check whether string value qualifies as a tuple"""
    if value.startswith("(") and value.endswith(")"):
        return True
    return False


def is_dict(value: str) -> bool:
    if value.startswith("{") and value.endswith("}") and value.find(":") > -1:
        return True
    return False


def strip(value: str, first: str, last: str) -> str:
    """Strip single matching first and last character only if both match"""
    if value.startswith(first) and value.endswith(last):
        return value[1:-1]
    return value  # pragma: no cover


def generate_field(key: str, default: typing.Optional[str] = None) -> typing.Any:
    """Get a new empty field with just the name attribute"""
    f = dataclasses.field()
    f.name = key
    if default:
        f.default = default
    return f


def is_dataclass(typ: typing.Type[T]) -> bool:
    """This is added for typing"""
    return dataclasses.is_dataclass(typ)


class ConfigParser(configparser.ConfigParser):
    """
    Extended configparser with support for typed configuration using dataclasses.

    Attributes:
        __config_class_mapper__ (Dict[str, Any]): A mapping of section names to corresponding
            dataclass types.

    Methods:
        _get_type(self, section: str, option: str) -> Any:
            Get the expected type for a given option in a section.

        _getitem(self, section: str, option: str) -> Any:
            Get the value of an option in a section and apply type conversion.

    """

    __config_class_mapper__: typing.Dict[str, typing.Any] = {}

    def _get_type(self, section: str, option: str) -> typing.Any:
        """
        Get the expected type for a given option in a section.

        Args:
            section (str): The name of the configuration section.
            option (str): The name of the configuration option.

        Returns:
            Any: The expected type of the option.

        Raises:
            Exception: If the option is not found in the dataclass annotations.

        """
        config_class = self.__config_class_mapper__.get(section)
        if config_class:
            try:
                typ = typing_extensions.get_type_hints(config_class)[option]
                return lambda val: cast_value_wrapper(section, option, val, get_types(typ))
            except KeyError:
                return str
            except Exception:  # pragma: no cover
                raise
        else:  # pragma: no cover
            raise TypeError("Config class not found")

    def _getitem(self, section: str, option: str) -> typing.Any:
        """
        Get the value of an option in a section and apply type conversion.
        Uses super class method _get_conv to do the converstion.

        Args:
            section (str): The name of the configuration section.
            option (str): The name of the configuration option.

        Returns:
            Any: The value of the option after type conversion.

        """
        conv = self._get_type(section, option)
        value = super()._get_conv(section, option, conv)
        return value

    def parse_section(
        self,
        using_dataclass: typing.Type[T],
        section_name: typing.Union[str, None] = None,
        extra: typing.Literal["allow", "ignore", "error"] = "allow",
        init_vars: typing.Dict[str, typing.Any] = {},
    ) -> T:
        """
        Parse a configuration section into a dataclass instance.

        Args:
            using_dataclass (Type[T]): The dataclass type to instantiate and populate.
            section_name (Union[str, None], optional): The name of the configuration section.
                If None, the name is derived from the dataclass name. Defaults to None.
            extra (Literal["allow", "ignore", "error"], optional): How to handle extra fields
                not present in the dataclass. "allow" allows extra fields, "ignore" ignores them,
                and "error" raises an ParseError. Defaults to "allow".
            init_vars (Dict[str, Any]): For any InitVars on dataclass, send values here as a dict
                which will be send to dataclasses's init method and eventually to post_init method.

        Returns:
            T: An instance of the specified dataclass populated with values from the configuration section.

        Raises:
            ParseError: If parsing of configuration fails.

        Note:
            This method modifies the provided dataclass type by setting its __init__ method to an
            empty function (_CUSTOM_INIT_METHOD) to avoid errors during instantiation.

            The function also sets the __repr__ and __str__ methods of the dataclass to custom methods
            (_CUSTOM_REPR_METHOD and _CUSTOM_STR_METHOD) for better representation.

        """
        section_name_ = section_name or using_dataclass.__name__
        if not is_dataclass(using_dataclass):
            raise ParseError(f"{using_dataclass.__name__} is not a valid dataclass", section_name_)

        if params := getattr(using_dataclass, "__dataclass_params__", None):
            if (init := getattr(params, "init", None)) is not None:
                if init is False:
                    raise TypeError(f"init flag must be True for dataclass '{using_dataclass.__name__}'")

        self.__config_class_mapper__[section_name_] = using_dataclass
        # This are just "fields" and doesn't contain classvar or initvar fields
        dataclass_fields = {item.name: item for item in dataclasses.fields(using_dataclass)}
        initvar_fields = {
            item.name: item
            for item in using_dataclass.__dataclass_fields__.values()
            if item._field_type is dataclasses._FIELD_INITVAR  # type: ignore [attr-defined]
        }
        options = []
        # Adding all keys to args initially to maintain the order of position arguments
        # to be sent to dataclass init method. It is not required for keyword arguments
        args = {k: v for k, v in dataclass_fields.items() if not is_field_default(v)}
        kwargs = {}
        extra_fields = {}
        seen = set()

        # Iterate through config section to update args & kwargs
        # for fields present in dataclass. Anything not found in
        # dataclass is added to extra_fields
        for key, _ in self.items(section_name_):
            value = self._getitem(section_name_, key)
            options.append(key)
            if key in dataclass_fields:
                field_info = dataclass_fields[key]
                if is_field_default(field_info):
                    kwargs[key] = value
                else:
                    args[key] = value
                seen.add(key)
            else:
                extra_fields[key] = generate_field(key, default=value)

        # Now iterate through dataclass fields and update default value of
        # any "Optional" fields to None.
        # Any non-"Optional" fields present in dataclass but not found in
        # config options are missing fields and should raise error
        missing_fields = []
        for field, field_info in dataclass_fields.items():
            field_type = typing_extensions.get_type_hints(using_dataclass)[field]
            if not is_field_default(field_info) and field not in seen:
                if is_field_optional(field_type):
                    args[field] = None  # type: ignore
                elif field not in options:
                    missing_fields.append(field)

        # Supply initvars as kwargs to the dataclass call
        for field, field_info in initvar_fields.items():
            if field in init_vars:
                kwargs[field] = init_vars[field]
            else:
                kwargs[field] = None

        if len(missing_fields) > 0:
            raise ParseError(
                "Unable to find value in section, default section or dataclass defaults",
                section_name_,
                ", ".join(missing_fields),
            )

        if len(extra_fields) > 0 and extra == "error":
            raise ParseError("Extra fields are not allowed in configuration.", section_name_)

        section = using_dataclass(*args.values(), **kwargs)

        if extra_fields and extra == "allow":
            for k, f in extra_fields.items():
                setattr(section, k, f.default)
            setattr(using_dataclass, "__dataclass_extra_fields__", extra_fields)
            using_dataclass.__dataclass_fields__.update(extra_fields)
            # Since __repr__ and __str__ are created when dataclass is created using @dataclass
            # decorator, we need to rewrite our own methods for extra fields
            using_dataclass.__repr__ = _CUSTOM_REPR_METHOD  # type: ignore[assignment]
            using_dataclass.__str__ = _CUSTOM_STR_METHOD  # type: ignore[assignment]
        return section

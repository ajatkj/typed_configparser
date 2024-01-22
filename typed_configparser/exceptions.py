import typing


class ParseError(TypeError):
    def __init__(self, message: str, section: str, option: typing.Optional[str] = None) -> None:
        super().__init__(message)
        self.section = section
        self.option = option

    def __str__(self) -> str:
        if self.option is not None:
            return f"ParseError in section '{self.section}' for option '{self.option}': {self.args[0]}"
        else:
            return f"ParseError in section '{self.section}': {self.args[0]}"

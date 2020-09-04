from typing import Any

from ..errors import InvalidArgError, MissingArgError, ValidateError
from ..unset import UNSET
from ..validation import validate

__all__ = [
    'Arg',
]


class Arg:
    __slots__ = ('name', 'type', 'default', 'is_positional', 'is_zipped')

    def __init__(self, name: str, type_: type, default: Any, is_positional: bool, is_zipped: bool):
        self.name = name
        self.type = type_
        self.default = default
        self.is_positional = is_positional
        self.is_zipped = is_zipped

    def __repr__(self) -> str:
        return '{}({}{}: {}{})'.format(
            self.__class__.__name__,
            {
                (True, True): '*',
                (True, False): '',
                (False, True): '**',
                (False, False): '*, ',
            }[self.is_positional, self.is_zipped],
            self.name,
            self.type,
            '' if self.default is UNSET else ' = {!r}'.format(self.default),
        )

    def validate(self, value: Any) -> Any:
        if value is UNSET:
            if self.default is UNSET:
                raise MissingArgError(self)
            else:
                result = self.default
        else:
            try:
                result = validate(self.type, value)
            except ValidateError as exc:
                raise InvalidArgError(self, value) from exc

        return result

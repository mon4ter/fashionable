from typing import Any

from ..errors import InvalidArgError, MissingArgError, ValidateError
from ..unset import UNSET
from ..validation import validate

__all__ = [
    'Arg',
]


class Arg:
    __slots__ = ('func', 'name', 'type', 'default', 'is_positional', 'is_zipped')

    def __init__(self, func: str, name: str, type_: type, default: Any, is_positional: bool, is_zipped: bool):
        self.func = func
        self.name = name
        self.type = type_
        self.default = default
        self.is_positional = is_positional
        self.is_zipped = is_zipped

    def __repr__(self) -> str:
        return '{}({}{}: {}{})'.format(
            type(self).__name__,
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
                raise MissingArgError(func=self.func, arg=self.name)
            else:
                result = self.default
        else:
            try:
                result = validate(self.type, value)
            except ValidateError as exc:
                raise InvalidArgError(func=self.func, arg=self.name) from exc

        return result

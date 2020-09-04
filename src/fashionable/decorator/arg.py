from ..errors import InvalidArgError, MissingArgError, ValidateError
from ..typedef import OptionalTyping, Value
from ..unset import UNSET
from ..validation import validate

__all__ = [
    'Arg',
]


# TODO refactor to subclass of Parameter
class Arg:
    __slots__ = ('_func', '_name', '_type', '_default', '_is_positional', '_is_zipped')

    def __init__(self, func: str, name: str, typ: OptionalTyping, default: Value, is_positional: bool, is_zipped: bool):
        self._func = func
        self._name = name
        self._type = typ
        self._default = default
        self._is_positional = is_positional
        self._is_zipped = is_zipped

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> OptionalTyping:
        return self._type

    @property
    def default(self) -> Value:
        return self._default

    @property
    def is_positional(self) -> bool:
        return self._is_positional

    @property
    def is_zipped(self) -> bool:
        return self._is_zipped

    def __repr__(self) -> str:
        return '{}{}{}{}{}'.format(
            '*' * self._is_zipped,
            '*' * (self._is_zipped and not self._is_positional),
            self._name,
            '' if self._type is UNSET else ': {}'.format(self._type),
            '' if self._default is UNSET else '{1}={1}{0!r}'.format(self._default, ' ' * (self._type is not UNSET)),
        )

    def validate(self, value: Value) -> Value:
        if value is UNSET:
            if self._default is UNSET:
                raise MissingArgError(func=self._func, arg=self._name)
            else:
                value = self._default
        elif self._type is not UNSET:
            try:
                value = validate(self._type, value)
            except ValidateError as exc:
                raise InvalidArgError(func=self._func, arg=self._name) from exc

        return value

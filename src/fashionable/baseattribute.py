from .errors import ValidateError
from .typedef import Limiter as L, Typing, Value as V
from .unset import UNSET
from .validation import validate

__all__ = [
    'BaseAttribute',
]


class BaseAttribute:
    # noinspection PyShadowingBuiltins
    def __init__(self, type: Typing, *, strict: bool = False, default: V = UNSET, min: L = UNSET, max: L = UNSET):
        self._type = None
        self._strict = None
        self._default = None
        self._min = None
        self._max = None
        self._name = None
        self._private_name = None

        self.type = type
        self.strict = strict
        self.min = min
        self.max = max
        self.default = default

    @property
    def type(self) -> Typing:
        return self._type

    @type.setter
    def type(self, value: Typing):
        try:
            validate(Typing, value, strict=True)
        except ValidateError:
            raise TypeError("Invalid {}.type: must be a type, not {!r}".format(type(self).__name__, value))

        self._type = value

    @property
    def strict(self) -> bool:
        return self._strict

    @strict.setter
    def strict(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(
                "Invalid {}.strict: must be a bool, not {}".format(type(self).__name__, type(value).__name__)
            )

        self._strict = value

    @property
    def default(self) -> V:
        return self._default

    @default.setter
    def default(self, value: V):
        if value is not UNSET:
            try:
                value = validate(self.type, value, self.strict)
                iterable = hasattr(value, '__iter__')

                if self._min is not UNSET and (len(value) if iterable else value) < self._min:
                    raise ValueError("{}should be >= {}".format('length ' * iterable, self._max))

                if self._max is not UNSET and (len(value) if iterable else value) > self._max:
                    raise ValueError("{}should be <= {}".format('length ' * iterable, self._max))
            except ValidateError as exc:
                raise type(exc)("Invalid {}.default: {}".format(type(self).__name__, exc)) from exc

        self._default = value

    @property
    def min(self) -> L:
        return self._min

    @min.setter
    def min(self, value: L):
        if value is not UNSET:
            try:
                value < value
            except TypeError as exc:
                raise TypeError("Invalid {}.min: {}".format(type(self).__name__, exc)) from exc

        self._min = value

    @property
    def max(self) -> L:
        return self._max

    @max.setter
    def max(self, value: L):
        if value is not UNSET:
            try:
                value > value
            except TypeError as exc:
                raise TypeError("Invalid {}.max: {}".format(type(self).__name__, exc)) from exc

        self._max = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not isinstance(value, str):
            raise TypeError("Invalid {}.name: must be a str, not {}".format(type(self).__name__, type(value).__name__))

        self._name = value
        self._private_name = '.' + value

    @property
    def private_name(self) -> str:
        return self._private_name

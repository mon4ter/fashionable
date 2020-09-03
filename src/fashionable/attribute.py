from typing import Optional, TypeVar, Union

from .modelerror import ModelAttributeError, ModelError, ModelTypeError, ModelValueError
from .validation import Typing, validate

__all__ = [
    'Attribute',
    'UNSET',
    'Unset',
]


class Unset:
    def __new__(cls):
        if not hasattr(cls, '.instance'):
            setattr(cls, '.instance', super().__new__(cls))

        return getattr(cls, '.instance')

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return 'UNSET'


UNSET = Unset()

T = TypeVar('T')
Value = Union[T, Unset]


# TODO replace limit with Iterable-aware min/max
class Attribute:
    # noinspection PyShadowingBuiltins
    def __init__(
            self, type: Typing,
            *,
            strict: bool = False,
            default: Value = UNSET,
            limit: Optional[int] = None,
            min: Value = UNSET,
            max: Value = UNSET
    ):
        self._type = None
        self._strict = None
        self._default = None
        self._limit = None
        self._min = None
        self._max = None
        self._name = None
        self._private_name = None

        self.type = type
        self.strict = strict
        self.limit = limit
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
        except (TypeError, ValueError):
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
    def default(self) -> Value:
        return self._default

    @default.setter
    def default(self, value: Value):
        if value is not UNSET:
            try:
                value = validate(self.type, value, self.strict)

                if self._limit is not None and len(value) > self._limit:
                    raise ValueError("too long. Max length is {}".format(self._limit))

                if self._min is not UNSET and value < self._min:
                    raise ValueError("should be >= {}".format(self._max))

                if self._max is not UNSET and value > self._max:
                    raise ValueError("should be <= {}".format(self._max))
            except (TypeError, ValueError, AttributeError) as exc:
                raise type(exc)("Invalid {}.default: {}".format(type(self).__name__, exc)) from exc

        self._default = value

    @property
    def limit(self) -> Optional[int]:
        return self._limit

    @limit.setter
    def limit(self, value: Optional[int]):
        if value is not None:
            if not isinstance(value, int):
                raise TypeError(
                    "Invalid {}.limit: must be a int, not {}".format(type(self).__name__, type(value).__name__)
                )

            if value < 0:
                raise ValueError("Invalid {}.limit: should be >= 0".format(type(self).__name__))

        self._limit = value

    @property
    def min(self) -> Value:
        return self._min

    @min.setter
    def min(self, value: Value):
        if value is not UNSET:
            try:
                value < value
            except TypeError as exc:
                raise TypeError("Invalid {}.min: {}".format(type(self).__name__, exc)) from exc

        self._min = value

    @property
    def max(self) -> Value:
        return self._max

    @max.setter
    def max(self, value: Value):
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

    def __get__(self, instance, owner) -> Value:
        return getattr(instance, self._private_name)

    def __set__(self, instance, value: Value):
        model = type(instance).__name__
        unset = value is UNSET

        try:
            value = validate(self.type, None if unset else value, self.strict)
        except Exception as exc:
            if unset or isinstance(exc, AttributeError):
                err = "missing required attribute %(attr)s"
                err_type = ModelAttributeError
            elif isinstance(exc, ValueError):
                err = "invalid value of attribute %(attr)s"
                err_type = ModelTypeError
            elif isinstance(exc, TypeError):
                err = "=invalid type of attribute %(attr)s"
                err_type = ModelTypeError
            else:
                err = "invalid attribute %(attr)s"
                err_type = ModelError

            raise err_type("Invalid %(model)s: " + err, model=model, attr=self._name) from exc

        if unset:
            value = self.default

        if self._limit is not None and len(value) > self._limit:
            raise ModelValueError(
                "Invalid %(model)s: attribute %(attr)s is too long. Max length: %(limit)d",
                model=model,
                attr=self._name,
                limit=self._limit,
            )

        if self._min is not UNSET and value < self._min:
            raise ModelValueError(
                "Invalid %(model)s: attribute %(attr)s: should be >= %(min)s",
                model=model,
                attr=self._name,
                min=self._min,
            )

        if self._max is not UNSET and value > self._max:
            raise ModelValueError(
                "Invalid %(model)s: attribute %(attr)s: should be <= %(max)s",
                model=model,
                attr=self._name,
                max=self._max,
            )

        setattr(instance, self._private_name, value)

    def __delete__(self, instance):
        self.__set__(instance, self.default)

from typing import Any, Optional

from .modelerror import ModelAttributeError, ModelError, ModelTypeError, ModelValueError
from .validation import Typing, validate

__all__ = [
    'Attribute',
    'UNSET',
]

UNSET = object()


class Attribute:
    # noinspection PyShadowingBuiltins
    def __init__(self, type: Typing, *, strict: Optional[bool] = None, default: Any = UNSET,
                 limit: Optional[int] = None, min: Any = None, max: Any = None):
        self._type = None
        self._strict = None
        self._limit = None
        self._min = None
        self._max = None
        self._name = None
        self._private_name = None

        self.type = type
        self.strict = strict
        self.default = default
        self.limit = limit
        self.min = min
        self.max = max

    @property
    def type(self) -> Typing:
        return self._type

    @type.setter
    def type(self, value: Typing):
        try:
            validate(Typing, value, strict=True)
        except (TypeError, ValueError):
            raise TypeError("Invalid type: must be a type, not {!r}".format(value))

        self._type = value

    @property
    def strict(self) -> bool:
        return self._strict

    @strict.setter
    def strict(self, value: Optional[bool]):
        if value is None:
            value = False

        if not isinstance(value, bool):
            raise TypeError("Invalid strict: must be a bool, not {}".format(value.__class__.__name__))

        self._strict = value

    @property
    def limit(self) -> Optional[int]:
        return self._limit

    @limit.setter
    def limit(self, value: Optional[int]):
        if value is not None:
            if not isinstance(value, int):
                raise TypeError("Invalid limit: must be a int, not {}".format(value.__class__.__name__))

            if value < 0:
                raise ValueError("Invalid limit: should be >= 0")

        self._limit = value

    @property
    def min(self) -> Any:
        return self._min

    @min.setter
    def min(self, value: Any):
        if value is not None:
            try:
                value < value
            except TypeError as exc:
                raise TypeError("Invalid min: should be comparable") from exc

        self._min = value

    @property
    def max(self) -> Any:
        return self._max

    @max.setter
    def max(self, value: Any):
        if value is not None:
            try:
                value > value
            except TypeError as exc:
                raise TypeError("Invalid max: should be comparable") from exc

        self._max = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not isinstance(value, str):
            raise TypeError("Invalid name: must be a str, not {}".format(value.__class__.__name__))

        self._name = value
        self._private_name = '.' + value

    @property
    def private_name(self) -> str:
        return self._private_name

    def __get__(self, instance, owner):
        return getattr(instance, self._private_name)

    def __set__(self, instance, value):
        model = instance.__class__.__name__
        unset = value is UNSET

        try:
            value = validate(self.type, None if unset else value, self.strict)
        except Exception as exc:
            if unset or isinstance(exc, AttributeError):
                err = "Invalid %(model)s: missing required attribute %(attr)s"
                err_type = ModelAttributeError
            elif isinstance(exc, ValueError):
                err = "Invalid %(model)s: invalid value of attribute %(attr)s"
                err_type = ModelTypeError
            elif isinstance(exc, TypeError):
                err = "Invalid %(model)s: invalid type of attribute %(attr)s"
                err_type = ModelTypeError
            else:
                err = "Invalid %(model)s: invalid attribute %(attr)s"
                err_type = ModelError

            raise err_type(err, model=model, attr=self._name) from exc

        if unset:
            value = self.default

        if self._limit is not None and len(value) > self._limit:
            raise ModelValueError(
                "Invalid %(model)s: attribute %(attr)s is too long. Max length: %(limit)d",
                model=model,
                attr=self._name,
                limit=self._limit,
            )

        if self._min is not None and value < self._min:
            raise ModelValueError(
                "Invalid %(model)s: attribute %(attr)s: should be >= %(min)s",
                model=model,
                attr=self._name,
                min=self._min,
            )

        if self._max is not None and value > self._max:
            raise ModelValueError(
                "Invalid %(model)s: attribute %(attr)s: should be <= %(max)s",
                model=model,
                attr=self._name,
                max=self._max,
            )

        setattr(instance, self._private_name, value)

    def __delete__(self, instance):
        self.__set__(instance, UNSET)

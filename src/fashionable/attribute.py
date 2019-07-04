from typing import Any, Optional, Type, Union

from .invalidmodelerror import InvalidModelError
from .validate import TypingMeta, validate

__all__ = [
    'Attribute',
]


class Attribute:
    # noinspection PyShadowingBuiltins
    def __init__(self, type: Union[Type, TypingMeta],
                 default: Any = None, limit: Optional[int] = None, min: Any = None, max: Any = None):
        self._type = None
        self._limit = None
        self._min = None
        self._max = None
        self._name = None
        self._private_name = None

        self.type = type
        self.default = default
        self.limit = limit
        self.min = min
        self.max = max

    @property
    def type(self) -> Union[Type, TypingMeta]:
        return self._type

    @type.setter
    def type(self, value: Union[Type, TypingMeta]):
        if not isinstance(value, type) and not isinstance(type(value), TypingMeta):
            raise TypeError("Invalid 'type': must be a type or TypingMeta, not {!r}".format(value))

        self._type = value

    @property
    def limit(self) -> Optional[int]:
        return self._limit

    @limit.setter
    def limit(self, value: Optional[int]):
        if value is not None:
            if not isinstance(value, int):
                raise TypeError("Invalid limit: must be int, not {}".format(value.__class__.__name__))

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
            raise TypeError("Invalid name: must be str, not {}".format(value.__class__.__name__))

        self._name = value
        self._private_name = '_m_' + value

    @property
    def private_name(self) -> str:
        return self._private_name

    def __get__(self, instance, owner):
        return getattr(instance, self._private_name)

    def __set__(self, instance, value):
        model = instance.__class__.__name__

        try:
            value = validate(self.type, value)
        except (TypeError, ValueError, InvalidModelError):
            if value is None:
                err = "Invalid %(model)s: missing required attribute %(attr)s"
            else:
                err = "Invalid %(model)s: invalid attribute %(attr)s"

            raise InvalidModelError(err, model=model, attr=self._name)

        if value is None:
            value = self.default

        if self._limit is not None and len(value) > self._limit:
            raise InvalidModelError(
                "Invalid %(model)s: attribute %(attr)s is too long. Max length: %(limit)d",
                model=model,
                attr=self._name,
                limit=self._limit,
            )

        if self._min is not None and value < self._min:
            raise InvalidModelError(
                "Invalid %(model)s: attribute %(attr)s should be >= %(min)s",
                model=model,
                attr=self._name,
                min=self._min,
            )

        if self._max is not None and value > self._max:
            raise InvalidModelError(
                "Invalid %(model)s: attribute %(attr)s should be <= %(max)s",
                model=model,
                attr=self._name,
                max=self._max,
            )

        setattr(instance, self._private_name, value)

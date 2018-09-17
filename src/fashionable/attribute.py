from typing import Any


from .unset import UNSET

__all__ = [
    'Attribute',
]


class Attribute:
    # noinspection PyShadowingBuiltins
    def __init__(self, type: type=UNSET, *,
                 default: Any=UNSET, limit: int=UNSET, min: Any=UNSET, max: Any=UNSET):
        self._type = UNSET
        self._default = UNSET
        self._limit = UNSET
        self._min = UNSET
        self._max = UNSET

        if type is not UNSET:
            self.type = type

        if default is not UNSET:
            self.default = default

        if limit is not UNSET:
            self.limit = limit

        if min is not UNSET:
            self.min = min

        if max is not UNSET:
            self.max = max

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if not isinstance(value, type):
            fmt = "Invalid type: must be a type, not %(value_type)s"
            kwargs = {'value_type': value.__class__.__name__}
            raise TypeError(fmt % kwargs, fmt, kwargs)

        self._type = value

    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, value):
        if not isinstance(value, int):
            fmt = "Invalid limit: must be a int, not %(value_type)s"
            kwargs = {'value_type': value.__class__.__name__}
            raise TypeError(fmt % kwargs, fmt, kwargs)

        if value < 0:
            raise ValueError("Invalid limit: should be >= 0")

        self._limit = value

    @property
    def min(self):
        return self._min

    @min.setter
    def min(self, value):
        try:
            value < value
        except TypeError as exc:
            raise TypeError("Invalid min: should be comparable") from exc
        else:
            self._min = value

    @property
    def max(self):
        return self._max

    @max.setter
    def max(self, value):
        try:
            value > value
        except TypeError as exc:
            raise TypeError("Invalid max: should be comparable") from exc
        else:
            self._max = value

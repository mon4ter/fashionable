from typing import Any

__all__ = [
    'Attribute',
]


class Attribute:
    # noinspection PyShadowingBuiltins
    def __init__(self, type: type=None, *,
                 optional: bool=False, default: Any=None, limit: int=None, min: Any=None, max: Any=None):
        self._type = None
        self._optional = None
        self._default = None
        self._limit = None
        self._min = None
        self._max = None

        if type is not None:
            self.type = type

        self.optional = optional

        if default is not None:
            self.default = default

        if limit is not None:
            self.limit = limit

        if min is not None:
            self.min = min

        if max is not None:
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
    def optional(self):
        return self._optional

    @optional.setter
    def optional(self, value):
        if not isinstance(value, bool):
            fmt = "Invalid optional: must be bool, not %(value_type)s"
            kwargs = {'value_type': value.__class__.__name__}
            raise TypeError(fmt % kwargs, fmt, kwargs)

        self._optional = value

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

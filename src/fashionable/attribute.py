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
        self._limit = None
        self._min = None
        self._max = None

        self.type = type
        self.optional = optional
        self.default = default
        self.limit = limit
        self.min = min
        self.max = max

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if value is not None and not isinstance(value, type):
            raise TypeError("Invalid type: must be a type, not {}".format(value.__class__.__name__))

        self._type = value

    @property
    def optional(self):
        return self._optional

    @optional.setter
    def optional(self, value):
        if value is not None and not isinstance(value, bool):
            raise TypeError("Invalid optional: must be bool, not {}".format(value.__class__.__name__))

        self._optional = value

    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, value):
        if value is not None:
            if not isinstance(value, int):
                raise TypeError("Invalid limit: must be int, not {}".format(value.__class__.__name__))

            if value < 0:
                raise ValueError("Invalid limit: should be >= 0")

        self._limit = value

    @property
    def min(self):
        return self._min

    @min.setter
    def min(self, value):
        if value is not None:
            try:
                value < value
            except TypeError as exc:
                raise TypeError("Invalid min: should be comparable") from exc

        self._min = value

    @property
    def max(self):
        return self._max

    @max.setter
    def max(self, value):
        if value is not None:
            try:
                value > value
            except TypeError as exc:
                raise TypeError("Invalid max: should be comparable") from exc

        self._max = value

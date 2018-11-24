from typing import Any

__all__ = [
    'Attribute',
    'InvalidModelError',
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
        self._name = None
        self._private_name = None

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

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self._private_name = '_m_' + value

    @property
    def private_name(self):
        return self._private_name

    def __get__(self, instance, owner):
        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        model = instance.__class__.__name__

        if value is None:
            if self.optional:
                value = self.default
            else:
                raise InvalidModelError(
                    "Invalid %(model)s: missing required attribute %(attr)s",
                    model=model,
                    attr=self.name,
                )
        else:
            if self.type is not None and not isinstance(value, self.type):
                try:
                    value = self.type(value)
                except (TypeError, ValueError) as exc:
                    raise InvalidModelError(
                        "Invalid %(model)s: invalid attribute %(attr)s",
                        model=model,
                        attr=self.name,
                    ) from exc

            if self.limit is not None and len(value) > self.limit:
                raise InvalidModelError(
                    "Invalid %(model)s: attribute %(attr)s is too long. Max length: %(limit)d",
                    model=model,
                    attr=self.name,
                    limit=self.limit,
                )

            if self.min is not None and value < self.min:
                raise InvalidModelError(
                    "Invalid %(model)s: attribute %(attr)s should be >= %(min)s",
                    model=model,
                    attr=self.name,
                    min=self.min,
                )

            if self.max is not None and value > self.max:
                raise InvalidModelError(
                    "Invalid %(model)s: attribute %(attr)s should be <= %(max)s",
                    model=model,
                    attr=self.name,
                    max=self.max,
                )

        setattr(instance, self.private_name, value)


class InvalidModelError(Exception):
    def __init__(self, fmt, **kwargs):
        super().__init__(fmt % kwargs)
        self.fmt = fmt
        self.kwargs = kwargs

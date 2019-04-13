from typing import Any, Mapping, Optional, Tuple, Type, Union

__all__ = [
    'Attribute',
    'InvalidModelError',
]


class Attribute:
    # noinspection PyShadowingBuiltins
    def __init__(self, *type: Optional[Union[Tuple[Type], Type]],
                 optional: bool = False, default: Any = None, limit: Optional[int] = None,
                 min: Any = None, max: Any = None):
        self._type = None
        self._optional = None
        self._limit = None
        self._min = None
        self._max = None
        self._name = None
        self._private_name = None

        self.type = type or None
        self.optional = optional
        self.default = default
        self.limit = limit
        self.min = min
        self.max = max

    @property
    def type(self) -> Optional[Type]:
        return self._type

    @type.setter
    def type(self, value: Optional[Union[Tuple[Type], Type]]):
        if value is not None:
            if not isinstance(value, tuple):
                value = value,

            if not all(isinstance(t, type) for t in value):
                raise TypeError(
                    "Invalid type: must be a type or tuple of types, not {}".format(value.__class__.__name__)
                )

        self._type = value

    @property
    def optional(self) -> bool:
        return self._optional

    @optional.setter
    def optional(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError("Invalid optional: must be bool, not {}".format(value.__class__.__name__))

        self._optional = value

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
        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        model = instance.__class__.__name__

        if value is None:
            if self._optional:
                value = self.default
            else:
                raise InvalidModelError(
                    "Invalid %(model)s: missing required attribute %(attr)s",
                    model=model,
                    attr=self._name,
                )
        else:
            if self._type is not None:
                for typ in self._type:
                    if isinstance(value, typ):
                        break

                    try:
                        value = typ(value)
                    except (TypeError, ValueError, InvalidModelError):
                        try:
                            if isinstance(value, Mapping):
                                value = typ(**value)
                            else:
                                value = typ(*value)
                        except (TypeError, ValueError):
                            pass
                        else:
                            break
                    else:
                        break
                else:
                    raise InvalidModelError(
                        "Invalid %(model)s: invalid attribute %(attr)s",
                        model=model,
                        attr=self._name,
                    )

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


class InvalidModelError(Exception):
    def __init__(self, fmt, **kwargs):
        super().__init__(fmt % kwargs)
        self.fmt = fmt
        self.kwargs = kwargs

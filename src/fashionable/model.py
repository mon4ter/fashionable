from collections import OrderedDict
from typing import Iterable, Mapping, Tuple, Union

from .attribute import Attribute, UNSET
from .modelerror import ModelError
from .validation import validate

__all__ = [
    'ModelMeta',
    'Model',
]


class ModelMeta(type):
    @classmethod
    def __prepare__(mcs, name, bases, **kwargs):
        return OrderedDict()

    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)

        slots = []
        attributes = [a for k in bases for a in getattr(k, '.attributes', ())]

        for attr_name, attr in namespace.items():
            if not isinstance(attr, Attribute):
                continue

            attr.name = attr_name
            slots.append(attr.private_name)

            if attr.name not in attributes:
                attributes.append(attr.name)

        cls.__slots__ = tuple(slots)
        setattr(cls, '.attributes', tuple(attributes))


class Model(metaclass=ModelMeta):
    def __init__(self, *args, **kwargs):
        attributes = getattr(self, '.attributes')

        for attr, value in zip(attributes, args):
            kwargs.setdefault(attr, value)

        lower_kwargs = {k.lower(): v for k, v in kwargs.items()}

        for attr in attributes:
            setattr(self, attr, kwargs.get(attr, lower_kwargs.get(attr.lower(), UNSET)))

    def __iter__(self):
        for attr in getattr(self, '.attributes'):
            value = getattr(self, attr)

            if value is not UNSET:
                yield attr, dict(value) if isinstance(value, Model) else value

    def __eq__(self, other: Union['Model', Mapping, Iterable, Tuple]):
        if not isinstance(other, Model):
            try:
                other = validate(self.__class__, other, strict=False)
            except (TypeError, ValueError, ModelError):
                return NotImplemented

        return dict(self) == dict(other)

    def __str__(self):
        id_ = self._id()
        return '{}({})'.format(self.__class__.__name__, '' if id_ is UNSET else id_)

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join('{}={!r}'.format(k, getattr(self, k)) for k, _ in self),
        )

    def _id(self):
        return next(iter(self))[1]

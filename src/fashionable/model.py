from collections import OrderedDict
from typing import Iterable, Mapping, Tuple, Union

from .attribute import Attribute
from .modelerror import ModelError
from .validate import validate

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
        attributes = [a for k in bases for a in getattr(k, '_attributes', ())]

        for attr_name, attr in namespace.items():
            if not isinstance(attr, Attribute):
                continue

            attr.name = attr_name
            slots.append(attr.private_name)

            if attr.name not in attributes:
                attributes.append(attr.name)

        cls.__slots__ = tuple(slots)
        cls._attributes = tuple(attributes)


class Model(metaclass=ModelMeta):
    def __init__(self, *args, **kwargs):
        for attr, value in zip(self._attributes, args):
            kwargs.setdefault(attr, value)

        lower_kwargs = {k.lower(): v for k, v in kwargs.items()}

        for attr in self._attributes:
            setattr(self, attr, kwargs.get(attr, lower_kwargs.get(attr.lower())))

    def __iter__(self):
        for attr in self._attributes:
            value = getattr(self, attr)

            if value is not None:
                yield attr, dict(value) if isinstance(value, Model) else value

    def __eq__(self, other: Union['Model', Mapping, Iterable, Tuple]):
        if not isinstance(other, Model):
            try:
                other = validate(self.__class__, other)
            except ModelError:
                return NotImplemented

        return dict(self) == dict(other)

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, self._id())

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, ', '.join('{}={!r}'.format(k, v) for k, v in self))

    def _id(self):
        return next(iter(self))[1]

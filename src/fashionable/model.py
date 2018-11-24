from collections import OrderedDict

from .attribute import Attribute

__all__ = [
    'ModelMeta',
    'Model',
]


class ModelMeta(type):
    @classmethod
    def __prepare__(mcs, name, bases, **kwargs):
        return OrderedDict()

    def __new__(mcs, name, bases, namespace):
        slots = []
        attributes = []

        for attr_name, attr in namespace.items():
            if not isinstance(attr, Attribute):
                continue

            attr.name = attr_name
            slots.append(attr.private_name)
            attributes.append(attr.name)

        namespace['__slots__'] = tuple(slots)
        klass = super().__new__(mcs, name, bases, namespace)
        klass._attributes = getattr(klass, '_attributes', ()) + tuple(attributes)
        return klass


class Model(metaclass=ModelMeta):
    def __init__(self, *args, **kwargs):
        for attr, value in zip(self._attributes, args):
            kwargs.setdefault(attr, value)

        for attr in self._attributes:
            setattr(self, attr, kwargs.get(attr))

    def __iter__(self):
        for attr in self._attributes:
            value = getattr(self, attr)

            if value is not None:
                yield attr, value

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, self._id())

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, ', '.join('{}={!r}'.format(k, v) for k, v in self))

    def _id(self):
        return next(iter(self))[1]

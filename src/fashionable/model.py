from copy import deepcopy
from sys import version_info
from typing import Any, Dict, Iterable, Mapping, Tuple, Union

from .attribute import Attribute, UNSET
from .modelerror import ModelError
from .validation import validate

__all__ = [
    'ModelMeta',
    'Model',
]


class ModelMeta(type):
    if version_info < (3, 7):
        @classmethod
        def __prepare__(mcs, *args, **kwargs):
            from collections import OrderedDict
            return OrderedDict()

    def __init__(cls, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any]):
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
    @classmethod
    def _to_dict(cls, obj: Any) -> dict:
        if hasattr(obj, 'to_dict'):
            obj = obj.to_dict()
        elif hasattr(obj, 'toDict'):
            obj = obj.toDict()
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
            obj = type(obj)(cls._to_dict(o) for o in (obj.items() if isinstance(obj, dict) else obj))

        return obj

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
                yield attr, value

    def __eq__(self, other: Union['Model', Mapping, Iterable, Tuple]):
        if not isinstance(other, type(self)):
            try:
                other = validate(type(self), other, strict=False)
            except (TypeError, ValueError, ModelError):
                return NotImplemented

        return all(getattr(other, attr) == getattr(self, attr) for attr in getattr(self, '.attributes'))

    def __str__(self):
        return '{}({})'.format(type(self).__name__, self._id())

    def __repr__(self):
        return '{}({})'.format(type(self).__name__, ', '.join('{}={!r}'.format(k, v) for k, v in self))

    def __copy__(self) -> 'Model':
        return type(self)(**dict(self))

    def __deepcopy__(self, *args, **kwargs) -> 'Model':
        return type(self)(**{k: deepcopy(v) for k, v in self})

    def _id(self):
        return getattr(self, getattr(self, '.attributes')[0])

    def to_dict(self) -> Dict[str, Any]:
        return {n: self._to_dict(v) for n, v in self}

    toDict = to_dict

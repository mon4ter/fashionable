from copy import deepcopy
from typing import Any, Dict, Iterable, Mapping, Tuple, Union

from .errors import ValidateError
from .modelmeta import ModelMeta
from .unset import UNSET
from .validation import validate

__all__ = [
    'Model',
]


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
            kwargs.setdefault(attr.name, value)

        for attr in attributes:
            name = attr.ciname or attr.name
            setattr(self, attr.name, next((v for k, v in kwargs.items() if name == k), UNSET))

    def __iter__(self):
        for attr in getattr(self, '.attributes'):
            value = getattr(self, attr.name)

            if value is not UNSET:
                yield attr.name, value

    def __eq__(self, other: Union['Model', Mapping, Iterable, Tuple]):
        if not isinstance(other, type(self)):
            try:
                other = validate(type(self), other, strict=False)
            except ValidateError:
                return NotImplemented

        return all(getattr(other, attr.name) == getattr(self, attr.name) for attr in getattr(self, '.attributes'))

    def __str__(self):
        return '{}({})'.format(type(self).__name__, self._id())

    def __repr__(self):
        return '{}({})'.format(type(self).__name__, ', '.join('{}={!r}'.format(k, v) for k, v in self))

    def __copy__(self) -> 'Model':
        return type(self)(**dict(self))

    def __deepcopy__(self, *args, **kwargs) -> 'Model':
        return type(self)(**{k: deepcopy(v) for k, v in self})

    def _id(self):
        return getattr(self, getattr(self, '.attributes')[0].name)

    def to_dict(self) -> Dict[str, Any]:
        return {n: self._to_dict(v) for n, v in self}

    toDict = to_dict

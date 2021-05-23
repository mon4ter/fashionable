from sys import version_info
from typing import Any, Dict, Tuple

from .baseattribute import BaseAttribute

__all__ = [
    'ModelMeta',
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
            if not isinstance(attr, BaseAttribute):
                continue

            attr.name = attr_name
            slots.append(attr.private_name)

            if attr not in attributes:
                attributes.append(attr)

        cls.__slots__ = tuple(slots)
        setattr(cls, '.attributes', tuple(attributes))

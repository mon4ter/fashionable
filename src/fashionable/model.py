from collections import OrderedDict

from .unset import UNSET
from .attribute import Attribute

__all__ = [
    'Model',
]


class _ModelMeta(type):
    @classmethod
    def __prepare__(mcs, name, bases, **kwargs):
        return OrderedDict()

    def __new__(mcs, name, bases, namespace):
        slots = []

        for attr_name, attr in namespace.copy().items():
            if attr.__class__ is not Attribute:
                continue

            private_name = '_p_' + attr_name

            def getter(self, pn=private_name):
                return getattr(self, pn, None)

            def setter(self, value, n=name, a=attr, an=attr_name, pn=private_name):
                if value is UNSET:
                    if a.default is UNSET:
                        fmt = "Invalid %(model)s: missing required attribute %(attr)s"
                        kwargs = {'model': n, 'attr': an}
                        raise ValueError(fmt % kwargs, fmt, kwargs)
                    else:
                        value = a.default
                else:
                    if a.type is not UNSET and not isinstance(value, a.type):
                        try:
                            value = a.type(value)
                        except (TypeError, ValueError) as exc:
                            fmt = "Invalid %(model)s: invalid attribute %(attr)s"
                            kwargs = {'model': n, 'attr': an}
                            raise ValueError(fmt % kwargs, fmt, kwargs) from exc

                    if a.limit is not UNSET and len(value) > a.limit:
                        fmt = "Invalid %(model)s: attribute %(attr)s is too long. Max length: %(limit)d"
                        kwargs = {'model': n, 'attr': an, 'limit': a.limit}
                        raise ValueError(fmt % kwargs, fmt, kwargs)

                    if a.min is not UNSET and value < a.min:
                        fmt = "Invalid %(model)s: attribute %(attr)s should be >= %(min)d"
                        kwargs = {'model': n, 'attr': an, 'min': a.min}
                        raise ValueError(fmt % kwargs, fmt, kwargs)

                    if a.max is not UNSET and value > a.max:
                        fmt = "Invalid %(model)s: attribute %(attr)s should be <= %(max)d"
                        kwargs = {'model': n, 'attr': an, 'max': a.max}
                        raise ValueError(fmt % kwargs, fmt, kwargs)

                setattr(self, pn, value)

            namespace[attr_name] = property(getter, setter)
            slots.append(private_name)

        namespace['__slots__'] = tuple(slots)
        return super().__new__(mcs, name, bases, namespace)


class Model(metaclass=_ModelMeta):
    def __init__(self, *args, **kwargs):
        attributes = [a[3:] for a in self.__slots__]

        for attr, value in zip(attributes, args):
            kwargs.setdefault(attr, value)

        for attr in attributes:
            setattr(self, attr, kwargs.get(attr, UNSET))

    def __iter__(self):
        for attr in self.__slots__:
            value = getattr(self, attr)

            if value is not UNSET:
                yield attr[3:], value

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, self._id())

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, ', '.join('{}={!r}'.format(k, v) for k, v in self))

    def _id(self):
        return next(iter(self))[1]

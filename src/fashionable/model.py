from collections import OrderedDict

from .attribute import Attribute

__all__ = [
    'ModelMeta',
    'Model',
    'InvalidModelError',
]


class ModelMeta(type):
    @classmethod
    def __prepare__(mcs, name, bases, **kwargs):
        return OrderedDict()

    def __new__(mcs, name, bases, namespace):
        slots = []
        attributes = []

        for attr_name, attr in namespace.copy().items():
            if attr.__class__ is not Attribute:
                continue

            private_name = '_m_' + attr_name

            def getter(self, pn=private_name):
                return getattr(self, pn)

            def setter(self, value, n=name, a=attr, an=attr_name, pn=private_name):
                if value is None:
                    if a.optional:
                        value = a.default
                    else:
                        raise InvalidModelError(
                            "Invalid %(model)s: missing required attribute %(attr)s",
                            model=n,
                            attr=an,
                        )
                else:
                    if a.type is not None and not isinstance(value, a.type):
                        try:
                            value = a.type(value)
                        except (TypeError, ValueError) as exc:
                            raise InvalidModelError(
                                "Invalid %(model)s: invalid attribute %(attr)s",
                                model=n,
                                attr=an,
                            ) from exc

                    if a.limit is not None and len(value) > a.limit:
                        raise InvalidModelError(
                            "Invalid %(model)s: attribute %(attr)s is too long. Max length: %(limit)d",
                            model=n,
                            attr=an,
                            limit=a.limit,
                        )

                    if a.min is not None and value < a.min:
                        raise InvalidModelError(
                            "Invalid %(model)s: attribute %(attr)s should be >= %(min)d",
                            model=n,
                            attr=an,
                            min=a.min,
                        )

                    if a.max is not None and value > a.max:
                        raise ValueError(
                            "Invalid %(model)s: attribute %(attr)s should be <= %(max)d",
                            model=n,
                            attr=an,
                            max=a.max,
                        )

                setattr(self, pn, value)

            namespace[attr_name] = property(getter, setter)
            slots.append(private_name)
            attributes.append(attr_name)

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


class InvalidModelError(Exception):
    def __init__(self, fmt, **kwargs):
        super().__init__(fmt % kwargs)
        self.fmt = fmt
        self.kwargs = kwargs

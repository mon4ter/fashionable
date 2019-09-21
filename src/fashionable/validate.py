from functools import lru_cache
from itertools import chain, product, repeat
from typing import Any, Iterable, Mapping, Tuple, Type, Union

from .types import AnyType, TypingMeta

__all__ = [
    'validate',
]


@lru_cache()
def _isinstance(typ: Union[Type, TypingMeta], types: Union[TypingMeta, Tuple[TypingMeta]]) -> bool:
    if not hasattr(typ, '__origin__'):
        return False

    if not isinstance(types, tuple):
        types = (types,)

    return any(
        typ.__origin__ is t for t in types
    ) or any(
        _isinstance(t, types) for t in getattr(typ, '__orig_bases__', ())
    )


def _validate_union(typ: TypingMeta, value: Any, strict: bool) -> Any:
    for strict, element_type in product(range(1, strict - 1, -1), typ.__args__):
        try:
            return _validate(element_type, value, strict)
        except (TypeError, ValueError):
            pass
    else:
        # TODO test invalid Union
        raise TypeError


def _validate_mapping(typ: TypingMeta, mapping: Union[Mapping, Iterable], strict: bool) -> Mapping:
    if not isinstance(mapping, (Mapping, Iterable)):
        # TODO test invalid Mapping
        raise TypeError

    mapping_type = typ.__extra__
    key_type, value_type = typ.__args__

    return mapping_type(
        (_validate(key_type, k, strict), _validate(value_type, v, strict))
        for k, v in (mapping.items() if isinstance(mapping, Mapping) else mapping)
    )


def _validate_iterable(typ: TypingMeta, iterable: Iterable, strict: bool) -> Iterable:
    if not isinstance(iterable, Iterable):
        # TODO test invalid Iterable
        raise TypeError

    iterable_type = typ.__extra__
    element_type = typ.__args__[0]

    return iterable_type(_validate(element_type, e, strict) for e in iterable)


def _validate_tuple(typ: TypingMeta, tpl: Union[Tuple, Iterable], strict: bool):
    if not isinstance(tpl, (Tuple, Iterable)):
        raise TypeError

    tuple_type = typ.__extra__
    filled_tuple = chain(tpl, repeat(None))

    return tuple_type(_validate(et, e, strict) for et, e in zip(typ.__args__, filled_tuple))


def _validate(typ: Union[Type, TypingMeta], value: Any, strict: bool) -> Any:
    if hasattr(typ, '__supertype__'):
        typ = typ.__supertype__

    if isinstance(typ, AnyType):
        pass
    elif _isinstance(typ, Union):
        value = _validate_union(typ, value, strict)
    elif _isinstance(typ, Mapping):
        value = _validate_mapping(typ, value, strict)
    elif _isinstance(typ, Iterable):
        value = _validate_iterable(typ, value, strict)
    elif _isinstance(typ, Tuple):
        value = _validate_tuple(typ, value, strict)
    elif not isinstance(value, typ):
        if strict:
            raise TypeError

        try:
            value = typ(value)
        except (TypeError, ValueError):
            if isinstance(value, Mapping):
                value = typ(**value)
            elif isinstance(value, (Iterable, tuple)):
                value = typ(*value)
            else:
                raise

    return value


def validate(typ: Union[Type, TypingMeta], value: Any, strict: bool = False) -> Any:
    try:
        return _validate(typ, value, strict)
    except TypeError as err:
        raise TypeError("must be {}, not {}".format(typ, type(value))) from err

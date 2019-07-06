from functools import lru_cache
from itertools import chain, product, repeat
from typing import Any, Iterable, Mapping, Tuple, Type, Union

__all__ = [
    'TypingMeta',
    'validate',
]

AnyType = type(Any)
TypingMeta = type(AnyType)
NoneType = type(None)


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


def _validate_union(typ: TypingMeta, value: Any) -> Any:
    for convert, element_type in product((False, True), typ.__args__):
        try:
            return validate(element_type, value, convert=convert)
        except (TypeError, ValueError):
            pass
    else:
        raise ValueError


def _validate_mapping(typ: TypingMeta, mapping: Union[Mapping, Iterable]) -> Mapping:
    if not isinstance(mapping, (Mapping, Iterable)):
        raise TypeError

    mapping_type = typ.__extra__
    key_type, value_type = typ.__args__

    return mapping_type(
        (validate(key_type, k), validate(value_type, v))
        for k, v in (mapping.items() if isinstance(mapping, Mapping) else mapping)
    )


def _validate_iterable(typ: TypingMeta, iterable: Iterable) -> Iterable:
    if not isinstance(iterable, Iterable):
        raise TypeError

    iterable_type = typ.__extra__
    element_type = typ.__args__[0]

    return iterable_type(validate(element_type, e) for e in iterable)


def _validate_tuple(typ: TypingMeta, tpl: Union[Tuple, Iterable]):
    if not isinstance(tpl, (Tuple, Iterable)):
        raise TypeError

    tuple_type = typ.__extra__
    filled_tuple = chain(tpl, repeat(None))

    return tuple_type(validate(et, e) for et, e in zip(typ.__args__, filled_tuple))


def validate(typ: Union[Type, TypingMeta], value: Any, *, convert: bool = True) -> Any:
    if hasattr(typ, '__supertype__'):
        typ = typ.__supertype__

    if isinstance(typ, AnyType):
        pass
    elif _isinstance(typ, Union):
        value = _validate_union(typ, value)
    elif _isinstance(typ, Mapping):
        value = _validate_mapping(typ, value)
    elif _isinstance(typ, Iterable):
        value = _validate_iterable(typ, value)
    elif _isinstance(typ, Tuple):
        value = _validate_tuple(typ, value)
    elif not isinstance(value, typ):
        if not convert:
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

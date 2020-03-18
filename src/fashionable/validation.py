from functools import lru_cache
from itertools import chain, product, repeat
from sys import version_info
from typing import Any, Dict, Iterable, List, Mapping, Set, Tuple, Union

__all__ = [
    'AnyType',
    'validate',
]

if version_info >= (3, 7):
    AnyType = Union[type, type(Union), type(Iterable)]
else:
    # TODO Real AnyType
    AnyType = Any


def _get_origin(typ: AnyType) -> AnyType:
    return getattr(typ, '__origin__', None) or typ


def _get_extra(typ: AnyType) -> AnyType:
    return getattr(typ, '__extra__', _get_origin(typ))


@lru_cache()
def _isinstance(value: AnyType, types: Tuple[AnyType, ...]) -> bool:
    origin = _get_origin(value)
    return any(_get_origin(t) == origin for t in types)


def _validate_union(typ: AnyType, value: Any, strict: bool) -> Any:
    for strict, element_type in product(range(1, strict - 1, -1), typ.__args__):
        try:
            return _validate(element_type, value, strict)
        except (TypeError, ValueError):
            pass
    else:
        raise TypeError


def _validate_mapping(typ: AnyType, mapping: Union[Mapping, Iterable], strict: bool) -> Mapping:
    if not isinstance(mapping, (Mapping, Iterable)):
        raise TypeError

    mapping_type = _get_extra(typ)
    key_type, value_type = typ.__args__

    return mapping_type(
        (_validate(key_type, k, strict), _validate(value_type, v, strict))
        for k, v in (mapping.items() if isinstance(mapping, Mapping) else mapping)
    )


def _validate_iterable(typ: AnyType, iterable: Iterable, strict: bool) -> Iterable:
    if not isinstance(iterable, Iterable):
        raise TypeError

    iterable_type = _get_extra(typ)
    element_type = typ.__args__[0]

    return iterable_type(_validate(element_type, e, strict) for e in iterable)


def _validate_tuple(typ: AnyType, tpl: Union[Tuple, Iterable], strict: bool):
    if not isinstance(tpl, (Tuple, Iterable)):
        raise TypeError

    tuple_type = _get_extra(typ)
    filled_tuple = chain(tpl, repeat(None))

    return tuple_type(_validate(et, e, strict) for et, e in zip(typ.__args__, filled_tuple))


def _validate(typ: AnyType, value: Any, strict: bool) -> Any:
    if hasattr(typ, '__supertype__'):
        typ = typ.__supertype__

    if typ is Any:
        pass
    elif _isinstance(typ, (Union,)):
        value = _validate_union(typ, value, strict)
    elif _isinstance(typ, (Mapping, Dict)):
        value = _validate_mapping(typ, value, strict)
    elif _isinstance(typ, (Iterable, List, Set)):
        value = _validate_iterable(typ, value, strict)
    elif _isinstance(typ, (Tuple,)):
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


def validate(typ: AnyType, value: Any, strict: bool = False) -> Any:
    try:
        return _validate(typ, value, strict)
    except TypeError as err:
        raise TypeError("must be {}, not {}".format(typ, type(value))) from err

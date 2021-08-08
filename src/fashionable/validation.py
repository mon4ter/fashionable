from functools import lru_cache
from itertools import chain, product, repeat
from logging import getLogger
from typing import Any, Dict, Iterable, List, Mapping, Set, Tuple, Type, Union

from .errors import ValidateError
from .typedef import Typing
from .unset import UNSET

__all__ = [
    'validate',
]

logger = getLogger(__name__)
NoneType = type(None)


def _get_origin(typ: Typing) -> Typing:
    return getattr(typ, '__origin__', None) or typ


def _get_extra(typ: Typing) -> Typing:
    return getattr(typ, '__extra__', _get_origin(typ))


@lru_cache()
def _isinstance(value: Typing, types: Tuple[Typing, ...]) -> bool:
    origin = _get_origin(value)

    if origin is value:
        return value is Any

    return any(_get_origin(t) == origin for t in types)


def _is_tuple(obj: Any) -> bool:
    return isinstance(obj, (Tuple, Iterable))


def _validate_union(typ: Typing, value: Any, strict: bool) -> Any:
    last = TypeError

    for strict, element_type in product(range(1, strict - 1, -1), typ.__args__):
        try:
            return _validate(element_type, value, strict)
        except ValidateError as exc:
            last = exc
    else:
        raise last


def _validate_mapping(typ: Typing, mapping: Union[Mapping, Iterable], strict: bool) -> Mapping:
    if not isinstance(mapping, (Mapping, Iterable)):
        raise TypeError

    mapping_type = _get_extra(typ)
    key_type, value_type = typ.__args__

    return mapping_type(
        (_validate(key_type, k, strict), _validate(value_type, v, strict))
        for k, v in (mapping.items() if isinstance(mapping, Mapping) else mapping)
    )


def _validate_iterable(typ: Typing, iterable: Iterable, strict: bool) -> Iterable:
    if not isinstance(iterable, Iterable):
        raise TypeError

    iterable_type = _get_extra(typ)
    element_type = typ.__args__[0]

    return iterable_type(_validate(element_type, e, strict) for e in iterable)


def _validate_tuple(typ: Typing, tpl: Union[Tuple, Iterable], strict: bool) -> Tuple:
    if not _is_tuple(tpl):
        raise TypeError

    tuple_type = _get_extra(typ)
    filled_tuple = chain(tpl, repeat(None))

    return tuple_type(_validate(et, e, strict) for et, e in zip(typ.__args__, filled_tuple))


def _validate(typ: Typing, value: Any, strict: bool) -> Any:
    unset = value is UNSET

    if hasattr(typ, '__supertype__'):
        typ = typ.__supertype__

    if typ is Any or unset and typ is NoneType or _isinstance(typ, (Type,)) and _isinstance(value, (typ.__args__[0],)):
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
        if unset:
            raise AttributeError

        if strict:
            raise TypeError

        try:
            value = typ(value)
        except ValidateError:
            if isinstance(value, Mapping):
                value = typ(**value)
            elif _is_tuple(value):
                if len(value) == 2 and _is_tuple(value[0]) and isinstance(value[1], Mapping):
                    value = typ(*value[0], **value[1])
                else:
                    value = typ(*value)
            else:
                raise

    return value


def validate(typ: Typing, value: Any, strict: bool = False) -> Any:
    try:
        return _validate(typ, value, strict)
    except TypeError as exc:
        err = TypeError("must be {}, not {}".format(typ, type(value)))
        logger.debug("%s(%s, %s, %s): %s", validate.__name__, typ, value, strict, exc)
        raise err from exc

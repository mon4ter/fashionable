from sys import version_info
from typing import Any, Coroutine, Dict, Iterable, Mapping, Optional, Tuple, Type, TypeVar, Union

from .unset import Unset

__all__ = [
    'Args',
    'AsyncRet',
    'Kwargs',
    'Limiter',
    'OptionalTyping',
    'Predefined',
    'Ret',
    'T',
    'Typing',
    'Value',
]

T = TypeVar('T')
Value = Union[T, Unset]
Limiter = Union[int, Value]
AsyncRet = Coroutine[T, None, None]
Ret = Union[T, AsyncRet]
Args = Tuple[Value, ...]
Kwargs = Dict[str, Value]


if version_info >= (3, 9):
    Typing = Union[type, type(Optional[int]).__base__.__base__, type(Any)]
elif version_info >= (3, 7):
    Typing = Union[type, type(Union), type(Iterable)]
else:
    Typing = Union[type, Type[Any], Type[Optional[T]], Type[Mapping], Type[Tuple]]

OptionalTyping = Union[Typing, Unset]
Predefined = Dict[Typing, Value]

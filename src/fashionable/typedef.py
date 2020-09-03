from sys import version_info
from typing import Any, Iterable, Mapping, Optional, Tuple, Type, TypeVar, Union

from .unset import Unset

__all__ = [
    'Limiter',
    'Typing',
    'Value',
]

T = TypeVar('T')
Value = Union[T, Unset]
Limiter = Union[int, Value]

if version_info >= (3, 7):
    Typing = Union[type, type(Union), type(Iterable)]
else:
    Typing = Union[type, Type[Any], Type[Optional[T]], Type[Mapping], Type[Tuple]]

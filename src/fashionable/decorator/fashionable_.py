from typing import Callable, Optional, Union, overload

from .func import Func
from ..typedef import Typing

__all__ = [
    'fashionable',
]


@overload
def fashionable(func: Callable) -> Func:
    ...  # pragma: no cover


@overload
def fashionable(
        name_: Optional[str] = None,
        case_insensitive_: bool = True,
        **annotations: Typing
) -> Callable[[Callable], Func]:
    ...  # pragma: no cover


def fashionable(
        name_: Union[Optional[str], Callable] = None,
        case_insensitive_: bool = True,
        **annotations: Typing
) -> Callable[[Callable], Func]:
    if isinstance(name_, Callable):
        return fashionable()(name_)

    def deco(func: Callable) -> Func:
        return Func.fashionable(func, name_, case_insensitive_, annotations)

    return deco

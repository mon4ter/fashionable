from typing import Callable, Optional, Union

from .func import Func
from ..typedef import Typing

__all__ = [
    'fashionable',
]


def fashionable(name_: Union[Optional[str], Callable] = None, **annotations: Typing) -> Callable:
    if isinstance(name_, Callable):
        return fashionable()(name_)

    def deco(func: Callable) -> Func:
        return Func.fashionable(func, name_, annotations)

    return deco

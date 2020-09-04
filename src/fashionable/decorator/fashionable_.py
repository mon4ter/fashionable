from typing import Callable, Optional

from .func import Func

__all__ = [
    'fashionable',
]


def fashionable(name_: Optional[str] = None, **annotations: type) -> Callable:
    if isinstance(name_, Callable):
        return fashionable()(name_)

    def deco(func: Callable) -> Func:
        return Func.from_inspect(func, name_, annotations)

    return deco

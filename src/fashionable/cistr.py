from re import compile as re_compile
from typing import Iterator

__all__ = [
    'CIStr',
]


class CIStr(str):
    __slots__ = '_cases',

    _word = re_compile(r'[A-Za-z]+?(?:(?=[-_])|(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)')
    _sep = '_', '-', ''

    def __new__(cls, *args, **kwargs) -> 'CIStr':
        self = super().__new__(cls, *args, **kwargs)
        words = cls._word.findall(self)
        self._cases = tuple(s.join(w.lower() for w in words) for s in cls._sep)
        return self

    def __eq__(self, other):
        eq = super().__eq__(other)

        if eq is False:
            lower = other.lower() if isinstance(other, str) else other
            eq = any(c == lower for c in self._cases)

        return eq

    def cases(self) -> Iterator[str]:
        yield from self._cases

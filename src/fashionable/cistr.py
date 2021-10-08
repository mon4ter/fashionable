from re import compile as re_compile
from typing import Iterator

__all__ = [
    'CIStr',
]


class CIStr(str):
    __slots__ = ('_cases', '_hash')

    _word = re_compile(r'[A-Za-z]+?(?:(?=[-_])|(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)')

    def __new__(cls, *args, **kwargs) -> 'CIStr':
        self = super().__new__(cls, *args, **kwargs)
        words = cls._word.findall(self)
        self._cases = (
            '_'.join(w.lower() for w in words),
            '-'.join(w.lower() for w in words),
            ''.join(w.lower().capitalize() if i else w.lower() for i, w in enumerate(words))
        )
        self._hash = hash(''.join(sorted(case.lower() for case in self._cases)))
        return self

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other):
        eq = super().__eq__(other)

        if eq is False:
            if not isinstance(other, type(self)) and isinstance(other, str):
                other = CIStr(other)

            eq = hash(self) == hash(other)

        return eq

    def cases(self) -> Iterator[str]:
        yield from self._cases

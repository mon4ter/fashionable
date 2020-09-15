from inspect import Parameter
from sys import version_info

__all__ = [
    'Arg',
]


class Arg(Parameter):
    _POSITIONAL_KINDS = {Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD, Parameter.VAR_POSITIONAL}
    _ZIPPED_KINDS = {Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD}

    @property
    def is_positional(self) -> bool:
        return self.kind in self._POSITIONAL_KINDS

    @property
    def is_zipped(self) -> bool:
        return self.kind in self._ZIPPED_KINDS

    if version_info < (3, 7):
        def __str__(self) -> str:
            return super().__str__().replace(':', ': ')

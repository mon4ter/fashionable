from inspect import Parameter

from ..errors import InvalidArgError, MissingArgError, ValidateError
from ..typedef import Value
from ..unset import UNSET
from ..validation import validate

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

    def validate(self, value: Value) -> Value:
        if value is UNSET:
            if self.default is Parameter.empty:
                raise MissingArgError(func=..., arg=self.name)
            else:
                value = self.default
        elif self.annotation is not Parameter.empty:
            try:
                value = validate(self.annotation, value)
            except ValidateError as exc:
                raise InvalidArgError(func=..., arg=self.name) from exc

        return value

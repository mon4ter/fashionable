from typing import Type

from .baseattribute import BaseAttribute
from .errors import ModelAttributeError, ModelTypeError, ModelValueError, ValidateError
from .model import Model
from .typedef import Value
from .unset import UNSET
from .validation import validate

__all__ = [
    'Attribute',
]


class Attribute(BaseAttribute):
    def __get__(self, model: Model, owner: Type[Model]) -> Value:
        return getattr(model, self._private_name)

    def __set__(self, model: Model, value: Value):
        if value is UNSET and self._default is not UNSET:
            value = self._default
        else:
            try:
                value = validate(self.type, value, self.strict)
            except ValidateError as exc:
                if isinstance(exc, AttributeError):
                    err_type = ModelAttributeError
                elif isinstance(exc, ValueError):
                    err_type = ModelValueError
                else:
                    err_type = ModelTypeError

                raise err_type(model=type(model).__name__, attr=self.name) from exc

        iterable = hasattr(value, '__iter__')

        if self._min is not UNSET and (len(value) if iterable else value) < self._min:
            raise ModelValueError(
                "{}should be >= %(min)s".format('length ' * iterable),
                model=type(model).__name__,
                attr=self.name,
                min=self._min,
            )

        if self._max is not UNSET and (len(value) if iterable else value) > self._max:
            raise ModelValueError(
                "{}should be <= %(max)s".format('length ' * iterable),
                model=type(model).__name__,
                attr=self.name,
                max=self._max,
            )

        setattr(model, self._private_name, value)

    def __delete__(self, model: Model):
        self.__set__(model, self.default)

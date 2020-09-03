from typing import Type

from .baseattribute import BaseAttribute
from .model import Model
from .modelerror import ModelAttributeError, ModelError, ModelTypeError, ModelValueError
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
        unset = value is UNSET

        try:
            value = validate(self.type, None if unset else value, self.strict)
        except Exception as exc:
            if unset or isinstance(exc, AttributeError):
                err = "missing required attribute %(attr)s"
                err_type = ModelAttributeError
            elif isinstance(exc, ValueError):
                err = "invalid value of attribute %(attr)s"
                err_type = ModelTypeError
            elif isinstance(exc, TypeError):
                err = "=invalid type of attribute %(attr)s"
                err_type = ModelTypeError
            else:
                err = "invalid attribute %(attr)s"
                err_type = ModelError

            raise err_type("Invalid %(model)s: " + err, model=type(model).__name__, attr=self._name) from exc

        if unset:
            value = self.default

        iterable = hasattr(value, '__iter__')

        if self._min is not UNSET and (len(value) if iterable else value) < self._min:
            raise ModelValueError(
                "Invalid %(model)s: attribute %(attr)s: {}should be >= %(min)s".format('length ' * iterable),
                model=type(model).__name__,
                attr=self._name,
                min=self._min,
            )

        if self._max is not UNSET and (len(value) if iterable else value) > self._max:
            raise ModelValueError(
                "Invalid %(model)s: attribute %(attr)s: {}should be <= %(max)s".format('length ' * iterable),
                model=type(model).__name__,
                attr=self._name,
                max=self._max,
            )

        setattr(model, self._private_name, value)

    def __delete__(self, model: Model):
        self.__set__(model, self.default)

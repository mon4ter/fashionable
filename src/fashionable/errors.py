__all__ = [
    'FashionableError',
    'ModelAttributeError',
    'ModelError',
    'ModelTypeError',
    'ModelValueError',
    'ValidateError',
]


ValidateError = TypeError, ValueError, AttributeError


class FashionableError(Exception):
    @staticmethod
    def _concat(fmt: str, suffix: str) -> str:
        return '{}{}{}'.format(fmt, ': ' * bool(suffix), suffix)

    def __init__(self, fmt: str, **kwargs):
        super().__init__(fmt % kwargs)
        self.fmt = fmt
        self.kwargs = kwargs


class ModelError(FashionableError):
    def __init__(self, suffix: str = '', *, model: str, **kwargs):
        super().__init__(self._concat("Invalid %(model)s", suffix), model=model, **kwargs)


class ModelTypeError(ModelError, TypeError):
    def __init__(self, suffix: str = '', *, attr: str, **kwargs):
        super().__init__(self._concat("invalid type of attribute %(attr)s", suffix), attr=attr, **kwargs)


class ModelValueError(ModelError, ValueError):
    def __init__(self, suffix: str = '', *, attr: str, **kwargs):
        super().__init__(self._concat("invalid value of attribute %(attr)s", suffix), attr=attr, **kwargs)


class ModelAttributeError(ModelError, AttributeError):
    def __init__(self, suffix: str = '', *, attr: str, **kwargs):
        super().__init__(self._concat("missing required attribute %(attr)s", suffix), attr=attr, **kwargs)


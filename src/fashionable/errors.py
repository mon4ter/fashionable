__all__ = [
    'ArgError',
    'FashionableError',
    'InvalidArgError',
    'MissingArgError',
    'ModelAttributeError',
    'ModelError',
    'ModelTypeError',
    'ModelValueError',
    'RetError',
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


class FuncError(FashionableError):
    def __init__(self, suffix: str = '', *, func: str, **kwargs):
        super().__init__(self._concat("Invalid usage of %(func)s", suffix), func=func, **kwargs)


class ArgError(FuncError):
    pass


class MissingArgError(ArgError):
    def __init__(self, suffix: str = '', *, arg: str, **kwargs):
        super().__init__(self._concat("missing required argument %(arg)s", suffix), arg=arg, **kwargs)


class InvalidArgError(ArgError):
    def __init__(self, suffix: str = '', *, arg: str, **kwargs):
        super().__init__(self._concat("invalid argument %(arg)s value", suffix), arg=arg, **kwargs)


class RetError(FuncError):
    def __init__(self, suffix: str = '', **kwargs):
        super().__init__(self._concat("invalid return value", suffix), **kwargs)

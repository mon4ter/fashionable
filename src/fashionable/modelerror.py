__all__ = [
    'InvalidModelError',
    'ModelAttributeError',
    'ModelError',
    'ModelTypeError',
    'ModelValueError',
]


class ModelError(Exception):
    def __init__(self, fmt, **kwargs):
        super().__init__(fmt % kwargs)
        self.fmt = fmt
        self.kwargs = kwargs


InvalidModelError = ModelError


class ModelTypeError(ModelError, TypeError):
    pass


class ModelValueError(ModelError, ValueError):
    pass


class ModelAttributeError(ModelError, AttributeError):
    pass

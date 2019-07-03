__all__ = [
    'InvalidModelError',
]


class InvalidModelError(Exception):
    def __init__(self, fmt, **kwargs):
        super().__init__(fmt % kwargs)
        self.fmt = fmt
        self.kwargs = kwargs

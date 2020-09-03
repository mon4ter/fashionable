__all__ = [
    'UNSET',
    'Unset',
]


class Unset:
    def __new__(cls):
        if not hasattr(cls, '.instance'):
            setattr(cls, '.instance', super().__new__(cls))

        return getattr(cls, '.instance')

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return 'UNSET'


UNSET = Unset()

__all__ = [
    'UNSET',
    'Unset',
]


class Unset:
    def __new__(cls):
        attr = '.instance'

        if not hasattr(cls, attr):
            setattr(cls, attr, super().__new__(cls))

        return getattr(cls, attr)

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return 'UNSET'


UNSET = Unset()

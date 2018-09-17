from .attribute import Attribute
from .model import Model
from .supermodel import Supermodel

__version__ = '0.1.0'
__all__ = [
    'Attribute',
    'Model',
    'Supermodel',
]

# Space is required to prevent string interning
UNSET = 'UNSET '

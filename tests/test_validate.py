from typing import Any, Dict, List, Mapping, NewType, Optional, Set, Tuple, Type, TypeVar, Union

from pytest import mark, raises

from fashionable import Attribute, Model, validate
from fashionable.typedef import Typing

Bool = NewType('Bool', bool)  # Because Union[float, int, bool] shrinks to Union[float, int]
T = TypeVar('T')


class Pair:
    def __init__(self, a: int, b: int):
        self.a = a
        self.b = b

    def __iter__(self):
        yield 'a', self.a
        yield 'b', self.b


class C(Model):
    x = Attribute(float)
    y = Attribute(float)


class Params(Model):
    a = Attribute(str)
    b = Attribute(Optional[int])
    c = Attribute(C)


@mark.parametrize('typ, value, result', [
    (int,                             4,                                      4),
    (int,                             '4',                                    4),
    (List[int],                       [2, 2, 3],                              [2, 2, 3]),
    (List[int],                       (2, 2, 3),                              [2, 2, 3]),
    (List[int],                       ('2', '2', '3'),                        [2, 2, 3]),
    (List[int],                       range(3),                               [0, 1, 2]),
    (List[int],                       '567',                                  [5, 6, 7]),
    (List[int],                       (e for e in '567'),                     [5, 6, 7]),
    (Set[int],                        ('2', '2', '3'),                        {2, 2, 3}),
    (Tuple[int, int, int],            ['2', '2', '3'],                        (2, 2, 3)),
    (Optional[int],                   3,                                      3),
    (Optional[str],                   None,                                   None),
    (Optional[int],                   '3',                                    3),
    (Optional[int],                   None,                                   None),
    (Optional[Tuple[int, int, int]],  ['2', '2', '3'],                        (2, 2, 3)),
    (Optional[Tuple[int, int, int]],  None,                                   None),
    (Union[Bool, int],                True,                                   True),
    (Union[Bool, int],                1,                                      1),
    (Union[Bool, int],                '0',                                    True),
    (Union[float, int, Bool],         1.0,                                    1.0),
    (Union[float, int, Bool],         1,                                      1),
    (Union[float, int, Bool],         True,                                   True),
    (Union[float, int, Bool],         '1',                                    1.0),
    (Union[float, int, Bool],         'a',                                    True),
    (Optional[Union[Bool, int]],      '0',                                    True),
    (Dict[int, Tuple[int, int]],      {'1': ['1', '2'], '2': ['3', '4']},     {1: (1, 2), 2: (3, 4)}),
    (Dict[int, Tuple[int, int]],      [['1', ['1', '2']], ['2', ['3', '4']]], {1: (1, 2), 2: (3, 4)}),
    (Tuple[int, str, Optional[Bool]], ['2', '2', '3'],                        (2, '2', True)),
    (Tuple[int, str, Optional[Bool]], ['2', '2'],                             (2, '2', None)),
    (Tuple[int, str, Optional[Bool]], ['2', '2'],                             (2, '2', None)),
    (List[Tuple[int, int]],           [['1', '2'], ['3', '4']],               [(1, 2), (3, 4)]),
    (Any,                             [['1', '2'], ['3', '4']],               [['1', '2'], ['3', '4']]),
    (Type[Optional[T]],               Optional[str],                          Optional[str]),
    (Typing,                          int,                                    int),
    (Typing,                          Optional[str],                          Optional[str]),
    (Typing,                          Mapping[str, int],                      Mapping[str, int]),
    (Typing,                          Any,                                    Any),
    (dict,                            Pair(1, 2),                             {'a': 1, 'b': 2}),
    (Params,                          [1, 2, [3, 4]],                         Params('1', 2, C(3.0, 4.0))),
    (Params,                          {'a': 1, 'c': {'x': 2, 'y': 3}},        Params('1', c=C(2.0, 3.0))),
])
def test_validate(typ, value, result):
    assert validate(typ, value) == result


@mark.parametrize('typ, value, exc', [
    (int,               'a',        ValueError),
    (Union[float, int], 'a',        TypeError),
    (Dict[str, int],    True,       TypeError),
    (Dict[str, int],    'a',        ValueError),
    (Dict[str, int],    {'a': 'a'}, ValueError),
    (List[int],         True,       TypeError),
    (List[int],         ['a'],      ValueError),
])
def test_fail(typ, value, exc):
    with raises(exc):
        validate(typ, value)

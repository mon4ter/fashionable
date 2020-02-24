from typing import Dict, List, NewType, Optional, Set, Tuple, Union, Any

from pytest import mark

from fashionable import validate

# Because Union[float, int, bool] shrinks to Union[float, int]
Bool = NewType('Bool', bool)


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
])
def test_validate(typ, value, result):
    assert validate(typ, value) == result

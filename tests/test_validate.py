from typing import List, Optional, Tuple, Set, Union, Dict

from pytest import mark

from fashionable.validate import validate


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
    (Union[bool, int],                True,                                   True),
    (Union[bool, int],                1,                                      1),
    (Union[bool, int],                '0',                                    False),
    (Optional[Union[bool, int]],      '0',                                    False),
    (Dict[int, Tuple[int, int]],      {'1': ['1', '2'], '2': ['3', '4']},     {1: (1, 2), 2: (3, 4)}),
    (Dict[int, Tuple[int, int]],      [['1', ['1', '2']], ['2', ['3', '4']]], {1: (1, 2), 2: (3, 4)}),
    (Tuple[int, str, Optional[bool]], ['2', '2', '3'],                        (2, '2', True)),
    (Tuple[int, str, Optional[bool]], ['2', '2'],                             (2, '2', None)),
    (Tuple[int, str, Optional[bool]], ['2', '2'],                             (2, '2', None)),
    (List[Tuple[int, int]],           [['1', '2'], ['3', '4']],               [(1, 2), (3, 4)]),
])
def test_validate(typ, value, result):
    assert validate(typ, value) == result

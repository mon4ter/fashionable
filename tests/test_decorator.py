import datetime
import decimal
import pathlib
from typing import Dict, Optional, Set, Tuple

from pytest import mark, raises

from fashionable import Attribute, InvalidArgError, MissingArgError, Model, RetError, fashionable


def test_no_parenthesis():
    def f():
        pass

    assert fashionable(f).func is fashionable()(f).func


def test_empty():
    @fashionable
    def empty():
        return

    assert empty() is None
    assert str(empty) == 'empty()'


def test_arg():
    @fashionable
    def arg(x):
        return x

    assert arg('x') == 'x'
    assert str(arg) == 'arg(x)'


def test_kwarg():
    @fashionable
    def kwarg(*, y):
        return y

    assert kwarg(y='y') == 'y'
    assert str(kwarg) == 'kwarg(*, y)'


def test_vararg():
    @fashionable
    def vararg(*varargs):
        return varargs

    assert vararg(1, 2, 3) == (1, 2, 3)
    assert str(vararg) == 'vararg(*varargs)'


def test_varkw():
    @fashionable
    def varkw(**keywords):
        return keywords

    assert varkw(a=1, b=2) == {'a': 1, 'b': 2}
    assert str(varkw) == 'varkw(**keywords)'


def test_all_in():
    @fashionable
    def all_in(x, *args, y, **kwargs):
        return x, args, y, kwargs

    assert all_in(1, 2, x=3, y=4, z=5) == (3, (1, 2), 4, {'z': 5})
    assert str(all_in) == 'all_in(x, *args, y, **kwargs)'


def test_default():
    @fashionable
    def default(a='a', *, b='b'):
        return a + b

    assert default() == 'ab'
    assert default('c') == 'cb'
    assert default('c', 'd') == 'cd'
    assert str(default) == "default(a='a', *, b='b')"


def test_simple_annotations():
    @fashionable
    def simple_annotations(a: int, *b: str, c: list, **d: set):
        return a, b[0], c, next(iter(d.values()))

    # noinspection PyTypeChecker
    assert simple_annotations('1', 2, c='3', x='4') == (1, '2', ['3'], {'4'})
    assert str(simple_annotations) == 'simple_annotations(a: int, *b: str, c: list, **d: set)'


def test_complex_annotations():
    @fashionable
    def complex_annotations(
            a: Dict[str, Tuple[float, float]],
            *b: decimal.Decimal,
            c: Set[datetime.datetime],
            **d: pathlib.Path
    ):
        return a, b, c, d

    # noinspection PyTypeChecker
    assert complex_annotations(
        [[1, [2, 3]]],
        '.1', .2,
        c=[(2020, 1, 1)],
        x='aa', y='bb'
    ) == (
        {'1': (2., 3.)},
        (decimal.Decimal('.1'), decimal.Decimal(.2)),
        {datetime.datetime(2020, 1, 1)},
        {'x': pathlib.Path('aa'), 'y': pathlib.Path('bb')}
    )
    assert str(complex_annotations) == (
        'complex_annotations('
        'a: Dict[str, Tuple[float, float]], '
        '*b: decimal.Decimal,'
        ' c: Set[datetime.datetime], '
        '**d: pathlib.Path)'
    )


def test_ret():
    @fashionable
    def ret() -> str:
        # noinspection PyTypeChecker
        return 5

    assert ret() == '5'
    assert str(ret) == 'ret() -> str'


def test_complex_ret():
    @fashionable
    def complex_ret() -> Dict[str, Set[str]]:
        # noinspection PyTypeChecker
        return [[1, [1, 1, 2, 2]], [pathlib.Path('aa'), 'sdsdsd']]

    assert complex_ret() == {'1': {'1', '2'}, 'aa': {'s', 'd'}}
    assert str(complex_ret) == 'complex_ret() -> Dict[str, Set[str]]'


# def test_model_out():


def test_name():
    @fashionable('some')
    def name():
        return

    assert name.name == 'some'
    assert str(name) == 'some()'


def test_annotations():
    @fashionable(a=pathlib.Path, b=float, return_=Tuple[pathlib.Path, float])
    def annotations(a: str, b: int) -> Tuple[str, int]:
        return a, b

    assert annotations('a', 1) == (pathlib.Path('a'), 1.)
    assert str(annotations) == 'annotations(a: pathlib.Path, b: float) -> Tuple[pathlib.Path, float]'


class Ctx:
    def __init__(self, x):
        self.x = x


def test_with_predefined():
    @fashionable
    def with_predefined(c: Ctx, x: int) -> int:
        c.x += 1
        return c.x + x

    predefined = {Ctx: Ctx(4)}

    assert with_predefined[predefined](5) == 10
    assert with_predefined[predefined](6) == 12
    assert str(with_predefined) == 'with_predefined(c: test_decorator.Ctx, x: int) -> int'


def test_func():
    def orig():
        pass

    func = fashionable(orig)

    assert func.func is orig


@mark.asyncio
async def test_coroutine():
    @fashionable
    async def coroutine(a: str, b: int) -> int:
        # noinspection PyTypeChecker
        return a * b

    # noinspection PyTypeChecker
    assert (await coroutine(1, '2')) == 11
    assert str(coroutine) == 'coroutine(a: str, b: int) -> int'


def test_missing_arg():
    @fashionable
    def missing_arg(some_name):
        return some_name

    with raises(MissingArgError) as err:
        missing_arg()

    assert str(err.value) == 'Invalid usage of missing_arg: missing required argument some_name'


def test_invalid_arg():
    @fashionable
    def invalid_arg(some_name: int):
        return some_name

    with raises(InvalidArgError) as err:
        # noinspection PyTypeChecker
        invalid_arg('a')

    assert str(err.value) == 'Invalid usage of invalid_arg: invalid argument some_name value'


def test_ret_error():
    @fashionable
    def ret_error() -> int:
        # noinspection PyTypeChecker
        return 'a'

    with raises(RetError) as err:
        ret_error()

    assert str(err.value) == 'Invalid usage of ret_error: invalid return value'


def test_recover():
    class Params(Model):
        a = Attribute(str)
        b = Attribute(str)
        c = Attribute(int, default=0)
        d = Attribute(Optional[float])

    @fashionable
    def recover(p: Params) -> dict:
        return p.to_dict()

    assert recover(1, 2) == {'a': '1', 'b': '2', 'c': 0}
    assert recover(3, 4, 5) == {'a': '3', 'b': '4', 'c': 5}
    assert recover(6, 7, 8, 9) == {'a': '6', 'b': '7', 'c': 8, 'd': 9.}
    assert recover(b=1, a=2) == {'a': '2', 'b': '1', 'c': 0}
    assert recover(c=3, b=4, a=5) == {'a': '5', 'b': '4', 'c': 3}
    assert recover(b=6, d=7, c=8, a=9) == {'a': '9', 'b': '6', 'c': 8, 'd': 7.}


def test_recover_default():
    class Params(Model):
        a = Attribute(str, default='a')
        b = Attribute(str, default='b')

    @fashionable
    def recover_default(params: Params = Params()) -> dict:
        return params.to_dict()

    assert recover_default() == {'a': 'a', 'b': 'b'}


def test_case_insensitivity():
    @fashionable
    def case_insensitivity(*, first_param: int, second_param: str) -> str:
        return second_param * first_param

    assert case_insensitivity(firstParam=2, SECOND_PARAM='a') == 'aa'
    assert case_insensitivity(**{'first-param': 3, 'SECOND-PARAM': 'b'}) == 'bbb'


def test_no_case_insensitivity():
    @fashionable(case_insensitive_=False)
    def no_case_insensitivity(*, first_param: int, second_param: str) -> str:
        return second_param * first_param

    with raises(MissingArgError):
        no_case_insensitivity(firstParam=2, second_param='a')

    with raises(MissingArgError):
        no_case_insensitivity(first_param=2, SECOND_PARAM='a')

    with raises(MissingArgError):
        no_case_insensitivity(**{'first-param': 3, 'second_param': 'b'})

    with raises(MissingArgError):
        no_case_insensitivity(**{'first_param': 3, 'SECOND-PARAM': 'b'})

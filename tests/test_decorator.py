import datetime
import decimal
import pathlib
from typing import Dict, Set, Tuple

from pytest import mark, raises

from fashionable import InvalidArgError, MissingArgError, RetError, fashionable


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


# def test_model_in():


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


def test_predefined():
    @fashionable
    def predefined(c: Ctx) -> int:
        c.x += 1
        return c.x

    ctx = Ctx(0)
    predefined.add_predefined(Ctx, ctx)

    assert predefined() == 1
    assert predefined() == 2
    assert str(predefined) == 'predefined(c: test_decorator.Ctx) -> int'


def test_func():
    def orig():
        pass

    func = fashionable(orig)

    # noinspection PyUnresolvedReferences
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
        pass

    with raises(MissingArgError) as err:
        missing_arg()

    assert str(err.value) == 'Invalid usage of missing_arg: missing required argument some_name'


def test_invalid_arg():
    @fashionable
    def invalid_arg(some_name: int):
        pass

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

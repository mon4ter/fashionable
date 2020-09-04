from fashionable import fashionable


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
    def simple_annotations(i: int, *s_: str, l: list, **s: set):
        return i, s_[0], l, next(iter(s.values()))

    # noinspection PyTypeChecker
    assert simple_annotations('1', 2, l='3', x='4') == (1, '2', ['3'], {'4'})
    assert str(simple_annotations) == 'simple_annotations(i: int, *s_: str, l: list, **s: set)'

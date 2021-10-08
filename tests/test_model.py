from copy import copy, deepcopy
from typing import Dict, List, Optional

from pytest import fail, raises

from fashionable import Attribute, FashionableError, Model, ModelError


def test_attributes():
    class M(Model):
        a = Attribute(str)
        b = Attribute(str)

    assert tuple(a.name for a in getattr(M, '.attributes')) == ('a', 'b')


def test_attributes_inheritance():
    class M1(Model):
        q = Attribute(str)
        w = Attribute(str)

    class M2(M1):
        e = Attribute(str)

    class M3(M2):
        r = Attribute(str)

    class M4(M2):
        w = Attribute(str)

    class M5(M3):
        w = Attribute(str)

    assert tuple(a.name for a in getattr(M2, '.attributes')) == ('q', 'w', 'e')
    assert tuple(a.name for a in getattr(M3, '.attributes')) == ('q', 'w', 'e', 'r')
    assert tuple(a.name for a in getattr(M4, '.attributes')) == ('q', 'w', 'e')
    assert tuple(a.name for a in getattr(M5, '.attributes')) == ('q', 'w', 'e', 'r')


def test_getter_setter():
    class M(Model):
        a = Attribute(str)

    assert M('a').a == 'a'


def test_fashionable_error():
    fmt = "Error %(a)s %(b)s"

    with raises(FashionableError) as exc:
        raise FashionableError(fmt, a='a', b='b')

    assert str(exc.value) == "Error a b"
    assert exc.value.fmt == fmt
    assert exc.value.kwargs == {'a': 'a', 'b': 'b'}


def test_type():
    class M1(Model):
        foo = Attribute(int)

    assert M1(1).foo == 1
    assert M1('1').foo == 1

    with raises(ModelError) as exc:
        M1('a')

    assert 'invalid' in str(exc.value)
    assert 'foo' in str(exc.value)

    class M2(Model):
        foo = Attribute(bool)

    assert M2(True).foo is True
    assert M2(0).foo == 0
    assert M2('').foo is False
    assert M2('0').foo is True


def test_optional():
    class M(Model):
        foo = Attribute(int)
        bar = Attribute(Optional[int])

    try:
        M(1).bar
    except ModelError as exc:
        fail("Unexpected InvalidModelError {}".format(exc))

    with raises(ModelError) as exc:
        M()

    assert 'missing' in str(exc.value)
    assert 'required' in str(exc.value)
    assert 'foo' in str(exc.value)


def test_default():
    default = 'bar'

    class M(Model):
        foo = Attribute(str, default=default)

    assert M().foo == default
    assert M('not bar').foo != default


def test_limit():
    min_ = 10
    max_ = 20

    class M(Model):
        foo = Attribute(str, min=min_, max=max_)

    try:
        v = 'a' * max_
        assert M(v).foo == v
    except ModelError as exc:
        fail("Unexpected InvalidModelError {}".format(exc))

    try:
        v = 'a' * min_
        assert M(v).foo == v
    except ModelError as exc:
        fail("Unexpected InvalidModelError {}".format(exc))

    with raises(ModelError) as exc:
        v = 'a' * (min_ - 1)
        M(v)

    assert str(min_) in str(exc.value)

    with raises(ModelError) as exc:
        v = 'a' * (max_ + 1)
        M(v)

    assert str(max_) in str(exc.value)
    assert 'length' in str(exc.value)
    assert 'foo' in str(exc.value)
    assert 'M' in str(exc.value)


def test_min():
    min_ = 10

    class M(Model):
        foo = Attribute(str, min=min_)

    with raises(ModelError) as exc:
        M('a' * (min_ - 1))

    assert '>=' in str(exc.value)
    assert 'foo' in str(exc.value)
    assert 'M' in str(exc.value)
    assert str(min_) in str(exc.value)

    try:
        assert M('a' * min_).foo
    except ModelError as exc:
        fail("Unexpected InvalidModelError {}".format(exc))

    try:
        assert M('a' * (min_ + 1)).foo
    except ModelError as exc:
        fail("Unexpected InvalidModelError {}".format(exc))


def test_max():
    max_ = 100

    class M(Model):
        foo = Attribute(str, max=max_)

    try:
        assert M('a' * (max_ - 1)).foo
    except ModelError as exc:
        fail("Unexpected InvalidModelError {}".format(exc))

    try:
        assert M('a' * max_).foo
    except ModelError as exc:
        fail("Unexpected InvalidModelError {}".format(exc))

    with raises(ModelError) as exc:
        M('a' * (max_ + 1))

    assert '<=' in str(exc.value)
    assert 'foo' in str(exc.value)
    assert 'M' in str(exc.value)
    assert str(max_) in str(exc.value)


def test_iter():
    class M1(Model):
        foo = Attribute(str)
        bar = Attribute(Optional[str])

    assert M1('a', 'b').to_dict() == {'foo': 'a', 'bar': 'b'}
    assert M1('a').to_dict() == {'foo': 'a'}

    class M2(Model):
        m = Attribute(M1)
        baz = Attribute(str)

    assert M2(M1('1'), '2').to_dict() == {'m': {'foo': '1'}, 'baz': '2'}


def test_id():
    class M1(Model):
        a = Attribute(int)
        b = Attribute(int)

    assert str(M1(1, 2)) == 'M1(1)'

    class M2(Model):
        a = Attribute(str)
        b = Attribute(int)

        def _id(self):
            return repr(str(self.b))

    assert str(M2('test', 123)) == "M2('123')"

    class M3(Model):
        a = Attribute(Optional[int])

    assert str(M3()) == 'M3(UNSET)'

    class M4(Model):
        a = Attribute(int)
        b = Attribute(Optional[str])

        def _id(self):
            return self.b

    assert str(M4(1)) == 'M4(UNSET)'


def test_repr():
    class M(Model):
        foo = Attribute(str)
        bar = Attribute(Optional[int])

    assert repr(M('a', 123)) == "M(foo='a', bar=123)"
    assert repr(M('a')) == "M(foo='a')"


def test_mixin():
    class B:
        def __bool__(self):
            return False

    class M(Model, B):
        a = Attribute(int)
        b = Attribute(int)

    assert tuple(a.name for a in getattr(M, '.attributes')) == ('a', 'b')
    assert bool(M(1, 2)) is False


def test_override():
    class M1(Model):
        a = Attribute(str)
        b = Attribute(str)

    class M2(M1):
        b = Attribute(int)

    assert M1('a', 1).b == '1'
    assert M2('a', '1').b == 1


def test_nested():
    class M1(Model):
        a = Attribute(int)
        b = Attribute(int)

    class M2(Model):
        x = Attribute(M1)
        y = Attribute(M1)

    m11 = M1(1, 2)
    m12 = M1(3, 4)

    m21 = M2(m11, m12)
    assert m21.x == m11
    assert m21.y == m12

    m22 = M2([1, 2], [3, 4])
    assert m22.x.a == 1
    assert m22.x.b == 2
    assert m22.y.a == 3
    assert m22.y.b == 4

    m23 = M2({'b': 2, 'a': 1}, {'b': 4, 'a': 3})
    assert m23.x.a == 1
    assert m23.x.b == 2
    assert m23.y.a == 3
    assert m23.y.b == 4

    with raises(AttributeError):
        M2(1, 2)


def test_list_of_models():
    class M1(Model):
        a = Attribute(int)
        b = Attribute(int)

    class M2(Model):
        x = Attribute(int)
        m1s = Attribute(List[M1])

    m21 = M2(5, [M1(1, 2), M1(3, 4)])
    m22 = M2('6', (['9', '8'], ['7', '6']))
    assert m21.m1s == [M1(1, 2), M1(3, 4)]
    assert m22.m1s == [M1(9, 8), M1(7, 6)]


def test_unknown_attribute_ignorance():
    class M(Model):
        a = Attribute(int)
        b = Attribute(int)

    assert M(3, 4, 5).to_dict() == {'a': 3, 'b': 4}
    assert M(a=5, c=6, b=7, d=7).to_dict() == {'a': 5, 'b': 7}


def test_case_insensitivity():
    class M(Model):
        someAttr = Attribute(str)
        OTHER_ATTR = Attribute(str)

    assert M(someATTR='1', other_attr='2').to_dict() == {'someAttr': '1', 'OTHER_ATTR': '2'}
    assert M(SOME_attr='3', OtherAttr='4').to_dict() == {'someAttr': '3', 'OTHER_ATTR': '4'}


def test_implicit_none():
    class M(Model):
        a = Attribute(Optional[int])

    assert M(1).to_dict() == {'a': 1}
    assert M(None).to_dict() == {'a': None}
    assert M().to_dict() == {}


def test_delete_attribute():
    class M1(Model):
        a = Attribute(Optional[int], default=432)

    m1 = M1(999)
    del m1.a
    assert m1.a == 432

    class M2(Model):
        some_name = Attribute(int)

    m2 = M2(321)

    with raises(AttributeError) as exc:
        del m2.some_name

    assert 'some_name' in str(exc.value)


def test_compare_with_non_model():
    class M(Model):
        a = Attribute(int)

    assert M(1) == 1
    assert 1 == M(1)
    assert M(1).__eq__('a') is NotImplemented


def test_copy():
    class M2(Model):
        c = Attribute(int)

    class M1(Model):
        a = Attribute(int)
        b = Attribute(M2)

    m = M1(1, M2(2))
    m1 = copy(m)
    m2 = deepcopy(m)

    m1.a = 3
    m2.b.c = 4

    assert m.a == 1
    assert m.b.c == 2
    assert m1.a == 3
    assert m2.b.c == 4


def test_to_dict():
    class Foo:
        def __init__(self, x):
            self.x = x

        # noinspection PyPep8Naming
        @staticmethod
        def toDict() -> dict:
            return {'foo': 1, 'bar': 3}

    class M1(Model):
        a = Attribute(int)
        b = Attribute(str)
        foo = Attribute(Foo)

    class M2(Model):
        x = Attribute(str)

    class M3(Model):
        lst = Attribute(List[M2])

    class M4(Model):
        key = Attribute(M1)
        val = Attribute(Dict[str, M3])

    m = M4((4, 5, 6), {1: [10, 11], 2: [20, 21]})
    d = {
        'key': {
            'a': 4,
            'b': '5',
            'foo': {'foo': 1, 'bar': 3}
        },
        'val': {
            '1': {
                'lst': [
                    {'x': '10'},
                    {'x': '11'},
                ]
            },
            '2': {
                'lst': [
                    {'x': '20'},
                    {'x': '21'},
                ]
            }
        }
    }
    assert m.to_dict() == d

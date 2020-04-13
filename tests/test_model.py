from typing import List, Optional

from pytest import fail, raises

from fashionable import Attribute, Model, ModelError


def test_attributes():
    class M(Model):
        a = Attribute(str)
        b = Attribute(str)

    assert getattr(M, '.attributes') == ('a', 'b')


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

    assert getattr(M2, '.attributes') == ('q', 'w', 'e')
    assert getattr(M3, '.attributes') == ('q', 'w', 'e', 'r')
    assert getattr(M4, '.attributes') == ('q', 'w', 'e')
    assert getattr(M5, '.attributes') == ('q', 'w', 'e', 'r')


def test_getter_setter():
    class M(Model):
        a = Attribute(str)

    assert M('a').a == 'a'


def test_invalid_model_error():
    fmt = "Error %(a)s %(b)s"

    with raises(ModelError) as exc:
        raise ModelError(fmt, a='a', b='b')

    assert "Error a b" in str(exc.value)
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
        foo = Attribute(Optional[str], default=default)

    assert M().foo == default
    assert M('not bar').foo != default


def test_limit():
    limit = 10

    class M(Model):
        foo = Attribute(str, limit=limit)

    try:
        v = 'a' * (limit - 1)
        assert M(v).foo == v
    except ModelError as exc:
        fail("Unexpected InvalidModelError {}".format(exc))

    try:
        v = 'a' * limit
        assert M(v).foo == v
    except ModelError as exc:
        fail("Unexpected InvalidModelError {}".format(exc))

    with raises(ModelError) as exc:
        v = 'a' * (limit + 1)
        M(v)

    assert 'too long' in str(exc.value)
    assert 'foo' in str(exc.value)
    assert 'M' in str(exc.value)
    assert str(limit) in str(exc.value)


def test_min():
    min_ = 'AAAAAB'

    class M(Model):
        foo = Attribute(str, min=min_)

    with raises(ModelError) as exc:
        M('AAAAAA')

    assert '>=' in str(exc.value)
    assert 'foo' in str(exc.value)
    assert 'M' in str(exc.value)
    assert min_ in str(exc.value)

    try:
        assert M(min_).foo == min_
    except ModelError as exc:
        fail("Unexpected InvalidModelError {}".format(exc))

    try:
        assert M('FFFFFF').foo == 'FFFFFF'
    except ModelError as exc:
        fail("Unexpected InvalidModelError {}".format(exc))


def test_max():
    max_ = 'FFFFFE'

    class M(Model):
        foo = Attribute(str, max=max_)

    try:
        assert M('AAAAAA').foo == 'AAAAAA'
    except ModelError as exc:
        fail("Unexpected InvalidModelError {}".format(exc))

    try:
        assert M(max_).foo == max_
    except ModelError as exc:
        fail("Unexpected InvalidModelError {}".format(exc))

    with raises(ModelError) as exc:
        M('FFFFFF')

    assert '<=' in str(exc.value)
    assert 'foo' in str(exc.value)
    assert 'M' in str(exc.value)
    assert max_ in str(exc.value)


def test_iter():
    class M1(Model):
        foo = Attribute(str)
        bar = Attribute(Optional[str])

    assert dict(M1('a', 'b')) == {'foo': 'a', 'bar': 'b'}
    assert dict(M1('a')) == {'foo': 'a'}

    class M2(Model):
        m = Attribute(M1)
        baz = Attribute(str)

    assert dict(M2(M1('1'), '2')) == {'m': {'foo': '1'}, 'baz': '2'}


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

    assert getattr(M, '.attributes') == ('a', 'b')
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

    assert dict(M(3, 4, 5)) == {'a': 3, 'b': 4}
    assert dict(M(a=5, c=6, b=7, d=7)) == {'a': 5, 'b': 7}


def test_case_insensitivity():
    class M(Model):
        someAttr = Attribute(str)
        OTHER_ATTR = Attribute(str)

    assert dict(M(someattr='1', other_attr='2')) == {'someAttr': '1', 'OTHER_ATTR': '2'}
    assert dict(M(SOMEATTR='3', OtHeR_aTtR='4')) == {'someAttr': '3', 'OTHER_ATTR': '4'}


def test_implicit_none():
    class M(Model):
        a = Attribute(Optional[int])

    assert dict(M(1)) == {'a': 1}
    assert dict(M(None)) == {'a': None}
    assert dict(M()) == {}


def test_delete_attribute():
    class M(Model):
        a = Attribute(Optional[int], default=432)

    m = M(999)
    del m.a
    assert m.a == 432


def test_invalid_attribute():
    class Raiser:
        def __init__(self):
            pass

        def __str__(self):
            raise Exception

    class Inner(Model):
        a = Attribute(str)

    class M(Model):
        b = Attribute(Inner)

    with raises(ModelError) as exc:
        M(Raiser())

    assert 'invalid attribute' in exc.value.fmt


def test_compare_with_non_model():
    class M(Model):
        a = Attribute(int)

    assert M(1) == 1
    assert 1 == M(1)
    assert M(1).__eq__('a') is NotImplemented

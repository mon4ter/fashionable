from pytest import raises, fail

from fashionable import Attribute, Model, InvalidModelError


def test_attributes():
    class M(Model):
        a = Attribute()
        b = Attribute()

    assert M._attributes == ('a', 'b')


def test_attributes_inheritance():
    class M1(Model):
        q = Attribute()
        w = Attribute()

    class M2(M1):
        e = Attribute()

    class M3(M2):
        r = Attribute()

    class M4(M2):
        w = Attribute()

    class M5(M3):
        w = Attribute()

    assert M2._attributes == ('q', 'w', 'e')
    assert M3._attributes == ('q', 'w', 'e', 'r')
    assert M4._attributes == ('q', 'w', 'e')
    assert M5._attributes == ('q', 'w', 'e', 'r')


def test_getter_setter():
    class M(Model):
        a = Attribute()

    assert M('a').a == 'a'


def test_invalid_model_error():
    fmt = "Error %(a)s %(b)s"

    with raises(InvalidModelError) as exc:
        raise InvalidModelError(fmt, a='a', b='b')

    assert "Error a b" in str(exc.value)
    assert exc.value.fmt == fmt
    assert exc.value.kwargs == {'a': 'a', 'b': 'b'}


def test_type():
    class M(Model):
        foo = Attribute(int)

    assert M(1).foo == 1
    assert M('1').foo == 1

    with raises(InvalidModelError) as exc:
        M('a')

    assert 'invalid' in str(exc.value)
    assert 'foo' in str(exc.value)


def test_optional():
    class M(Model):
        foo = Attribute()
        bar = Attribute(optional=True)

    try:
        M(1).bar
    except InvalidModelError as exc:
        fail("Unexpected InvalidModelError {}".format(exc))

    with raises(InvalidModelError) as exc:
        M()

    assert 'missing' in str(exc.value)
    assert 'required' in str(exc.value)
    assert 'foo' in str(exc.value)


def test_default():
    default = 'bar'

    class M(Model):
        foo = Attribute(optional=True, default=default)

    assert M().foo == default
    assert M('not bar') != default


def test_limit():
    limit = 10

    class M(Model):
        foo = Attribute(limit=limit)

    try:
        v = 'a' * (limit - 1)
        assert M(v).foo == v
    except InvalidModelError as exc:
        fail("Unexpected InvalidModelError {}".format(exc))

    try:
        v = 'a' * limit
        assert M(v).foo == v
    except InvalidModelError as exc:
        fail("Unexpected InvalidModelError {}".format(exc))

    with raises(InvalidModelError) as exc:
        v = 'a' * (limit + 1)
        M(v)

    assert 'too long' in str(exc.value)
    assert 'foo' in str(exc.value)
    assert 'M' in str(exc.value)
    assert str(limit) in str(exc.value)


def test_min():
    min_ = 'AAAAAB'

    class M(Model):
        foo = Attribute(min=min_)

    with raises(InvalidModelError) as exc:
        M('AAAAAA')

    assert '>=' in str(exc.value)
    assert 'foo' in str(exc.value)
    assert 'M' in str(exc.value)
    assert min_ in str(exc.value)

    try:
        assert M(min_).foo == min_
    except InvalidModelError as exc:
        fail("Unexpected InvalidModelError {}".format(exc))

    try:
        assert M('FFFFFF').foo == 'FFFFFF'
    except InvalidModelError as exc:
        fail("Unexpected InvalidModelError {}".format(exc))


def test_max():
    max_ = 'FFFFFE'

    class M(Model):
        foo = Attribute(max=max_)

    try:
        assert M('AAAAAA').foo == 'AAAAAA'
    except InvalidModelError as exc:
        fail("Unexpected InvalidModelError {}".format(exc))

    try:
        assert M(max_).foo == max_
    except InvalidModelError as exc:
        fail("Unexpected InvalidModelError {}".format(exc))

    with raises(InvalidModelError) as exc:
        M('FFFFFF')

    assert '<=' in str(exc.value)
    assert 'foo' in str(exc.value)
    assert 'M' in str(exc.value)
    assert max_ in str(exc.value)


def test_iter():
    class M(Model):
        foo = Attribute()
        bar = Attribute(optional=True)

    assert dict(M('a', 'b')) == {'foo': 'a', 'bar': 'b'}
    assert dict(M('a')) == {'foo': 'a'}


def test_id():
    class M1(Model):
        a = Attribute()
        b = Attribute()

    assert str(M1(1, 2)) == 'M1(1)'

    class M2(Model):
        a = Attribute()
        b = Attribute()

        def _id(self):
            return repr(str(self.b))

    assert str(M2('test', 123)) == "M2('123')"


def test_repr():
    class M(Model):
        foo = Attribute()
        bar = Attribute(optional=True)

    assert repr(M('a', 123)) == "M(foo='a', bar=123)"
    assert repr(M('a')) == "M(foo='a')"


def test_mixin():
    class B:
        def __bool__(self):
            return False

    class M(Model, B):
        a = Attribute()
        b = Attribute()

    assert M._attributes == ('a', 'b')
    assert bool(M(1, 2)) is False


def test_override():
    class M1(Model):
        a = Attribute(str)
        b = Attribute(str)

    class M2(M1):
        b = Attribute(int)

    assert M1('a', 1).b == '1'
    assert M2('a', '1').b == 1

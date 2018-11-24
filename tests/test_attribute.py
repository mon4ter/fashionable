from pytest import raises

from fashionable import Attribute


def test_without_parameters():
    a = Attribute()
    assert a.type is None
    assert a.optional is False
    assert a.default is None
    assert a.limit is None
    assert a.min is None
    assert a.max is None


def test_type_validation():
    with raises(TypeError):
        Attribute('123')

    assert Attribute(str).type == str


def test_optional_validation():
    with raises(TypeError):
        Attribute(optional='yes')

    assert Attribute(optional=True).optional is True


def test_default():
    assert Attribute(default='').default == ''


def test_limit():
    with raises(TypeError):
        Attribute(limit=0.5)

    with raises(ValueError):
        Attribute(limit=-5)

    assert Attribute(limit=0).limit == 0
    assert Attribute(limit=100).limit == 100


def test_min():
    with raises(TypeError):
        Attribute(min=type)

    assert Attribute(min=0).min == 0
    assert Attribute(min='000000').min == '000000'


def test_max():
    with raises(TypeError):
        Attribute(max=type)

    assert Attribute(max=0).max == 0
    assert Attribute(max='FFFFFF').max == 'FFFFFF'

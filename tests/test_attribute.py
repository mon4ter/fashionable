from typing import Any, Optional

from pytest import raises

from fashionable import Attribute, UNSET, Unset


def test_name():
    name = 'a'
    a = Attribute(Any)
    a.name = name
    assert a.name == name
    assert a.private_name == '.' + name

    with raises(TypeError):
        Attribute(Any).name = 123


def test_without_parameters():
    a = Attribute(Any)
    assert a.type is Any
    assert a.strict is False
    assert a.default is UNSET
    assert a.min is UNSET
    assert a.max is UNSET


def test_type():
    with raises(TypeError):
        # noinspection PyTypeChecker
        Attribute('123')

    assert Attribute(str).type == str


def test_default():
    assert Attribute(Optional[str], default='').default == ''
    assert Attribute(Optional[str], default=5).default == '5'
    assert Attribute(Optional[str], default=None).default is None

    with raises(ValueError):
        Attribute(int, default='a')

    with raises(TypeError):
        Attribute(int, default='a', strict=True)

    with raises(ValueError):
        Attribute(int, default=0, min=1)

    with raises(ValueError):
        Attribute(int, default=1000, max=999)

    with raises(ValueError):
        Attribute(str, default='a', min=2)

    with raises(ValueError):
        Attribute(str, default='abc', max=2)


def test_min():
    with raises(TypeError):
        Attribute(str, min=type)

    assert Attribute(str, min=0).min == 0
    assert Attribute(str, min='000000').min == '000000'


def test_max():
    with raises(TypeError):
        Attribute(str, max=type)

    assert Attribute(str, max=0).max == 0
    assert Attribute(str, max='FFFFFF').max == 'FFFFFF'


def test_strict():
    assert Attribute(str).strict is False
    assert Attribute(str, strict=True).strict is True
    assert Attribute(str, strict=False).strict is False

    with raises(TypeError):
        # noinspection PyTypeChecker
        Attribute(str, strict=5)


def test_unset():
    assert Unset() is UNSET
    assert Unset() is Unset()
    assert not UNSET

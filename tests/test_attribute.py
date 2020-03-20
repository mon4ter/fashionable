from sys import version_info
from typing import Any

from pytest import raises, mark

from fashionable import Attribute, UNSET


def test_name():
    name = 'a'
    a = Attribute(Any)
    a.name = name
    assert a.name == name
    # noinspection PyProtectedMember
    assert a._private_name == '_m_' + name

    with raises(TypeError):
        Attribute(Any).name = 123


def test_without_parameters():
    a = Attribute(Any)
    assert a.type is Any
    assert a.default is UNSET
    assert a.limit is None
    assert a.min is None
    assert a.max is None


def test_type():
    # TODO Fix test for py35
    if version_info >= (3, 7):
        with raises(TypeError):
            # noinspection PyTypeChecker
            Attribute('123')

    assert Attribute(str).type == str


@mark.parametrize('default', ['', None])
def test_default(default):
    assert Attribute(str, default=default).default == default


def test_limit():
    with raises(TypeError):
        # noinspection PyTypeChecker
        Attribute(str, limit=0.5)

    with raises(ValueError):
        Attribute(str, limit=-5)

    assert Attribute(str, limit=0).limit == 0
    assert Attribute(str, limit=100).limit == 100


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

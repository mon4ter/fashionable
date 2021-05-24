from typing import Any, List, Optional

from pytest import mark, raises

from fashionable import Attribute, UNSET, Unset


def test_name():
    name = 'a'
    a = Attribute(Any)
    a.name = name
    assert a.name == name
    assert name in a.names
    assert a.private_name == '.' + name

    with raises(TypeError):
        Attribute(Any).name = 123


@mark.parametrize('name,ci_names', [
    ('someName', ['some-name', 'some_name', 'somename']),
    ('SomeName', ['some-name', 'some_name', 'somename']),
    ('some-name', ['some-name', 'some_name', 'somename']),
    ('ABCSomeName', ['abc-some-name', 'abc_some_name', 'abcsomename']),
])
def test_ci_name(name: str, ci_names: List[str]):
    a = Attribute(Any)
    a.name = name
    assert a.name == name
    assert name in a.names
    assert all(n in a.names for n in ci_names)


def test_case_sensitive_name():
    name = 'Case_Sensitive'
    a = Attribute(Any, case_insensitive=False)
    a.name = name
    assert all(n not in a.names for n in ['CaseSensitive', 'Case-Sensitive', 'case_sensitive'])


def test_without_parameters():
    a = Attribute(Any)
    assert a.type is Any
    assert a.strict is False
    assert a.default is UNSET
    assert a.min is UNSET
    assert a.max is UNSET
    assert a.case_insensitive is True


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


def test_case_insensitive():
    a = Attribute(Any)
    a.name = 'some_name'
    assert 'some-name' in a.names
    a.case_insensitive = False
    assert 'some-name' not in a.names

    with raises(TypeError):
        # noinspection PyTypeChecker
        Attribute(str, case_insensitive='-')


def test_unset():
    assert Unset() is UNSET
    assert Unset() is Unset()
    assert not UNSET


def test_eq():
    a1 = Attribute(Any)
    a1.name = 'a'
    a2 = Attribute(Any)
    a2.name = 'a'
    b = Attribute(Any)
    b.name = 'b'
    assert a1 == a2
    assert hash(a1) == hash(a2)
    assert a1 != b
    assert hash(a1) != hash(b)
    # noinspection PyTypeChecker
    assert a1.__eq__('a') is NotImplemented

from typing import Optional

from pytest import mark, raises

from fashionable import Attribute, Supermodel


# noinspection PyAbstractClass
def test_supermodel():
    class S(Supermodel):
        a = Attribute(int)

    assert S(1).a == 1


# noinspection PyAbstractClass,PyProtectedMember
def test_ttl():
    class S1(Supermodel):
        a = Attribute(int)

    class S2(S1):
        _ttl = 5

    class S3(S2):
        _ttl = 10

    class S4(S2):
        b = Attribute(int)

    assert S1._ttl is None
    assert S2._ttl == 5
    assert S3._ttl == 10
    assert S4._ttl == 5

    with raises(TypeError):
        # noinspection PyUnusedLocal
        class S(Supermodel):
            _ttl = '1'


# noinspection PyAbstractClass
@mark.asyncio
async def test_create():
    class S1(Supermodel):
        a = Attribute(str)
        b = Attribute(Optional[int])

        @staticmethod
        async def _create(raw: dict):
            return raw

    s1 = await S1.create('z', 3)
    assert isinstance(s1, Supermodel)
    assert isinstance(s1, S1)
    assert s1.a == 'z'
    assert s1.b == 3

    s2 = await S1.create(b=2, a='x')
    assert s2.a == 'x'
    assert s2.b == 2


# noinspection PyAbstractClass
@mark.asyncio
async def test_get():
    class S1(Supermodel):
        a = Attribute(str)
        b = Attribute(Optional[int])

        @staticmethod
        async def _create(raw: dict):
            return raw

        @staticmethod
        async def _get(id_: str):
            if id_ == 'f':
                return {'a': 'f', 'b': 123}

    s1 = await S1.get('f')
    assert isinstance(s1, Supermodel)
    assert isinstance(s1, S1)
    assert s1.a == 'f'
    assert s1.b == 123

    assert await S1.get('foo') is None

    await S1.create('c', 88)
    s2 = await S1.get('c')
    assert isinstance(s2, Supermodel)
    assert isinstance(s2, S1)
    assert s2.a == 'c'
    assert s2.b == 88


@mark.asyncio
async def test_abc():
    # noinspection PyAbstractClass
    class S(Supermodel):
        a = Attribute(int)

    with raises(NotImplementedError):
        await S.get(1)

    with raises(NotImplementedError):
        await S.find(a=1)

    with raises(NotImplementedError):
        await S.create(1)

    with raises(NotImplementedError):
        await S(1).update(a=1)

    with raises(NotImplementedError):
        await S(1).delete()

from pytest import mark

from fashionable import Attribute, Supermodel


# noinspection PyAbstractClass
def test_supermodel():
    class S(Supermodel):
        a = Attribute()

    assert S(1).a == 1


# noinspection PyAbstractClass
def test_ttl():
    class S1(Supermodel):
        a = Attribute()

    class S2(S1):
        _ttl = 5

    class S3(S2):
        _ttl = 10

    class S4(S2):
        b = Attribute()

    assert S1._ttl is None
    assert S2._ttl == 5
    assert S3._ttl == 10
    assert S4._ttl == 5


# noinspection PyAbstractClass
@mark.asyncio
async def test_create():
    class S1(Supermodel):
        a = Attribute(str)
        b = Attribute(int, optional=True)

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
        b = Attribute(int, optional=True)

        @staticmethod
        async def _create(raw: dict):
            return raw

        @staticmethod
        async def _get(id_: str):
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

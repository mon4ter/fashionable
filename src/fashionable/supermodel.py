from asyncio import get_event_loop
from copy import copy
from logging import getLogger
from typing import Any, AsyncIterator, Dict, Optional, Tuple, Type, Union

from .model import Model
from .modelmeta import ModelMeta
from .unset import UNSET

__all__ = [
    'logger',
    'SupermodelMeta',
    'SupermodelIterator',
    'Supermodel',
]

logger = getLogger(__name__)


class SupermodelMeta(ModelMeta):
    @property
    def _ttl(cls) -> Optional[Union[int, float]]:
        return getattr(cls, '.ttl', None)

    @_ttl.setter
    def _ttl(cls, value: Optional[Union[int, float]]):
        if value is None or isinstance(value, (int, float)):
            setattr(cls, '.ttl', value)
        else:
            raise TypeError("Invalid _ttl: must be int or float, not {}".format(type(value).__name__))

    def __new__(mcs, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any]) -> type:
        ttl = namespace.pop('_ttl', UNSET)
        namespace['.cache'] = {}
        namespace['.trash'] = {}
        namespace['.expire_handles'] = {}
        namespace['.refresh_tasks'] = {}
        cls = super().__new__(mcs, name, bases, namespace)

        if ttl is not UNSET:
            cls._ttl = ttl

        return cls


class SupermodelIterator:
    def __init__(self, model: Type['Supermodel'], iterator: AsyncIterator[dict]):
        self.model = model
        self.iterator = iterator
        self.iterable = None

    def __aiter__(self) -> AsyncIterator['Supermodel']:
        self.iterable = self.iterator.__aiter__()
        return self

    async def __anext__(self) -> 'Supermodel':
        raw = await self.iterable.__anext__()
        model = self.model(**raw)
        # noinspection PyProtectedMember
        self.model._cache(model._id(), model)
        return model


class Supermodel(Model, metaclass=SupermodelMeta):
    @classmethod
    def _cache(cls, id_: Any, model: Optional['Supermodel'] = None, reset: bool = True):
        cache = getattr(cls, '.cache')
        trash = getattr(cls, '.trash')
        expire_handles = getattr(cls, '.expire_handles')
        refresh_tasks = getattr(cls, '.refresh_tasks')

        if id_ in cache:
            del cache[id_]

        if id_ in trash:
            del trash[id_]

        if id_ in expire_handles:
            expire_handles.pop(id_).cancel()

        if id_ in refresh_tasks:
            refresh_tasks.pop(id_).cancel()

        if reset:
            if cls._ttl:
                logger.debug("Creating expire %s(%s)", cls.__name__, id_)
                expire_handles[id_] = get_event_loop().call_later(cls._ttl, cls._expire, id_)

            cache[id_] = model

    @classmethod
    def _expire(cls, id_: Any):
        cache = getattr(cls, '.cache')
        trash = getattr(cls, '.trash')

        if id_ in cache:
            logger.debug("%s(%s) expired", cls.__name__, id_)
            trash[id_] = cache.pop(id_)

    @classmethod
    async def _refresh(cls, id_: Any):
        raw = await cls._get(id_)
        model = cls(**raw) if raw else None
        get_event_loop().call_soon(cls._cache, id_, model)
        logger.debug("%s(%s) refreshed", cls.__name__, id_)
        return model

    @staticmethod
    async def _create(raw: dict):
        raise NotImplementedError

    @staticmethod
    async def _get(id_: Any) -> Optional[dict]:
        raise NotImplementedError

    @staticmethod
    async def _find(**kwargs) -> AsyncIterator[dict]:
        raise NotImplementedError

    @staticmethod
    async def _update(id_: Any, raw: dict):
        raise NotImplementedError

    @staticmethod
    async def _delete(id_: Any):
        raise NotImplementedError

    @classmethod
    async def create(cls, *args, **kwargs):
        model = cls(*args, **kwargs)
        await cls._create(model.to_dict())
        cls._cache(model._id(), model)
        return model

    @classmethod
    async def get(cls, id_: Any, fresh: bool = False) -> Optional['Supermodel']:
        cache = getattr(cls, '.cache')
        trash = getattr(cls, '.trash')
        refresh_tasks = getattr(cls, '.refresh_tasks')

        if id_ in cache:
            logger.debug("%s(%s) hit", cls.__name__, id_)
            model = cache[id_]
        else:
            logger.debug("%s(%s) miss", cls.__name__, id_)

            if id_ not in refresh_tasks:
                logger.debug("Creating refresh %s(%s)", cls.__name__, id_)
                refresh_tasks[id_] = get_event_loop().create_task(cls._refresh(id_))

            if not fresh and id_ in trash:
                logger.debug("Getting %s(%s) out of trash", cls.__name__, id_)
                model = trash[id_]
            else:
                logger.debug("Waiting for new %s(%s)", cls.__name__, id_)
                model = await refresh_tasks[id_]

        return model

    @classmethod
    async def find(cls, **kwargs) -> AsyncIterator['Supermodel']:
        return SupermodelIterator(cls, await cls._find(**kwargs))

    async def update(self, **raw):
        attributes = getattr(self, '.attributes')
        id_ = self._id()
        new = copy(self)

        for attr in attributes:
            name = attr.ciname or attr.name
            value = next((v for k, v in raw.items() if name == k), None)

            if value:
                setattr(new, attr.name, value)

        await self._update(id_, new.to_dict())

        for attr in attributes:
            name = attr.ciname or attr.name
            value = next((v for k, v in raw.items() if name == k), None)

            if value:
                setattr(self, attr.name, value)

        self._cache(id_, self)

    async def delete(self):
        id_ = self._id()
        await self._delete(id_)
        self._cache(id_, reset=False)

    @classmethod
    def close(cls):
        for tasks in (getattr(cls, '.expire_handles'), getattr(cls, '.refresh_tasks')):
            while tasks:
                id_ = next(iter(tasks))
                tasks.pop(id_).cancel()

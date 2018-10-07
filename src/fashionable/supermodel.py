from asyncio import get_event_loop
from logging import getLogger
from typing import Optional

from .model import Model

__all__ = [
    'Supermodel',
]

logger = getLogger(__name__)


class Supermodel(Model):
    _models = {}
    _old_models = {}
    _expire_handles = {}
    _refresh_tasks = {}

    ttl = None

    @classmethod
    def _cache(cls, id_: str, model: Optional[Model]=None, reset: bool=True):
        if id_ in cls._models:
            del cls._models[id_]

        if id_ in cls._old_models:
            del cls._old_models[id_]

        if id_ in cls._expire_handles:
            cls._expire_handles[id_].cancel()
            del cls._expire_handles[id_]

        if id_ in cls._refresh_tasks:
            del cls._refresh_tasks[id_]

        if reset:
            if cls.ttl:
                logger.debug("Creating expire %s(%s)", cls.__name__, id_)
                cls._expire_handles[id_] = get_event_loop().call_later(cls.ttl, cls._expire, id_)

            cls._models[id_] = model

    @classmethod
    def _expire(cls, id_: str):
        if id_ in cls._models:
            logger.debug("%s(%s) expired", cls.__name__, id_)
            cls._old_models[id_] = cls._models.pop(id_)

    @classmethod
    async def _refresh(cls, id_: str):
        raw = await cls._get(id_)
        model = cls(**raw) if raw else None
        cls._cache(id_, model)
        logger.debug("%s(%s) refreshed", cls.__name__, id_)
        return model

    @staticmethod
    async def _create(raw: dict):
        raise NotImplementedError

    @staticmethod
    async def _get(id_: str) -> Optional[dict]:
        raise NotImplementedError

    @staticmethod
    async def _update(id_: str, raw: dict):
        raise NotImplementedError

    @staticmethod
    async def _delete(id_: str):
        raise NotImplementedError

    @classmethod
    async def create(cls, *args, **kwargs):
        model = cls(*args, **kwargs)
        await cls._create(dict(model))
        cls._cache(model._id(), model)
        return model

    @classmethod
    async def get(cls, id_: str, fresh: bool=False) -> Optional[Model]:
        if id_ in cls._models:
            logger.debug("%s(%s) hit", cls.__name__, id_)
            model = cls._models[id_]
        else:
            logger.debug("%s(%s) miss", cls.__name__, id_)

            if id_ not in cls._refresh_tasks:
                cls._refresh_tasks[id_] = get_event_loop().create_task(cls._refresh(id_))
                logger.debug("Created refresh %s(%s)", cls.__name__, id_)

            if not fresh and id_ in cls._old_models:
                logger.debug("Using old %s(%s)", cls.__name__, id_)
                model = cls._old_models[id_]
            else:
                logger.debug("Waiting for new %s(%s)", cls.__name__, id_)
                model = await cls._refresh_tasks[id_]

        return model

    async def update(self, **raw: dict):
        id_ = self._id()
        backup = dict(self)

        for attr in self._attributes:
            if attr in raw:
                setattr(self, attr, raw[attr])

        try:
            await self._update(id_, dict(self))
        except Exception:
            for attr in self._attributes:
                setattr(self, attr, backup.get(attr))

            raise

        self._cache(id_, self)

    async def delete(self):
        id_ = self._id()
        await self._delete(id_)
        self._cache(id_, reset=False)

    @classmethod
    def close(cls):
        for handle in cls._expire_handles.values():
            handle.cancel()

        for task in cls._refresh_tasks.values():
            task.cancel()

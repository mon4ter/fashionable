from asyncio import iscoroutine
from inspect import Parameter, Signature, signature
from typing import Any, Callable, Dict, Optional, Tuple

from .arg import Arg
from ..errors import ArgError, RetError
from ..typedef import AsyncRet, Ret, Typing, Value
from ..unset import UNSET

__all__ = [
    'Func',
]


class Func:
    __slots__ = ('_func', '_name', '_args', '_ret', '_predefined')

    _POSITIONAL_KINDS = {Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD, Parameter.VAR_POSITIONAL}
    _ZIPPED_KINDS = {Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD}

    @classmethod
    def from_inspect(cls, func: Callable, name: Optional[str], annotations: Dict[str, Typing]) -> 'Func':
        if not name:
            name = func.__name__

        sign = signature(func)

        args = tuple(Arg(
            name,
            parameter.name,
            Any if parameter.annotation is Parameter.empty else parameter.annotation,
            UNSET if parameter.default is Parameter.empty else parameter.default,
            parameter.kind in cls._POSITIONAL_KINDS,
            parameter.kind in cls._ZIPPED_KINDS
        ) for parameter in sign.parameters.values())

        ret_annotation = sign.return_annotation
        ret_type = annotations.get('return', Any if ret_annotation is Signature.empty else ret_annotation)
        ret = Arg(name, 'return', ret_type, UNSET, False, False) if ret_type else None

        return cls(func, name, args, ret)

    def __init__(self, func: Callable, name: str, args: Tuple[Arg, ...], ret: Optional[Arg]):
        self._func = func
        self._name = name
        self._args = args
        self._ret = ret
        self._predefined = {}

    def add_predefined(self, typ: Typing, value: Value):
        self._predefined[typ] = value

    def _validate(self, *args, **kwargs) -> Tuple[list, dict]:
        new_args = []
        new_kwargs = {}
        recover_allowed = True

        list_params = list(args)
        dict_params = dict(kwargs)

        for arg in self._args:
            if arg.is_zipped:
                for param_name in list(dict_params):
                    new_kwargs[param_name] = arg.validate(dict_params.pop(param_name))
                    recover_allowed = False

                while list_params:
                    new_args.append(arg.validate(list_params.pop(0)))
                    recover_allowed = False

                continue

            value = self._predefined.get(arg.type, UNSET)

            name = arg.name

            if value is UNSET:
                try:
                    value = arg.validate(
                        dict_params.pop(name, UNSET) if dict_params else list_params.pop(0) if list_params else UNSET
                    )
                except ArgError:
                    if not recover_allowed:
                        raise

                    value = arg.validate(*args, **kwargs)

            if arg.is_positional:
                new_args.append(value)
            else:
                new_kwargs[name] = value

            recover_allowed = False

        return new_args, new_kwargs

    def _in(self, *args, **kwargs) -> Ret:
        args, kwargs = self._validate(*args, **kwargs)
        return self._func(*args, **kwargs)

    def _out(self, ret: Any) -> Any:
        if self._ret:
            try:
                ret = self._ret.validate(ret)
            except ArgError as err:
                raise RetError(func=self._name) from err

        return ret

    async def _async_out(self, ret: AsyncRet) -> Any:
        return self._out(await ret)

    def __call__(self, *args, **kwargs) -> Ret:
        ret = self._in(*args, **kwargs)

        if iscoroutine(ret):
            ret = self._async_out(ret)
        else:
            ret = self._out(ret)

        return ret

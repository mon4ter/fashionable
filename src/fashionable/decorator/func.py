from asyncio import iscoroutine
from inspect import Parameter, Signature, signature
from typing import Any, Callable, Dict, Optional, Tuple

from .arg import Arg
from ..errors import ArgError, RetError
from ..typedef import AsyncRet, Ret
from ..unset import UNSET

__all__ = [
    'Func',
]


class Func:
    __slots__ = ('func', 'name', 'args', 'ret')

    _POSITIONAL_KINDS = {Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD, Parameter.VAR_POSITIONAL}
    _ZIPPED_KINDS = {Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD}

    @classmethod
    def from_inspect(cls, func: Callable, name: Optional[str], annotations: Dict[str, type]) -> 'Func':
        if not name:
            name = func.__name__

        sign = signature(func)

        args = tuple(Arg(
            parameter.name,
            Any if parameter.annotation is Parameter.empty else parameter.annotation,
            UNSET if parameter.default is Parameter.empty else parameter.default,
            parameter.kind in cls._POSITIONAL_KINDS,
            parameter.kind in cls._ZIPPED_KINDS
        ) for parameter in sign.parameters.values())

        ret_annotation = sign.return_annotation
        ret_type = annotations.get('return', Any if ret_annotation is Signature.empty else ret_annotation)
        ret = Arg('result', ret_type, UNSET, False, False) if ret_type else None

        return cls(func, name, args, ret)

    def __init__(self, func: Callable, name: str, args: Tuple[Arg, ...], ret: Optional[Arg]):
        self.func = func
        self.name = name
        self.args = args
        self.ret = ret

    def _validate(self, params: Any, customs: Dict[type, Any]) -> Tuple[list, dict]:
        list_params = []
        dict_params = {}

        if isinstance(params, list):
            list_params = params.copy()
        elif isinstance(params, dict):
            dict_params = params.copy()
        else:
            list_params = [params]

        args = []
        kwargs = {}
        recover_allowed = True

        for arg in self.args:
            if arg.is_zipped:
                for param_name in list(dict_params):
                    kwargs[param_name] = arg.validate(dict_params.pop(param_name))
                    recover_allowed = False

                while list_params:
                    args.append(arg.validate(list_params.pop(0)))
                    recover_allowed = False

                continue

            value = customs.get(arg.type, UNSET)

            name = arg.name

            if value is UNSET:
                try:
                    value = arg.validate(
                        dict_params.pop(name, UNSET) if dict_params else list_params.pop(0) if list_params else UNSET
                    )
                except ArgError:
                    if not recover_allowed:
                        raise

                    value = arg.validate(params)

            if arg.is_positional:
                args.append(value)
            else:
                kwargs[name] = value

            recover_allowed = False

        return args, kwargs

    def _in(self, *args, **kwargs) -> Ret:
        args, kwargs = self._validate(*args, **kwargs)
        return self.func(*args, **kwargs)

    def _out(self, ret: Any) -> Any:
        if self.ret:
            try:
                ret = self.ret.validate(ret)
            except ArgError as err:
                raise RetError(err.arg, ret) from err

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

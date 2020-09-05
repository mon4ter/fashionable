from asyncio import iscoroutine
from inspect import Signature
from typing import Callable, Dict, Optional, Tuple

from .arg import Arg
from ..errors import ArgError, InvalidArgError, MissingArgError, RetError, ValidateError
from ..typedef import Args, AsyncRet, Kwargs, Ret, Typing, Value
from ..unset import UNSET
from ..validation import validate

__all__ = [
    'Func',
]


class Func(Signature):
    __slots__ = ('_func', '_name', '_predefined')

    _parameter_cls = Arg

    @classmethod
    def fashionable(cls, func: Callable, name: Optional[str], annotations: Dict[str, Typing]) -> 'Func':
        if not name:
            name = func.__name__

        self = cls.from_callable(func)
        self._func = func
        self._name = name

        for parameter in self.parameters.values():
            parameter._annotation = annotations.get(parameter.name, parameter.annotation)

        return self

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._func = None
        self._name = None
        self._predefined = {}

    def __str__(self) -> str:
        return self._name + super().__str__()

    @property
    def func(self) -> Callable:
        return self._func

    @property
    def name(self) -> str:
        return self._name

    def add_predefined(self, typ: Typing, value: Value):
        self._predefined[typ] = value

    def _validate_arg(self, arg: Arg, value: Value) -> Value:
        if value is UNSET:
            if arg.default is Arg.empty:
                raise MissingArgError(func=self._name, arg=arg.name)
            else:
                value = arg.default
        elif arg.annotation is not Arg.empty:
            try:
                value = validate(arg.annotation, value)
            except ValidateError as exc:
                raise InvalidArgError(func=self._name, arg=arg.name) from exc

        return value

    def _validate(self, args: Args, kwargs: Kwargs) -> Tuple[Args, Kwargs]:
        new_args = []
        new_kwargs = {}
        recover_allowed = True

        list_params = list(args)
        dict_params = dict(kwargs)

        for arg in self.parameters.values():  # type: Arg
            if arg.is_zipped:
                if arg.is_positional:
                    while list_params:
                        new_args.append(self._validate_arg(arg, list_params.pop(0)))
                        recover_allowed = False
                else:
                    for param_name in list(dict_params):
                        new_kwargs[param_name] = self._validate_arg(arg, dict_params.pop(param_name))
                        recover_allowed = False

                continue

            value = self._predefined.get(arg.annotation, UNSET)

            name = arg.name

            if value is UNSET:
                try:
                    value = self._validate_arg(
                        arg,
                        dict_params.pop(name) if name in dict_params else list_params.pop(0) if list_params else UNSET
                    )
                except ArgError:
                    if not recover_allowed:
                        raise

                    # TODO fix recover
                    value = self._validate_arg(arg, *args, **kwargs)

            if arg.is_positional:
                new_args.append(value)
            else:
                new_kwargs[name] = value

            recover_allowed = False

        return tuple(new_args), new_kwargs

    def _in(self, *args, **kwargs) -> Ret:
        args, kwargs = self._validate(args, kwargs)
        return self._func(*args, **kwargs)

    def _out(self, ret: Value) -> Value:
        if self.return_annotation is not Signature.empty:
            try:
                ret = validate(self.return_annotation, ret)
            except ValidateError as err:
                raise RetError(func=self._name) from err

        return ret

    async def _async_out(self, ret: AsyncRet) -> Value:
        return self._out(await ret)

    def __call__(self, *args, **kwargs) -> Ret:
        ret = self._in(*args, **kwargs)

        if iscoroutine(ret):
            ret = self._async_out(ret)
        else:
            ret = self._out(ret)

        return ret

from typing import Callable, Type, TypeAlias
from functools import wraps
from abc import ABC
from enum import Enum

from .connection import get_executor
from .utils import LOGGER
from .javaobj_handler import Server
from .type_dict import TypeDict


CallbackFunction: TypeAlias = Callable[[Server, TypeDict], None]


class Middleman:
    def __init__(self, func: CallbackFunction, info: TypeDict) -> None:
        self.func = func
        self.info = info

    def accept(self, server):
        """This function is called from java side."""
        self.func(Server(server), self.info)

    class Java:
        implements = ["java.util.function.Consumer"]


class DecoratorBase(ABC):
    func: CallbackFunction

    def __call__(self, func: CallbackFunction) -> CallbackFunction:
        self.func = func

        self.wrapped = self._get_wrapper()
        self.modify_when_def()

        return self.wrapped

    def _get_wrapper(self) -> CallbackFunction:

        @wraps(self.func)
        def wrapper(server: Server, info: TypeDict) -> None:
            if self.modify_when_run(server, info):
                self.func(server, info)

        return wrapper

    def modify_when_def(self) -> None:
        pass

    def modify_when_run(self, server: Server, info: TypeDict) -> bool:
        return True


class AtFlag:
    def __rand__(self, value: "Callable[[], AbstractAt]") -> Callable:
        return value() & self


class RunningFlag(Enum, AtFlag):
    ALWAYS = "always"
    ONCE = "once"
    NEVER = "never"


class MaxTimesFlag(AtFlag):
    times: int

    def __init__(self, times: int) -> None:
        self.times = times


class AbstractAt(DecoratorBase):
    at: str
    flag: TypeDict = TypeDict()
    AVAILABLE_FLAGS: list[Type[AtFlag]] = [RunningFlag]

    def __init__(self, at: str, *flags: AtFlag) -> None:
        self.at = at
        for flag in flags:
            self &= flag
        if RunningFlag not in self.flag:
            self.flag[RunningFlag] = RunningFlag.ONCE

    def __and__(self, other: AtFlag) -> "AbstractAt":
        if type(other) not in self.AVAILABLE_FLAGS:
            raise TypeError(
                f"Invalid flag for At class {self.__class__.__name__}:", other
            )

        self.flag[type(other)] = other

        return self

    def __or__(self, other: CallbackFunction) -> "AbstractAt":
        self(other)
        return self

    def modify_when_def(self) -> None:
        for flag_type in At.AVAILABLE_FLAGS:
            if flag_value := self.flag.get(flag_type):
                self._sub_modify_when_def_with_flag(flag_value)

    def _sub_modify_when_def_with_flag(self, flag: AtFlag) -> None:
        pass

    def _get_middleman(self) -> Middleman:
        return Middleman(self.func, self.flag)

    def cancel(self) -> None:
        self.flag[RunningFlag] = RunningFlag.NEVER


class At(AbstractAt):
    def _sub_modify_when_def_with_flag(self, flag: AtFlag) -> None:
        if type(flag) is RunningFlag:
            match flag:
                case RunningFlag.ALWAYS:
                    LOGGER.debug(f"push_continuous {self.wrapped.__name__}")
                    get_executor().push_continuous(self._get_middleman(), self.at)
                case RunningFlag.ONCE:
                    LOGGER.debug(f"push_once {self.wrapped.__name__}")
                    get_executor().push_once(
                        Middleman(self.wrapped, self.flag), self.at
                    )
                case RunningFlag.NEVER:
                    pass
                case _:
                    raise ValueError(f"Should never reached! Invalid flag: {self.flag}")


class After(AbstractAt):
    after: int
    AVAILABLE_FLAGS = [MaxTimesFlag, RunningFlag]

    def __init__(
        self, at: str, after: int, flag: RunningFlag = RunningFlag.ONCE
    ) -> None:
        super().__init__(at, flag)
        self.after = after

    def _sub_modify_when_def_with_flag(self, flag: AtFlag) -> None:
        if type(flag) is MaxTimesFlag:
            if flag.times > 0:
                flag.times -= 1
            else:
                self.cancel()
        elif type(flag) is RunningFlag:
            match flag:
                case RunningFlag.ALWAYS:
                    LOGGER.debug(
                        f"push_scheduled(Ready to repeat) {self.wrapped.__name__}"
                    )
                    get_executor().push_scheduled(
                        self.after, Middleman(self.wrapped, self.flag), self.at
                    )
                case RunningFlag.ONCE:
                    LOGGER.debug(f"push_scheduled(Just once) {self.wrapped.__name__}")
                    get_executor().push_scheduled(
                        self.after, Middleman(self.wrapped, self.flag), self.at
                    )
                case RunningFlag.NEVER:
                    pass
                case _:
                    raise ValueError(f"Should never reached! Invalid flag: {self.flag}")

    def modify_when_run(self, server: Server, info: TypeDict) -> bool:
        if self.flag == RunningFlag.ALWAYS:
            get_executor().push_scheduled(
                self.after, Middleman(self.wrapped, self.flag), self.at
            )
        return True


class AtTick(At):
    def __init__(self, flag: RunningFlag = RunningFlag.ONCE) -> None:
        super().__init__("tick", flag)


class AtTickAfter(After):
    def __init__(self, after: int, flag: RunningFlag = RunningFlag.ONCE) -> None:
        super().__init__("tick", after, flag)

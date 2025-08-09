"""提供装饰器，将回调函数信息传递至java端"""

from typing import Callable, Type, TypeAlias
from functools import wraps
from abc import ABC, abstractmethod
from enum import Enum

from .utils import LOGGER
from .javaobj_handler import Server, NamedAdvancedExecutor
from .type_dict import TypeDict
from .connection import get_executor


CallbackFunction: TypeAlias = Callable[[Server, TypeDict], None]


class Middleman:
    """
    中间人类，用于在Java和Python之间传递回调函数。

    这个类实现了Java的Consumer接口，作为Java调用Python函数的桥梁。
    """

    def __init__(self, func: CallbackFunction, info: TypeDict) -> None:
        """
        初始化Middleman实例。

        Args:
            func (CallbackFunction): 要被调用的Python回调函数
            info (TypeDict): 传递给回调函数的额外信息字典
        """
        self.func = func
        self.info = info

    def accept(self, server):
        """
        Java端调用的方法，用于执行Python回调函数。

        Args:
            server: Java端传入的服务器对象
        """
        self.func(Server(server), self.info)

    class Java:
        """标记为实现Java接口"""

        implements = ["java.util.function.Consumer"]


class DecoratorBase(ABC):
    """
    装饰器基类，为所有装饰器提供基础功能。

    提供装饰器的基本结构，包括包装函数和运行时修改功能。
    """

    func: CallbackFunction
    wrapped: CallbackFunction

    def __call__(self, func: CallbackFunction) -> CallbackFunction:
        """
        使类实例可调用，作为装饰器使用。

        Args:
            func (CallbackFunction): 被装饰的函数

        Returns:
            CallbackFunction: 包装后的函数
        """
        self.func = func

        self.wrapped = self._get_wrapper()
        self.modify_when_def()

        return self.wrapped

    def _get_wrapper(self) -> CallbackFunction:
        """
        创建包装函数，处理函数调用逻辑。

        Returns:
            CallbackFunction: 包装后的函数
        """

        @wraps(self.func)
        def wrapper(server: Server, info: TypeDict) -> None:
            if self.modify_when_run(server, info):
                self.func(server, info)

        return wrapper

    def modify_when_def(self) -> None:
        """
        在装饰器定义时执行的修改操作。

        可以被子类重写以实现特定逻辑。
        """

    @abstractmethod
    def modify_when_run(self, server: Server, info: TypeDict) -> bool:
        """
        在函数运行时执行的修改操作。

        Args:
            server (Server): 服务器实例
            info (TypeDict): 附加信息字典

        Returns:
            bool: 是否继续执行原函数
        """
        return True


class AtFlag:
    """
    标志基类，为装饰器提供各种标志选项的基础类。
    """

    def __rand__(self, value: "Callable[[], AbstractAt]") -> Callable:
        """
        支持 & 操作符，用于将标志应用到装饰器实例。

        Args:
            value (Callable[[], AbstractAt]): 返回AbstractAt实例的可调用对象

        Returns:
            Callable: 应用了标志的装饰器
        """
        return value() & self


class RunningFlag(AtFlag, Enum):
    """
    运行标志枚举，控制装饰器的执行行为。

    Attributes:
        ALWAYS: 持续执行
        ONCE: 只执行一次
        NEVER: 从不执行
    """

    ALWAYS = "always"
    ONCE = "once"
    NEVER = "never"


class MaxTimesFlag(AtFlag):
    """
    最大执行次数标志，限制装饰器的执行次数。

    Attributes:
        times (int): 剩余可执行次数
    """

    times_left: int
    stopped: bool = False

    def __init__(self, times: int) -> None:
        """
        初始化最大执行次数标志。

        Args:
            times (int): 允许执行的最大次数
        """
        self.times_left = times


class AbstractAt(DecoratorBase):
    """
    抽象的At装饰器类，为实现的At装饰器提供基础实现。

    Attributes:
        at (str): 触发装饰器执行的位置
        flag (TypeDict): 存储各种标志的字典
        AVAILABLE_FLAGS (list[Type[AtFlag]]): 当前装饰器支持的标志类型列表
    """

    at: str
    flag: TypeDict = TypeDict()
    executor: NamedAdvancedExecutor
    AVAILABLE_FLAGS: list[Type[AtFlag]] = [RunningFlag]

    def __init__(self, at: str, *flags: AtFlag) -> None:
        """
        初始化AbstractAt实例。

        Args:
            at (str): 触发装饰器执行的位置
            *flags (AtFlag): 应用于装饰器的标志
        """

        self.at = at
        for flag in flags:
            self &= flag
        if RunningFlag not in self.flag:
            self.flag[RunningFlag] = RunningFlag.ONCE

        self.executor = get_executor()

    def __and__(self, other: AtFlag) -> "AbstractAt":
        """
        支持 & 操作符，用于添加标志到装饰器。

        Args:
            other (AtFlag): 要添加的标志

        Returns:
            AbstractAt: 返回自身以支持链式调用
        """
        if type(other) not in self.AVAILABLE_FLAGS:
            raise TypeError(
                f"Invalid flag for At class {self.__class__.__name__}:", other
            )

        self.flag[type(other)] = other

        return self

    def __or__(self, other: CallbackFunction) -> "AbstractAt":
        """
        支持 | 操作符，用于将装饰器应用到函数上。

        Args:
            other (CallbackFunction): 被装饰的函数

        Returns:
            AbstractAt: 返回自身
        """
        self(other)
        return self

    def modify_when_def(self) -> None:
        """
        在装饰器定义时执行，处理所有已设置的标志。
        """
        for flag_type in At.AVAILABLE_FLAGS:
            if flag_value := self.flag.get(flag_type):
                self._sub_modify_when_def_with_flag(flag_value)

    def _sub_modify_when_def_with_flag(self, flag: AtFlag) -> None:
        """
        根据特定标志在装饰器定义时执行相应的操作。

        Args:
            flag (AtFlag): 要处理的标志
        """

    def _get_middleman(self) -> Middleman:
        """
        创建Middleman实例用于Java回调。

        Returns:
            Middleman: 中间人实例
        """
        return Middleman(self.wrapped, self.flag)

    def cancel(self) -> None:
        """
        取消装饰器的执行，将其设置为从不执行。
        """
        self.flag[RunningFlag] = RunningFlag.NEVER


class At(AbstractAt):
    """
    At装饰器，用于在特定位置执行函数。
    """

    def _sub_modify_when_def_with_flag(self, flag: AtFlag) -> None:
        """
        根据运行标志在装饰器定义时注册相应的执行器任务。

        Args:
            flag (AtFlag): 运行标志
        """
        if isinstance(flag, RunningFlag):
            match flag:
                case RunningFlag.ALWAYS:
                    LOGGER.debug("push_continuous %s", self.wrapped.__name__)
                    self.executor.push_continuous(self._get_middleman(), self.at)
                case RunningFlag.ONCE:
                    LOGGER.debug("push_once %s", self.wrapped.__name__)
                    self.executor.push_once(self._get_middleman(), self.at)
                case RunningFlag.NEVER:
                    pass
                case _:
                    raise ValueError(f"Should never reached! Invalid flag: {flag}")
        else:
            raise ValueError(f"Should never reached! Invalid type of flag: {flag}")


class After(AbstractAt):
    """
    After装饰器，在特定位置处，并等待之后一段时间执行函数。

    Attributes:
        after (int): 延迟执行的时间（tick单位）
        AVAILABLE_FLAGS: After装饰器支持的标志类型
    """

    after: int
    AVAILABLE_FLAGS = [MaxTimesFlag, RunningFlag]

    def __init__(
        self, at: str, after: int, flag: RunningFlag = RunningFlag.ONCE
    ) -> None:
        """
        初始化After装饰器实例。

        Args:
            at (str): 触发装饰器执行的位置
            after (int): 延迟执行的时间（tick单位）
            flag (RunningFlag): 运行标志，默认为ONCE
        """
        super().__init__(at, flag)
        self.after = after

    def _sub_modify_when_def_with_flag(self, flag: AtFlag) -> None:
        """
        根据标志在装饰器定义时注册相应的延迟执行任务。

        Args:
            flag (AtFlag): 要处理的标志
        """
        if isinstance(flag, RunningFlag):
            match flag:
                case RunningFlag.ALWAYS:
                    LOGGER.debug(
                        "push_scheduled(Ready to repeat) %s", self.wrapped.__name__
                    )
                    self.executor.push_scheduled(
                        self.after, self._get_middleman(), self.at
                    )
                case RunningFlag.ONCE:
                    LOGGER.debug("push_scheduled(Just once) %s", self.wrapped.__name__)
                    self.executor.push_scheduled(
                        self.after, self._get_middleman(), self.at
                    )
                case RunningFlag.NEVER:
                    pass
                case _:
                    raise ValueError(
                        f"Should never reached! Invalid runing flag: {flag}"
                    )
        else:
            raise ValueError(f"Should never reached! Invalid type of flag: {flag}")

    def modify_when_run(self, server: Server, info: TypeDict) -> bool:
        """
        在函数运行时根据标志决定是否重新安排任务执行。

        Args:
            server (Server): 服务器实例
            info (TypeDict): 附加信息字典

        Returns:
            bool: 是否继续执行原函数
        """

        if flag := self.flag.get(MaxTimesFlag):
            if flag.times_left > 0:
                flag.times_left -= 1
            else:
                flag.stopped = True
                self.cancel()
        if self.flag[RunningFlag] == RunningFlag.ALWAYS:
            self.executor.push_scheduled(self.after, self._get_middleman(), self.at)
        return True


class AtTick(At):
    """
    AtTick装饰器，在每个游戏tick执行函数。
    """

    def __init__(self, flag: RunningFlag = RunningFlag.ONCE) -> None:
        """
        初始化AtTick装饰器实例。

        Args:
            flag (RunningFlag): 运行标志，默认为ONCE
        """
        super().__init__("tick", flag)


class AtTickAfter(After):
    """
    AtTickAfter装饰器，在指定数量的tick之后执行函数。
    """

    def __init__(self, after: int, flag: RunningFlag = RunningFlag.ONCE) -> None:
        """
        初始化AtTickAfter装饰器实例。

        Args:
            after (int): 延迟执行的tick数
            flag (RunningFlag): 运行标志，默认为ONCE
        """
        super().__init__("tick", after, flag)

"""提供装饰器，将回调函数信息传递至java端"""

from typing import Callable, Self, Literal, TypeAlias
from functools import wraps
from abc import ABC
from enum import Enum

from py4j.java_gateway import JavaObject

from .utils import LOGGER
from .javaobj import (
    JavaObjectProxy,
    NamedAdvancedExecutor,
    Middleman,
    Entity,
    Server,
    PymcMngr,
    CallbackFunction,
)
from .type_dict import TypeDict
from .connection import get_gateway


class DecoratorBase[T: JavaObjectProxy](ABC):
    """
    装饰器基类，为所有装饰器提供基础功能。

    提供装饰器的基本结构，包括包装函数和运行时修改功能。
    """

    func: CallbackFunction[T]
    wrapped: CallbackFunction[T]

    def __call__(self, func: CallbackFunction[T]) -> CallbackFunction[T]:
        """
        使类实例可调用，作为装饰器使用。

        Args:
            func (CallbackFunction): 被装饰的函数

        Returns:
            CallbackFunction: 包装后的函数
        """
        self.func = func

        self.wrapped = self._get_wrapper()
        self._modify_when_def()

        return self.wrapped

    def _get_wrapper(self) -> CallbackFunction[T]:
        """
        创建包装函数，处理函数调用逻辑。

        Returns:
            CallbackFunctionBase: 包装后的函数
        """

        @wraps(self.func)
        def wrapper(obj: T, data: TypeDict) -> None:
            if self._modify_before_run(obj):
                self.func(obj, data)
                self._modify_after_run()

        return wrapper

    def _modify_when_def(self) -> None:
        """
        在装饰器定义时执行的修改操作。

        可以被子类重写以实现特定逻辑。
        """

    def _modify_after_run(self) -> None:
        """
        在函数运行时执行的修改操作。

        可以被子类重写以实现特定逻辑。
        """

    def _modify_before_run(self, _obj: T) -> bool:
        """
        在函数运行之前执行的修改操作。

        可以被子类重写以实现特定逻辑。

        返回True则执行函数，返回False则执行函数。
        """
        return True


class AtFlag:
    """
    标志基类，为装饰器提供各种标志选项的基础类。
    """

    def __rand__[T: AbstractAt](
        self, value: Callable[[CallbackFunction], T]
    ) -> Callable[[CallbackFunction], T]:
        """
        支持反向的 & 操作符。

        Args:
            value: 要绑定的 At 类型
        """

        @wraps(value)
        def wrapper(func: CallbackFunction) -> T:
            return value(func) & self

        return wrapper


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

    times_all: int
    times_left: int

    def __init__(self, times: int) -> None:
        """
        初始化最大执行次数标志。

        Args:
            times (int): 允许执行的最大次数
        """
        self.times_left = times
        self.times_all = times

    def step(self, when_stop: Callable[[], None] | None = None):
        """
        执行一次。

        Args:
            when_stop (Callable[[], None] | None, optional): 任务执行完毕时调用的函数。默认为None
        """
        if self.times_left > 0:
            self.times_left -= 1
            if self.times_left == 0:
                if when_stop is not None:
                    when_stop()

    @property
    def stopped(self) -> bool:
        """任务是否已停止"""
        return self.times_left <= 0

    @property
    def the_last(self) -> bool:
        """是否正在执行最后一次"""
        return self.times_left == 1

    @property
    def the_first(self) -> bool:
        """是否正在执行第一次"""
        return self.times_left == self.times_all


class AbstractAt[T: JavaObjectProxy](DecoratorBase[T]):
    """
    抽象的At装饰器类，为实现的At装饰器提供基础实现。

    Attributes:
        at (str): 触发装饰器执行的位置
        flag (TypeDict): 存储各种标志的字典
        AVAILABLE_FLAGS (list[Type[AtFlag]]): 当前装饰器支持的标志类型列表
    """

    at: str
    data: TypeDict
    executor: NamedAdvancedExecutor
    arg_type: type[T]
    AVAILABLE_FLAGS: tuple[type[AtFlag], ...] = (RunningFlag,)

    def __init__(
        self, at: str, *flags: AtFlag, arg_type: type[T] = JavaObjectProxy
    ) -> None:
        """
        初始化AbstractAt实例。

        Args:
            at (str): 触发装饰器执行的位置
            *flags (AtFlag): 应用于装饰器的标志
        """
        self.data = TypeDict()

        self.at = at
        for flag in flags:
            self &= flag

        if RunningFlag not in self.data:
            self.data[RunningFlag] = RunningFlag.ONCE

        if dict not in self.data:
            self.data[dict] = {}

        self.data[type(self)] = self

        self.executor = PymcMngr.from_gateway(get_gateway()).executor

        self.arg_type = arg_type

    def __and__(self, other: AtFlag) -> Self:
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

        self.data[type(other)] = other

        return self

    def __or__(self, other: CallbackFunction[T]) -> Self:
        """
        支持 | 操作符，用于将装饰器应用到函数上。

        Args:
            other (CallbackFunction): 被装饰的函数

        Returns:
            AbstractAt: 返回自身
        """
        self(other)
        return self

    def _get_middleman(self) -> Middleman:
        """
        创建Middleman实例用于Java回调。

        Returns:
            Middleman: 中间人实例
        """
        return Middleman(self.wrapped, self.handle, self.data)

    def handle(self, java_object: JavaObject) -> T:
        """包装java对象"""
        return self.arg_type(java_object, get_gateway())

    def cancel(self) -> None:
        """
        取消装饰器的执行，将其设置为从不执行。
        """
        self.data[RunningFlag] = RunningFlag.NEVER


class At[T: JavaObjectProxy](AbstractAt[T]):
    """
    At装饰器，用于在特定位置执行函数。
    """

    def _modify_when_def(self) -> None:
        match flag := self.data.get(RunningFlag):
            case None:
                pass
            case RunningFlag.ALWAYS:
                LOGGER.info("push_continuous %s", self.wrapped.__name__)
                self.executor.push_continuous(self._get_middleman(), self.at)
            case RunningFlag.ONCE:
                LOGGER.info("push_once %s", self.wrapped.__name__)
                self.executor.push_once(self._get_middleman(), self.at)
            case RunningFlag.NEVER:
                pass
            case _:
                raise ValueError(f"Should never reached! Invalid running flag: {flag}")

    def cancel(self) -> None:
        # TODO: At.cancel()
        super().cancel()
        raise NotImplementedError


class After[T: JavaObjectProxy](AbstractAt[T]):
    """
    After装饰器，在特定位置处，并等待之后一段时间执行函数。

    Attributes:
        after (int): 延迟执行的时间（tick单位）
        AVAILABLE_FLAGS: After装饰器支持的标志类型
    """

    after: int
    AVAILABLE_FLAGS = MaxTimesFlag, RunningFlag

    def __init__(
        self,
        at: str,
        after: int,
        *flags: RunningFlag,
        arg_type: type[T] = JavaObjectProxy,
    ) -> None:
        """
        初始化After装饰器实例。

        Args:
            at (str): 触发装饰器执行的位置
            after (int): 延迟执行的时间（tick单位）
            flag (RunningFlag): 运行标志，默认为ONCE
        """
        super().__init__(at, *flags, arg_type=arg_type)
        self.after = after

    def _modify_when_def(self) -> None:
        match flag := self.data.get(RunningFlag):
            case None:
                pass
            case RunningFlag.ALWAYS:
                LOGGER.info("push_scheduled(Ready to repeat) %s", self.wrapped.__name__)
                self.executor.push_scheduled(self.after, self._get_middleman(), self.at)
            case RunningFlag.ONCE:
                LOGGER.info("push_scheduled(Just once) %s", self.wrapped.__name__)
                self.executor.push_scheduled(self.after, self._get_middleman(), self.at)
            case RunningFlag.NEVER:
                pass
            case _:
                raise ValueError(f"Should never reached! Invalid runing flag: {flag}")

    def _modify_after_run(self) -> None:
        if flag := self.data.get(MaxTimesFlag):
            flag.step(self.cancel)
        if self.data[RunningFlag] == RunningFlag.ALWAYS:
            self.executor.push_scheduled(self.after, self._get_middleman(), self.at)


class AtTick(At[Server]):
    """AtTick装饰器，在每个游戏tick执行函数。"""

    def __init__(self, func: CallbackFunction[Server]) -> None:
        super().__init__("tick", arg_type=Server)
        self(func)


class AtTickAfter(After[Server]):
    """AtTickAfter装饰器，在指定数量的tick之后执行函数。"""

    def __init__(self, after: int, *flags: RunningFlag) -> None:
        """
        初始化AtTickAfter装饰器实例。

        Args:
            after (int): 延迟执行的tick数
            flag (RunningFlag): 运行标志，默认为ONCE
        """
        super().__init__("tick", after, *flags, arg_type=Server)


class AtEntity[T: Entity](At[T]):
    """
    AtEntity装饰器类

    用于实体相关
    """

    Matches: TypeAlias = Literal["name", "uuid"]
    _entity: str | T
    _match: Matches | Callable[[T, str], bool]

    def __init__(
        self,
        at: str,
        entity: str | T,
        *flags: RunningFlag,
        match: Matches | Callable[[T, str], bool] = "name",
    ) -> None:
        super().__init__(f"entity {at}", *flags, arg_type=Entity)

        self._entity = entity
        self.match = match

    def _modify_before_run(self, obj: T) -> bool:
        if isinstance(self._entity, Entity):
            return self._entity.uuid == obj.uuid

        if callable(self.match):
            return self.match(obj, self._entity)

        if self.match == "name":
            return obj.name == self._entity
        if self.match == "uuid":
            return obj.uuid == self._entity

        return False


class AtEntityInteract(AtEntity[Entity]):
    """
    AtEntityInteract装饰器类

    用于在特定实体被交互时执行任务
    """

    def __init__(
        self,
        entity: str | Entity,
        *flags: RunningFlag,
        match: AtEntity.Matches | Callable[[Entity, str], bool] = "name",
    ) -> None:
        super().__init__("interact", entity, *flags, match=match)


class AtEntityTick(AtEntity[Entity]):
    """
    AtEntityTick装饰器类

    用于在特定实体的tick时执行任务
    """

    def __init__(
        self,
        entity: str | Entity,
        *flags: RunningFlag,
        match: AtEntity.Matches | Callable[[Entity, str], bool] = "name",
    ) -> None:
        super().__init__("tick", entity, *flags, match=match)

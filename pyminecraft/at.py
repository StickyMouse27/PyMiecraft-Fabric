"""提供装饰器，将回调函数信息传递至java端"""

from __future__ import annotations

from typing import Callable, Self, Literal, TypeAlias
from functools import wraps
from abc import ABC
from enum import Enum

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


class At[T: JavaObjectProxy](DecoratorBase[T]):
    """At装饰器，用于在特定位置执行函数。"""

    at: str
    data: TypeDict
    executor: NamedAdvancedExecutor
    arg_type: type[T]

    def __init__(
        self,
        at: str,
        *flags: AtFlag,
        arg_type: type[T] = JavaObjectProxy,
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

    def get_middleman(self) -> Middleman:
        """
        创建Middleman实例用于Java回调。

        Returns:
            Middleman: 中间人实例
        """
        return Middleman(
            self.wrapped, lambda obj: self.arg_type(obj, get_gateway()), self.data
        )

    def cancel(self) -> None:
        """
        取消装饰器的执行，将其设置为从不执行。
        """

    def _modify_when_def(self) -> None:
        for flag_type in self.data:
            if issubclass(flag_type, AtFlag):
                self.data[flag_type].on_define(self)

    def _modify_after_run(self) -> None:
        for flag_type in self.data:
            if issubclass(flag_type, AtFlag):
                self.data[flag_type].on_after_run(self)

    def _modify_before_run(self, obj: T) -> bool:
        run = True
        for flag_type in self.data:
            if issubclass(flag_type, AtFlag):
                if not self.data[flag_type].on_before_run(self, obj):
                    run = False
        return run


class AtTick(At[Server]):
    """AtTick装饰器，在每个游戏tick执行函数。"""

    def __init__(self, func: CallbackFunction[Server] | None = None) -> None:
        super().__init__("tick", arg_type=Server)
        if func is not None:
            self(func)


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
        arg_type: type[T] = Entity,
    ) -> None:
        super().__init__(f"entity {at}", *flags, arg_type=arg_type)

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


class AtFlag[T: At]:
    """
    标志基类，为装饰器提供各种标志选项的基础类。
    """

    def __rand__(self, value: Callable[[], T]) -> T:
        """
        支持反向的 & 操作符。

        Args:
            value: 要绑定的 At 类型
        """

        return value() & self

    def on_define(self, _decorator: T) -> None:
        """
        在装饰器定义时执行的操作。

        Args:
            decorator: 关联的装饰器实例
        """

    def on_before_run(self, _decorator: T, _obj: JavaObjectProxy) -> bool:
        """
        在函数运行前执行的操作。

        Args:
            decorator: 关联的装饰器实例
            obj: 传递给回调函数的对象

        Returns:
            bool: True表示继续执行，False表示跳过执行
        """
        return True

    def on_after_run(self, _decorator: T) -> None:
        """
        在函数运行后执行的操作。

        Args:
            decorator: 关联的装饰器实例
        """

    def on_cancel(self, decorator: T) -> None:
        """
        在装饰器取消执行时执行。

        Args:
            decorator: 关联的装饰器实例
        """
        decorator.data[RunningFlag] = RunningFlag.NEVER


class RunningFlag[T: At](AtFlag[T], Enum):
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

    __id: int | None

    def on_define(self, decorator: T) -> None:
        if self == RunningFlag.ALWAYS:
            LOGGER.info("push_continuous %s", decorator.wrapped.__name__)
            __id = decorator.executor.push_continuous(
                decorator.get_middleman(), decorator.at
            )
        elif self == RunningFlag.ONCE:
            LOGGER.info("push_once %s", decorator.wrapped.__name__)
            __id = decorator.executor.push_once(decorator.get_middleman(), decorator.at)
        elif self == RunningFlag.NEVER:
            pass
        else:
            raise ValueError(f"Should never reached! Invalid running flag: {self}")

    def on_cancel(self, decorator: T) -> None:
        if self.__id is not None:
            decorator.executor.remove(self.__id)


class After[T: At](AtFlag[T]):
    """
    After标志，控制装饰器的执行时间。

    Attributes:
        after (int): 延迟执行的tick数
    """

    after: int

    def __init__(self, after: int) -> None:
        """
        初始化After标志。

        Args:
            after (int): 延迟执行的tick数
        """
        self.after = after

    def on_define(self, decorator: T) -> None:
        if self == RunningFlag.ALWAYS:
            LOGGER.info(
                "push_scheduled(Ready to repeat) %s", decorator.wrapped.__name__
            )
            decorator.executor.push_scheduled(
                self.after, decorator.get_middleman(), decorator.at
            )
        elif self == RunningFlag.ONCE:
            LOGGER.info("push_scheduled(Just once) %s", decorator.wrapped.__name__)
            decorator.executor.push_scheduled(
                self.after, decorator.get_middleman(), decorator.at
            )
        elif self == RunningFlag.NEVER:
            pass
        else:
            raise ValueError(f"Should never reached! Invalid runing flag: {self}")

    def on_after_run(self, decorator: T) -> None:
        if decorator.data[RunningFlag] == RunningFlag.ALWAYS:
            decorator.executor.push_scheduled(
                self.after, decorator.get_middleman(), decorator.at
            )


class MaxTimes[T: At](AtFlag[T]):
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

    def step(self) -> bool:
        """
        执行一次。

        Args:
            when_stop (Callable[[], None] | None, optional): 任务执行完毕时调用的函数。默认为None
        """
        if self.times_left > 0:
            self.times_left -= 1
            if self.times_left == 0:
                return False
        return True

    def on_before_run(self, _decorator: T, _obj: JavaObjectProxy) -> bool:
        return self.step()

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

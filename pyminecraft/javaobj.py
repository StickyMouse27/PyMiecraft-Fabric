"""java对象包装类"""

from abc import ABC
from typing import Protocol, overload
from collections.abc import Sequence
from py4j.java_gateway import JavaObject, Py4JError, JavaGateway
from py4j.java_collections import JavaList

# from .utils import LOGGER


class JavaConsumer(Protocol):
    """
    Java Consumer接口的Python协议定义

    用于定义接受服务器对象并执行操作的回调函数接口
    """

    def accept(self, obj: JavaObject) -> None:
        """对应java的accept方法"""


class JavaObjectHandler(ABC):
    """
    Java对象处理器基类

    用于包装Java对象，提供统一的访问接口
    """

    _obj: JavaObject
    _gateway: JavaGateway

    def __init__(self, java_object: JavaObject, java_gateway: JavaGateway):
        """
        初始化Java对象处理器

        Args:
            java_object (JavaObject): 要包装的Java对象
        """
        self._obj = java_object
        self._gateway = java_gateway

    def __bool__(self) -> bool:
        """判断Java对象是否存在"""
        return not self.is_null() and self._obj is not None

    def get_object(self) -> JavaObject:
        """获取Java对象"""
        return self._obj

    def to_string(self) -> str:
        """将Java对象转换为字符串"""
        return str(self._obj)

    def is_null(self) -> bool:
        """检查对象是否为null"""
        if self._obj is None:
            return True
        return self._gateway.jvm.java.util.Objects.isNull(self._obj)  # type: ignore


class JavaListHandler[T: JavaObjectHandler](Sequence[T]):
    """
    Java列表包装类
    """

    _list: JavaList
    _item_handler_type: type[T]
    _gateway: JavaGateway

    def __init__(
        self, java_list: JavaList, java_gateway: JavaGateway, item_handler_type: type[T]
    ):
        """
        初始化Java列表处理器

        Args:
            java_list (JavaList): 要包装的Java列表
            item_handler_type (type[T]): 列表项处理器的类型
        """
        self._list = java_list
        self._item_handler_type = item_handler_type
        self._gateway = java_gateway

    @overload
    def __getitem__(self, index: int) -> T: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[T]: ...

    def __getitem__(self, index: int | slice) -> T | Sequence[T]:
        """
        获取指定索引处的元素

        Args:
            index (int): 元素索引

        Returns:
            T: 指定索引处的元素
        """
        if isinstance(index, slice):
            # 处理切片
            sliced_list = self._list[index]
            return JavaListHandler(sliced_list, self._gateway, self._item_handler_type)
        return self._item_handler_type(self._list[index], self._gateway)

    def __len__(self) -> int:
        """
        返回列表长度

        Returns:
            int: 列表元素数量
        """
        return len(self._list)


class JavaLogger(JavaObjectHandler):
    """
    Java日志记录器包装类

    提供对Java端Logger对象的Python接口访问，支持不同级别的日志记录
    """

    def debug(self, message: str) -> None:
        """
        记录调试级别日志

        Args:
            message (str): 日志消息
        """
        self._obj.debug(message)  # type: ignore

    def info(self, message: str) -> None:
        """
        记录信息级别日志

        Args:
            message (str): 日志消息
        """
        self._obj.info(message)  # type: ignore

    def warn(self, message: str) -> None:
        """
        记录警告级别日志

        Args:
            message (str): 日志消息
        """
        self._obj.warn(message)  # type: ignore

    def error(self, message: str) -> None:
        """
        记录错误级别日志

        Args:
            message (str): 日志消息
        """
        self._obj.error(message)  # type: ignore


class JavaUtils(JavaObjectHandler):
    """
    Java工具类包装

    提供对Java端Utils类的访问，包含MOD_ID和LOGGER等静态属性
    """

    @property
    def logger(self) -> JavaLogger:
        """
        获取Java端日志记录器实例

        Returns:
            JavaLogger: Java日志记录器包装对象
        """
        return JavaLogger(
            self._obj.LOGGER,  # type: ignore
            self._gateway,
        )

    @property
    def mod_id(self) -> str:
        """
        获取模组ID

        Returns:
            str: 模组ID字符串
        """
        return self._obj.MOD_ID  # type: ignore

    def get_command_source(self, name: str) -> JavaObject:
        """
        获取命令源对象

        Args:
            name (str): 命令源名称

        Returns:
            命令源对象
        """

        return self._obj.getCommandSource(name)  # type: ignore

    def send_command(self, command: str, name: str) -> None:
        """
        发送命令

        Args:
            command (str): 命令
        """

        self._obj.sendCommand(command, name)  # type: ignore

    def get_entities(self, selector: str) -> JavaList:
        """
        获取实体对象

        Args:
            selector (str): 选择器

        Returns:
            实体对象
        """

        return self._obj.getEntities(selector)  # type: ignore

    def get_entity(self, selector: str) -> JavaObject:
        """
        获取实体对象

        Args:
            selector (str): 选择器

        Returns:
            实体对象
        """

        return self._obj.getEntity(selector)  # type: ignore


# 未使用
# class NamedExecutor(JavaObjectHandler):
#     """
#     Java命名执行器包装类

#     对应Java端NamedExecutor类，用于在特定时间点执行命名任务
#     """

#     def push(self, tick: int, callback: JavaConsumer, name: str) -> None:
#         """
#         添加一个在指定tick执行的命名任务

#         Args:
#             tick (int): 执行的tick时间点
#             callback (JavaConsumer): 回调函数
#             name (str): 任务名称
#         """
#         self._obj.push(tick, callback, name)  # type: ignore


# This object inherits from JavaObjectHandler but not NamedExecutor
# because we don't want a push function interfere with the developers.
class NamedAdvancedExecutor(JavaObjectHandler):
    """
    Java高级命名执行器包装类

    对应Java端NamedAdvancedExecutor类，提供更丰富的任务调度功能，
    包括计划任务、连续任务和一次性任务
    """

    def push_scheduled(self, tick: int, callback: JavaConsumer, name: str) -> None:
        """
        添加一个计划任务，在指定tick执行一次

        Args:
            tick (int): 执行的tick时间点（相对当前tick）
            callback (JavaConsumer): 回调函数
            name (str): 任务名称
        """
        self._obj.pushScheduled(tick, callback, name)  # type: ignore

    def push_continuous(self, callback: JavaConsumer, name: str) -> None:
        """
        添加一个连续任务，每个tick都会执行

        Args:
            callback (JavaConsumer): 回调函数
            name (str): 任务名称
        """
        self._obj.pushContinuous(callback, name)  # type: ignore

    def push_once(self, callback: JavaConsumer, name: str) -> None:
        """
        添加一个一次性任务，在下一个匹配的tick执行后自动移除

        Args:
            callback (JavaConsumer): 回调函数
            name (str): 任务名称
        """
        self._obj.pushOnce(callback, name)  # type: ignore


class Entity(JavaObjectHandler):
    """对应net.minecraft.entity.Entity"""

    @property
    def name(self) -> str:
        """获取实体名称"""
        return self._obj.getName().getString()  # type: ignore

    @property
    def uuid(self) -> str:
        """获取实体UUID"""
        raise NotImplementedError  # TODO

    def move(self, movement: tuple[float, float, float]):
        """net.minecraft.entity.Entity.move"""
        raise NotImplementedError  # TODO


class Server(JavaObjectHandler):
    """
    面向用户的Minecraft服务器对象包装类

    提供对Minecraft服务器实例的访问接口，包括命令执行和日志记录功能
    """

    logger: JavaLogger
    _utlis: JavaUtils

    def __init__(
        self, server: JavaObject, java_gateway: JavaGateway, java_utlis: JavaUtils
    ) -> None:
        """
        初始化服务器包装对象

        Args:
            server (JavaObject): Minecraft服务器Java对象
        """

        super().__init__(server, java_gateway)
        self._utlis = java_utlis
        self.logger = self._utlis.logger

    def cmd(self, command: str, name: str = "PYMC"):
        """
        执行Minecraft命令

        Args:
            str (str): 要执行的命令字符串
        """
        source = self._utlis.get_command_source(name)
        self._obj.getCommandManager().executeWithPrefix(source, command)  # type: ignore

    def log(self, msg: str):
        """
        记录信息日志

        等效于 server.logger.info

        Args:
            msg (str): 日志消息
        """
        self.logger.info(msg)

    def get_entities(self, selector: str = "@e") -> JavaListHandler[Entity]:
        """
        获取指定实体

        Args:
            selector (str): 命令方块中的实体选择器
        """
        return JavaListHandler(
            self._utlis.get_entities(selector), self._gateway, Entity
        )

    def get_entity(self, selector: str = "@e") -> Entity | None:
        """
        获取指定实体（只返回第一个）

        Args:
            selector (str, optional): 命令方块中的实体选择器. Defaults to "@e".

        Returns:
            Entity | None: 返回选中的实体，如果没有，则返回None
        """
        entity = self._utlis.get_entity(selector)
        return Entity(entity, self._gateway) if entity else None

"""java对象包装类"""

from abc import ABC
from typing import Callable, overload, Any, TypeAlias, TypeVar, Self
from collections.abc import Sequence
from py4j.java_gateway import JavaObject, JavaGateway
from py4j.java_collections import JavaList

from .type_dict import TypeDict


class JavaClassFactory:
    """提供java类实例化方法"""

    gateway: JavaGateway

    def __init__(self, gateway: JavaGateway) -> None:
        self.gateway = gateway

    def new(self, clazz: str, *args: Any) -> JavaObject:
        """根据类名实例化java类"""
        return getattr(self.gateway.jvm, clazz)(*args)  # type: ignore

    def get_static(self, clazz: str, field: str) -> JavaObject:
        """获取静态类实例"""
        return getattr(getattr(self.gateway.jvm, clazz), field)

    def new_handled[T: JavaObjectHandler](
        self, clazz: str, handle_class: type[T], *args: Any
    ) -> T:
        """根据类名实例化java类并使用handle_class处理"""
        return handle_class(self.new(clazz, *args), self.gateway)

    def v3d(self, v: tuple[float, float, float]) -> JavaObject:
        """创建Vec3d对象 net.minecraft.util.math.Vec3d"""
        return self.new("net.minecraft.util.math.Vec3d", *(float(w) for w in v))


class JavaObjectHandler(ABC):
    """
    Java对象处理器基类

    用于包装Java对象，提供统一的访问接口
    """

    obj: JavaObject
    gateway: JavaGateway
    class_factory: JavaClassFactory

    def __init__(self, java_object: JavaObject, java_gateway: JavaGateway):
        """
        初始化Java对象处理器

        Args:
            java_object (JavaObject): 要包装的Java对象
        """
        self.obj = java_object
        self.gateway = java_gateway
        self.class_factory = JavaClassFactory(java_gateway)

    @classmethod
    def default_handle(cls, java_object: JavaObject, java_gateway: JavaGateway) -> Self:
        """返回默认实现"""
        return cls(java_object, java_gateway)

    def __bool__(self) -> bool:
        """判断Java对象是否存在"""
        return not self.is_null() and self.obj is not None

    def get_object(self) -> JavaObject:
        """获取Java对象"""
        return self.obj

    def to_string(self) -> str:
        """将Java对象转换为字符串"""
        return str(self.obj)

    def is_null(self) -> bool:
        """检查对象是否为null"""
        if self.obj is None:
            return True
        return self.gateway.jvm.java.util.Objects.isNull(self.obj)  # type: ignore


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
        self.obj.debug(message)  # type: ignore

    def info(self, message: str) -> None:
        """
        记录信息级别日志

        Args:
            message (str): 日志消息
        """
        self.obj.info(message)  # type: ignore

    def warn(self, message: str) -> None:
        """
        记录警告级别日志

        Args:
            message (str): 日志消息
        """
        self.obj.warn(message)  # type: ignore

    def error(self, message: str) -> None:
        """
        记录错误级别日志

        Args:
            message (str): 日志消息
        """
        self.obj.error(message)  # type: ignore


V = TypeVar("V", bound=JavaObjectHandler)
CallbackFunction: TypeAlias = Callable[[V, TypeDict], None]


class Middleman[T: JavaObjectHandler]:
    """
    中间人类，用于在Java和Python之间传递回调函数。

    这个类实现了Java的Consumer接口，作为Java调用Python函数的桥梁。
    """

    def __init__(
        self,
        func: CallbackFunction[T],
        handler: Callable[[JavaObject], T],
        data: TypeDict,
    ) -> None:
        """
        初始化Middleman实例。

        Args:
            func (CallbackFunction): 要被调用的Python回调函数
            info (TypeDict): 传递给回调函数的额外信息字典
        """
        self.func: CallbackFunction[T] = func
        self.data = data
        self.handler = handler

    def accept(self, obj: JavaObject) -> None:
        """
        Java端调用的方法，用于执行Python回调函数。

        Args:
            server: Java端传入的服务器对象
        """
        self.func(self.handle(obj), self.data)

    def handle(self, java_object: JavaObject) -> T:
        """包装JavaObject"""
        return self.handler(java_object)

    class Java:
        """标记为实现Java接口"""

        implements = ["java.util.function.Consumer"]


class PymcMngr(JavaObjectHandler):
    """top.fish1000.pymcfabric.PymcMngr"""

    @staticmethod
    def from_gateway(gateway: JavaGateway):
        return PymcMngr(gateway.entry_point, gateway)

    @property
    def logger(self) -> JavaLogger:
        """
        获取Java端日志记录器实例

        Returns:
            JavaLogger: Java日志记录器包装对象
        """
        return JavaLogger(
            self.obj.LOGGER,  # type: ignore
            self.gateway,
        )

    @property
    def mod_id(self) -> str:
        """
        获取模组ID

        Returns:
            str: 模组ID字符串
        """
        return self.obj.MOD_ID  # type: ignore

    def get_command_source(self, name: str) -> JavaObject:
        """
        获取命令源对象

        Args:
            name (str): 命令源名称

        Returns:
            命令源对象
        """

        return self.obj.getCommandSource(name)  # type: ignore

    def send_command(self, command: str, name: str) -> None:
        """
        发送命令

        Args:
            command (str): 命令
        """

        self.obj.sendCommand(command, name)  # type: ignore

    def get_entities(self, selector: str) -> JavaList:
        """
        获取实体对象

        Args:
            selector (str): 选择器

        Returns:
            实体对象
        """

        return self.obj.getEntities(selector)  # type: ignore

    def get_entity(self, selector: str) -> JavaObject:
        """
        获取实体对象

        Args:
            selector (str): 选择器

        Returns:
            实体对象
        """

        return self.obj.getEntity(selector)  # type: ignore

    @property
    def server(self) -> "Server":
        """获取服务器对象"""

        return Server(
            self.obj.server,  # type: ignore
            self.gateway,
        )

    @property
    def executor(self) -> "NamedAdvancedExecutor":
        """获取执行器对象"""

        return NamedAdvancedExecutor(self.obj.executor, self.gateway)  # type: ignore


class NamedAdvancedExecutor(JavaObjectHandler):
    """
    Java高级命名执行器包装类

    对应Java端NamedAdvancedExecutor类，提供更丰富的任务调度功能，
    包括计划任务、连续任务和一次性任务
    """

    def push_scheduled(self, tick: int, callback: Middleman, name: str) -> None:
        """
        添加一个计划任务，在指定tick执行一次

        Args:
            tick (int): 执行的tick时间点（相对当前tick）
            callback (Middleman): 回调函数
            name (str): 任务名称
        """
        self.obj.pushScheduled(tick, callback, name)  # type: ignore

    def push_continuous(self, callback: Middleman, name: str) -> None:
        """
        添加一个连续任务，每个tick都会执行

        Args:
            callback (JavaConsumer): 回调函数
            name (str): 任务名称
        """
        self.obj.pushContinuous(callback, name)  # type: ignore

    def push_once(self, callback: Middleman, name: str) -> None:
        """
        添加一个一次性任务，在下一个匹配的tick执行后自动移除

        Args:
            callback (JavaConsumer): 回调函数
            name (str): 任务名称
        """
        self.obj.pushOnce(callback, name)  # type: ignore


class Entity(JavaObjectHandler):
    """对应net.minecraft.entity.Entity"""

    @property
    def name(self) -> str:
        """获取实体名称"""
        return self.obj.getName().getString()  # type: ignore

    @property
    def uuid(self) -> str:
        """获取实体UUID"""
        return self.obj.getUuidAsString()  # type: ignore

    def move(self, movement: tuple[float, float, float]):
        """net.minecraft.entity.Entity.move"""
        movement_type = self.class_factory.get_static(
            "net.minecraft.entity.MovementType", "SELF"
        )
        movement_obj = self.class_factory.v3d(movement)
        self.obj.move(movement_type, movement_obj)  # type: ignore


class Server(JavaObjectHandler):
    """
    面向用户的Minecraft服务器对象包装类
    net.minecraft.server.MinecraftServer

    提供对Minecraft服务器实例的访问接口，包括命令执行和日志记录功能
    """

    logger: JavaLogger
    mngr: PymcMngr

    def __init__(self, server: JavaObject, java_gateway: JavaGateway) -> None:
        super().__init__(server, java_gateway)
        self.mngr = PymcMngr.from_gateway(java_gateway)
        self.logger = self.mngr.logger

    def cmd(self, command: str, name: str = "PYMC"):
        """
        执行Minecraft命令

        Args:
            str (str): 要执行的命令字符串
        """
        source = self.mngr.get_command_source(name)
        self.obj.getCommandManager().executeWithPrefix(source, command)  # type: ignore

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
        return JavaListHandler(self.mngr.get_entities(selector), self.gateway, Entity)

    def get_entity(self, selector: str = "@e") -> Entity | None:
        """
        获取指定实体（只返回第一个）

        Args:
            selector (str, optional): 命令方块中的实体选择器. Defaults to "@e".

        Returns:
            Entity | None: 返回选中的实体，如果没有，则返回None
        """
        entity = self.mngr.get_entity(selector)
        return Entity(entity, self.gateway) if entity else None

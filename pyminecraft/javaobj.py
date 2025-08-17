"""java对象包装类"""

from __future__ import annotations

from abc import ABC
from typing import Callable, overload, Any, TypeAlias, TypeVar
from collections.abc import Sequence
from py4j.java_gateway import JavaObject, JavaGateway, get_field
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

    def new_handled[T: JavaObjectProxy](
        self, clazz: str, handle_class: type[T], *args: Any
    ) -> T:
        """根据类名实例化java类并使用handle_class处理"""
        return handle_class(self.new(clazz, *args), self.gateway)

    def v3d(self, v: tuple[float, float, float]) -> JavaObject:
        """创建Vec3d对象 net.minecraft.util.math.Vec3d"""
        return self.new("net.minecraft.util.math.Vec3d", *(float(w) for w in v))


class JavaObjectProxy(ABC):
    """
    Java对象代理基类

    用于包装Java对象，提供统一的访问接口
    """

    obj: JavaObject
    gateway: JavaGateway

    def __init__(self, java_object: JavaObject, java_gateway: JavaGateway):
        """
        初始化Java对象代理

        Args:
            java_object (JavaObject): 要包装的Java对象
        """
        self.obj = java_object
        self.gateway = java_gateway
        self.class_factory = JavaClassFactory(java_gateway)

    @property
    def mngr(self) -> PymcMngr:
        """获取pymc管理器"""
        if isinstance(self, PymcMngr):
            return self

        return PymcMngr.from_gateway(self.gateway)

    def proxy[T](self, obj: Any, cls: type[T]) -> T:
        """
        获取代理对象

        Args:
            obj: Java对象
            cls: 代理对象类型

        Returns:
            代理对象
        """
        if isinstance(obj, cls):
            return obj

        if not issubclass(cls, JavaObjectProxy):
            raise TypeError(f"{cls} is not a JavaObjectProxy and {obj} is not a {cls}")

        return cls(obj, self.gateway)  # 元素是 JavaObject ，使用cls包装

    def proxy_list[T](self, obj: Any, cls: type[T]) -> JavaListProxy[T]:
        """列表代理"""
        return JavaListProxy(obj, self.gateway, cls)

    @overload
    def call[T](self, path: str, cls: type[T], *args: Any) -> T: ...
    @overload
    def call(self, path: str, cls: None, *args: Any) -> None: ...

    def call[T](self, path: str, cls: type[T] | None, *args: Any) -> T | None:
        """
        调用指定路径的方法

        Args:
            path: 方法路径
            cls: 返回值类型
            *args: 方法参数

        Returns:
            返回值
        """

        func: Callable = getattr(self.obj, path)
        if not callable(func):
            raise TypeError(f"{path} is not a function")

        obj: Any = func(*args)

        if obj is None and cls is None:
            return None

        if cls is None or obj is None:
            raise TypeError(f"{path} not return type {cls} but {type(obj)}")

        return self.proxy(obj, cls)

    def call_list[T](self, path: str, cls: type[T], *args: Any) -> JavaListProxy[T]:
        """
        调用指定路径的方法（返回列表）

        Args:
            path: 方法路径
            cls: 返回值类型
            *args: 方法参数

        Returns:
            列表返回值
        """
        return self.new_list(self.call(path, JavaList, *args), cls)

    def get[T](self, path: str, cls: type[T]) -> T:
        """
        从Java对象中获取指定路径的值

        Args:
            cls (type[T]): 如果是java对象代理类，就返回对应的Java对象代理；否则判断并直接返回值
            path (str): 要获取的值

        Returns:
            T: 生成的Java对象代理
        """
        return self.proxy(get_field(self.obj, path), cls)

    def get_list[T](self, path: str, cls: type[T]) -> JavaListProxy[T]:
        """从Java对象中获取指定路径的列表

        Args:
            cls (type[T]): 列表中元素的类型
            path (str): 要获取的列表

        Returns:
            JavaListProxy[T]: 生成的Java列表代理
        """
        return self.proxy_list(get_field(self.obj, path), cls)

    def new_list[T](self, java_list: JavaList, cls: type[T]) -> JavaListProxy[T]:
        """
        生成Java对象列表代理

        Args:
            cls (type[T]): 要生成的Java对象列表代理类
            java_list (JavaList): 要包装的Java对象列表

        Returns:
            T: 生成的Java对象列表代理
        """
        return JavaListProxy(java_list, self.gateway, cls)

    def __bool__(self) -> bool:
        """判断Java对象是否存在"""
        return not self.is_null()

    def get_object(self) -> JavaObject:
        """获取Java对象"""
        return self.obj

    def __str__(self) -> str:
        """将Java对象转换为字符串"""
        return str(self.obj)

    def is_null(self) -> bool:
        """检查对象是否为null"""
        if self.obj is None:
            return True
        return self.gateway.jvm.java.util.Objects.isNull(self.obj)  # type: ignore


class JavaListProxy[T](JavaObjectProxy, Sequence[T]):
    """
    Java列表包装类
    """

    _list: JavaList
    _item_handler_type: type[T]

    def __init__(
        self,
        java_list: JavaList,
        java_gateway: JavaGateway,
        item_handler_type: type[T],
    ):
        """
        初始化Java列表代理

        Args:
            java_list (JavaList): 要包装的Java列表
            item_handler_type (type[T]): 列表项代理的类型
        """
        super().__init__(java_list, java_gateway)
        self._list = java_list
        self._item_handler_type = item_handler_type

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
            return JavaListProxy(sliced_list, self.gateway, self._item_handler_type)
        return (
            self._item_handler_type(self._list[index], self.gateway)
            if issubclass(self._item_handler_type, JavaObjectProxy)
            else self._list[index]
        )

    def __len__(self) -> int:
        """
        返回列表长度

        Returns:
            int: 列表元素数量
        """
        return len(self._list)


class PymcMngr(JavaObjectProxy):
    """top.fish1000.pymcfabric.PymcMngr"""

    @staticmethod
    def from_gateway(gateway: JavaGateway) -> PymcMngr:
        """从gateway中获取PymcMngr实例"""
        return PymcMngr(gateway.entry_point, gateway)

    @property
    def mod_id(self) -> str:
        """
        获取模组ID

        Returns:
            str: 模组ID字符串
        """
        return self.get("MOD_ID", str)

    @property
    def logger(self) -> JavaLogger:
        """
        获取Java端日志记录器实例

        Returns:
            JavaLogger: Java日志记录器包装对象
        """
        return self.get("LOGGER", JavaLogger)

    @property
    def server(self) -> Server:
        """获取服务器对象"""

        return self.get("server", Server)

    @property
    def executor(self) -> NamedAdvancedExecutor:
        """获取执行器对象"""

        return self.get("executor", NamedAdvancedExecutor)

    def get_command_source(self, name: str) -> JavaObject:
        """
        获取命令源对象

        Args:
            name (str): 命令源名称

        Returns:
            命令源对象
        """

        return self.call("getCommandSource", JavaObject, name)

    def send_command(self, command: str, name: str) -> None:
        """
        发送命令

        Args:
            command (str): 命令
        """

        self.call("sendCommand", None, command, name)

    def get_entities(self, selector: str) -> JavaListProxy[Entity]:
        """
        获取实体对象

        Args:
            selector (str): 选择器

        Returns:
            实体对象
        """

        return self.call_list("getEntities", Entity, selector)

    def log(self, msg: str):
        """PymcMngr.logger.info方法的别名"""
        self.logger.info(msg)


class JavaLogger(JavaObjectProxy):
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
        self.call("debug", None, message)

    def info(self, message: str) -> None:
        """
        记录信息级别日志

        Args:
            message (str): 日志消息
        """
        self.call("info", None, message)

    def warn(self, message: str) -> None:
        """
        记录警告级别日志

        Args:
            message (str): 日志消息
        """
        self.call("warn", None, message)

    def error(self, message: str) -> None:
        """
        记录错误级别日志

        Args:
            message (str): 日志消息
        """
        self.call("error", None, message)


V = TypeVar("V", bound=JavaObjectProxy)
CallbackFunction: TypeAlias = Callable[[V, TypeDict], None]


class Middleman[T: JavaObjectProxy]:
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


class NamedAdvancedExecutor(JavaObjectProxy):
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
        self.call("pushScheduled", None, tick, callback, name)

    def push_continuous(self, callback: Middleman, name: str) -> None:
        """
        添加一个连续任务，每个tick都会执行

        Args:
            callback (JavaConsumer): 回调函数
            name (str): 任务名称
        """
        self.call("pushContinuous", None, callback, name)

    def push_once(self, callback: Middleman, name: str) -> None:
        """
        添加一个一次性任务，在下一个匹配的tick执行后自动移除

        Args:
            callback (JavaConsumer): 回调函数
            name (str): 任务名称
        """
        self.call("pushOnce", None, callback, name)


class Entity(JavaObjectProxy):
    """对应net.minecraft.entity.Entity"""

    @property
    def name(self) -> str:
        """获取实体名称"""
        # return self.obj.getName().getString()  # type: ignore
        return self.call("getName", JavaObjectProxy).call("getString", str)

    @property
    def uuid(self) -> str:
        """获取实体UUID"""
        # return self.obj.getUuidAsString()  # type: ignore
        return self.call("getUuidAsString", str)

    def move(self, movement: tuple[float, float, float]):
        """移动一个实体"""
        x = float(movement[0] + self.call("getX", float))
        y = float(movement[1] + self.call("getY", float))
        z = float(movement[2] + self.call("getZ", float))
        self.call("setPosition", None, x, y, z)


class Server(JavaObjectProxy):
    """
    面向用户的Minecraft服务器对象包装类
    net.minecraft.server.MinecraftServer

    提供对Minecraft服务器实例的访问接口，包括命令执行和日志记录功能
    """

    def cmd(self, command: str, name: str = "PYMC"):
        """
        执行Minecraft命令

        Args:
            str (str): 要执行的命令字符串
        """
        source = self.mngr.get_command_source(name)
        # self.obj.getCommandManager().executeWithPrefix(source, command)  # type: ignore
        self.call("getCommandManager", JavaObjectProxy).call(
            "executeWithPrefix", None, source, command
        )

    def get_entities(self, selector: str = "@e") -> JavaListProxy[Entity]:
        """
        获取指定实体

        Args:
            selector (str): 命令方块中的实体选择器
        """
        return self.mngr.get_entities(selector)

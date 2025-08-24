"""java对象包装类"""

from __future__ import annotations

from typing import Callable, overload, Any, TypeAlias, TypeVar, Literal, Iterable, Self
from collections.abc import Sequence

from py4j.java_gateway import JavaObject, JavaGateway, get_field
from py4j.java_collections import JavaList

from .type_dict import TypeDict


class JavaObjectProxy:
    """
    Java对象代理基类

    用于包装Java对象，提供统一的访问接口
    """

    _obj: JavaObject
    _gateway: JavaGateway

    def __init__(self, java_object: JavaObject, java_gateway: JavaGateway):
        """
        初始化Java对象代理

        Args:
            java_object (JavaObject): 要包装的Java对象
        """
        self._obj = java_object
        self._gateway = java_gateway

    @property
    def mngr(self) -> PymcMngr:
        """获取pymc管理器"""
        if isinstance(self, PymcMngr):
            return self

        return PymcMngr.from_gateway(self._gateway)

    @property
    def class_factory(self) -> JavaClassFactory:
        """获取JavaGateway实例"""
        if isinstance(self, JavaClassFactory):
            return self

        return JavaClassFactory(self._obj, self._gateway)

    @property
    def obj(self) -> JavaObject:
        """获取Java对象"""
        return self._obj

    @property
    def gateway(self) -> JavaGateway:
        """获取Java对象对应的JavaGateway"""
        return self._gateway

    @overload
    def proxy(self, obj: JavaObject) -> JavaObjectProxy: ...

    @overload
    def proxy[T](self, obj: Any, cls: type[T]) -> T: ...
    @overload
    def proxy[T](self, obj: Any, cls: type[T] | None) -> T | JavaObjectProxy: ...
    def proxy[T](self, obj: Any, cls: type[T] | None = None) -> T | JavaObjectProxy:
        """
        获取代理对象

        Args:
            obj: Java对象
            cls: 代理对象类型

        Returns:
            代理对象
        """
        if cls is None:
            return JavaObjectProxy(obj, self._gateway)

        if isinstance(obj, cls):
            return obj

        if not issubclass(cls, JavaObjectProxy):
            raise TypeError(f"{cls} is not a JavaObjectProxy and {obj} is not a {cls}")

        return cls(obj, self._gateway)  # 元素是 JavaObject ，使用cls包装

    def proxy_list[T](self, obj: Any, cls: type[T]) -> JavaListProxy[T]:
        """列表代理"""
        return JavaListProxy(obj, self._gateway, cls)

    @overload
    def call[T](self, path: str, args: Iterable[Any], ret: type[T]) -> T: ...
    @overload
    def call(self, path: str, args: Iterable[Any], ret: None) -> None: ...

    @overload
    def call(self, path: str, args: Iterable[Any] = ()) -> JavaObjectProxy: ...

    def call[T](
        self,
        path: str,
        args: Iterable[Any] = (),
        ret: type[T] | None | Literal["JavaObjectProxy"] = "JavaObjectProxy",
    ) -> T | JavaObjectProxy | None:
        """
        调用指定路径的方法

        Args:
            path: 方法路径
            cls: 返回值类型
            *args: 方法参数

        Returns:
            返回值
        """

        func: Callable = getattr(self._obj, path)
        if not callable(func):
            raise TypeError(f"{path} is not a function")

        obj: Any = func(
            *(arg.obj if isinstance(arg, JavaObjectProxy) else arg for arg in args)
        )  # 如果是包装后的，则使用本身

        if obj is None and ret is None:
            return None

        if ret is None or obj is None:
            raise TypeError(f"{path} not return type {ret} but {type(obj)}")

        return self.proxy(obj, JavaObjectProxy if ret == "JavaObjectProxy" else ret)

    @overload
    def call_list[T](
        self, path: str, args: Iterable[Any], ret: type[T]
    ) -> JavaListProxy[T]: ...

    @overload
    def call_list(
        self, path: str, args: Iterable[Any] = ()
    ) -> JavaListProxy[JavaObjectProxy]: ...
    def call_list[T](
        self, path: str, args: Iterable[Any] = (), ret: type[T] | None = None
    ) -> JavaListProxy[T] | JavaListProxy[JavaObjectProxy]:
        """
        调用指定路径的方法（返回列表）

        Args:
            path: 方法路径
            cls: 返回值类型
            *args: 方法参数

        Returns:
            列表返回值
        """
        if ret is None:
            return self.new_list(self.call(path, args, JavaList))
        return self.new_list(self.call(path, args, JavaList), ret)

    @overload
    def get(self, path: str) -> JavaObjectProxy: ...

    @overload
    def get[T](self, path: str, cls: type[T]) -> T: ...

    @overload
    def get[T](self, path: str, cls: type[T] | None = None) -> T | JavaObjectProxy: ...

    def get[T](self, path: str, cls: type[T] | None = None) -> T | JavaObjectProxy:
        """
        从Java对象中获取指定路径的值

        Args:
            cls (type[T]): 如果是java对象代理类，就返回对应的Java对象代理；否则判断并直接返回值
            path (str): 要获取的值

        Returns:
            T: 生成的Java对象代理
        """
        return self.proxy(get_field(self._obj, path), cls)

    def get_list[T](self, path: str, cls: type[T]) -> JavaListProxy[T]:
        """从Java对象中获取指定路径的列表

        Args:
            cls (type[T]): 列表中元素的类型
            path (str): 要获取的列表

        Returns:
            JavaListProxy[T]: 生成的Java列表代理
        """
        return self.proxy_list(get_field(self._obj, path), cls)

    @overload
    def new_list[T](self, java_list: JavaList, cls: type[T]) -> JavaListProxy[T]: ...

    @overload
    def new_list(self, java_list: JavaList) -> JavaListProxy[JavaObjectProxy]: ...

    def new_list[T](
        self, java_list: JavaList, cls: type[T] | None = None
    ) -> JavaListProxy[T] | JavaListProxy[JavaObjectProxy]:
        """
        生成Java对象列表代理

        Args:
            cls (type[T]): 要生成的Java对象列表代理类
            java_list (JavaList): 要包装的Java对象列表

        Returns:
            T: 生成的Java对象列表代理
        """
        if cls is None:
            return JavaListProxy(java_list, self._gateway, JavaObjectProxy)
        return JavaListProxy(java_list, self._gateway, cls)

    def __bool__(self) -> bool:
        """判断Java对象是否存在"""
        return not self.is_null()

    def __str__(self) -> str:
        """将Java对象转换为字符串"""
        return str(self._obj)

    def is_null(self) -> bool:
        """检查对象是否为null"""
        if self._obj is None:
            return True
        return self.class_factory.call_static("java.util.Objects.isNull", (self,), bool)


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
            return JavaListProxy(sliced_list, self._gateway, self._item_handler_type)
        return (
            self._item_handler_type(self._list[index], self._gateway)
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


class JavaClassFactory(JavaObjectProxy):
    """提供java类实例化方法 此类内的路径为绝对路径"""

    @staticmethod
    def __phrase(clazz: str):
        return clazz.rpartition(".")

    @overload
    def new(self, clazz: str, args: Iterable[Any] = ()) -> JavaObjectProxy: ...
    @overload
    def new[T](self, clazz: str, args: Iterable[Any], cls: type[T]) -> T: ...
    @overload
    def new[T](
        self, clazz: str, args: Iterable[Any], cls: type[T] | None = None
    ) -> T | JavaObjectProxy: ...
    def new[T](
        self, clazz: str, args: Iterable[Any] = (), cls: type[T] | None = None
    ) -> T | JavaObjectProxy:
        """根据类名实例化java类"""
        return self.call_static(clazz, args, cls)

    @overload
    def get_static(self, clazz: str) -> JavaObjectProxy: ...
    @overload
    def get_static[T](self, clazz: str, cls: type[T]) -> T: ...
    @overload
    def get_static[T](
        self, clazz: str, cls: type[T] | None = None
    ) -> T | JavaObjectProxy: ...
    def get_static[T](
        self, clazz: str, cls: type[T] | None = None
    ) -> T | JavaObjectProxy:
        """获取静态类实例"""
        path, _, field = self.__phrase(clazz)
        return self.proxy(getattr(getattr(self._gateway.jvm, path), field), cls)

    @overload
    def call_static(self, clazz: str, args: Iterable[Any]) -> JavaObjectProxy: ...
    @overload
    def call_static[T](self, clazz: str, args: Iterable[Any], cls: type[T]) -> T: ...
    @overload
    def call_static[T](
        self, clazz: str, args: Iterable[Any], cls: type[T] | None = None
    ) -> T | JavaObjectProxy: ...
    def call_static[T](
        self, clazz: str, args: Iterable[Any], cls: type[T] | None = None
    ) -> T | JavaObjectProxy:
        """调用静态方法"""
        path, _, method = self.__phrase(clazz)
        return self.proxy(
            getattr(getattr(self._gateway.jvm, path), method)(
                *(arg.obj if isinstance(arg, JavaObjectProxy) else arg for arg in args)
            ),
            cls,
        )


V = TypeVar("V", bound=JavaObjectProxy)
CallbackFunction: TypeAlias = Callable[[V, TypeDict], None]
V3dTup: TypeAlias = tuple[float, float, float]
V3iTup: TypeAlias = tuple[int, int, int]
RotTup: TypeAlias = tuple[float, float]
PosRotTup: TypeAlias = tuple[float, float, float, float, float]


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

    def get_command_source(self, name: str = "PYMC") -> JavaObjectProxy:
        """
        获取命令源对象

        Args:
            name (str): 命令源名称

        Returns:
            命令源对象
        """

        return self.call("getCommandSource", (name,))

    def send_command(self, command: str, name: str) -> None:
        """
        发送命令

        Args:
            command (str): 命令
        """

        self.call("sendCommand", (command, name), None)

    def get_entities(self, selector: str) -> JavaListProxy[Entity]:
        """
        获取实体对象

        Args:
            selector (str): 选择器

        Returns:
            实体对象
        """

        return self.call_list("getEntities", (selector,), Entity)

    def load_entity(
        self,
        name: str,
        world: World,
        *,
        nbt: NbtCompound | None = None,
        where: PosRotTup | V3dTup | None = None,
    ) -> Entity:
        """加载实体对象

        Args:
            id (str): 实体id

        Returns:
            实体对象
        """
        if where is None:
            where = world.spawn_pos.to_v3d().xyz

        if len(where) <= 3:
            where = where + (0, 0)

        return self.call(
            "loadEntity",
            (name, world, nbt, *(float(x) for x in where)),
            Entity,
        )

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
        self.call("debug", (message,), None)

    def info(self, message: str) -> None:
        """
        记录信息级别日志

        Args:
            message (str): 日志消息
        """
        self.call("info", (message,), None)

    def warn(self, message: str) -> None:
        """
        记录警告级别日志

        Args:
            message (str): 日志消息
        """
        self.call("warn", (message,), None)

    def error(self, message: str) -> None:
        """
        记录错误级别日志

        Args:
            message (str): 日志消息
        """
        self.call("error", (message,), None)


class V3i(JavaObjectProxy):
    """net.minecraft.util.math.Vec3i"""

    @property
    def x(self) -> int:
        """x"""
        return self.call("getX", (), int)

    @property
    def y(self) -> int:
        """y"""
        return self.call("getY", (), int)

    @property
    def z(self) -> int:
        """z"""
        return self.call("getZ", (), int)

    @property
    def xyz(self) -> V3iTup:
        """x, y, z"""
        return self.x, self.y, self.z

    def __iter__(self):
        """允许将 V3d 解包为 (x, y, z)"""
        yield self.x
        yield self.y
        yield self.z

    @classmethod
    def create(cls, source: JavaObjectProxy, vec: V3iTup) -> V3i:
        """新建一个V3对象"""
        return source.class_factory.new(
            "net.minecraft.util.math.Vec3i", (int(w) for w in vec), V3i
        )

    def to_v3d(self) -> V3d:
        """转为V3d对象"""
        return V3d.create(self, (self.x, self.y, self.z))


class V3d(JavaObjectProxy):
    """net.minecraft.util.math.Vec3d"""

    @property
    def x(self) -> float:
        """x"""
        return self.call("getX", (), float)

    @property
    def y(self) -> float:
        """y"""
        return self.call("getY", (), float)

    @property
    def z(self) -> float:
        """z"""
        return self.call("getZ", (), float)

    @property
    def xyz(self) -> V3dTup:
        """x, y, z"""
        return self.x, self.y, self.z

    def __iter__(self):
        """允许将 V3d 解包为 (x, y, z)"""
        yield self.x
        yield self.y
        yield self.z

    @classmethod
    def create(cls, source: JavaObjectProxy, vec: V3dTup) -> V3d:
        """新建一个V3d对象"""
        return source.class_factory.new(
            "net.minecraft.util.math.Vec3d", (int(w) for w in vec), V3d
        )


class BlockPos(V3i):
    """net.minecraft.util.math.BlockPos"""


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

    def push_scheduled(self, tick: int, callback: Middleman, name: str) -> int:
        """
        添加一个计划任务，在指定tick执行一次

        Args:
            tick (int): 执行的tick时间点（相对当前tick）
            callback (Middleman): 回调函数
            name (str): 任务名称
        """
        return self.call("pushScheduled", (tick, callback, name), int)

    def remove_scheduled(self, identity: int) -> None:
        """
        删除一个计划任务

        Args:
            identity (int): 任务ID
        """
        self.call("removeScheduled", (identity,), int)

    def push_continuous(self, callback: Middleman, name: str) -> int:
        """
        添加一个连续任务，每个tick都会执行

        Args:
            callback (JavaConsumer): 回调函数
            name (str): 任务名称
        """
        return self.call("pushContinuous", (callback, name), int)

    def remove_continuous(self, identity: int) -> None:
        """
        删除一个连续任务

        Args:
            identity (int): 任务ID
        """
        self.call("removeContinuous", (identity,), int)

    def push_once(self, callback: Middleman, name: str) -> int:
        """
        添加一个一次性任务，在下一个匹配的tick执行后自动移除

        Args:
            callback (JavaConsumer): 回调函数
            name (str): 任务名称
        """
        return self.call("pushOnce", (callback, name), int)

    def remove_once(self, identity: int) -> None:
        """
        移除一个一次性任务

        Args:
            identity (int): 任务id
        """
        self.call("removeOnce", (identity,), int)


class NbtValue(JavaObjectProxy):
    """nbt基类"""

    BASE = "net.minecraft.nbt.%s.of"
    TYPE_MAP: dict[type, str] = {
        bool: BASE % "NbtByte",
        int: BASE % "NbtLong",
        float: BASE % "NbtDouble",
        str: BASE % "NbtString",
    }

    @staticmethod
    def of(source: JavaObjectProxy, value: NbtType):
        """将Python对象转为NbtValue"""
        if isinstance(value, NbtValue):
            return value
        return source.class_factory.call_static(
            NbtValue.TYPE_MAP[type(value)], (value,), NbtValue
        )


class NbtCompound(NbtValue):
    """对应net.minecraft.nbt.NbtCompound"""

    @staticmethod
    def create(source: JavaObjectProxy, **kwargs: NbtType) -> NbtCompound:
        """生成一个NbtCompound"""
        nbt = source.class_factory.new("net.minecraft.nbt.NbtCompound", (), NbtCompound)
        for key, value in kwargs.items():
            nbt.put(key, value)
        return nbt

    def put(self, key: str, value: NbtType) -> Self:
        """
        向 compound 中添加一个元素

        Args:
            key (str): 元素的 key
            value (Any): 元素的 value
        """
        if isinstance(value, list):
            self.call("put", (key, NbtList.create(self, *value)), None)
        elif isinstance(value, dict):
            self.call("put", (key, NbtCompound.create(self, **value)), None)
        else:
            self.call("put", (key, self.of(self, value)), None)
        return self


class NbtList[T: NbtType](NbtValue):
    """对应net.minecraft.nbt.NbtList"""

    @staticmethod
    def create(source: JavaObjectProxy, *values: T) -> NbtList[T]:
        """生成一个NbtList"""
        nbt = source.class_factory.new("net.minecraft.nbt.NbtList", (), NbtList)
        for value in values:
            nbt.add(value)
        return nbt

    def add(self, value: T) -> Self:
        """向列表中添加一个元素"""
        if isinstance(value, list):
            self.call(
                "add", (self.call("size", (), int), NbtList.create(self, *value)), None
            )
        elif isinstance(value, dict):
            self.call(
                "add",
                (self.call("size", (), int), NbtCompound.create(self, **value)),
                None,
            )
        else:
            self.call("add", (self.call("size", (), int), self.of(self, value)), None)
        return self


NbtType: TypeAlias = (
    "int | str | float | bool | dict[str, NbtType] | list[NbtType] | NbtValue"
)


class Entity(JavaObjectProxy):
    """对应net.minecraft.entity.Entity"""

    @property
    def name(self) -> str:
        """获取实体名称"""
        # return self.obj.getName().getString()  # type: ignore
        return self.call("getName").call("getString", (), str)

    @property
    def uuid(self) -> str:
        """获取实体UUID"""
        # return self.obj.getUuidAsString()  # type: ignore
        return self.call("getUuidAsString", (), str)

    def move(self, movement: V3dTup):
        """移动一个实体"""
        x = float(movement[0] + self.call("getX", (), float))
        y = float(movement[1] + self.call("getY", (), float))
        z = float(movement[2] + self.call("getZ", (), float))
        self.call("setPosition", (x, y, z), None)

    @property
    def pos(self) -> V3d:
        """获取实体的位置"""
        return self.call("getPos", (), V3d)

    @pos.setter
    def pos(self, pos: V3d | V3dTup) -> None:
        """设置实体的位置"""
        self.call("setPosition", (*pos,), None)

    @property
    def rotation(self) -> RotTup:
        """获取实体的旋转角度（俯仰角、偏航角）"""
        return self.pitch, self.yaw

    @rotation.setter
    def rotation(self, rot: RotTup) -> None:
        """设置实体的旋转角度（俯仰角、偏航角）"""
        self.call("setRotation", (*rot,), None)

    @property
    def pitch(self) -> float:
        """获取实体的俯仰角度"""
        return self.call("getPitch", (), float)

    @pitch.setter
    def pitch(self, pitch: float) -> None:
        """设置实体的俯仰角度"""
        self.call("setPitch", (pitch,), None)

    @property
    def yaw(self) -> float:
        """获取实体的偏航角度"""
        return self.call("getYaw", (), float)

    @yaw.setter
    def yaw(self, yaw: float) -> None:
        """设置实体的偏航角度"""
        self.call("setYaw", (yaw,), None)

    def refresh_position_and_angles(
        self, x: float, y: float, z: float, yaw: float, pitch: float
    ) -> None:
        """刷新实体的位置和角度"""
        self.call("refreshPositionAndAngles", (x, y, z, yaw, pitch), None)

    def effect(self, effect: str, duration: int, amplifier: int = 1) -> bool:
        """给一个实体添加一个效果"""
        return self.call(
            "addStatusEffect",
            (
                self.class_factory.new(
                    "net.minecraft.entity.effect.StatusEffectInstance",
                    (
                        self.class_factory.get_static(
                            f"net.minecraft.entity.effect.StatusEffects.{effect.upper()}"
                            # TODO: 更好的方式
                        ),
                        duration,
                        amplifier,
                    ),
                ),
            ),
            bool,
        )


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
        self.call("getCommandManager").call(
            "executeWithPrefix", (source, command), None
        )

    def say(self, message: str, name: str = "PYMC"):
        """Server.cmd("say <message>")"""
        self.cmd(f"say {message}", name)

    def get_entities(self, selector: str = "@e") -> JavaListProxy[Entity]:
        """
        获取指定实体

        Args:
            selector (str): 命令方块中的实体选择器
        """
        return self.mngr.get_entities(selector)

    @property
    def overworld(self) -> World:
        """获取主世界"""
        return self.call("getOverworld", (), World)


class World(JavaObjectProxy):
    """世界对象"""

    @property
    def spawn_pos(self) -> BlockPos:
        """世界出生点"""
        return self.call("getSpawnPos", (), BlockPos)

    @property
    def overworld(self):
        """主世界"""
        return self.call("OVERWORLD")

    @property
    def nether(self):
        """下界"""
        return self.call("NETHER")

    @property
    def end(self):
        """末地"""
        return self.call("END")

    def summon(self, name: str, pos: V3dTup | None = None, **nbt: NbtType) -> Entity:
        """召唤实体"""
        entity = self.mngr.load_entity(
            name, self, where=pos, nbt=NbtCompound.create(self, **nbt)
        )
        self.call("spawnNewEntityAndPassengers", (entity,), bool)
        return entity

from py4j.java_gateway import JavaObject
from typing import Protocol

from .utils import LOGGER


class JavaConsumer(Protocol):
    """
    Java Consumer接口的Python协议定义

    用于定义接受服务器对象并执行操作的回调函数接口
    """

    def accept(self, server: JavaObject) -> None: ...


class JavaObjectHandler:
    """
    Java对象处理器基类

    用于包装Java对象，提供统一的访问接口
    """

    obj: JavaObject

    def __init__(self, java_object: JavaObject):
        """
        初始化Java对象处理器

        Args:
            java_object (JavaObject): 要包装的Java对象
        """
        self.obj = java_object


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


class JavaUtils(JavaObjectHandler):
    """
    Java工具类包装

    提供对Java端Utils类的访问，包含MOD_ID和LOGGER等静态属性
    """

    @property
    def LOGGER(self) -> JavaLogger:
        """
        获取Java端日志记录器实例

        Returns:
            JavaLogger: Java日志记录器包装对象
        """
        return JavaLogger(self.obj.LOGGER)  # type: ignore

    @property
    def MOD_ID(self) -> str:
        """
        获取模组ID

        Returns:
            str: 模组ID字符串
        """
        return self.obj.MOD_ID  # type: ignore

    def get_command_source(self, server: "Server", name: str):
        """
        获取命令源对象

        Args:
            server (Server): 服务器对象
            name (str): 命令源名称

        Returns:
            命令源对象
        """

        return self.obj.getCommandSource(server.obj, name)  # type: ignore


class NamedExecutor(JavaObjectHandler):
    """
    Java命名执行器包装类

    对应Java端NamedExecutor类，用于在特定时间点执行命名任务
    """

    def push(self, tick: int, callback: JavaConsumer, name: str) -> None:
        """
        添加一个在指定tick执行的命名任务

        Args:
            tick (int): 执行的tick时间点
            callback (JavaConsumer): 回调函数
            name (str): 任务名称
        """
        self.obj.push(tick, callback, name)  # type: ignore


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
        self.obj.pushScheduled(tick, callback, name)  # type: ignore

    def push_continuous(self, callback: JavaConsumer, name: str) -> None:
        """
        添加一个连续任务，每个tick都会执行

        Args:
            callback (JavaConsumer): 回调函数
            name (str): 任务名称
        """
        self.obj.pushContinuous(callback, name)  # type: ignore

    def push_once(self, callback: JavaConsumer, name: str) -> None:
        """
        添加一个一次性任务，在下一个匹配的tick执行后自动移除

        Args:
            callback (JavaConsumer): 回调函数
            name (str): 任务名称
        """
        self.obj.pushOnce(callback, name)  # type: ignore


class Server(JavaObjectHandler):
    """
    Minecraft服务器对象包装类

    提供对Minecraft服务器实例的访问接口，包括命令执行和日志记录功能
    """

    logger: JavaLogger
    _utlis: JavaUtils

    def __init__(self, server: JavaObject) -> None:
        """
        初始化服务器包装对象

        Args:
            server (JavaObject): Minecraft服务器Java对象
        """
        from .connection import get_javautils

        super().__init__(server)
        self._utlis = get_javautils()
        self.logger = self._utlis.LOGGER

    def cmd(self, str: str, name: str = "PYMC"):
        """
        执行Minecraft命令

        Args:
            str (str): 要执行的命令字符串
        """
        source = self._utlis.get_command_source(self, name)
        self.obj.getCommandManager().executeWithPrefix(source, str)  # type: ignore

    def log(self, str: str):
        """
        记录信息日志

        等效于 server.logger.info

        Args:
            str (str): 日志消息
        """
        LOGGER.debug(f"logging {str}")
        self.logger.info(str)

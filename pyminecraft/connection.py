"""
PyMinecraft Fabric 模块的连接管理模块

该模块负责管理与Java端的Py4J网关连接，提供连接建立、获取网关实例、
执行器和工具类等功能。
同时只有一个网关连接实例存在。

主要功能:
- 建立与Java端的Py4J网关连接
- 提供全局访问点获取网关、执行器和工具类实例
- 处理连接异常和重试机制
- 断开与Java端的连接并释放资源
"""

import threading
import time
from py4j.java_gateway import (
    JavaGateway,
    CallbackServerParameters,
    GatewayParameters,
    Py4JNetworkError,
    Py4JJavaError,
)

from .utils import LOGGER
from .javaobj import NamedAdvancedExecutor, JavaUtils


class Connection:
    """
    Minecraft与Java端的Py4J网关连接管理类

    使用单例模式确保整个应用中只存在一个连接实例。提供连接、断开连接、
    获取网关实例、执行器和工具类等功能的统一管理。
    """

    _instance: "Connection | None" = None
    _lock = threading.Lock()
    _connected: bool
    _gateway: JavaGateway | None
    _executor: NamedAdvancedExecutor | None
    _javautils: JavaUtils | None

    # 全局网关参数配置
    gateway_params: GatewayParameters | None = None

    def __new__(cls):
        """确保类的单例实例"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    # 初始化实例变量
                    cls._instance._connected = False
                    cls._instance._gateway = None
                    cls._instance._executor = None
                    cls._instance._javautils = None
        return cls._instance

    def connect(self) -> JavaGateway:
        """
        建立与Java端的Py4J网关连接

        如果网关已经存在，则返回现有网关实例并记录警告日志；
        否则创建新的网关连接，并初始化相关的执行器和工具类实例。

        Returns:
            JavaGateway: Py4J网关实例

        Raises:
            Py4JNetworkError: 当无法连接到Java网关时抛出
            Py4JJavaError: 当Java端发生错误时抛出
        """
        if self._connected and self._gateway is not None:
            LOGGER.warning("Gateway already exists. Returning existing gateway.")
            return self._gateway

        self._gateway = JavaGateway(
            callback_server_parameters=CallbackServerParameters(),
            auto_field=True,
            gateway_parameters=self.gateway_params,
        )
        self._executor = NamedAdvancedExecutor(
            self._gateway.entry_point.getExecutor(),  # type: ignore
        )
        self._javautils = JavaUtils(self._gateway.entry_point.getUtils())  # type: ignore
        self._connected = True
        return self._gateway

    def disconnect(self) -> None:
        """
        断开与Java端的Py4J网关连接

        关闭网关连接和回调服务器，释放相关资源
        """
        if self._gateway is not None:

            def delayed_disconnect():
                time.sleep(0.1)  # 延迟0.1秒
                try:
                    if self._gateway is not None:
                        self._gateway.close()
                        LOGGER.info("Successfully disconnected from Java gateway")
                    else:
                        LOGGER.error("Cannot disconnect. Have not connected")
                except Py4JNetworkError as e:
                    LOGGER.error("Error while disconnecting from Java gateway: %s", e)
                finally:
                    # 在连接关闭后清理全局变量引用
                    self._gateway = None
                    self._executor = None
                    self._javautils = None
                    self._connected = False

            # 在新线程中执行延迟断开连接
            disconnect_thread = threading.Thread(target=delayed_disconnect, daemon=True)
            disconnect_thread.start()
        else:
            LOGGER.warning("Java gateway is not connected")

    def try_connect(
        self,
        msg: str = "Tried to connect to server, but failed.",
        should_raise: bool = True,
    ) -> JavaGateway | None:
        """
        尝试建立与Java端的连接，包含异常处理机制

        Args:
            msg (str): 连接失败时记录的日志消息，默认为"Tried to connect to server, but failed."
            should_raise (bool): 连接失败时是否抛出异常，默认为True

        Returns:
            JavaGateway | None: 成功时返回网关实例，失败且should_raise=False时返回None

        Raises:
            Py4JNetworkError: 当无法连接到Java网关且should_raise=True时抛出
            Py4JJavaError: 当Java端发生错误时抛出
        """
        try:
            return self.connect()
        except Py4JNetworkError:
            if should_raise:
                LOGGER.error(msg)
                raise
            LOGGER.info(msg)
            return None
        except Py4JJavaError:
            LOGGER.error(
                "Something wrong happened in java side while connecting. "
                "Check whether you are using the the mod in the correct version"
            )
            raise

    def get_gateway(self) -> JavaGateway:
        """
        获取网关实例（全局访问点）

        如果网关已存在则直接返回，否则尝试建立新连接

        Returns:
            JavaGateway: Py4J网关实例
        """
        if self._gateway is not None:
            return self._gateway
        self.try_connect()
        if self._gateway is not None:
            return self._gateway
        raise RuntimeError("Cannnot connect to the gateway. This should never happen.")

    def get_executor(self) -> NamedAdvancedExecutor:
        """
        获取执行器实例（全局访问点）

        如果执行器已存在则直接返回，否则尝试建立连接并获取执行器

        Returns:
            NamedAdvancedExecutor: Java执行器包装类实例

        Raises:
            RuntimeError: 当无法获取执行器实例时抛出
        """
        if self._executor:
            return self._executor
        self.try_connect()
        if self._executor:
            return self._executor
        raise RuntimeError("Cannot get executor. This should never happen")

    def get_javautils(self) -> JavaUtils:
        """
        获取Java工具类实例（全局访问点）

        如果工具类实例已存在则直接返回，否则尝试建立连接并获取工具类实例

        Returns:
            JavaUtils: Java工具类包装实例

        Raises:
            RuntimeError: 当无法获取工具类实例时抛出
        """
        if self._javautils:
            return self._javautils
        self.try_connect()
        if self._javautils:
            return self._javautils
        raise RuntimeError("Cannot get javautils. This should never happen")

    @property
    def connected(self) -> bool:
        """
        获取连接状态

        Returns:
            bool: 连接状态
        """
        return self._connected

    @property
    def gateway(self) -> JavaGateway | None:
        """
        获取网关实例

        Returns:
            JavaGateway | None: 网关实例或None
        """
        return self._gateway

    @property
    def executor(self) -> NamedAdvancedExecutor | None:
        """
        获取执行器实例

        Returns:
            NamedAdvancedExecutor | None: 执行器实例或None
        """
        return self._executor

    @property
    def javautils(self) -> JavaUtils | None:
        """
        获取Java工具类实例

        Returns:
            JavaUtils | None: Java工具类实例或None
        """
        return self._javautils


# 创建单例实例并尝试连接
_connection = Connection()
_connection.try_connect(msg="", should_raise=False)


def get_gateway() -> JavaGateway:
    """
    获取网关实例的全局函数接口

    Returns:
        JavaGateway: Py4J网关实例
    """
    return _connection.get_gateway()


def get_executor() -> NamedAdvancedExecutor:
    """
    获取执行器实例的全局函数接口

    Returns:
        NamedAdvancedExecutor: Java执行器包装类实例
    """
    return _connection.get_executor()


def get_javautils() -> JavaUtils:
    """
    获取Java工具类实例的全局函数接口

    Returns:
        JavaUtils: Java工具类包装实例
    """
    return _connection.get_javautils()


def disconnect() -> None:
    """
    断开与Java端的连接
    """
    _connection.disconnect()

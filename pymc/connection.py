from py4j.java_gateway import (
    JavaGateway,
    CallbackServerParameters,
    GatewayParameters,
    Py4JNetworkError,
    Py4JJavaError,
)

from .utils import LOGGER
from .javaobj_handler import NamedAdvancedExecutor, JavaUtils

# 全局网关参数配置
gateway_params: GatewayParameters | None = None


def connect() -> JavaGateway:
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
    global gateway, executor, javautils, connected
    if gateway is not None:
        LOGGER.warning("Gateway already exists. Returning existing gateway.")
        return gateway
    gateway = JavaGateway(
        callback_server_parameters=CallbackServerParameters(),
        auto_field=True,
        gateway_parameters=gateway_params,
    )
    executor = NamedAdvancedExecutor(gateway.entry_point.getExecutor())  # type: ignore
    javautils = gateway.entry_point.getUtils()  # type: ignore
    connected = True
    return gateway


def try_connect(
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
        return connect()
    except Py4JNetworkError:
        if should_raise:
            LOGGER.error(msg)
            raise
        else:
            LOGGER.info(msg)
            return None
    except Py4JJavaError:
        LOGGER.error(
            "Something wrong happened in java side while connecting. "
            "Check whether you are using the the mod in the correct version"
        )
        raise


# 连接状态标志
connected: bool = False

# 全局网关相关实例变量
gateway: JavaGateway | None = None
executor: NamedAdvancedExecutor | None = None
javautils: JavaUtils | None = None

# 程序启动时尝试静默连接
try_connect(msg="", should_raise=False)


def get_gateway() -> JavaGateway:
    """
    获取网关实例（全局访问点）
    
    如果网关已存在则直接返回，否则尝试建立新连接
    
    Returns:
        JavaGateway: Py4J网关实例
    """
    return gateway or try_connect()  # type: ignore


def get_executor() -> NamedAdvancedExecutor:
    """
    获取执行器实例（全局访问点）
    
    如果执行器已存在则直接返回，否则尝试建立连接并获取执行器
    
    Returns:
        NamedAdvancedExecutor: Java执行器包装类实例
        
    Raises:
        RuntimeError: 当无法获取执行器实例时抛出
    """
    if executor:
        return executor
    else:
        try_connect()
        if executor:
            return executor
        raise RuntimeError("Cannot get executor. This should never happen")


def get_javautils() -> JavaUtils:
    """
    获取Java工具类实例（全局访问点）
    
    如果工具类实例已存在则直接返回，否则尝试建立连接并获取工具类实例
    
    Returns:
        JavaUtils: Java工具类包装实例
        
    Raises:
        RuntimeError: 当无法获取工具类实例时抛出
    """
    if javautils:
        return javautils
    else:
        try_connect()
        if javautils:
            return javautils
        raise RuntimeError("Cannot get javautils. This should never happen")
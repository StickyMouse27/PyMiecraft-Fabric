from py4j.java_gateway import JavaObject
from typing import Callable, Protocol

from .utils import LOGGER


class JavaConsumer(Protocol):
    def accept(self, server: JavaObject) -> None: ...


class JavaObjectHandler:
    obj: JavaObject

    def __init__(self, java_object: JavaObject):
        self.obj = java_object


class JavaLogger(JavaObjectHandler):
    def debug(self, message: str) -> None:
        self.obj.debug(message)  # type: ignore

    def info(self, message: str) -> None:
        self.obj.info(message)  # type: ignore

    def warn(self, message: str) -> None:
        self.obj.warn(message)  # type: ignore

    def error(self, message: str) -> None:
        self.obj.error(message)  # type: ignore


class JavaUtils(JavaObjectHandler):
    @property
    def LOGGER(self) -> JavaLogger:
        return JavaLogger(self.obj.LOGGER)  # type: ignore

    @property
    def MOD_ID(self) -> str:
        return self.obj.MOD_ID  # type: ignore


class NamedExecutor(JavaObjectHandler):

    def push(self, tick: int, callback: JavaConsumer, name: str) -> None:
        self.obj.push(tick, callback, name)  # type: ignore


# This object inherits from JavaObjectHandler but not NamedExecutor
# because we don't want a push function interfere with the developers.
class NamedAdvancedExecutor(JavaObjectHandler):

    def push_scheduled(self, tick: int, callback: JavaConsumer, name: str) -> None:
        self.obj.pushScheduled(tick, callback, name)  # type: ignore

    def push_continuous(self, callback: JavaConsumer, name: str) -> None:
        self.obj.pushContinuous(callback, name)  # type: ignore

    def push_once(self, callback: JavaConsumer, name: str) -> None:
        self.obj.pushOnce(callback, name)  # type: ignore


class Server(JavaObjectHandler):
    logger: JavaLogger

    def __init__(self, server: JavaObject) -> None:
        from .connection import get_javautils

        super().__init__(server)
        self.logger = get_javautils().LOGGER

    def cmd(self, str: str):
        source = self.obj.getCommandSource()  # type: ignore
        self.obj.getCommandManager().executeWithPrefix(source, str)  # type: ignore

    def log_debug(self, str: str):
        self.logger.debug(str)

    def log_info(self, str: str):
        self.logger.info(str)

    def log_warn(self, str: str):
        self.logger.warn(str)

    def log_error(self, str: str):
        self.logger.error(str)

    def log(self, str: str):
        LOGGER.debug(f"logging {str}")
        self.log_info(str)

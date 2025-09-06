"""工具"""

from logging import getLogger
from typing import Callable
from functools import wraps
import time

__all__ = ["LOGGER", "time_it"]

LOGGER = getLogger("pymc")


def time_it(func: Callable, name="", time_limit=0) -> Callable:
    """
    装饰器，用于计算函数执行时间。

    Args:
        func: 要装饰的函数

    Returns:
        装饰后的函数
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter_ns()
        result = func(*args, **kwargs)
        spent = (time.perf_counter_ns() - start_time) / 1e6
        if spent > time_limit:
            print(f"{name or func.__name__} | {spent:.4f}ms")
        return result

    return wrapper

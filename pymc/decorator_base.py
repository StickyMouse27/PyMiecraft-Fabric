from functools import wraps
from typing import Any, Callable
from abc import ABC, abstractmethod


class DecoratorBase(ABC):
    func: Callable | None

    def __call__(self, func: Callable[..., None]) -> Callable[..., None]:
        return self._get_wrapper(func)

    def __and__(self, other: "DecoratorBase") -> Callable:
        def wrapper(func: Callable):
            return other(self(func))

        return wrapper

    def _get_wrapper(self, func: Callable) -> Callable:

        @wraps(func)
        def wrapper(args: Any, **kwargs: Any):
            return func(*args, **kwargs)

        self.modify()

        return wrapper

    @abstractmethod
    def modify(self) -> None:
        pass

    # def __init__(self, at: str | Callable | None) -> None:
    # if self.at is None:
    #     if at is None:
    #         raise ValueError("Argument at value must be provided.")
    #     elif isinstance(at, str):
    #         self.at = at
    #     elif isinstance(at, Callable):
    #         if self.at is None:
    #             raise ValueError(
    #                 "At class cannot be used with an @ decorator directly."
    #             )
    #         self.func = at
    #     else:
    #         raise ValueError("Argument at must be a string or a function")

    # def __call__(self, *args: Any, **kwargs: Any) -> Any:
    #     if self.func is None:
    #         assert isinstance(args[0], Callable)
    #         return self._get_wrapper(args[0])
    #     else:
    #         return self._direct_wrap(*args, **kwargs)

    # def _direct_wrap(self, *args: Any, **kwargs: Any) -> Any:
    #     assert self.func is not None

    #     @wraps(self.func)
    #     def wrapper(*args: Any, **kwargs: Any):
    #         assert self.func is not None
    #         return self.func(*args, **kwargs)

    #     self.modify()

    #     return wrapper(*args, **kwargs)

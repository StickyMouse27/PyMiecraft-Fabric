"""类型字典支持"""

from typing import (
    KeysView,
    ItemsView,
    ValuesView,
    Any,
    Optional,
    Iterator,
    override,
    overload,
)
from collections.abc import MutableMapping

__all__ = ("AtDict",)


class TypeDict(MutableMapping[type[Any], Any]):
    """
    一个类似字典的类，使用值的类型作为键

    示例:
    ```
    td = TypeDict()
    td[int] = 42
    td[str] = "hello"
    print(td[int])  # 输出: 42
    ```
    """

    _data: dict[type[Any], Any]

    def __init__(self) -> None:
        self._data = {}

    def __setitem__[T](self, key: type[T], value: T) -> None:
        """
        设置指定类型的值

        Args:
            key: 值的类型
            value: 要存储的值
        """
        if not isinstance(value, key):
            raise TypeError(f"Value {value} is not an instance of {key}")
        self._data[key] = value

    def __getitem__[T](self, key: type[T]) -> T:
        """
        获取指定类型的值

        Args:
            key: 要获取值的类型

        Returns:
            对应类型的值

        Raises:
            KeyError: 如果指定类型不存在
        """
        return self._data[key]

    def __delitem__(self, key: type[Any]) -> None:
        """
        删除指定类型的值

        Args:
            key: 要删除值的类型

        Raises:
            KeyError: 如果指定类型不存在
        """
        del self._data[key]

    def __iter__(self) -> Iterator[type[Any]]:
        """
        迭代所有存储的类型键

        Returns:
            类型键的迭代器
        """
        return iter(self._data)

    def __len__(self) -> int:
        """
        返回存储的元素数量

        Returns:
            元素数量
        """
        return len(self._data)

    def __contains__(self, key: object) -> bool:
        """
        检查是否包含指定类型

        Args:
            key: 要检查的类型

        Returns:
            如果包含该类型返回True，否则返回False
        """
        return key in self._data

    def get[T](self, key: type[T], default: Optional[T] = None) -> Optional[T]:
        """
        获取指定类型的值，如果不存在则返回默认值

        Args:
            key: 要获取值的类型
            default: 默认值

        Returns:
            对应类型的值或默认值
        """
        return self._data.get(key, default)

    def setdefault[T](self, key: type[T], default: T = None) -> T:
        """
        如果指定类型不存在，则设置默认值并返回

        Args:
            key: 类型键
            default: 默认值

        Returns:
            已存在的值或新设置的默认值
        """
        if key not in self._data:
            self[key] = default
        return self._data[key]

    def clear(self) -> None:
        """
        清空所有数据
        """
        self._data.clear()

    def keys(self) -> KeysView[type[Any]]:
        """
        返回所有类型键的视图

        Returns:
            类型键的迭代器
        """
        return self._data.keys()

    def values(self) -> ValuesView[Any]:
        """
        返回所有值的视图

        Returns:
            值的迭代器
        """
        return self._data.values()

    def items(self) -> ItemsView[type[Any], Any]:
        """
        返回所有键值对的视图

        Returns:
            键值对的迭代器
        """
        return self._data.items()

    def __repr__(self) -> str:
        """
        返回对象的字符串表示

        Returns:
            对象的字符串表示
        """
        return f"{self.__class__.__name__}({dict(self._data)})"


class AtDict(TypeDict):
    """加强 Type Dict ，将 typedict[string] 映射到 typedict[dict][string]"""

    def __init__(self) -> None:
        super().__init__()
        self[dict] = {}

    @overload
    def __setitem__(self, key: str, value: Any) -> None: ...
    @overload
    def __setitem__[T](self, key: type[T], value: T) -> None: ...
    @override
    def __setitem__[T](self, key: type[T] | str, value: Any) -> None:
        if isinstance(key, str):
            self[dict][key] = value
        else:
            super().__setitem__(key, value)

    @overload
    def __getitem__(self, key: str) -> Any: ...
    @overload
    def __getitem__[T](self, key: type[T]) -> T: ...
    @override
    def __getitem__[T](self, key: type[T] | str) -> Any:
        if isinstance(key, str):
            return self[dict][key]
        return super().__getitem__(key)


# 使用示例
if __name__ == "__main__":
    # 创建TypeDict实例
    td = TypeDict()

    # 添加不同类型的数据
    td[int] = 42
    td[str] = "hello world"
    td[float] = 3.14
    td[list] = [1, 2, 3]

    # 访问数据
    print(f"整数值: {td[int]}")
    print(f"字符串值: {td[str]}")
    print(f"浮点数值: {td[float]}")
    print(f"列表值: {td[list]}")

    # 查看所有数据
    print(f"所有数据: {td}")

    # 检查是否存在某种类型
    print(f"是否存在int类型: {int in td}")
    print(f"是否存在dict类型: {dict in td}")

    # 使用get方法
    print(f"获取存在的值: {td.get(str)}")
    print(f"获取不存在的值: {td.get(dict, '默认字典')}")

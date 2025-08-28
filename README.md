PyMinecraft Fabric
---

PyMinecraft Fabric 为 Minecraft Java Edition 开发的 Python 接口，基于 Fabric 开发，使玩家能够用 Python 脚本控制 Minecraft。

**项目仍在施工中，可能会遇到各种bug或者运行不了的情况，欢迎提交issue和PR~**

## 如何使用？

### Python 端
1. 复制本项目的 pyminecraft 文件夹于你的目录下，并在同目录下开发 Python 脚本；
2. 安装 py4j ： `pip install py4j`

### Minecraft 端
1. 在 mod 目录中添加本项目的 jar 文件

## 项目是怎么工作的？

本项目基于 [py4j](https://www.py4j.org/)  ，使用套接字实现 Python 与 Java 之间的通信。

## 已知问题

- 运行时 Python 脚本无法自动断开连接，导致进程无法停止。解决方法：关闭终端或强制结束 Python 进程。
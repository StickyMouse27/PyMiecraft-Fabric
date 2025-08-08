"""
PyMiecraft Fabric
示例文档

Link: https://github.com/StickyMouse27/PyMiecraft-Fabric
"""

import pyminecraft as pymc

# import logging

# logging.basicConfig(level=logging.DEBUG)


@ pymc.AtTick & pymc.ONCE
def start_timer(server: pymc.Server, info: pymc.TypeDict):
    """开始倒计时"""
    print("Say hello to mc")
    server.log("Hello from pymc-fabric!")
    server.cmd("say hello!!!!!!")

    info[dict]["timer"] = pymc.AtTickAfter(20 * 5) & pymc.ALWAYS | func_after_5_sec
    info[dict]["counter"] = 0


@ pymc.AtTickAfter(20) & pymc.ALWAYS & pymc.MaxTimesFlag(64)
def tick(server: pymc.Server, info: pymc.TypeDict):
    """每秒给大家一个钻石"""

    times_left = info[pymc.MaxTimesFlag].times_left
    print(f"They must need more diamonds (diamond: {64 - times_left}/64)")
    server.cmd("say Wanna diamonds?")
    server.cmd("give @a diamond")

    if info[pymc.MaxTimesFlag].stopped:
        print("They are full of diamonds")

        pymc.connection.disconnect()


def func_after_5_sec(server: pymc.Server, info: pymc.TypeDict):
    """每5秒执行一次"""
    server.log("5 sec passed")
    server.cmd("say 5 sec passed")

    info[dict]["counter"] += 1

    # 计数器实现和MaxTimesFlag实现效果相同
    if info[dict]["counter"] > 6:
        timer: pymc.AtTickAfter = info[dict]["timer"]
        timer.cancel()
        server.log("total 30 sec passed, stoped")
        server.cmd("say total 30 sec passed, stoped")

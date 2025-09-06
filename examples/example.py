"""
PyMiecraft Fabric
示例：基础示例

Link: https://github.com/StickyMouse27/PyMiecraft-Fabric
"""

import logging
import pyminecraft as pymc


logging.basicConfig(level=logging.INFO)


@ pymc.AtTick & pymc.ONCE
def start_timer(server: pymc.Server, _data: pymc.AtDict):
    """开始倒计时"""
    print("Say hello to mc")
    server.mngr.log("Hello from pymc-fabric!")
    server.cmd("say hello!!!!!!")

    (pymc.AtTick & pymc.After(20 * 5) & pymc.ALWAYS & pymc.Data(counter=1))(
        func_after_5_sec
    )


def func_after_5_sec(server: pymc.Server, data: pymc.AtDict):
    """每5秒执行一次"""
    print("5 sec passed")
    server.cmd("say 5 sec passed")

    data["counter"] += 1

    # 计数器实现和MaxTimesFlag实现效果相同
    if data["counter"] >= 6:
        at = data[pymc.At]
        at.cancel()
        print("total 30 sec passed, stoped")
        server.cmd("say total 30 sec passed, stoped")


@ pymc.AtTick & pymc.After(20) & pymc.ALWAYS & pymc.MaxTimes(64)
def tick(server: pymc.Server, data: pymc.AtDict):
    """每秒给大家一个钻石"""

    times_left = data[pymc.MaxTimes].times_left
    print(f"They must need more diamonds (diamond: {64 - times_left}/64)")
    server.cmd("say Wanna diamonds?")
    server.cmd("give @a diamond")

    if data[pymc.MaxTimes].the_last:
        print("They are full of diamonds")

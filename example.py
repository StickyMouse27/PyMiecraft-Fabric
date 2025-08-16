"""
PyMiecraft Fabric
示例

Link: https://github.com/StickyMouse27/PyMiecraft-Fabric
"""

import logging

import pyminecraft as pymc


logging.basicConfig(level=logging.INFO)


@ pymc.AtTick & pymc.ONCE
def start_timer(server: pymc.Server, data: pymc.TypeDict):
    """开始倒计时"""
    print("Say hello to mc")
    server.mngr.log("Hello from pymc-fabric!")
    server.cmd("say hello!!!!!!")

    at = pymc.AtTickAfter(20 * 5) & pymc.ALWAYS | func_after_5_sec
    at.data[dict]["counter"] = 1

    # 也可以使用全局变量实现
    # global counter
    # counter = 1


def func_after_5_sec(server: pymc.Server, data: pymc.TypeDict):
    """每5秒执行一次"""
    print("5 sec passed")
    server.cmd("say 5 sec passed")

    data[dict]["counter"] += 1

    # 计数器实现和MaxTimesFlag实现效果相同
    if data[dict]["counter"] >= 6:
        timer = data[pymc.AtTickAfter]
        timer.cancel()
        print("total 30 sec passed, stoped")
        server.cmd("say total 30 sec passed, stoped")


@ pymc.AtTickAfter(20) & pymc.ALWAYS & pymc.MaxTimesFlag(64)
def tick(server: pymc.Server, data: pymc.TypeDict):
    """每秒给大家一个钻石"""

    times_left = data[pymc.MaxTimesFlag].times_left
    print(f"They must need more diamonds (diamond: {64 - times_left}/64)")
    server.cmd("say Wanna diamonds?")
    server.cmd("give @a diamond")

    if data[pymc.MaxTimesFlag].the_last:
        print("They are full of diamonds")

        # pymc.connection.disconnect()


@ pymc.AtTickAfter(20) & pymc.ONCE
def entity_test(server: pymc.Server, data: pymc.TypeDict):
    """功能测试：实体"""
    server.cmd("say entity test")
    server.cmd("summon snowball")
    entities = server.get_entities()

    for eneity in entities:
        print(eneity.name)

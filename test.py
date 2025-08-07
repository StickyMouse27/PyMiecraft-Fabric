import pymc

# import logging

# logging.basicConfig(level=logging.DEBUG)

timer: pymc.AbstractAt
counter: int = 0


@ pymc.AtTick & pymc.ONCE
def start_timer(server: pymc.Server, info: pymc.TypeDict):
    """开始倒计时"""
    print("Say hello to mc")
    server.log("Hello from pymc-fabric!")
    server.cmd("say hello!!!!!!")

    global timer
    timer = pymc.AtTickAfter(20 * 5) & pymc.ALWAYS | func_after_5_sec


@ pymc.AtTickAfter(20) & pymc.ALWAYS & pymc.MaxTimesFlag(10)
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
    server.log("5 sec passed")
    server.cmd("say 5 sec passed")

    global timer, counter
    counter += 1

    # 计数器实现和MaxTimesFlag实现效果相同
    if counter > 6:
        timer.cancel()
        server.log("total 30 sec passed, stoped")
        server.cmd("say total 30 sec passed, stoped")

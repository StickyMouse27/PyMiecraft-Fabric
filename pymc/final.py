from .. import pymc


@pymc.At("start")
def start(server: pymc.Server):
    server.log("Hello from pymc-fabric!")


@ pymc.atTick & pymc.once
def tick(server: pymc.Server):
    server.cmd("give @a diamond")
    server.cmd.give(pymc.Command.at_a, pymc.MC.diamond)

"""
PyMiecraft Fabric
示例：苦力怕游戏

Link: https://github.com/StickyMouse27/PyMiecraft-Fabric
"""

import random
import pyminecraft as pymc


@ pymc.AtTick & pymc.ONCE
def creeper_game(server: pymc.Server, _data: pymc.AtDict) -> None:
    """苦力怕游戏，单击苦力怕后随机移动"""
    server.say("欢迎来到PyMiecraft！")
    creeper = server.overworld.summon(
        "creeper", (0, 67, 0), NoGravity=True, Invulnerable=True, Glowing=True
    )

    @ pymc.AtEntityInteract(creeper) & pymc.ALWAYS
    def interact(entity: pymc.Entity, _data: pymc.AtDict) -> None:
        entity.pos += (
            (random.random() * 2 - 1) * 5,
            (random.random() * 2 - 1) * 5,
            (random.random() * 2 - 1) * 5,
        )

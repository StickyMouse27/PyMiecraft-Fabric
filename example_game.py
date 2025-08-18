"""
PyMiecraft Fabric
示例游戏

Link: https://github.com/StickyMouse27/PyMiecraft-Fabric
"""

# import logging
import random

import pyminecraft as pymc

# logging.basicConfig(level=logging.DEBUG)


@ pymc.AtTick & pymc.ONCE
def init(server: pymc.Server, _data: pymc.TypeDict) -> None:
    """初始化"""
    server.say("欢迎来到PyMiecraft！")
    creeper = server.overworld.summon(
        "creeper", (0, 67, 0), NoGravity=True, Invulnerable=True
    )
    creeper.effect("glowing", -1)

    @ pymc.AtEntityInteract(creeper) & pymc.ALWAYS
    def interact(entity: pymc.Entity, _data: pymc.TypeDict) -> None:
        movement = (
            (random.random() * 2 - 1) * 5,
            (random.random() * 2 - 1) * 5,
            (random.random() * 2 - 1) * 5,
        )
        entity.move(movement)
        print("interact")


# @ pymc.AtEntityInteract("Creeper", match="uuid") & pymc.ALWAYS
# def entity_test(entity: pymc.Entity, data: pymc.TypeDict) -> None:
#     """
#     功能测试：实体
#     效果：在玩家与Creeper交互时，Creeper随机移动
#     """
#     movement = (
#         (random.random() * 2 - 1) * 5,
#         (random.random() * 2 - 1) * 5,
#         (random.random() * 2 - 1) * 5,
#     )
#     entity.move(movement)
#     print("interact")


# @pymc.AtTick
# def entity_move(server: pymc.Server, data: pymc.TypeDict):
#     entities = server.get_entities()

#     for eneity in entities:
#         print(eneity.name)

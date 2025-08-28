"""
PyMiecraft Fabric
示例游戏

Link: https://github.com/StickyMouse27/PyMiecraft-Fabric
"""

import random

# import logging

import pyminecraft as pymc

# logging.basicConfig(level=logging.INFO)

# @ pymc.AtTick & pymc.ONCE
# def init(server: pymc.Server, _data: pymc.TypeDict) -> None:
#     """初始化"""
#     server.say("欢迎来到PyMiecraft！")
#     creeper = server.overworld.summon(
#         "creeper", (0, 67, 0), NoGravity=True, Invulnerable=True
#     )
#     creeper.effect("glowing", -1)

#     @ pymc.AtEntityInteract(creeper) & pymc.ALWAYS
#     def interact(entity: pymc.Entity, _data: pymc.TypeDict) -> None:
#         movement = (
#             (random.random() * 2 - 1) * 5,
#             (random.random() * 2 - 1) * 5,
#             (random.random() * 2 - 1) * 5,
#         )
#         entity.move(movement)
#         print("interact")


@ pymc.AtTick & pymc.ONCE
def init(server: pymc.Server, _data: pymc.TypeDict):
    """烟花"""
    # _data[pymc.AtTick].executor.remove_all()

    def firework_data(colors: list[int], fade_colors: list[int]) -> dict:
        return {
            "FireworksItem": {
                "id": "minecraft:firework_rocket",
                "components": {
                    "fireworks": {
                        "explosions": [
                            {
                                "colors": colors,
                                "fade_colors": fade_colors,
                                "shape": "small_ball",
                            }
                        ]
                    }
                },
            },
        }

    firework = server.overworld.summon(
        "firework_rocket",
        (0, 67, 0),
        **firework_data([random.randint(0, 0xFFFFFF)], [random.randint(0, 0xFFFFFF)]),
        LifeTime=40,
    )

    at = pymc.AtEntity("removed", firework)
    at.data[dict]["chance"] = 1
    at.data[dict]["amount"] = 10

    @at
    def tick(entity: pymc.Entity, data: pymc.TypeDict) -> None:
        if random.random() < 1 - data[dict]["chance"] or data[dict]["amount"] <= 0:
            return

        for _ in range(data[dict]["amount"]):
            new = server.overworld.summon(
                "firework_rocket",
                entity.pos.xyz,
                **firework_data(
                    [random.randint(0, 0xFFFFFF)], [random.randint(0, 0xFFFFFF)]
                ),
                ShotAtAngle=True,
                LifeTime=random.randint(10, 20),
            )

            def r():
                return (random.random() * 2 - 1) / 2

            vy = random.random() / 2 if entity.y <= 100 else r()

            new.move((r(), r(), r()))
            new.velocity = (r(), vy, r())
            at = pymc.AtEntity("removed", new)
            at.data[dict]["chance"] = data[dict]["chance"] * 0.8
            at.data[dict]["amount"] = data[dict]["amount"] - random.randint(1, 10)
            at(tick)


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

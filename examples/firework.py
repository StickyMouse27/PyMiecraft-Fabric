"""
PyMiecraft Fabric
示例：烟花

Link: https://github.com/StickyMouse27/PyMiecraft-Fabric
"""

import random
import pyminecraft as pymc


@ pymc.AtTick & pymc.ONCE
def init(server: pymc.Server, _data: pymc.AtDict):
    """烟花"""

    def firework_data(
        colors: list[tuple[list[int], list[int]]], shape: str = "small_ball"
    ) -> dict:
        return {
            "FireworksItem": {
                "id": "minecraft:firework_rocket",
                "components": {
                    "fireworks": {
                        "explosions": [
                            {
                                "colors": color,
                                "fade_colors": fade_color,
                                "shape": shape,
                            }
                            for color, fade_color in colors
                        ]
                    }
                },
            },
        }

    colors = [
        [([0x6AB727, 0xFFFE91], [0xABABAB, 0xFFF5A4])],
        [([0xFFB6FD, 0xFF27A9], [0xABABAB, 0xFFF5A4])],
    ]

    firework = server.overworld.summon(
        "firework_rocket",
        (0, 67, 0),
        **firework_data(random.choice(colors), "large_ball"),
        LifeTime=40,
    )

    @ pymc.AtEntity("removed", firework) & pymc.Data(chance=1, amount=20)
    def on_removed(entity: pymc.Entity, data: pymc.AtDict) -> None:
        # server.mngr.executor.print_debug()
        if random.random() < 1 - data["chance"] or data["amount"] <= 0:
            return

        for _ in range(data["amount"]):
            new_firework = server.overworld.summon(
                "firework_rocket",
                entity.pos,
                **firework_data(random.choice(colors)),
                ShotAtAngle=True,
                LifeTime=random.randint(5, 15),
            )

            new_firework.velocity = (
                random.uniform(-1, 1),
                random.uniform(-1, 1),
                random.uniform(-1, 1),
            )
            (
                pymc.AtEntity("removed", new_firework)
                & pymc.Data(
                    amount=data["amount"] - random.randint(5, 20),
                )
            )(on_removed)

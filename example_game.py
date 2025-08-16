"""
PyMiecraft Fabric
示例游戏

Link: https://github.com/StickyMouse27/PyMiecraft-Fabric
"""

import logging

import pyminecraft as pymc

logging.basicConfig(level=logging.DEBUG)


@ pymc.AtEntityInteract("Creeper", match_name=True) & pymc.ALWAYS
def entity_test(entity: pymc.Entity, data: pymc.TypeDict) -> None:
    """功能测试：实体"""
    # entity.move((0, 1, 0))
    print("interact")
    entity.gateway.entry_point.move(entity.obj)


@pymc.AtTick
def entity_move(server: pymc.Server, data: pymc.TypeDict):
    entities = server.get_entities()

    for eneity in entities:
        print(eneity.name)

    # movement_type = server.class_factory.get_static(
    #     "net.minecraft.entity.MovementType", "SELF"
    # )
    # movement_obj = server.class_factory.v3d((0, 1, 0))

    # server.mngr.obj.move(entities[0].obj)

    # entities[0].move((0, 1, 0))

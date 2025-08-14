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
    print(entity.name, 1111111)

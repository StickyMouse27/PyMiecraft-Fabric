"""
PyMinecraft-Fabric

Link: https://github.com/PyMinecraft/PyMinecraft-Fabric
"""

from .at import (
    At,
    AtTick,
    After,
    AtTickAfter,
    AtEntityInteract,
    RunningFlag,
    MaxTimesFlag,
)
from .javaobj import Server, NamedAdvancedExecutor, Entity
from .utils import LOGGER
from .type_dict import TypeDict

# 还有些问题…
# from .connection import disconnect

ONCE = RunningFlag.ONCE
ALWAYS = RunningFlag.ALWAYS
NEVER = RunningFlag.NEVER

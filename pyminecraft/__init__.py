"""
PyMinecraft-Fabric

Link: https://github.com/PyMinecraft/PyMinecraft-Fabric
"""

from .at import *
from .javaobj import *
from .utils import LOGGER
from .type_dict import TypeDict

# 还有些问题…
# from .connection import disconnect

ONCE = Running.once()
ALWAYS = Running.always()
NEVER = Running.never()

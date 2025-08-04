from py4j.java_gateway import (
    JavaGateway,
    CallbackServerParameters,
)

from .at import *
from .server import *
from .mc import *
from .when import *

gateway = JavaGateway(
    callback_server_parameters=CallbackServerParameters(), auto_field=True
)

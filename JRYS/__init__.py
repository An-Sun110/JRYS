import sys
from importlib import import_module

from gsuid_core.sv import Plugins

Plugins(
    name="JRYS",
    force_prefix=[],
    allow_empty_prefix=True,
    alias=["jrys-prpr"],
)

# GsCore loads nested plugins with a synthetic module name whose parent
# packages may not exist. Register the real package alias before importing
# business modules so sibling imports remain isolated from other plugins.
sys.modules["JRYS"] = sys.modules[__name__]
import_module("JRYS.jrys")

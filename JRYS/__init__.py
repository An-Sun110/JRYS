"""GsCore port of koishi-plugin-jrys-prpr."""

import sys
from pathlib import Path

from gsuid_core.sv import Plugins

Plugins(
    name="JRYS",
    force_prefix=[],
    allow_empty_prefix=True,
    alias=["jrys-prpr"],
)

_module_path = str(Path(__file__).parent)
if _module_path not in sys.path:
    sys.path.insert(0, _module_path)

import jrys  # noqa: E402,F401

from pathlib import Path

from gsuid_core.data_store import get_res_path

PLUGIN_PATH = Path(__file__).parent
DATA_PATH = get_res_path() / "JRYS"
DATA_PATH.mkdir(parents=True, exist_ok=True)

BACKGROUND_PATH = DATA_PATH / "bg"
BACKGROUND_PATH.mkdir(parents=True, exist_ok=True)

RECORD_PATH = DATA_PATH / "original_images.json"
ASSET_PATH = PLUGIN_PATH / "assets"
FORTUNE_PATH = ASSET_PATH / "jrys.json"
DEFAULT_BACKGROUND_PATH = ASSET_PATH / "backgrounds" / "miao.jpg"
FONT_PATH = ASSET_PATH / "千图马克手写体lite.ttf"

import random
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

import httpx
import aiofiles
from PIL import Image
from jrys_paths import BACKGROUND_PATH, DEFAULT_BACKGROUND_PATH
from jrys_types import BackgroundAsset
from jrys_config import JRYS_CONFIG

from gsuid_core.logger import logger

_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}


async def _read_text(path: Path) -> str:
    async with aiofiles.open(path, encoding="utf-8") as file:
        return await file.read()


async def _read_bytes(path: Path) -> bytes:
    async with aiofiles.open(path, "rb") as file:
        return await file.read()


async def _expand_source(source: str) -> list[str]:
    if source.startswith(("http://", "https://")):
        return [source]
    if source.startswith("file://"):
        source = urlparse(source).path
    path = Path(source)
    if path.is_dir():
        candidates: list[str] = []
        for child in path.rglob("*"):
            if child.is_file() and child.suffix.lower() in _IMAGE_SUFFIXES:
                candidates.append(str(child))
            elif child.is_file() and child.suffix.lower() == ".txt":
                candidates.extend(
                    line.strip()
                    for line in (await _read_text(child)).splitlines()
                    if line.strip()
                )
        return candidates
    if path.is_file() and path.suffix.lower() == ".txt":
        return [
            line.strip()
            for line in (await _read_text(path)).splitlines()
            if line.strip()
        ]
    if path.is_file() and path.suffix.lower() in _IMAGE_SUFFIXES:
        return [str(path)]
    return []


async def _load_source(source: str) -> BackgroundAsset | None:
    if source.startswith(("http://", "https://")):
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(source)
        if response.status_code >= 400:
            return None
        image = Image.open(BytesIO(response.content)).convert("RGBA")
        return BackgroundAsset(source=source, image=image)
    path = Path(source)
    if not path.exists():
        return None
    image = Image.open(BytesIO(await _read_bytes(path))).convert("RGBA")
    return BackgroundAsset(source=source, image=image)


async def get_background() -> BackgroundAsset:
    configured = JRYS_CONFIG.get_config("background_sources").data
    sources = list(configured) if configured else []
    if str(DEFAULT_BACKGROUND_PATH) not in sources:
        sources.append(str(DEFAULT_BACKGROUND_PATH))
    if str(BACKGROUND_PATH) not in sources:
        sources.append(str(BACKGROUND_PATH))
    candidates: list[str] = []
    for source in sources:
        candidates.extend(await _expand_source(source))
    if not candidates:
        raise FileNotFoundError("JRYS 没有可用的背景图片")
    random.shuffle(candidates)
    for candidate in candidates:
        background = await _load_source(candidate)
        if background is not None:
            if JRYS_CONFIG.get_config("debug").data:
                logger.info(f"[JRYS] 使用背景: {candidate}")
            return background
    raise FileNotFoundError("JRYS 背景图片均无法读取")


async def load_background(source: str) -> BackgroundAsset | None:
    return await _load_source(source)

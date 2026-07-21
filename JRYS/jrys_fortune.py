import json
import asyncio
import hashlib
from typing import Dict, List
from datetime import date

import aiofiles

from JRYS.jrys_paths import FORTUNE_PATH
from JRYS.jrys_types import FortuneEntry, FortuneResult
from JRYS.jrys_config import JRYS_CONFIG

_fortune_cache: Dict[int, List[FortuneEntry]] | None = None
_fortune_lock = asyncio.Lock()
_LUCK_VALUES = (0, 14, 28, 42, 56, 70, 84, 98)


async def _read_fortune_data() -> Dict[int, List[FortuneEntry]]:
    global _fortune_cache
    if _fortune_cache is not None:
        return _fortune_cache
    async with _fortune_lock:
        if _fortune_cache is not None:
            return _fortune_cache
        async with aiofiles.open(FORTUNE_PATH, encoding="utf-8") as file:
            raw = json.loads(await file.read())
        if not isinstance(raw, dict):
            raise ValueError("JRYS 数据文件必须是对象")
        parsed: Dict[int, List[FortuneEntry]] = {}
        for key, values in raw.items():
            luck_value = int(key)
            if not isinstance(values, list):
                raise ValueError(f"JRYS 数据项 {key} 必须是数组")
            entries: List[FortuneEntry] = []
            for value in values:
                if not isinstance(value, dict):
                    raise ValueError(f"JRYS 数据项 {key} 包含非法条目")
                entries.append(
                    FortuneEntry(
                        fortuneSummary=str(value["fortuneSummary"]),
                        luckyStar=str(value["luckyStar"]),
                        signText=str(value["signText"]),
                        unsignText=str(value["unsignText"]),
                        luckValue=(
                            int(value["luckValue"])
                            if "luckValue" in value
                            else luck_value
                        ),
                    )
                )
            parsed[luck_value] = entries
        _fortune_cache = parsed
        return parsed


def _config_int(key: str) -> int:
    return int(JRYS_CONFIG.get_config(key).data)


def _weights() -> Dict[int, int]:
    configured = {
        luck_value: _config_int(f"weight_{luck_value}")
        for luck_value in _LUCK_VALUES
    }
    if any(configured.values()):
        return configured
    return {0: 5, 14: 10, 28: 12, 42: 15, 56: 30, 70: 35, 84: 45, 98: 25}


def _seed_bytes(user_id: str, day: date, salt: str) -> bytes:
    value = f"{user_id}|{day.isoformat()}|{salt}".encode("utf-8")
    return hashlib.sha256(value).digest()


async def get_fortune(user_id: str, day: date, salt: str = "") -> FortuneResult:
    data = await _read_fortune_data()
    seed = _seed_bytes(user_id, day, salt)
    weights = _weights()
    total = sum(weight for weight in weights.values() if weight > 0)
    if total <= 0:
        raise ValueError("JRYS 运势权重总和必须大于 0")
    pick = int.from_bytes(seed[:8], "big") % total
    luck_value = 0
    for candidate in _LUCK_VALUES:
        weight = max(weights[candidate], 0)
        if pick < weight:
            luck_value = candidate
            break
        pick -= weight
    entries = data[luck_value]
    entry = entries[int.from_bytes(seed[8:16], "big") % len(entries)]
    if JRYS_CONFIG.get_config("debug").data:
        from gsuid_core.logger import logger

        logger.info(f"[JRYS] {user_id} {day.isoformat()} -> {luck_value}")
    return FortuneResult(
        fortune_summary=entry["fortuneSummary"],
        lucky_star=entry["luckyStar"],
        sign_text=entry["signText"],
        unsign_text=entry["unsignText"],
        luck_value=entry["luckValue"],
    )


def fortune_text(result: FortuneResult) -> str:
    return "\n".join(
        (
            result.fortune_summary,
            result.lucky_star,
            result.sign_text,
            result.unsign_text,
        )
    )

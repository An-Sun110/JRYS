import json
import time
import asyncio
import secrets
from typing import TypedDict

import aiofiles

from JRYS.jrys_paths import RECORD_PATH


class OriginalImageRecord(TypedDict):
    token: str
    source: str
    message_ids: list[str]
    bot_id: str
    group_id: str
    user_id: str
    created_at: int


_record_lock = asyncio.Lock()


async def _read_records() -> list[OriginalImageRecord]:
    if not RECORD_PATH.exists():
        return []
    async with aiofiles.open(RECORD_PATH, encoding="utf-8") as file:
        raw = json.loads(await file.read())
    if not isinstance(raw, list):
        raise ValueError("JRYS 原图记录文件必须是数组")
    records: list[OriginalImageRecord] = []
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError("JRYS 原图记录包含非法条目")
        message_ids_raw = item["message_ids"]
        if not isinstance(message_ids_raw, list):
            raise ValueError("JRYS 原图记录 message_ids 必须是数组")
        records.append(
            OriginalImageRecord(
                token=str(item["token"]),
                source=str(item["source"]),
                message_ids=[str(message_id) for message_id in message_ids_raw],
                bot_id=str(item["bot_id"]) if "bot_id" in item else "",
                group_id=(str(item["group_id"]) if "group_id" in item else ""),
                user_id=str(item["user_id"]) if "user_id" in item else "",
                created_at=int(item["created_at"]),
            )
        )
    return records


async def _write_records(records: list[OriginalImageRecord]) -> None:
    RECORD_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(RECORD_PATH, "w", encoding="utf-8") as file:
        await file.write(json.dumps(records, ensure_ascii=False, indent=2))


async def create_original_record(
    source: str,
    bot_id: str,
    group_id: str,
    user_id: str,
) -> str:
    async with _record_lock:
        records = await _read_records()
        token = secrets.token_hex(4)
        records.append(
            OriginalImageRecord(
                token=token,
                source=source,
                message_ids=[],
                bot_id=bot_id,
                group_id=group_id,
                user_id=user_id,
                created_at=int(time.time()),
            )
        )
        await _write_records(records)
        return token


async def attach_message_ids(token: str, message_ids: list[str] | None) -> None:
    if not message_ids:
        return
    async with _record_lock:
        records = await _read_records()
        for record in records:
            if record["token"] == token:
                record["message_ids"] = message_ids
                break
        await _write_records(records)


async def find_original_source(
    identifier: str,
    remove: bool,
    bot_id: str,
    group_id: str,
    user_id: str,
    allow_scope_fallback: bool,
) -> str | None:
    async with _record_lock:
        records = await _read_records()
        matched_index: int | None = None
        for index, record in enumerate(records):
            if (
                record["token"] == identifier
                or identifier in record["message_ids"]
            ):
                matched_index = index
                break
        if matched_index is None and allow_scope_fallback:
            for index in range(len(records) - 1, -1, -1):
                record = records[index]
                if (
                    record["bot_id"] == bot_id
                    and record["group_id"] == group_id
                    and record["user_id"] == user_id
                ):
                    matched_index = index
                    break
        if matched_index is None:
            return None
        source = records[matched_index]["source"]
        if remove:
            records.pop(matched_index)
            await _write_records(records)
        return source

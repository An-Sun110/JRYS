from datetime import datetime

from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from JRYS.jrys_config import JRYS_CONFIG
from gsuid_core.models import Event
from JRYS.jrys_fortune import get_fortune, fortune_text
from JRYS.jrys_storage import (
    attach_message_ids,
    find_original_source,
    create_original_record,
)
from gsuid_core.segment import MessageSegment
from JRYS.jrys_renderer import render_fortune_card
from JRYS.jrys_background import get_background, load_background
from gsuid_core.message_models import Button
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import get_event_avatar

sv_jrys = SV("JRYS今日运势", priority=5000)


def _nickname(ev: Event) -> str:
    if "nickname" in ev.sender and ev.sender["nickname"]:
        return str(ev.sender["nickname"])
    return ev.user_id


def _command_aliases() -> tuple[str, ...]:
    configured = JRYS_CONFIG.get_config("command").data.strip()
    aliases = ["jrysprpr", "今日运势", "运势", "jrys"]
    if configured and configured not in aliases:
        aliases.insert(0, configured)
    return tuple(aliases)


def _original_command_aliases() -> tuple[str, ...]:
    configured = JRYS_CONFIG.get_config("original_image_command").data.strip()
    aliases = ["查看运势背景图", "获取原图", "原图"]
    if configured and configured not in aliases:
        aliases.insert(0, configured)
    return tuple(aliases)


def _is_split_mode(text: str) -> bool:
    return text.strip().lower() in {"-s", "--split", "split", "图文"}


async def _send_controls(bot: Bot, token: str) -> None:
    mode = JRYS_CONFIG.get_config("original_image_hint_mode").data
    if mode == "off":
        return
    original_command = JRYS_CONFIG.get_config("original_image_command").data
    original_text = f"{original_command} {token}"
    if mode == "separate":
        await bot.send(f"获取本次背景原图：{original_text}")
        return
    await bot.send_option(
        reply=f"原图令牌：{token}",
        option_list=[
            Button("再来一张", "jrysprpr", "正在重新抽取"),
            Button("查看原图", original_text, "正在获取原图"),
        ],
        unsuported_platform=True,
    )


@sv_jrys.on_command(
    _command_aliases(),
    to_ai="""查看用户当天的固定运势。
    当用户询问今日运势、今日手气或想抽运势卡时调用。

    Args:
        text: 留空生成运势卡；传入 -s 或 图文 时返回背景图和文字。
    """,
)
async def cmd_jrys(bot: Bot, ev: Event) -> None:
    hint = JRYS_CONFIG.get_config("render_hint").data.strip()
    hint_ids = None
    if hint:
        hint_ids = await bot.send(hint, wait_recall=True)

    now = datetime.now()
    result = await get_fortune(ev.user_id, now.date())
    background = await get_background()
    token: str | None = None
    if JRYS_CONFIG.get_config("enable_original_image").data:
        token = await create_original_record(
            background.source,
            ev.bot_id,
            ev.group_id or "",
            ev.user_id,
        )

    if _is_split_mode(ev.text):
        original_image = await convert_img(background.image)
        message_ids = await bot.send(
            [
                MessageSegment.image(original_image),
                MessageSegment.text(f"\n{fortune_text(result)}"),
            ],
            wait_recall=token is not None,
        )
    else:
        avatar = await get_event_avatar(ev)
        card = await render_fortune_card(
            background.image,
            avatar,
            _nickname(ev),
            now.strftime("%Y/%m/%d"),
            result,
        )
        message_ids = await bot.send(
            await convert_img(card),
            wait_recall=token is not None,
        )

    if token is not None:
        await attach_message_ids(token, message_ids)
        await _send_controls(bot, token)
    if hint_ids is not None and JRYS_CONFIG.get_config(
        "recall_render_hint"
    ).data:
        await bot.unsend(hint_ids)


@sv_jrys.on_command(_original_command_aliases())
async def cmd_original_image(bot: Bot, ev: Event) -> None:
    if not JRYS_CONFIG.get_config("enable_original_image").data:
        await bot.send("原图功能当前未启用。")
        return
    identifier = ev.text.strip()
    has_reply = ev.reply is not None
    if not identifier and ev.reply is not None:
        identifier = ev.reply
    if not identifier:
        return
    source = await find_original_source(
        identifier,
        remove=JRYS_CONFIG.get_config("auto_clean_original_image").data,
        bot_id=ev.bot_id,
        group_id=ev.group_id or "",
        user_id=ev.user_id,
        allow_scope_fallback=has_reply,
    )
    if source is None:
        await bot.send("没有找到你最近一次运势使用的背景图。")
        return
    background = await load_background(source)
    if background is None:
        await bot.send("背景图片已不存在或暂时无法访问。")
        return
    await bot.send(await convert_img(background.image))

import re
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageFilter

from gsuid_core.pool import to_thread
from JRYS.jrys_paths import FONT_PATH
from JRYS.jrys_types import FortuneResult
from JRYS.jrys_config import JRYS_CONFIG

_WIDTH = 1080
_HEIGHT = 1920
_OVERLAY_TOP = 1240
_GRADIENT_COLORS = (
    (252, 181, 181),
    (252, 214, 174),
    (253, 232, 166),
    (195, 247, 177),
    (174, 214, 250),
    (196, 175, 245),
    (241, 175, 204),
)


def _font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size)


def _rgba(value: str) -> tuple[int, int, int, int]:
    if value.startswith("#"):
        return ImageColor.getcolor(value, "RGBA")
    match = re.fullmatch(
        r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)"
        r"(?:\s*,\s*([0-9.]+))?\s*\)",
        value,
    )
    if match is None:
        raise ValueError(f"不支持的颜色格式: {value}")
    red, green, blue = (int(match.group(index)) for index in range(1, 4))
    alpha_text = match.group(4)
    alpha = 255
    if alpha_text is not None:
        alpha_value = float(alpha_text)
        alpha = (
            round(alpha_value * 255)
            if alpha_value <= 1
            else round(alpha_value)
        )
    return red, green, blue, alpha


def _cover(image: Image.Image, width: int, height: int) -> Image.Image:
    ratio = max(width / image.width, height / image.height)
    resized = image.resize(
        (round(image.width * ratio), round(image.height * ratio)),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height)).convert("RGBA")


def _circle_avatar(avatar: Image.Image, size: int) -> Image.Image:
    result = _cover(avatar, size, size)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    result.putalpha(mask)
    return result


def _wrap(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    lines: list[str] = []
    current = ""
    for char in text:
        candidate = current + char
        box = draw.textbbox((0, 0), candidate, font=font)
        if box[2] - box[0] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = char
    if current:
        lines.append(current)
    return lines


def _center_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
) -> None:
    draw.text((_WIDTH // 2, y), text, font=font, fill=fill, anchor="ma")


def _draw_gradient_text(
    image: Image.Image,
    text: str,
    y: int,
    font: ImageFont.FreeTypeFont,
) -> None:
    draw = ImageDraw.Draw(image)
    box = draw.textbbox((0, 0), text, font=font)
    width = box[2] - box[0]
    x = (_WIDTH - width) // 2
    for index, char in enumerate(text):
        color = _GRADIENT_COLORS[index % len(_GRADIENT_COLORS)]
        draw.text((x, y), char, font=font, fill=color + (255,))
        char_box = draw.textbbox((0, 0), char, font=font)
        x += char_box[2] - char_box[0]


def _draw_dashed_box(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    color: tuple[int, int, int, int],
    width: int,
) -> None:
    left, top, right, bottom = box
    dash = 18
    gap = 12
    for x in range(left, right, dash + gap):
        draw.line((x, top, min(x + dash, right), top), fill=color, width=width)
        draw.line(
            (x, bottom, min(x + dash, right), bottom),
            fill=color,
            width=width,
        )
    for y in range(top, bottom, dash + gap):
        draw.line((left, y, left, min(y + dash, bottom)), fill=color, width=width)
        draw.line(
            (right, y, right, min(y + dash, bottom)),
            fill=color,
            width=width,
        )


@to_thread
def render_fortune_card(
    background: Image.Image,
    avatar: Image.Image,
    nickname: str,
    date_text: str,
    result: FortuneResult,
) -> bytes:
    image = _cover(background, _WIDTH, _HEIGHT)
    blur_radius = int(JRYS_CONFIG.get_config("mask_blur").data)
    blurred = image.crop((0, _OVERLAY_TOP, _WIDTH, _HEIGHT)).filter(
        ImageFilter.GaussianBlur(blur_radius)
    )
    image.paste(blurred, (0, _OVERLAY_TOP))
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ImageDraw.Draw(overlay).rounded_rectangle(
        (0, _OVERLAY_TOP, _WIDTH, _HEIGHT + 30),
        radius=42,
        fill=_rgba(JRYS_CONFIG.get_config("mask_color").data),
    )
    image = Image.alpha_composite(image, overlay)
    draw = ImageDraw.Draw(image)

    avatar_image = _circle_avatar(avatar, 128)
    image.paste(avatar_image, (42, _OVERLAY_TOP + 34), avatar_image)
    draw.text(
        (190, _OVERLAY_TOP + 72),
        nickname,
        font=_font(44),
        fill=(255, 255, 255, 245),
        anchor="lm",
    )

    text_color = _rgba(JRYS_CONFIG.get_config("text_color").data)
    description_color = _rgba(
        JRYS_CONFIG.get_config("description_color").data
    )
    _center_text(draw, date_text, _OVERLAY_TOP + 48, _font(48), text_color)
    _center_text(
        draw,
        result.fortune_summary,
        _OVERLAY_TOP + 132,
        _font(62),
        text_color,
    )
    if JRYS_CONFIG.get_config("gradient_stars").data:
        _draw_gradient_text(
            image,
            result.lucky_star,
            _OVERLAY_TOP + 215,
            _font(58),
        )
    else:
        _center_text(
            draw,
            result.lucky_star,
            _OVERLAY_TOP + 215,
            _font(58),
            text_color,
        )

    box_left = 44
    box_right = _WIDTH - 44
    sign_top = _OVERLAY_TOP + 310
    sign_font = _font(32)
    description_font = _font(26)
    sign_lines = _wrap(
        draw,
        result.sign_text,
        sign_font,
        box_right - box_left - 48,
    )
    desc_lines = _wrap(
        draw,
        result.unsign_text,
        description_font,
        box_right - box_left - 48,
    )
    line_height = 49
    description_line_height = 38
    sign_height = max(90, len(sign_lines) * line_height + 38)
    desc_height = max(
        150,
        len(desc_lines) * description_line_height + 38,
    )
    dashed_color = _rgba(JRYS_CONFIG.get_config("dashed_color").data)
    dashed_width = max(
        1,
        int(JRYS_CONFIG.get_config("dashed_width").data),
    )
    sign_box = (
        box_left,
        sign_top,
        box_right,
        sign_top + sign_height,
    )
    _draw_dashed_box(draw, sign_box, dashed_color, dashed_width)
    for index, line in enumerate(sign_lines):
        draw.text(
            (box_left + 24, sign_top + 19 + index * line_height),
            line,
            font=sign_font,
            fill=description_color,
        )

    desc_top = sign_top + sign_height + 22
    desc_box = (
        box_left,
        desc_top,
        box_right,
        desc_top + desc_height,
    )
    _draw_dashed_box(draw, desc_box, dashed_color, dashed_width)
    for index, line in enumerate(desc_lines):
        draw.text(
            (
                box_left + 24,
                desc_top + 19 + index * description_line_height,
            ),
            line,
            font=description_font,
            fill=description_color,
        )

    _center_text(
        draw,
        "仅供娱乐 | 相信科学 | 请勿迷信",
        _HEIGHT - 38,
        _font(26),
        (255, 255, 255, 210),
    )
    output = BytesIO()
    quality = min(
        95,
        max(20, int(JRYS_CONFIG.get_config("quality").data)),
    )
    image.convert("RGB").save(
        output,
        format="JPEG",
        quality=quality,
        optimize=True,
    )
    return output.getvalue()

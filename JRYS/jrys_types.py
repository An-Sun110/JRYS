from typing import TypedDict
from dataclasses import dataclass

from PIL import Image


class FortuneEntry(TypedDict):
    fortuneSummary: str
    luckyStar: str
    signText: str
    unsignText: str
    luckValue: int


@dataclass(frozen=True)
class FortuneResult:
    fortune_summary: str
    lucky_star: str
    sign_text: str
    unsign_text: str
    luck_value: int


@dataclass(frozen=True)
class BackgroundAsset:
    source: str
    image: Image.Image

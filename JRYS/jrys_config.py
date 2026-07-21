from typing import Dict

from jrys_paths import BACKGROUND_PATH, DEFAULT_BACKGROUND_PATH

from gsuid_core.data_store import get_res_path
from gsuid_core.utils.plugins_config.models import (
    GSC,
    GsIntConfig,
    GsStrConfig,
    GsBoolConfig,
    GsColorConfig,
    GsListStrConfig,
)
from gsuid_core.utils.plugins_config.gs_config import StringConfig

CONFIG_DEFAULT: Dict[str, GSC] = {
    "command": GsStrConfig(
        title="运势指令",
        desc="查看今日运势的主指令，可留空以使用默认别名",
        data="jrysprpr",
    ),
    "original_image_command": GsStrConfig(
        title="原图指令",
        desc="通过令牌获取本次运势使用的背景图",
        data="查看运势背景图",
    ),
    "enable_original_image": GsBoolConfig(
        title="启用原图功能",
        desc="为每张运势图生成原图令牌",
        data=True,
    ),
    "auto_clean_original_image": GsBoolConfig(
        title="获取后清理令牌",
        desc="成功获取背景图后删除对应的令牌记录",
        data=True,
    ),
    "render_hint": GsStrConfig(
        title="渲染提示语",
        desc="生成图片期间发送的提示语，留空则不发送",
        data="正在分析你的运势哦~请稍等~~",
    ),
    "recall_render_hint": GsBoolConfig(
        title="自动撤回提示语",
        desc="运势图片发送成功后撤回渲染提示语",
        data=True,
    ),
    "original_image_hint_mode": GsStrConfig(
        title="原图提示方式",
        desc="图片后附带原图令牌的方式",
        data="combined",
        options=["off", "combined", "separate"],
    ),
    "background_sources": GsListStrConfig(
        title="背景图片来源",
        desc="支持图片文件、目录、txt 文件或网络 URL；留空时使用内置背景",
        data=[str(DEFAULT_BACKGROUND_PATH), str(BACKGROUND_PATH)],
    ),
    "quality": GsIntConfig(
        title="图片质量",
        desc="JPEG 图片质量，范围 20-95",
        data=88,
        max_value=95,
    ),
    "mask_color": GsColorConfig(
        title="底部蒙版颜色",
        desc="支持 rgba()/rgb() 或十六进制颜色",
        data="rgba(0,0,0,0.55)",
    ),
    "mask_blur": GsIntConfig(
        title="蒙版模糊半径",
        desc="背景底部的模糊半径",
        data=10,
        max_value=100,
    ),
    "text_color": GsColorConfig(
        title="运势文字颜色",
        desc="主运势文字颜色",
        data="#FFFFFF",
    ),
    "description_color": GsColorConfig(
        title="说明文字颜色",
        desc="签文和说明文字颜色",
        data="#FFFFFF",
    ),
    "dashed_color": GsColorConfig(
        title="虚线框颜色",
        desc="签文区域边框颜色",
        data="rgba(255,255,255,0.55)",
    ),
    "dashed_width": GsIntConfig(
        title="虚线框粗细",
        desc="签文区域虚线框粗细",
        data=5,
        max_value=20,
    ),
    "gradient_stars": GsBoolConfig(
        title="彩色星星",
        desc="是否使用彩色渐变绘制星星",
        data=True,
    ),
    "debug": GsBoolConfig(
        title="调试日志",
        desc="输出运势抽取和背景选择日志",
        data=False,
    ),
    "weight_0": GsIntConfig(
        title="0 分运势权重",
        desc="运势抽取权重",
        data=5,
        max_value=100,
    ),
    "weight_14": GsIntConfig(
        title="14 分运势权重",
        desc="运势抽取权重",
        data=10,
        max_value=100,
    ),
    "weight_28": GsIntConfig(
        title="28 分运势权重",
        desc="运势抽取权重",
        data=12,
        max_value=100,
    ),
    "weight_42": GsIntConfig(
        title="42 分运势权重",
        desc="运势抽取权重",
        data=15,
        max_value=100,
    ),
    "weight_56": GsIntConfig(
        title="56 分运势权重",
        desc="运势抽取权重",
        data=30,
        max_value=100,
    ),
    "weight_70": GsIntConfig(
        title="70 分运势权重",
        desc="运势抽取权重",
        data=35,
        max_value=100,
    ),
    "weight_84": GsIntConfig(
        title="84 分运势权重",
        desc="运势抽取权重",
        data=45,
        max_value=100,
    ),
    "weight_98": GsIntConfig(
        title="98 分运势权重",
        desc="运势抽取权重",
        data=25,
        max_value=100,
    ),
}


JRYS_CONFIG = StringConfig(
    "JRYS",
    get_res_path("JRYS") / "config.json",
    CONFIG_DEFAULT,
)

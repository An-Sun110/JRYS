# JRYS · jrys-prpr

Koishi 插件 `jrys-prpr` 的 GsCore 移植版，使用同源运势数据、字体和默认背景，
通过 PIL 生成 `1080 x 1920` 运势卡片。

## 安装

在 `gsuid_core/plugins` 目录中克隆仓库：

```bash
git clone https://github.com/An-Sun110/JRYS.git
```

最终目录必须保持为：

```text
gsuid_core/plugins/JRYS/
├── __init__.py
├── __nest__.py
└── JRYS/
    ├── __init__.py
    └── __full__.py
```

GsCore 的嵌套插件加载要求外层目录和内层包同名，因此不要将目录改为
`gsuid-core-jrys`、`JRYS-main` 或其他名称。

## 命令

| 命令 | 说明 |
|---|---|
| `jrysprpr` / `今日运势` / `运势` / `jrys` | 获取当天固定运势卡 |
| `jrysprpr -s` / `今日运势 图文` | 返回背景原图与文字运势 |
| `查看运势背景图 <令牌>` / `获取原图 <令牌>` / `原图 <令牌>` | 获取运势卡所用背景 |

使用 `原图` 时必须回复一张运势图片。适配器支持消息回执时，插件会优先按消息 ID
查找；无法提供出站消息 ID 的平台会回退到该用户在当前会话中的最近一次运势背景。
未引用消息时插件会静默忽略；携带明确令牌的原图命令不受引用限制。

## 配置

在 WebConsole 的插件配置中打开 `JRYS`，可以调整：

- 主命令与原图命令
- 原图令牌开关、获取后自动清理
- 渲染提示语及自动撤回
- 背景图片文件、目录、txt 列表或网络 URL
- 图片质量、蒙版、颜色、模糊和虚线框
- 0 / 14 / 28 / 42 / 56 / 70 / 84 / 98 八档运势权重

自定义背景也可以直接放入：

```text
gsuid_core/data/JRYS/bg
```

## 与 Koishi 版本的差异

- QQ 模板 ID、原生 Markdown JSON 改为 GsCore 跨平台按钮。
- Koishi `monetary` 服务没有跨框架通用接口，因此未移植货币奖励。
- 运势卡、图文模式、概率权重、背景来源和原图获取均已保留。

## 数据与资源

运势文案、轻量字体和默认背景来自
`koishi-plugin-jrys-prpr`，原项目采用 MIT License。

本功能仅供娱乐，请相信科学，勿迷信。

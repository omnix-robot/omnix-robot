"""生成 GitHub 主页横幅（浅色 / 深色两版）。

用法: python -I tools/make_banner.py
输出: assets/banner-light.svg, assets/banner-dark.svg
"""
import math
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

THEMES = {
    "light": dict(bg="#f3f3ef", ink="#182124", sub="#5b6366", line="#9aa0a0", accent="#9a5a12", rule="#d9d9d2"),
    "dark": dict(bg="#11171a", ink="#ecebe6", sub="#a3a9aa", line="#5d666a", accent="#d08a3a", rule="#2a3236"),
}

W, H = 1280, 400
FONT = "'PingFang SC','Microsoft YaHei','Noto Sans CJK SC','Source Han Sans SC',system-ui,sans-serif"


def logo_paths(fill: str) -> str:
    src = (ASSETS / "omnix-logo.svg").read_text(encoding="utf-8")
    paths = re.findall(r"<path\b.*?/>", src, flags=re.S)
    return "\n".join(re.sub(r'fill="[^"]*"', f'fill="{fill}"', p) for p in paths)


def line_field(t: dict) -> str:
    """右侧图案：左边散乱的短笔划逐渐汇聚成右边整齐的平行线（示范数据 → 结构化数据）。"""
    rng = random.Random(7)
    x0, x1, xm = 700, 1220, 940
    y_top, y_bot = 90, 310
    n_lanes = 9
    lanes = [y_top + i * (y_bot - y_top) / (n_lanes - 1) for i in range(n_lanes)]
    out = []
    # 散乱笔划：越靠近 xm 越贴近各自的车道、方向越水平
    for _ in range(420):
        u = rng.random() ** 0.8
        x = x0 + u * (xm - x0)
        lane = rng.choice(lanes)
        spread = (1 - u) * 110 + 4
        y = lane + rng.gauss(0, spread * 0.45)
        if not (y_top - 45 < y < y_bot + 45):
            continue
        ang = rng.gauss(0, (1 - u) * 1.3 + 0.05)
        L = 6 + rng.random() * 9
        dx, dy = math.cos(ang) * L / 2, math.sin(ang) * L / 2
        op = 0.35 + 0.5 * u
        out.append(
            f'<line x1="{x-dx:.1f}" y1="{y-dy:.1f}" x2="{x+dx:.1f}" y2="{y+dy:.1f}" '
            f'stroke="{t["line"]}" stroke-width="1.1" stroke-linecap="round" opacity="{op:.2f}"/>'
        )
    # 分界竖线
    out.append(f'<line x1="{xm}" y1="{y_top-60}" x2="{xm}" y2="{y_bot+60}" stroke="{t["rule"]}" stroke-width="1"/>')
    # 整齐的平行线，其中一条为点缀色并带流动动画
    for i, y in enumerate(lanes):
        end = x1 - rng.random() * 18
        if i == 4:
            L = end - xm
            out.append(f'<line x1="{xm}" y1="{y:.1f}" x2="{end:.1f}" y2="{y:.1f}" stroke="{t["accent"]}" stroke-width="1.8"/>')
            out.append(
                f'<line x1="{xm}" y1="{y:.1f}" x2="{end:.1f}" y2="{y:.1f}" stroke="{t["accent"]}" stroke-width="5" stroke-linecap="round" '
                f'stroke-dasharray="26 {L:.0f}" opacity="0.55">'
                f'<animate attributeName="stroke-dashoffset" from="26" to="{-L:.0f}" dur="3.2s" repeatCount="indefinite"/>'
                f"</line>"
            )
        else:
            out.append(f'<line x1="{xm}" y1="{y:.1f}" x2="{end:.1f}" y2="{y:.1f}" stroke="{t["line"]}" stroke-width="1.1" opacity="0.85"/>')
    return "\n".join(out)


def banner(name: str, t: dict) -> str:
    # 原 logo 3898x2005，缩放到宽 300
    s = 250 / 3898
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="OMNI-X 全为具身 — 为物理 AI 打造硬件与数据">
<rect width="{W}" height="{H}" fill="{t['bg']}"/>
<g transform="translate(74,48) scale({s:.5f})">
{logo_paths(t['ink'])}
</g>
<text x="74" y="250" font-family="{FONT}" font-size="40" font-weight="600" fill="{t['ink']}" letter-spacing="2">为物理 AI 打造硬件与数据</text>
<text x="76" y="285" font-family="{FONT}" font-size="19" fill="{t['sub']}" letter-spacing="0.5">Hardware &amp; Data for Physical AI</text>
<line x1="76" y1="322" x2="112" y2="322" stroke="{t['accent']}" stroke-width="3"/>
<text x="124" y="328" font-family="{FONT}" font-size="16" fill="{t['sub']}" letter-spacing="1">关节模组 · 力传感 · 数采系统 · 机器人</text>
{line_field(t)}
</svg>
"""


if __name__ == "__main__":
    for name, t in THEMES.items():
        (ASSETS / f"banner-{name}.svg").write_text(banner(name, t), encoding="utf-8")
        print("wrote", f"banner-{name}.svg")

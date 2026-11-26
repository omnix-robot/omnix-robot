"""生成主页主视觉与社交图标行。

用法: python -I tools/make_hero.py
输出:
  assets/hero.svg                   纸白素描主视觉卡（明暗模式共用）
  assets/icon-<名>-{light,dark}.svg  社交图标
"""
import base64
import io
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
TOOLS = ROOT / "tools"

INK = "#182124"
ACCENT = "#9a5a12"
ACCENT_HI = "#d08a3a"
FONT = "'PingFang SC','Microsoft YaHei','Noto Sans CJK SC','Source Han Sans SC',system-ui,-apple-system,'Segoe UI',sans-serif"


def logo_paths(fill: str) -> str:
    src = (ASSETS / "omnix-logo.svg").read_text(encoding="utf-8")
    return "\n".join(re.sub(r'fill="[^"]*"', f'fill="{fill}"', p) for p in re.findall(r"<path\b.*?/>", src, flags=re.S))


def sketch_data_uri(target_w: int) -> tuple[str, int, int]:
    im = Image.open(TOOLS / "robot-sketch.webp").convert("RGBA")
    s = target_w / im.width
    im = im.resize((target_w, round(im.height * s)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=78)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode(), im.width, im.height


def pencil(x0, x1, y, seed, amp=0.9, color=INK, op=0.55, w=1.0):
    """略带抖动的铅笔线。"""
    import random
    r = random.Random(seed)
    pts, x = [], x0
    while x < x1:
        pts.append(f"{x:.1f},{y + r.uniform(-amp, amp):.1f}")
        x += r.uniform(18, 34)
    pts.append(f"{x1:.1f},{y:.1f}")
    return f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-opacity="{op}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'


def hero() -> str:
    W, H = 1280, 560
    PAPER, SUB = "#f3f3ef", "#6b7275"
    uri, iw, ih = sketch_data_uri(1300)
    disp_w = 760
    disp_h = ih * disp_w / iw
    ix, iy = W - disp_w - 24, (H - disp_h) / 2 + 6
    s = 200 / 3898
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="OMNI-X 全为具身：为物理 AI 打造硬件与数据">
<defs><clipPath id="card"><rect width="{W}" height="{H}" rx="16"/></clipPath></defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="{PAPER}"/>
<image x="{ix:.1f}" y="{iy:.1f}" width="{disp_w}" height="{disp_h:.1f}" xlink:href="{uri}" href="{uri}"/>
<g transform="translate(72,62) scale({s:.5f})">
{logo_paths(INK)}
</g>
<line x1="290" y1="96" x2="290" y2="128" stroke="{INK}" stroke-opacity="0.25"/>
<text x="306" y="119" font-family="{FONT}" font-size="17" fill="{INK}" fill-opacity="0.8" letter-spacing="4">全为具身</text>
<text x="72" y="240" font-family="{FONT}" font-size="46" font-weight="700" fill="{INK}" letter-spacing="2">为物理 AI</text>
<text x="72" y="300" font-family="{FONT}" font-size="46" font-weight="700" fill="{INK}" letter-spacing="2">打造硬件与数据</text>
{pencil(74, 236, 318, 3, color=ACCENT, op=0.9, w=2.2)}
<text x="74" y="356" font-family="{FONT}" font-size="17" fill="{SUB}" letter-spacing="0.5">Hardware &amp; Data for Physical AI</text>
</g>
</svg>
"""


# 自绘图标（24 视框，描边风格）
GLOBE = '<g fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><ellipse cx="12" cy="12" rx="4.2" ry="10"/><path d="M2.5 9h19M2.5 15h19"/></g>'
MAIL = '<g fill="none" stroke="{c}" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"><rect x="2" y="4.5" width="20" height="15" rx="2.5"/><path d="M3 6.5l9 6.5 9-6.5"/></g>'

ICONS = ["site", "bilibili", "tiktok", "xiaohongshu", "linkedin", "x", "mail"]
ICON_COLORS = {"light": INK, "dark": "#e6e6e1"}


def icon(name: str, color: str) -> str:
    if name == "site":
        glyph = GLOBE.format(c=color)
    elif name == "mail":
        glyph = MAIL.format(c=color)
    else:
        src = (TOOLS / "icons" / f"{name}.svg").read_text(encoding="utf-8")
        d = re.search(r'<path d="([^"]+)"', src).group(1)
        glyph = f'<path d="{d}" fill="{color}"/>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="48" height="40" viewBox="-12 -8 48 40">{glyph}</svg>\n'


if __name__ == "__main__":
    (ASSETS / "hero.svg").write_text(hero(), encoding="utf-8")
    for n in ICONS:
        for theme, c in ICON_COLORS.items():
            (ASSETS / f"icon-{n}-{theme}.svg").write_text(icon(n, c), encoding="utf-8")
    print("hero.svg", (ASSETS / "hero.svg").stat().st_size, "bytes")

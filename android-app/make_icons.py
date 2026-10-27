# -*- coding: utf-8 -*-
"""生成 App 启动图标。

用法：
  1) 把图片命名为 custom-icon.png 放在 android-app/ 下（也支持 jpg/jpeg/webp/bmp）
  2) 或运行时指定：python make_icons.py "D:\\some\\logo.png"

自动识别三种图：
  · 白底墨迹/印章图 → 自动裁出主体、把白底转透明、铺在指定底色上（默认黑）
  · 透明底 logo     → 直接居中，边缘取底色
  · 照片/满版图      → 等比裁切铺满，由系统裁形

没有自定义图片时，兜底生成朱红印章「清」字版。

输出：
  mipmap-<dpi>/ic_launcher.png            传统方形图标（API 24-25）
  mipmap-<dpi>/ic_launcher_round.png      圆形图标
  mipmap-<dpi>/ic_launcher_background.png 自适应图标底层（108dp）
  mipmap-<dpi>/ic_launcher_foreground.png 自适应图标前景层（108dp）
  mipmap-anydpi-v26/ic_launcher*.xml      自适应图标描述
  icon-preview.png                        圆角方形 + 圆形两种呈现预览
"""
import os
import sys
from collections import deque
from PIL import Image, ImageDraw, ImageFont, ImageFilter

APP_RES = r"F:\WorkBuddy\personal-website\android-app\app\src\main\res"
APP_DIR = r"F:\WorkBuddy\personal-website\android-app"
PREVIEW = os.path.join(APP_DIR, "icon-preview.png")

# ── 可调参数 ─────────────────────────────────────────────
CUSTOM_BG = (0, 0, 0, 255)      # 自定义图片的底色（logo / 墨迹图模式使用）
SAFE_RATIO = 0.76               # 图形在图标中的占比（越大越满，过大圆角遮罩会切边）
PAPER = (244, 241, 234, 255)    # 兜底印章版的纸色
SEAL = (176, 58, 46, 255)       # 兜底印章版的朱红
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"

DENSITIES = {"mdpi": 1.0, "hdpi": 1.5, "xhdpi": 2.0, "xxhdpi": 3.0, "xxxhdpi": 4.0}
LEGACY_BASE = 48
ADAPTIVE_BASE = 108
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".bmp")


# ───────────────────────── 基础图像操作 ─────────────────────────

def center_square(im):
    w, h = im.size
    s = min(w, h)
    left, top = (w - s) // 2, (h - s) // 2
    return im.crop((left, top, left + s, top + s))


def cover(im, size):
    """等比缩放并居中裁切，铺满 size×size。"""
    return center_square(im).resize((size, size), Image.LANCZOS)


def contain(im, size, sharpen=True):
    """等比缩放放进 size×size 透明画布，四周留白不裁切。"""
    w, h = im.size
    r = min(size / w, size / h)
    nw, nh = max(1, int(round(w * r))), max(1, int(round(h * r)))
    resized = im.resize((nw, nh), Image.LANCZOS)
    if sharpen and r > 1.2:
        # 小图放大后适度锐化，让笔画边缘不发虚
        resized = resized.filter(ImageFilter.UnsharpMask(radius=1.2, percent=90, threshold=2))
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(resized, ((size - nw) // 2, (size - nh) // 2), resized)
    return canvas


def rounded(img, radius_ratio=0.19):
    S = img.size[0]
    k = 4
    big = img.resize((S * k, S * k), Image.LANCZOS)
    mask = Image.new("L", (S * k, S * k), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, S * k - 1, S * k - 1], radius=S * k * radius_ratio, fill=255)
    out = Image.new("RGBA", (S * k, S * k), (0, 0, 0, 0))
    out.paste(big, (0, 0), mask)
    return out.resize((S, S), Image.LANCZOS)


def circular(img):
    S = img.size[0]
    k = 4
    big = img.resize((S * k, S * k), Image.LANCZOS)
    mask = Image.new("L", (S * k, S * k), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, S * k - 1, S * k - 1], fill=255)
    out = Image.new("RGBA", (S * k, S * k), (0, 0, 0, 0))
    out.paste(big, (0, 0), mask)
    return out.resize((S, S), Image.LANCZOS)


def has_transparent_border(im):
    """边缘是否大量透明 —— 判断是否为透明底 logo。"""
    im = im.convert("RGBA")
    w, h = im.size
    alpha = im.split()[3]
    px = alpha.load()
    total = trans = 0
    sx, sy = max(1, w // 48), max(1, h // 48)
    for x in range(0, w, sx):
        for y in (0, h - 1):
            total += 1
            if px[x, y] < 250:
                trans += 1
    for y in range(0, h, sy):
        for x in (0, w - 1):
            total += 1
            if px[x, y] < 250:
                trans += 1
    return total > 0 and (trans / total) > 0.5


def alpha_content_bbox(im, pad=2, thr=8):
    """按 alpha 通道求出实际内容边界，去掉四周大片透明留白。"""
    im = im.convert("RGBA")
    a = im.split()[3].point(lambda v: 255 if v > thr else 0)
    box = a.getbbox()
    if not box:
        return None
    x0, y0, x1, y1 = box
    return (max(0, x0 - pad), max(0, y0 - pad),
            min(im.width, x1 + pad), min(im.height, y1 + pad))


def is_paper_art(im):
    """大面积浅色底 + 少量深色笔画 → 典型的白底墨迹/印章图。"""
    im = im.convert("RGBA")
    w, h = im.size
    px = im.load()
    step = max(1, min(w, h) // 120)
    total = light = 0
    for y in range(0, h, step):
        for x in range(0, w, step):
            r, g, b, a = px[x, y]
            total += 1
            if a > 8 and min(r, g, b) > 235:
                light += 1
    return total > 0 and (light / total) > 0.6


# ───────────────────────── 主体定位与抠图 ─────────────────────────

def auto_crop_subject(im, cell=6, ink_threshold=200):
    """用连通域找画面中最主要的一团墨迹，返回其像素边界框。

    白底图上常伴随大量极淡的水印、噪点，直接取全图边界会把留白也算进去。
    这里按格子统计墨量，做八连通聚类，取墨量最大的连通域。
    """
    im = im.convert("RGBA")
    W, H = im.size
    px = im.load()
    gw, gh = (W + cell - 1) // cell, (H + cell - 1) // cell

    ink = [[0] * gw for _ in range(gh)]
    for y in range(H):
        row = ink[y // cell]
        for x in range(W):
            r, g, b, a = px[x, y]
            if a > 8 and min(r, g, b) < ink_threshold:
                row[x // cell] += 1

    thr = max(2, int(cell * cell * 0.03))
    marked = [[ink[j][i] >= thr for i in range(gw)] for j in range(gh)]

    seen = [[False] * gw for _ in range(gh)]
    best = None
    for j in range(gh):
        for i in range(gw):
            if not marked[j][i] or seen[j][i]:
                continue
            q = deque([(i, j)])
            seen[j][i] = True
            total = 0
            x0 = x1 = i
            y0 = y1 = j
            while q:
                ci, cj = q.popleft()
                total += ink[cj][ci]
                x0, x1 = min(x0, ci), max(x1, ci)
                y0, y1 = min(y0, cj), max(y1, cj)
                for di in (-1, 0, 1):
                    for dj in (-1, 0, 1):
                        ni, nj = ci + di, cj + dj
                        if 0 <= ni < gw and 0 <= nj < gh and marked[nj][ni] and not seen[nj][ni]:
                            seen[nj][ni] = True
                            q.append((ni, nj))
            if best is None or total > best[0]:
                best = (total, x0, y0, x1, y1)

    if best is None:
        return None
    _, x0, y0, x1, y1 = best
    pad = 2
    return (max(0, x0 * cell - pad), max(0, y0 * cell - pad),
            min(W, (x1 + 1) * cell + pad), min(H, (y1 + 1) * cell + pad))


def key_out_paper(im, paper=255.0):
    """把白纸底转为透明，并反解出真实墨色与覆盖率。

    模型：观测像素 = 覆盖率 × 墨色 + (1-覆盖率) × 纸色。
    先由最深的墨色确定满分覆盖率，再逐像素反解，得到干净的透明边缘，
    这样叠到任何底色（含纯黑）上都不会残留白边或灰雾。
    """
    im = im.convert("RGBA")
    w, h = im.size
    px = im.load()

    darkest = 255
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 8:
                darkest = min(darkest, min(r, g, b))
    darkest = min(darkest, 200)
    span = max(1.0, paper - darkest)

    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    op = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a <= 8:
                continue
            cov = (paper - min(r, g, b)) / span
            if cov <= 0.02:
                continue
            cov = min(1.0, cov)
            alpha = int(round(cov * 255))
            # 反解墨色
            k = paper * (1.0 - cov)
            cr = max(0, min(255, int(round((r - k) / cov))))
            cg = max(0, min(255, int(round((g - k) / cov))))
            cb = max(0, min(255, int(round((b - k) / cov))))
            op[x, y] = (cr, cg, cb, alpha)
    return out


# ───────────────────────── 三种图片来源 ─────────────────────────

def find_custom_image():
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        return sys.argv[1]
    for name in sorted(os.listdir(APP_DIR)):
        stem, ext = os.path.splitext(name)
        if stem.lower() == "custom-icon" and ext.lower() in IMAGE_EXTS:
            return os.path.join(APP_DIR, name)
    return None


def render_from_image(src_path):
    """返回 (background(size), foreground(size), 说明文字)。"""
    src = Image.open(src_path).convert("RGBA")

    if is_paper_art(src):
        box = auto_crop_subject(src)
        if box:
            src = src.crop(box)
        src = key_out_paper(src)
        mode = "白底墨迹（已抠主体并转透明）"
    elif has_transparent_border(src):
        box = alpha_content_bbox(src)
        if box:
            src = src.crop(box)
        mode = "透明底 logo（已裁去透明留白）"
    else:
        # 照片类：满版铺满
        def background_full(size):
            return cover(src, size)

        def foreground_full(size):
            return Image.new("RGBA", (size, size), (0, 0, 0, 0))

        return background_full, foreground_full, "照片（满版裁切铺满）"

    def background(size):
        return Image.new("RGBA", (size, size), CUSTOM_BG)

    def foreground(size):
        box = int(round(size * SAFE_RATIO))
        inner = contain(src, box)
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        canvas.paste(inner, ((size - box) // 2, (size - box) // 2), inner)
        return canvas

    return background, foreground, mode


# ───────────────────────── 兜底：印章版 ─────────────────────────

def render_seal():
    def seal_layer(size, ratio=0.56, radius_ratio=0.15, char="清", char_ratio=0.44):
        k = 4
        big = size * k
        img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        seal_px = big * ratio
        pad = (big - seal_px) / 2
        d.rounded_rectangle([pad, pad, pad + seal_px, pad + seal_px],
                            radius=seal_px * radius_ratio, fill=SEAL)
        font = ImageFont.truetype(FONT_BOLD, int(seal_px * char_ratio))
        bbox = d.textbbox((0, 0), char, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        d.text(((big - tw) / 2 - bbox[0], (big - th) / 2 - bbox[1]),
               char, font=font, fill=PAPER)
        return img.resize((size, size), Image.LANCZOS)

    def background(size):
        return Image.new("RGBA", (size, size), PAPER)

    def foreground(size):
        return seal_layer(size)

    return background, foreground, "兜底印章「清」"


# ───────────────────────── 输出 ─────────────────────────

def main():
    src = find_custom_image()
    if src:
        background, foreground, mode = render_from_image(src)
        print("图片:", src)
        print("识别:", mode)
        print("底色:", CUSTOM_BG[:3])
    else:
        background, foreground, mode = render_seal()
        print("未找到 custom-icon.*，使用兜底印章图标「清」")

    anydpi = os.path.join(APP_RES, "mipmap-anydpi-v26")
    os.makedirs(anydpi, exist_ok=True)
    adaptive_tpl = '''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@mipmap/ic_launcher_background" />
    <foreground android:drawable="@mipmap/ic_launcher_foreground" />
</adaptive-icon>
'''
    for name in ("ic_launcher.xml", "ic_launcher_round.xml"):
        with open(os.path.join(anydpi, name), "w", encoding="utf-8") as f:
            f.write(adaptive_tpl)

    for dpi, k in DENSITIES.items():
        folder = os.path.join(APP_RES, "mipmap-" + dpi)
        os.makedirs(folder, exist_ok=True)

        a = int(round(ADAPTIVE_BASE * k))
        background(a).save(os.path.join(folder, "ic_launcher_background.png"), "PNG", optimize=True)
        foreground(a).save(os.path.join(folder, "ic_launcher_foreground.png"), "PNG", optimize=True)

        n = int(round(LEGACY_BASE * k))
        flat = background(n)
        flat.alpha_composite(foreground(n))
        # 方形图标不做圆角裁切，保持整块方图，形状交给桌面启动器决定
        flat.save(os.path.join(folder, "ic_launcher.png"), "PNG", optimize=True)
        circular(flat).save(os.path.join(folder, "ic_launcher_round.png"), "PNG", optimize=True)

    p = 512
    flat = background(p)
    flat.alpha_composite(foreground(p))
    ci = circular(flat)
    sheet = Image.new("RGBA", (p * 2 + 48, p), (255, 255, 255, 255))
    sheet.paste(flat, (0, 0), flat)
    sheet.paste(ci, (p + 48, 0), ci)
    sheet.save(PREVIEW, "PNG")
    print("预览:", PREVIEW)


if __name__ == "__main__":
    main()

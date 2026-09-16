# -*- coding: utf-8 -*-
"""一键压缩 + 统一转 JPG + 自动更新 data.js（全自动版）

用法（超简单）：
  1. 把新照片丢进 assets/images 文件夹（什么格式都行）
  2. 双击 compress.bat
  3. 完事，不用再做任何操作

脚本会自动完成：
  · 把 png / webp / bmp 等统一转成 .jpg（透明的地方补白底）
  · 压缩过大的图片（超过 800KB 或长边超过 1600px 的，缩到长边1600、质量82）
  · 已经是 jpg 且不大不小的，原样保留，不做无谓的二次压缩
  · 文件名变了（如 png→jpg）会自动把 data.js 里的引用同步改掉
  · 自动扫描 data.js 是否引用了不存在的图片文件，并提示

关于原图（重要）：
  · 不保留原图，压缩后直接覆盖源文件，图片只留一份
  · 安全兜底：先写入临时文件，确认生成成功后才替换原图，
    所以「压缩中途报错 / 断电」的情况下原图仍然是完好的
  · 唯一例外：若 a.png 要转成的 a.jpg 已被另一张不同的图占用，
    则跳过不处理（不会覆盖、也不会删除），并在报告里提示

不会碰的文件：
  · .svg 矢量图（网站的山水背景、占位图等）—— 原样保留
  · .gif 动图 —— 原样保留（转成 jpg 会丢动画）
"""
import os
import re
from PIL import Image, ImageOps

# ─────────── 配置 ───────────
BASE = r"F:\WorkBuddy\personal-website"
IMG_DIR = os.path.join(BASE, "assets", "images")
DATA_JS = os.path.join(BASE, "js", "data.js")

MAX_SIDE = 1600
QUALITY = 82
SIZE_THRESHOLD = 800 * 1024            # jpg 超过 800KB 才重压
CONVERT_EXTS = (".png", ".webp", ".bmp")  # 这些格式一律转成 jpg

# 永不处理的文件类型：svg 是矢量图（网站的山水背景、占位图等），
# gif 可能是动图，转成 jpg 都会损坏，这里一律跳过，原样保留。
NEVER_TOUCH = (".svg", ".gif")


def save_jpg(path, out_path):
    """把任意图片转成 jpg 存到 out_path：统一白底 + 缩到长边 MAX_SIDE。"""
    # 用 with 打开，确保下面替换 / 删除原图时文件句柄已释放（否则 Windows 会报占用）
    with Image.open(path) as src:
        try:
            src = ImageOps.exif_transpose(src)
        except Exception:
            pass

        # 有透明通道的先合到白底，避免透明区变黑
        has_alpha = src.mode in ("RGBA", "LA") or (src.mode == "P" and "transparency" in src.info)
        if has_alpha:
            src = src.convert("RGBA")
            bg = Image.new("RGB", src.size, (255, 255, 255))
            bg.paste(src, mask=src.split()[-1])
            img = bg
        else:
            img = src.convert("RGB")

    w, h = img.size
    scale = MAX_SIDE / float(max(w, h))
    if scale < 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    img.save(out_path, "JPEG", quality=QUALITY, optimize=True, progressive=True)


def update_data_js(rename_map):
    """把 data.js 里引用的旧文件名替换成新文件名。"""
    if not rename_map or not os.path.exists(DATA_JS):
        return 0
    with open(DATA_JS, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = content
    count = 0
    for old, new in rename_map.items():
        hits = content.count(old)
        if hits:
            new_content = new_content.replace(old, new)
            count += hits
    if new_content != content:
        with open(DATA_JS, "w", encoding="utf-8") as f:
            f.write(new_content)
    return count


def check_missing_refs():
    """检查 data.js 里引用了但 images 目录里不存在的图片文件。"""
    if not os.path.exists(DATA_JS):
        return []
    with open(DATA_JS, "r", encoding="utf-8") as f:
        content = f.read()
    existing = set(os.listdir(IMG_DIR))
    missing = []
    # 匹配 assets/images/xxx.xxx 的引用
    refs = re.findall(r'assets/images/([A-Za-z0-9_.\-]+\.(?:jpg|jpeg|png|svg))', content)
    seen = set()
    for ref in refs:
        if ref not in existing and ref not in seen:
            seen.add(ref)
            missing.append(ref)
    return missing


def main():
    # 扫描范围包含 svg / gif，好让下面的「已保护」提示能如实列出它们
    exts = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".svg", ".gif")
    files = sorted(f for f in os.listdir(IMG_DIR)
                   if f.lower().endswith(exts) and not f.startswith("_"))

    report = []
    rename_map = {}   # 旧文件名 -> 新文件名
    changed = 0
    skipped = 0
    protected = []    # svg / gif，原样保留

    for name in files:
        path = os.path.join(IMG_DIR, name)
        ext = os.path.splitext(name)[1].lower()

        if ext in NEVER_TOUCH:
            protected.append(name)
            continue

        size = os.path.getsize(path)
        must_convert = ext in CONVERT_EXTS   # 非 jpg 一律转 jpg

        if not must_convert:
            # 已经是 jpg：只有太大或尺寸过长才重压，避免无谓的画质损失
            too_big = size > SIZE_THRESHOLD
            if not too_big:
                try:
                    with Image.open(path) as im:
                        too_big = max(im.size) > MAX_SIDE
                except Exception:
                    too_big = False
            if not too_big:
                skipped += 1
                continue

        # 目标文件名若已被别的图占用，跳过（不覆盖、也不删除，因为没有原图备份了）
        base, _e = os.path.splitext(name)
        target_path = os.path.join(IMG_DIR, base + ".jpg")
        same_file = (os.path.normcase(os.path.abspath(target_path))
                     == os.path.normcase(os.path.abspath(path)))
        if os.path.exists(target_path) and not same_file:
            report.append("%s  ->  跳过：已存在另一张 %s.jpg，为避免覆盖未处理" % (name, base))
            skipped += 1
            continue

        # 先写临时文件，成功后再替换原图：压缩失败时原图不受影响
        tmp_path = os.path.join(IMG_DIR, "__tmp_%d.jpg" % os.getpid())
        try:
            save_jpg(path, tmp_path)
            new_size = os.path.getsize(tmp_path)
        except Exception as e:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            report.append("%s  ->  处理失败，原图已保留：%s" % (name, e))
            continue

        os.replace(tmp_path, target_path)   # 原地覆盖，不保留原图
        if not same_file:
            os.remove(path)                        # 删除旧格式文件
            rename_map[name] = base + ".jpg"       # 记录改名，稍后同步 data.js
        report.append("%s  ->  %s   %.2fMB -> %.2fMB" % (
            name, base + ".jpg", size / 1048576.0, new_size / 1048576.0))
        changed += 1

    # 自动更新 data.js
    sync_count = update_data_js(rename_map)

    # 检查缺失引用
    missing = check_missing_refs()

    if not report:
        report.append("没有需要处理的图片（已全部是 jpg，且都在 800KB / 1600px 以内）")
    report.append("")
    report.append("共处理 %d 张，跳过 %d 张（已合格的 jpg）。" % (changed, skipped))
    if protected:
        shown = "、".join(protected[:8])
        more = " 等 %d 个" % len(protected) if len(protected) > 8 else ""
        report.append("已保护 %d 个文件，原样不动：%s%s" % (len(protected), shown, more))
        report.append("（svg 矢量图与 gif 动图不会被压缩或转换）")
    if rename_map:
        report.append("已自动更新 data.js 中 %d 处文件名引用（如 png→jpg）。" % sync_count)
    if missing:
        report.append("")
        report.append("注意：data.js 引用了但 images 里没有的文件：")
        report.extend("  · " + m for m in missing)
    else:
        report.append("data.js 引用检查：全部正常。")

    msg = "\n".join(report)
    print(msg)
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, msg, "处理完成（已统一为 jpg 并同步 data.js）", 0)
    except Exception:
        pass


if __name__ == "__main__":
    main()

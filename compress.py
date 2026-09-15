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
  · 原图备份到 网站文件夹外 的 _原图备份_个人网站
  · 文件名变了（如 png→jpg）会自动把 data.js 里的引用同步改掉
  · 自动扫描 data.js 是否引用了不存在的图片文件，并提示
"""
import os
import shutil
import re
from PIL import Image, ImageOps

# ─────────── 配置 ───────────
BASE = r"F:\WorkBuddy\personal-website"
IMG_DIR = os.path.join(BASE, "assets", "images")
DATA_JS = os.path.join(BASE, "js", "data.js")
BACKUP_DIR = r"F:\WorkBuddy\_原图备份_个人网站"

MAX_SIDE = 1600
QUALITY = 82
SIZE_THRESHOLD = 800 * 1024            # jpg 超过 800KB 才重压
CONVERT_EXTS = (".png", ".webp", ".bmp")  # 这些格式一律转成 jpg


def to_jpg(path):
    """把任意图片转成 jpg：统一白底 + 缩到长边 MAX_SIDE，返回输出文件名。"""
    img = Image.open(path)
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass

    # 有透明通道的先合到白底，避免透明区变黑
    has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
    if has_alpha:
        img = img.convert("RGBA")
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    else:
        img = img.convert("RGB")

    w, h = img.size
    scale = MAX_SIDE / float(max(w, h))
    if scale < 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    base, _ext = os.path.splitext(os.path.basename(path))
    out_name = base + ".jpg"
    img.save(os.path.join(IMG_DIR, out_name), "JPEG",
             quality=QUALITY, optimize=True, progressive=True)
    return out_name


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
    os.makedirs(BACKUP_DIR, exist_ok=True)
    exts = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
    files = sorted(f for f in os.listdir(IMG_DIR)
                   if f.lower().endswith(exts) and not f.startswith("_"))

    report = []
    rename_map = {}   # 旧文件名 -> 新文件名
    changed = 0
    skipped = 0

    for name in files:
        path = os.path.join(IMG_DIR, name)
        size = os.path.getsize(path)
        ext = os.path.splitext(name)[1].lower()
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

        # 目标文件名若已被别的图占用，不覆盖，只备份并清理源文件
        base, _e = os.path.splitext(name)
        target_path = os.path.join(IMG_DIR, base + ".jpg")
        if os.path.exists(target_path) and os.path.abspath(target_path) != os.path.abspath(path):
            bak = os.path.join(BACKUP_DIR, name)
            if not os.path.exists(bak):
                shutil.copy2(path, bak)
            os.remove(path)
            report.append("%s  ->  已存在同名 %s.jpg，原文件已备份并移除（未覆盖）"
                          % (name, base))
            changed += 1
            continue

        # 备份原图
        bak = os.path.join(BACKUP_DIR, name)
        if not os.path.exists(bak):
            shutil.copy2(path, bak)

        out = to_jpg(path)
        new_size = os.path.getsize(os.path.join(IMG_DIR, out))
        if out != name:
            os.remove(path)          # 删除旧格式文件
            rename_map[name] = out   # 记录改名，稍后同步 data.js
        report.append("%s  ->  %s   %.2fMB -> %.2fMB" % (
            name, out, size / 1048576.0, new_size / 1048576.0))
        changed += 1

    # 自动更新 data.js
    sync_count = update_data_js(rename_map)

    # 检查缺失引用
    missing = check_missing_refs()

    if not report:
        report.append("没有需要处理的图片（已全部是 jpg，且都在 800KB / 1600px 以内）")
    report.append("")
    report.append("共处理 %d 张，跳过 %d 张（已合格的 jpg）。" % (changed, skipped))
    report.append("现在 assets/images 里已全部是 jpg。")
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

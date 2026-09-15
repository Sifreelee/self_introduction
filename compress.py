# -*- coding: utf-8 -*-
"""一键压缩照片 + 自动更新 data.js（全自动版）

用法（超简单）：
  1. 把要压缩的照片丢进 assets/images 文件夹
  2. 双击「一键压缩照片.bat」
  3. 完事，不用再做任何操作

脚本会自动完成：
  · 压缩所有超过 800KB 的图片（最长边1600px、质量82）
  · 原图备份到 网站文件夹外 的 _原图备份_个人网站
  · 若 .png 被转成 .jpg，自动把 data.js 里的文件名引用同步改掉
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
SIZE_THRESHOLD = 800 * 1024  # 超过 800KB 才压缩


def compress(path):
    """压缩单张图，返回输出文件名。实拍图 png -> jpg，透明图保留 png。"""
    img = Image.open(path)
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass

    has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
    if has_alpha:
        img = img.convert("RGBA")
        fmt = "PNG"
    else:
        img = img.convert("RGB")
        fmt = "JPEG"

    w, h = img.size
    scale = MAX_SIDE / max(w, h)
    if scale < 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    name = os.path.basename(path)
    base, _ext = os.path.splitext(name)
    if fmt == "PNG":
        out_name = base + ".png"
        img.save(os.path.join(IMG_DIR, out_name), "PNG", optimize=True)
    else:
        out_name = base + ".jpg"
        img.save(os.path.join(IMG_DIR, out_name), "JPEG", quality=QUALITY, optimize=True, progressive=True)
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
        if old in new_content:
            new_content = new_content.replace(old, new)
            count += new_content.count(old)  # 统计替换次数
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
    exts = (".jpg", ".jpeg", ".png")
    files = [f for f in os.listdir(IMG_DIR)
             if f.lower().endswith(exts) and not f.startswith("_")]

    report = []
    rename_map = {}   # 旧文件名 -> 新文件名
    changed = 0

    for name in files:
        path = os.path.join(IMG_DIR, name)
        size = os.path.getsize(path)
        if size <= SIZE_THRESHOLD:
            continue
        # 备份
        bak = os.path.join(BACKUP_DIR, name)
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        out = compress(path)
        new_size = os.path.getsize(os.path.join(IMG_DIR, out))
        if out != name:
            os.remove(path)          # 删除旧格式文件
            rename_map[name] = out   # 记录改名，稍后同步 data.js
        report.append("%s  ->  %s   %.1fMB -> %.2fMB" % (
            name, out, size / 1048576, new_size / 1048576))
        changed += 1

    # 自动更新 data.js
    sync_count = update_data_js(rename_map)

    # 检查缺失引用
    missing = check_missing_refs()

    if not report:
        report.append("没有需要压缩的图片（都已在 800KB 以下）")
    report.append("")
    report.append("共压缩 %d 张。" % changed)
    if rename_map:
        report.append("已自动更新 data.js 中 %d 处文件名引用（png→jpg）。" % sync_count)
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
        ctypes.windll.user32.MessageBoxW(0, msg, "压缩完成（已自动同步 data.js）", 0)
    except Exception:
        pass


if __name__ == "__main__":
    main()

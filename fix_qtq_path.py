# -*- coding: utf-8 -*-
"""把青铜器图集的图片目录从 qtq1 改为 qtq。
可反复运行：没有 qtq1 引用时直接退出，不会重复改动。
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "js", "data.js")
QTQ_DIR = os.path.join(ROOT, "assets", "images", "bowu", "qtq")

# qtq1 里的旧名 → qtq 里的新名（同一件文物，只是分类后缀改了）
RENAME_MAP = {
    "青铜器 吉林省博 汉代 夫余鎏金铜面具 祭祀用器.jpg":
        "青铜器 吉林省博 汉代 夫余鎏金铜面具 供奉像.jpg",
    "青铜器 考古博 商代 妇好圈足铜觥 盛酒器.jpg":
        "青铜器 考古博 商代 妇好圈足铜觥 青铜礼器.jpg",
}


def read_text(path):
    for enc in ("utf-8-sig", "utf-8", "gbk"):
        try:
            with io.open(path, encoding=enc) as f:
                return f.read(), enc
        except UnicodeDecodeError:
            continue
    raise SystemExit("无法解码：" + path)


def main():
    src, enc = read_text(DATA)
    if "/qtq1/" not in src:
        print("data.js 已无 qtq1 引用，无需改动。")
        return

    # 1) 目录名整体替换
    src = src.replace("/qtq1/", "/qtq/")

    # 2) 个别文件名在 qtq 里改了后缀，逐个纠偏（src 和 title 一起改）
    fixed = 0
    for old, new in RENAME_MAP.items():
        if new not in os.listdir(QTQ_DIR):
            print("  跳过（qtq 里也没有）：" + new)
            continue
        if old in src:
            stem_old = old.rsplit(".", 1)[0]
            stem_new = new.rsplit(".", 1)[0]
            src = src.replace(old, new)          # 文件名
            src = src.replace(stem_old, stem_new)  # 同名 title
            fixed += 1
    with io.open(DATA, "w", encoding=enc, newline="\n") as f:
        f.write(src)
    print("已把 qtq1 改为 qtq，纠偏文件名 %d 个。" % fixed)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""通用「其一 / 其二」顺序重命名工具（不动 rename_album.py）

把文件夹里同一大标题的一组文件，按原有编号顺序改成：
    天安门01.png / 天安门05.png / 天安门08.png
        -> 天安门 其一.png / 天安门 其二.png / 天安门 其三.png
大标题（去掉末尾编号后的部分）保持不变，与序号之间空一格（--sep 可改）。

==================== 三种用法 ====================
  1) 双击 rename_qi.bat      —— 弹窗选文件夹，看预览表，回车执行
  2) 把文件夹拖到 bat 上     —— 直接对该文件夹执行（同样先预览后确认）
  3) 命令行（适合固定流程）
       python rename_qi.py --dir "F:\\照片\\国庆" --dry-run   # 只预览
       python rename_qi.py --dir "F:\\照片\\国庆" --yes       # 直接执行
       python rename_qi.py --rollback "国庆_重命名对照表.csv"  # 改回原名

==================== 分组与排序规则 ====================
  · 大标题 = 文件名去掉末尾的编号（含分隔符），如「太庙桂花04」-> 太庙桂花
  · 只认 1~4 位末尾数字（--max-digits 可调），避免把 20231008 这类日期当编号
  · 无编号的排在最前（视作其一），其余按数字从小到大
  · 每组独立编号：太庙桂花 其一..其四、太庙菊花 其一..其五，互不影响
  · 大标题和序号之间默认空一格（--sep 可改成 _ 或 · 等，空串则紧贴）
  · 已经叫「XX 其一」的也能识别，序号会被读回来参与排序，重复运行不会乱序

==================== 只有一张的组 ====================
  --single strip  默认，去掉末尾编号，只留大标题（国博02 -> 国博）
  --single keep   保持原名不动
  --single qi     也写成「其一」

==================== 顺带产出 ====================
  · <文件夹名>_照片清单.txt   始终生成，整段粘进 add-tool.html 的「照片清单」框
  · <文件夹名>_datajs片段.txt 给了 --city 才生成，直接粘进 js/data.js 的 albums 数组
      例：python rename_qi.py --dir "...\\gq" --city "北京 国庆" --seal "京" --tags 天安门,太庙

产出文件都放在目标文件夹的上一级。不删文件、不压缩。
"""

import argparse
import csv
import os
import re
import shutil
import sys

try:  # Windows 控制台中文
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = os.path.dirname(os.path.abspath(__file__))

# 序号 -> 中文数字
CN_DIGITS = "零一二三四五六七八九"
SEPARATORS = " \t_-–—．."


# ───────────────────────── 基础工具 ─────────────────────────
def cn_number(n):
    """1 -> 一，10 -> 十，11 -> 十一，21 -> 二十一。"""
    if n <= 0:
        return str(n)
    if n < 10:
        return CN_DIGITS[n]
    if n == 10:
        return "十"
    if n < 20:
        return "十" + CN_DIGITS[n - 10]
    if n < 100:
        tens, unit = divmod(n, 10)
        return CN_DIGITS[tens] + "十" + (CN_DIGITS[unit] if unit else "")
    return str(n)


def cn_parse(text):
    """中文数字 -> int。一->1，十->10，十一->11，二十一->21；解析不了返回 None。"""
    if text.isdigit():
        return int(text)
    if not text or any(ch not in CN_DIGITS + "十百" for ch in text):
        return None
    total, cur = 0, 0
    for ch in text:
        if ch in "十百":
            total += (cur or 1) * (10 if ch == "十" else 100)
            cur = 0
        else:
            cur = CN_DIGITS.index(ch)
    return (total + cur) or None


def ordinal(n):
    """1 -> 其一，2 -> 其二 ..."""
    return "其" + cn_number(n)


def make_parser(max_digits):
    return re.compile(r"^(?P<title>.*?)[%s]*(?P<num>\d{1,%d})$"
                      % (re.escape(SEPARATORS), max_digits))


# 已存在的「其一 / 其二」后缀：再跑一次时把序号读回来，保证不乱序
ORDINAL_RE = re.compile(r"^(?P<title>.*?)[%s]*其(?P<ord>[%s十百]+|\d+)$"
                        % (re.escape(SEPARATORS), CN_DIGITS))


def split_name(stem, num_re):
    """拆出 (大标题, 编号, 已有序号)。不存在的一律 None。

    先剥「其一」这类已有序号（序号会被读回来参与排序），再剥末尾数字编号。
    """
    ordv = None
    m = ORDINAL_RE.match(stem)
    if m:
        ordv = cn_parse(m.group("ord"))
        if ordv is not None and m.group("title").rstrip(SEPARATORS):
            stem = m.group("title").rstrip(SEPARATORS)
        else:
            ordv = None
    m = num_re.match(stem)
    if not m:
        return stem, None, ordv
    title = m.group("title").rstrip(SEPARATORS)
    if not title:
        return stem, None, ordv
    return title, int(m.group("num")), ordv


def list_files(folder, exts):
    """列出待处理文件（跳过子文件夹、隐藏文件、临时文件）。"""
    if not os.path.isdir(folder):
        raise SystemExit("文件夹不存在：%s" % folder)
    out = []
    for name in os.listdir(folder):
        p = os.path.join(folder, name)
        if not os.path.isfile(p) or name.startswith(".") or name.startswith("__tmp"):
            continue
        if exts and os.path.splitext(name)[1].lower().lstrip(".") not in exts:
            continue
        out.append(name)
    return sorted(out)


def pick_folder_gui():
    """弹窗选文件夹；没有 tkinter 就返回 None。"""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        folder = filedialog.askdirectory(title="选择要整理的文件夹")
        root.destroy()
        return folder or None
    except Exception:
        return None


# ───────────────────────── 生成方案 ─────────────────────────
def build_plan(folder, files, max_digits, single_mode, sort_by, sep=" "):
    """返回 [(旧名, 新名, 大标题, 序号 or '')]。"""
    num_re = make_parser(max_digits)
    groups = {}
    for name in files:
        stem, ext = os.path.splitext(name)
        title, num, ordv = split_name(stem, num_re)
        groups.setdefault((title, ext.lower()), []).append((num, ordv, stem, name))

    def sort_key(item):
        num, ordv, stem, name = item
        if sort_by == "time":
            return (0, os.path.getmtime(os.path.join(folder, name)))
        if sort_by == "name":
            return (0, stem)
        # 已有序号优先（重复运行时保序），其次原编号，都没有的排最前
        rank = ordv if ordv is not None else (-1 if num is None else num)
        return (0, rank, stem)

    plan = []
    for (title, ext), items in groups.items():
        items.sort(key=sort_key)
        if len(items) == 1:
            _num, _ordv, _stem, name = items[0]
            if single_mode == "qi":
                plan.append((name, "%s%s%s%s" % (title, sep, ordinal(1), ext), title, 1))
            elif single_mode == "strip":
                plan.append((name, "%s%s" % (title, ext), title, ""))
            else:
                plan.append((name, name, title, ""))
            continue
        for i, (_num, _ordv, _stem, name) in enumerate(items, 1):
            plan.append((name, "%s%s%s%s" % (title, sep, ordinal(i), ext), title, i))
    plan.sort(key=lambda x: x[0])
    return plan


def print_plan(plan, folder):
    changed = [p for p in plan if p[0] != p[1]]
    print("\n将要这样改（共 %d 个，其中 %d 个实际变动）：" % (len(plan), len(changed)))
    print("-" * 68)
    for old, new, title, idx in plan:
        mark = " " if old == new else "*"
        print(" %s %-34s -> %-24s [%s 第%s]"
              % (mark, old, new, title, idx if idx else "-"))
    print("-" * 68)
    print("所在文件夹：%s" % folder)
    print("* 表示会改动，空格表示保持原名\n")


def find_conflicts(folder, plan):
    existing = set(os.listdir(folder))
    sources = {old for old, _n, _t, _i in plan}
    return [new for _o, new, _t, _i in plan if new != _o and new in existing and new not in sources]


def safe_move(src, dst):
    """改名；遇到 exFAT / 权限拒绝时退化成「复制 -> 校验 -> 删除」。"""
    try:
        os.rename(src, dst)
        return
    except OSError:
        pass
    shutil.copy2(src, dst)
    if os.path.getsize(src) != os.path.getsize(dst):
        try:
            os.remove(dst)
        except OSError:
            pass
        raise SystemExit("复制校验失败，已中止：%s -> %s" % (src, dst))
    os.remove(src)


def do_rename(folder, plan):
    """两步改名（先临时名再正式名），中途出错也不会撞名。"""
    todo = [(o, n) for o, n, _t, _i in plan if o != n]
    tmps = []
    for i, (old, new) in enumerate(todo):
        ext = os.path.splitext(new)[1]
        tmp = "__tmp_%d_%d%s" % (os.getpid(), i, ext)
        safe_move(os.path.join(folder, old), os.path.join(folder, tmp))
        tmps.append((tmp, new))
    for tmp, new in tmps:
        safe_move(os.path.join(folder, tmp), os.path.join(folder, new))
    return len(todo)


# ───────────────────────── 输出 / 回滚 ─────────────────────────
def web_prefix_of(folder):
    """求网页路径前缀：assets/images，或它在站点里的子目录（正斜杠）。"""
    images_dir = os.path.join(BASE, "assets", "images")
    prefix = "assets/images"
    try:
        rel = os.path.relpath(os.path.abspath(folder), images_dir).replace("\\", "/")
    except ValueError:
        rel = ""
    if rel and rel != "." and not rel.startswith(".."):
        prefix = "%s/%s" % (prefix, rel)
    return prefix


def album_name(folder):
    return os.path.basename(os.path.normpath(folder)) or "文件夹"


def write_extras(out_dir, folder, plan, city, seal, desc, tags, star):
    """生成照片清单（add-tool 用）与 data.js 片段（给了城市名才生成）。"""
    os.makedirs(out_dir, exist_ok=True)
    made = []
    base = album_name(folder)
    prefix = web_prefix_of(folder)
    # 按「大标题 + 序号」排序：同一组的照片挨在一起，且其一/其二/其三顺序正确
    # （直接按文件名排会出乱：二的码点比三大，其二会被排到其三后面）
    rows = sorted(plan, key=lambda x: (x[2], x[3] if x[3] else 0, x[1]))
    tag_list = []
    if tags:
        tag_list = tags if isinstance(tags, (list, tuple)) else re.split(r"[,，、\s]+", tags)
        tag_list = [t.strip() for t in tag_list if t.strip()]

    # 1) 照片清单：文件名 空格 标题（必须带扩展名，否则 add-tool 会补成 .jpg）
    list_path = os.path.join(out_dir, "%s_照片清单.txt" % base)
    with open(list_path, "w", encoding="utf-8") as f:
        for _old, new, _title, _idx in rows:
            f.write("%s %s\n" % (new, os.path.splitext(new)[0]))
    made.append(list_path)

    # 2) data.js 片段
    if city:
        path = os.path.join(out_dir, "%s_datajs片段.txt" % base)
        lines = ["    {", '      city: "%s",' % city, '      desc: "%s",' % (desc or "")]
        if seal:
            lines.append('      seal: "%s",' % seal)
        if star:
            lines.append("      star: true,")
        if tag_list:
            lines.append('      tags: [%s],' % ", ".join('"%s"' % t for t in tag_list))
        lines.append("      photos: [")
        lines.append(",\n".join('        { src: "%s/%s", title: "%s" }'
                                % (prefix, new, os.path.splitext(new)[0])
                                for _o, new, _t, _i in rows))
        lines.append("      ]")
        lines.append("    },")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        made.append(path)
        print("网页路径前缀：%s（填到 add-tool 的「图片所在文件夹」就是它）" % prefix)
    return made


def write_csv(out_dir, folder, plan):
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.basename(os.path.normpath(folder)) or "文件夹"
    path = os.path.join(out_dir, "%s_重命名对照表.csv" % base)

    # 同一个文件夹改过多次时，沿用上一版对照表里的「最初原名」，
    # 这样回滚能一步回到没改过之前，而不是只退回上一版
    origin_of = {}
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                for r in csv.DictReader(f):
                    if r.get("新文件名") and r.get("原文件名"):
                        origin_of[r["新文件名"]] = r["原文件名"]
        except OSError:
            pass

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["大标题", "序号", "新文件名", "原文件名", "是否改动"])
        for old, new, title, idx in plan:
            w.writerow([title, ("其" + cn_number(idx)) if idx else "", new,
                        origin_of.get(old, old), "是" if old != new else "否"])
        w.writerow([])
        w.writerow(["说明：大标题 = 文件名去掉末尾编号后的部分，保持不变；"
                    "无编号的文件排在该组最前。"])
        w.writerow(["回滚命令：python rename_qi.py --rollback \"%s\"" % os.path.basename(path)])
    return path


def rollback(csv_path, folder):
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not folder:
        folder = os.path.dirname(os.path.abspath(csv_path))
    plan = [(r["新文件名"], r["原文件名"]) for r in rows
            if r.get("新文件名") and r.get("原文件名") and r["新文件名"] != r["原文件名"]]
    if not plan:
        raise SystemExit("对照表里没有需要回滚的条目：%s" % csv_path)
    print("准备把 %d 个文件改回原名：" % len(plan))
    for new, old in plan[:10]:
        print("  %s -> %s" % (new, old))
    if len(plan) > 10:
        print("  ... 其余 %d 个" % (len(plan) - 10))
    missing = [n for n, _o in plan if not os.path.exists(os.path.join(folder, n))]
    if missing:
        raise SystemExit("这些文件在当前文件夹里找不到，请确认路径：%s\n当前文件夹：%s"
                         % ("、".join(missing[:5]), folder))
    if input("\n确认回滚？[y/N] ").strip().lower() != "y":
        print("已取消。")
        return
    do_rename(folder, [(o, n, "", "") for n, o in plan])
    print("已回滚 %d 个文件。" % len(plan))


# ───────────────────────── 入口 ─────────────────────────
def interactive(folder):
    print("=" * 60)
    print("  其一 / 其二 顺序重命名工具")
    print("=" * 60)
    if not folder:
        print("\n正在打开文件夹选择窗口...")
        folder = pick_folder_gui()
    if not folder:
        folder = input("\n没弹出窗口就把文件夹路径粘这里：").strip().strip('"')
    return folder


def main():
    ap = argparse.ArgumentParser(description="按编号顺序重命名为「其一 / 其二」，大标题不变")
    ap.add_argument("folder", nargs="?", help="目标文件夹（拖拽到 bat 上会自动带上）")
    ap.add_argument("--dir", dest="dir_opt", help="同 folder，命令行写法")
    ap.add_argument("--ext", help="只处理这些扩展名，逗号分隔，如 png,jpg；不给=全部文件")
    ap.add_argument("--max-digits", type=int, default=4, help="末尾编号最大位数，默认 4")
    ap.add_argument("--single", choices=["strip", "keep", "qi"], default="strip",
                    help="只有一张的组：strip=去掉编号（默认）/ keep=保持原名 / qi=也叫其一")
    ap.add_argument("--sort", choices=["number", "name", "time"], default="number",
                    help="组内排序：number=按原编号（默认）/ name=文件名 / time=修改时间")
    ap.add_argument("--sep", default=" ",
                    help="大标题与序号之间的分隔，默认一个空格；可改 _ 或 ·，空串则紧贴")
    ap.add_argument("--out", help="对照表输出目录，默认目标文件夹的上一级")
    ap.add_argument("--city", help="城市/图集名，给了就顺带生成 data.js 片段，如「北京 国庆」")
    ap.add_argument("--seal", help="印章字（1 个字），配合 --city 使用")
    ap.add_argument("--desc", default="", help="图集简介，写进 data.js 的 desc")
    ap.add_argument("--tags", help="标签，逗号分隔，如 天安门,太庙")
    ap.add_argument("--star", action="store_true", help="data.js 片段里加 star: true（封面星标）")
    ap.add_argument("--dry-run", action="store_true", help="只预览，不改文件")
    ap.add_argument("--yes", action="store_true", help="跳过确认直接执行")
    ap.add_argument("--rollback", help="传入对照表 csv，把文件名改回原名")
    args = ap.parse_args()

    folder = args.dir_opt or args.folder

    if args.rollback:
        rollback(args.rollback, folder)
        return

    interactive_mode = not folder
    if interactive_mode:
        folder = interactive(folder)
    folder = os.path.abspath(folder.strip().strip('"'))
    if not os.path.isdir(folder):
        raise SystemExit("文件夹不存在：%s" % folder)

    exts = [e.strip().lower().lstrip(".") for e in args.ext.split(",")] if args.ext else []
    files = list_files(folder, exts)
    if not files:
        raise SystemExit("这个文件夹里没有可处理的文件：%s" % folder)

    plan = build_plan(folder, files, args.max_digits, args.single, args.sort, args.sep)
    print_plan(plan, folder)

    out_dir = args.out or os.path.dirname(os.path.normpath(folder)) or BASE

    # 双击/手填路径进来时，顺口问一下要不要生成 data.js 片段
    if interactive_mode and not args.city:
        args.city = input("要不要顺带生成 data.js 片段？需要就填城市/图集名（如 北京 国庆），"
                          "不需要直接回车：").strip()
        if args.city and not args.seal:
            args.seal = input("印章字（1 个字，可留空）：").strip()

    changed = sum(1 for p in plan if p[0] != p[1])
    if changed == 0:
        # 名字已经是最终形态：不改名，但清单 / 片段照样给出来
        print("文件名已经符合要求，无需改动。")
        for p in write_extras(out_dir, folder, plan, args.city, args.seal,
                              args.desc, args.tags, args.star):
            print("已生成：%s" % p)
        return

    conflicts = find_conflicts(folder, plan)
    if conflicts:
        raise SystemExit("目标文件名已被占用，请先处理：%s" % "、".join(conflicts[:5]))

    if args.dry_run:
        for p in write_extras(out_dir, folder, plan, args.city, args.seal,
                              args.desc, args.tags, args.star):
            print("已生成：%s" % p)
        print("预览模式，未改动任何文件。去掉 --dry-run 才会真的执行。")
        return

    if not args.yes:
        if input("确认执行？[y/N] ").strip().lower() != "y":
            print("已取消，没动任何文件。")
            return

    n = do_rename(folder, plan)
    print("\n改名完成，共 %d 个。" % n)

    csv_path = write_csv(out_dir, folder, plan)
    print("对照表：%s" % csv_path)
    for p in write_extras(out_dir, folder, plan, args.city, args.seal,
                          args.desc, args.tags, args.star):
        print("已生成：%s" % p)
    if args.city:
        print("data.js 片段：粘进 js/data.js 的 albums 数组即可（末尾自带逗号）。")
    print("回滚命令：python rename_qi.py --rollback \"%s\"" % csv_path)


if __name__ == "__main__":
    main()

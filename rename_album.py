# -*- coding: utf-8 -*-
"""通用图集照片批量重命名工具（以后任何图集都能直接用）

双击 rename_album.bat 进入「问答模式」，一路回车即可；
也可以在命令行里一次性给参数，适合固定流程。

==================== 双击 bat 的典型流程 ====================
  1. 把新照片丢进 assets/images
  2. 双击 rename_album.bat
  3. 输入前缀（如 changchun / dunhuang / weiman），选范围、排序
  4. 确认预览表 -> 回车执行
  5. 得到三样东西，直接用于做图集：
       <前缀>_照片清单.txt   —— 整段粘进 add-tool.html 的「照片清单」框
       <前缀>_对照表.csv     —— 编号 / 新文件名 / 标题 / 原文件名（Excel 直开）
       <前缀>_datajs片段.txt —— 直接粘进 js/data.js 的 photos 数组（可选）

==================== 命令行用法示例 ====================
  # 把最近导入的 32 张命名为 weiman1~weiman32（按导入时间排序）
  python rename_album.py --prefix weiman --newest 32

  # 命名 2026-09-16 15:00 之后导入的全部图片，编号补成 3 位（weiman001）
  python rename_album.py --prefix weiman --since "2026-09-16 15:00" --pad 3

  # 指定文件夹 + 按文件名排序 + 从第 10 号开始 + 直接生成 data.js 片段
  python rename_album.py --prefix dunhuang --dir "F:\\照片\\敦煌" --sort name ^
         --start 10 --city "中国 敦煌" --seal "敦"

  # 中文文件名的图默认会被跳过；确实要连它们一起改，才加 --allow-chinese
  python rename_album.py --prefix changchun --since "2026-09-16 17:00" --allow-chinese

  # 只看会怎么改，不动文件（强烈建议第一次先跑这个）
  python rename_album.py --prefix test --newest 5 --dry-run

  # 改回原名（用当时生成的对照表）
  python rename_album.py --rollback "weiman_对照表.csv"

默认规则（两条，都是为了避免误伤已有内容）：
  1. 文件名里含中文的，一律跳过不改名（多是已经整理好的图），
     编号在剩下的文件上继续，不会跳号；
     想连中文名的文件一起改，加 --allow-chinese
  2. 已经叫 <前缀><数字> 的文件自动跳过，重复运行不会把编号搞乱（除非加 --force）

被上面两条挡下的文件不会从清单里消失：它们保持原名，但照样写进
照片清单 / 对照表 / data.js 片段，排在改名条目之后，整段复制即可。
（只想要改名部分的话，加 --exclude-kept）
注意「最近 N 张」现在按全部图片计数（含中文名的），不是只数要改名的。

说明：
  · 不删图、不压缩，只改文件名；编号默认按「文件修改时间」= 导入顺序
  · 改名分两步走（先临时名再正式名），中途出错也不会把两张图撞成同一个名字
"""

import argparse
import csv
import os
import re
import sys
import time
from datetime import datetime

try:  # Windows 控制台中文
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = r"F:\WorkBuddy\personal-website"
DEFAULT_IMG_DIR = os.path.join(BASE, "assets", "images")
DEFAULT_OUT = BASE

IMG_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff")

# 文件名里出现这些字符就跳过：中日韩汉字（含扩展区）
CJK_RE = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]")


def has_cjk(name):
    return bool(CJK_RE.search(name))


# ───────────────────────── 基础工具 ─────────────────────────
def list_images(folder):
    """列出文件夹里的图片（跳过子文件夹与临时文件）。"""
    if not os.path.isdir(folder):
        raise SystemExit("文件夹不存在：%s" % folder)
    out = []
    for name in os.listdir(folder):
        p = os.path.join(folder, name)
        if not os.path.isfile(p):
            continue
        if not name.lower().endswith(IMG_EXTS):
            continue
        if name.startswith("__tmp") or name.startswith("."):
            continue
        out.append((os.path.getmtime(p), name))
    return out


def parse_time(text):
    """把 '2026-09-16 15:00' / '2026-09-16' 之类转成时间戳。"""
    text = (text or "").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y/%m/%d %H:%M"):
        try:
            return time.mktime(time.strptime(text, fmt))
        except ValueError:
            continue
    raise SystemExit("时间格式看不懂，请用：2026-09-16 15:00")


def select_files(items, mode, arg, sort_by, prefix, force, allow_chinese=False):
    """先按模式圈定「这一批」，再套两条保护规则。

    顺序很重要：先圈范围、后套规则，这样被保护规则挡下的文件仍属于这一批，
    能一并写进清单；反过来的话，别的图集里的中文名文件也会被误带进来。

    返回 (files, keeps, 跳过已编号数, 跳过中文名数)
      files —— 要改名的 [(mtime, 文件名)]，已按 sort_by 排好序
      keeps —— 在范围内但不改名的 [(文件名, 原因)]，同样排好序
    """
    # 1) 先圈定本次处理的范围（中文名、已编号的都先算进来）
    if mode == "newest":
        scoped = sorted(items, key=lambda x: (-x[0], x[1]))[:int(arg)]
    elif mode == "since":
        cut = parse_time(arg)
        scoped = [x for x in items if x[0] >= cut]
    elif mode == "match":
        key = arg.lower()
        scoped = [x for x in items if key in x[1].lower()]
    else:                       # all
        scoped = list(items)

    # 2) 规则一：文件名含中文的不改名（多为已整理好的图，避免误改）
    keeps = []                  # [(mtime, 文件名, 原因)]
    if not allow_chinese:
        rest, cjk = [], []
        for x in scoped:
            (cjk if has_cjk(x[1]) else rest).append(x)
        keeps += [(m, n, "中文文件名，保持原样") for m, n in cjk]
        skipped_cjk = len(cjk)
    else:
        rest, skipped_cjk = scoped, 0

    # 3) 规则二：已经编过号的（同前缀）不改名，避免重复运行时二次编号
    if not force and prefix:
        pat = re.compile(r"^%s\d+\.[A-Za-z0-9]+$" % re.escape(prefix), re.I)
        picked, numbered = [], []
        for x in rest:
            (numbered if pat.match(x[1]) else picked).append(x)
        keeps += [(m, n, "已经是 %s+数字，不重复编号" % prefix) for m, n in numbered]
        skipped_existing = len(numbered)
    else:
        picked, skipped_existing = rest, 0

    if sort_by == "time":
        files = sorted(picked, key=lambda x: (x[0], x[1]))
        keeps_sorted = sorted(keeps, key=lambda x: (x[0], x[1]))
    else:
        files = sorted(picked, key=lambda x: x[1])
        keeps_sorted = sorted(keeps, key=lambda x: x[1])
    return files, [(n, why) for _m, n, why in keeps_sorted], skipped_existing, skipped_cjk


def build_plan(files, prefix, start, pad):
    """生成 [(旧文件名, 新文件名, 标题)] 对照表。"""
    plan = []
    for i, (_m, name) in enumerate(files, start):
        ext = os.path.splitext(name)[1]
        num = str(i).zfill(pad) if pad else str(i)
        plan.append((name, "%s%s%s" % (prefix, num, ext), os.path.splitext(name)[0]))
    return plan


def print_plan(plan, folder, keeps=()):
    print("\n将要这样改（共 %d 张）：" % len(plan))
    print("-" * 62)
    for old, new, title in plan:
        print("  %-42s -> %s" % (old, new))
    if keeps:
        print("-" * 62)
        print("以下 %d 张不改文件名，但会原样写进清单：" % len(keeps))
        for name, why in keeps:
            print("  %-42s （%s）" % (name, why))
    print("-" * 62)
    print("所在文件夹：%s\n" % folder)


def find_conflicts(folder, plan):
    """目标名已被「不在本次计划里」的文件占用时，必须拦下来（Windows 上会直接改名失败）。"""
    existing = set(os.listdir(folder))
    sources = {old for old, _n, _t in plan}
    return [new for _o, new, _t in plan if new in existing and new not in sources]


def do_rename(folder, plan):
    """两步改名，避免新旧名字互相撞车。"""
    tmps = []
    for idx, (old, new, _t) in enumerate(plan):
        ext = os.path.splitext(new)[1]
        tmp = "__tmp_%d_%d%s" % (os.getpid(), idx, ext)
        os.rename(os.path.join(folder, old), os.path.join(folder, tmp))
        tmps.append((tmp, new))
    for tmp, new in tmps:
        os.rename(os.path.join(folder, tmp), os.path.join(folder, new))


# ───────────────────────── 输出文件 ─────────────────────────
def write_outputs(out_dir, prefix, plan, city, seal, keeps=()):
    """输出照片清单 / 对照表 / data.js 片段。

    keeps 是「不改名但要列入清单」的文件 [(文件名, 原因)]，
    中文名文件就走这条路：文件名不动，照样出现在清单里方便整段复制。
    """
    os.makedirs(out_dir, exist_ok=True)
    made = []

    # 保持原名的条目：文件名即最终名，标题 = 去掉扩展名
    kept_items = [(name, name, os.path.splitext(name)[0]) for name, _why in keeps]
    everything = list(plan) + kept_items

    # 1) 照片清单：add-tool.html 的「照片清单」框，格式 = 文件名 空格 标题
    #    注意：必须带扩展名，否则 add-tool 会给 png/webp 自动补成 .jpg，引用就断了
    list_path = os.path.join(out_dir, "%s_照片清单.txt" % prefix)
    with open(list_path, "w", encoding="utf-8") as f:
        for _old, new, title in everything:
            f.write("%s %s\n" % (new, title))
    made.append(list_path)

    # 2) 对照表 CSV（UTF-8 BOM，Excel 双击不乱码）
    csv_path = os.path.join(out_dir, "%s_对照表.csv" % prefix)
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["编号", "新文件名", "照片标题", "原文件名"])
        for old, new, title in plan:
            w.writerow([os.path.splitext(new)[0], new, title, old])
        for name, _why in keeps:
            w.writerow(["原名保留", name, os.path.splitext(name)[0], name])
        w.writerow([])
        w.writerow(["说明：标题取自文件名（去掉扩展名）；「原名保留」行的文件名未被改动，"
                    "回滚时会自动跳过。"])
        w.writerow(["回滚命令：python rename_album.py --rollback \"%s\""
                    % os.path.basename(csv_path)])
    made.append(csv_path)

    # 3) data.js 片段（给了城市名才生成）
    if city:
        snippet_path = os.path.join(out_dir, "%s_datajs片段.txt" % prefix)
        lines = ["    {", '      city: "%s",' % city]
        if seal:
            lines.append('      seal: "%s",' % seal)
        lines.append("      photos: [")
        body = []
        for _old, new, title in everything:
            body.append('        { src: "assets/images/%s", title: "%s" }' % (new, title))
        lines.append(",\n".join(body))
        lines.append("      ]")
        lines.append("    },")
        with open(snippet_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        made.append(snippet_path)

    return made


def rollback(csv_path, folder):
    """用对照表把文件名改回原来的样子。"""
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    # 「原名保留」行（中文名文件）新旧同名，直接跳过，不做无谓的改名
    plan = [(r["新文件名"], r["原文件名"]) for r in rows
            if r.get("新文件名") and r.get("原文件名") and r["新文件名"] != r["原文件名"]]
    if not plan:
        raise SystemExit("对照表里没读到有效内容（或全部是「原名保留」行，无需回滚）：%s" % csv_path)
    print("准备把 %d 个文件改回原名：" % len(plan))
    for new, old in plan[:10]:
        print("  %s -> %s" % (new, old))
    if len(plan) > 10:
        print("  ... 其余 %d 个" % (len(plan) - 10))
    if input("\n确认执行？[y/N] ").strip().lower() != "y":
        print("已取消。")
        return
    do_rename(folder, [(new, old, "") for new, old in plan])
    print("已回滚 %d 个文件。" % len(plan))


# ───────────────────────── 问答模式 ─────────────────────────
def ask(prompt, default=""):
    tip = prompt + (("（直接回车 = %s）" % default) if default else "")
    v = input(tip + "：").strip()
    return v or default


def interactive():
    print("=" * 58)
    print("  通用图集重命名工具 —— 照片编号 + 清单生成")
    print("=" * 58)

    prefix = ask("\n1) 英文前缀，编号就长在它后面（如 weiman -> weiman1）")
    while not prefix:
        prefix = ask("   前缀不能为空，请输入（如 changchun）")

    folder = ask("\n2) 照片所在文件夹", DEFAULT_IMG_DIR)
    items = list_images(folder)
    if not items:
        raise SystemExit("这个文件夹里没有图片：%s" % folder)
    print("   找到 %d 张图片。" % len(items))

    print("\n3) 要处理哪些？")
    print("   1) 最近导入的 N 张   2) 某个时间之后导入的")
    print("   3) 全部              4) 文件名里包含某个字")
    choice = ask("   选 1/2/3/4", "1")
    if choice == "1":
        mode = "newest"
        arg = ask("   最近多少张", str(len(items)))
    elif choice == "2":
        mode = "since"
        arg = ask("   时间（如 2026-09-16 15:00）")
    elif choice == "3":
        mode, arg = "all", None
    else:
        mode = "match"
        arg = ask("   包含什么字（如 伪满）")

    sort_by = "time" if ask("\n4) 排序方式：1) 导入时间  2) 文件名 [1/2]", "1") == "1" else "name"
    start = int(ask("\n5) 起始编号", "1") or 1)
    pad_raw = ask("\n6) 编号补零位数（0 = 不补零，如 3 -> weiman001）", "0")
    pad = int(pad_raw or 0)
    allow_cjk = ask("\n7) 连中文文件名的文件一起改？[y/N]", "n").lower() == "y"

    files, keeps, skipped, skipped_cjk = select_files(items, mode, arg, sort_by, prefix,
                                                      force=False, allow_chinese=allow_cjk)
    if skipped_cjk:
        print("\n（%d 个中文文件名的文件不改名，编号在剩下的图里接着排，"
              "但它们会原样写进清单）" % skipped_cjk)
    if skipped:
        print("（%d 个早就叫 %s+数字 的文件不重复编号，同样写进清单）" % (skipped, prefix))
    if not files and not keeps:
        raise SystemExit("按这个条件没选到任何图片。")

    plan = build_plan(files, prefix, start, pad)
    print_plan(plan, folder, keeps)

    conflicts = find_conflicts(folder, plan)
    if conflicts:
        raise SystemExit(
            "目标文件名已被占用：%s\n"
            "请换个前缀，或用 --start 从更大的编号开始，或加 --force 把旧的编号文件一起重编。"
            % "、".join(conflicts[:5]))

    if input("确认执行？[y/N] ").strip().lower() != "y":
        print("已取消，没动任何文件。")
        return

    do_rename(folder, plan)
    print("\n改名完成，共 %d 张。" % len(plan))

    city = ask("\n要不要顺带生成 data.js 片段？需要就填城市名（如 中国 长春），不需要直接回车")
    city = city if city else ""
    seal = ask("印章字（1 个字，可留空）") if city else ""
    made = write_outputs(ask("\n清单输出到哪个文件夹", DEFAULT_OUT), prefix, plan, city, seal, keeps)
    print("\n已生成：")
    for p in made:
        print("  " + p)
    if city:
        print("\ndata.js 片段：粘到 js/data.js 的 photos: [ 里面即可（末尾自带逗号）。")
    print("\n回滚命令：python rename_album.py --rollback \"%s_对照表.csv\"" % prefix)


# ───────────────────────── 入口 ─────────────────────────
def main():
    ap = argparse.ArgumentParser(description="通用图集照片批量重命名工具",
                                 add_help=True)
    ap.add_argument("--prefix", help="英文前缀，如 weiman")
    ap.add_argument("--dir", default=DEFAULT_IMG_DIR, help="照片文件夹，默认 assets/images")
    ap.add_argument("--newest", type=int, help="只处理最近导入的 N 张")
    ap.add_argument("--since", help="只处理该时间之后导入的，如 '2026-09-16 15:00'")
    ap.add_argument("--match", help="只处理文件名包含该文字的图片")
    ap.add_argument("--all", action="store_true", help="处理文件夹里全部图片")
    ap.add_argument("--sort", choices=["time", "name"], default="time", help="排序：导入时间 / 文件名")
    ap.add_argument("--start", type=int, default=1, help="起始编号，默认 1")
    ap.add_argument("--pad", type=int, default=0, help="编号补零位数，如 3 -> weiman001")
    ap.add_argument("--city", help="城市名，给了就额外生成 data.js 片段")
    ap.add_argument("--seal", help="印章字，配合 --city 使用")
    ap.add_argument("--out", default=DEFAULT_OUT, help="清单输出文件夹，默认项目根目录")
    ap.add_argument("--force", action="store_true", help="连已经编过号的同前缀文件也一起重编")
    ap.add_argument("--allow-chinese", action="store_true",
                    help="默认跳过中文文件名的文件；加这个参数才连它们一起改")
    ap.add_argument("--exclude-kept", action="store_true",
                    help="清单里只列本次改名的文件，不列入「保持原名」的中文名文件")
    ap.add_argument("--dry-run", action="store_true", help="只预览不改文件")
    ap.add_argument("--yes", action="store_true", help="跳过确认直接执行")
    ap.add_argument("--rollback", help="传入对照表 csv，把文件名改回原名")
    args = ap.parse_args()

    if args.rollback:
        rollback(args.rollback, args.dir)
        return

    if not args.prefix:
        interactive()
        return

    items = list_images(args.dir)
    if args.newest:
        mode, arg = "newest", args.newest
    elif args.since:
        mode, arg = "since", args.since
    elif args.match:
        mode, arg = "match", args.match
    else:
        mode, arg = "all", None

    files, keeps, skipped, skipped_cjk = select_files(items, mode, arg, args.sort, args.prefix,
                                                      args.force, args.allow_chinese)
    if skipped_cjk:
        print("（%d 个中文文件名的文件不改名，编号在剩余图片上继续，但会原样写进清单）" % skipped_cjk)
    if skipped:
        print("（%d 个已编号为 %s+数字 的文件不重复编号，同样写进清单）" % (skipped, args.prefix))
    if args.exclude_kept:
        keeps = []
    if not files and not keeps:
        raise SystemExit("没有符合条件的图片。")

    plan = build_plan(files, args.prefix, args.start, args.pad)
    print_plan(plan, args.dir, keeps)

    if args.dry_run:
        print("预览模式，未改动任何文件。去掉 --dry-run 才会真的执行。")
        return

    conflicts = find_conflicts(args.dir, plan)
    if conflicts:
        raise SystemExit(
            "目标文件名已被占用：%s\n"
            "请换个前缀，或用 --start 从更大的编号开始，或加 --force 把旧的编号文件一起重编。"
            % "、".join(conflicts[:5]))
    if not args.yes:
        if input("确认执行？[y/N] ").strip().lower() != "y":
            print("已取消，没动任何文件。")
            return

    do_rename(args.dir, plan)
    print("改名完成，共 %d 张。" % len(plan))
    made = write_outputs(args.out, args.prefix, plan, args.city, args.seal, keeps)
    print("已生成：")
    for p in made:
        print("  " + p)


if __name__ == "__main__":
    main()

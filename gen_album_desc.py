# -*- coding: utf-8 -*-
"""
生成 / 刷新 js/album-desc.js（相册简介的纯文本编写区）。

用法：python gen_album_desc.py
  · 扫描 js/data.js，把所有相册名列进 album-desc.js（按 data.js 里的顺序）
  · 已经写过的简介原样保留，只补新增的相册名、清理已删除的相册名
  · 重复运行不会丢内容，可放心当「同步相册名」的工具用
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(ROOT, "js", "data.js")
OUT_PATH = os.path.join(ROOT, "js", "album-desc.js")

HEADER = u"""/* ═══════════ 相册简介 · 纯文本编写区 ═══════════
   这里是全站相册简介的唯一正式来源。想改哪本相册的简介，只改这个文件。

   写法（不需要懂 JS，照着填字就行）：
     ### 相册名
     正文随便写，不限字数。
     中间空一行，页面里就分成两段。

   规则：
     ·「### 相册名」必须和 js/data.js 里的 city 一字不差（空格也算）；
       相册名由 gen_album_desc.py 自动生成，不要自己改这一行。
     · 正文里不要出现反引号 ` 和 ${ —— 这两个符号会打断整段文本。
     · 不想显示简介，就让它下面空着，页面上的「简介」入口会自动隐藏。
     · 改完存盘，刷新网页即可；推到 GitHub Pages 后所有人都看得到。

   另外两种写简介的方式（优先级从高到低）：
     ① 网页上点开相册 →「简介」→「编辑」：只存在这台电脑的浏览器里，改着玩用
     ② js/data.js 每个图集的 desc 字段：早期写法，仅作兜底
*/\n
window.ALBUM_DESC_TEXT = `
"""

FOOTER = u"""`;
"""

HEADING_RE = re.compile(r"^#{1,3}\s*(.+?)\s*$")


def read_text(path):
    with io.open(path, "r", encoding="utf-8") as f:
        return f.read()


def album_names():
    """从 data.js 里按顺序取出所有相册名"""
    src = read_text(DATA_PATH)
    seen, names = set(), []
    for name in re.findall(r'city:\s*"([^"]+)"', src):
        if name not in seen:
            seen.add(name)
            names.append(name)
    return names


def parse_existing():
    """读回旧的 album-desc.js，返回 (有序相册名, {相册名: 正文})"""
    if not os.path.exists(OUT_PATH):
        return [], {}
    text = read_text(OUT_PATH)
    m = re.search(r"ALBUM_DESC_TEXT\s*=\s*`(.*?)`\s*;", text, re.S)
    if not m:
        return [], {}
    order, body, cur, buf = [], {}, None, []

    def flush():
        if cur is not None:
            body[cur] = u"\n".join(buf).strip(u"\n")

    for line in m.group(1).split(u"\n"):
        h = HEADING_RE.match(line.strip())
        if h:
            flush()
            cur = h.group(1).strip()
            buf = []
            if cur not in body:
                order.append(cur)
            continue
        if cur is not None:
            buf.append(line.rstrip())
    flush()
    return order, body


def main():
    if not os.path.exists(DATA_PATH):
        print(u"找不到 js/data.js，脚本要在项目根目录下运行")
        return 1

    names = album_names()
    order, body = parse_existing()
    if not names:
        print(u"data.js 里没读到相册名，未做任何改动")
        return 1

    added = [n for n in names if n not in body]
    kept = [n for n in order if n in body and n not in names]

    out = [HEADER]
    for i, name in enumerate(names):
        text = body.get(name, u"").strip(u"\n")
        out.append(u"### " + name + u"\n")
        if text:
            out.append(text + u"\n")
        if i != len(names) - 1:
            out.append(u"\n")
    if kept:
        out.append(u"\n")
        for name in kept:
            out.append(u"### " + name + u"\n")
            out.append(body.get(name, u"").strip(u"\n") + u"\n")
    out.append(FOOTER)

    with io.open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(u"".join(out))

    print(u"已写入 js/album-desc.js，共 %d 本相册" % len(names))
    if added:
        print(u"  新增：%s" % u"、".join(added))
    if kept:
        print(u"  data.js 里已没有、但文件里还留着的：%s" % u"、".join(kept))
    return 0


if __name__ == "__main__":
    sys.exit(main())

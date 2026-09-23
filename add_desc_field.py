# -*- coding: utf-8 -*-
"""
给 data.js 里每个图集加一个 desc 字段（相册简介）。
只动 photos: [ ... ] 里的图集条目（缩进 6 空格的 city 行），不动 site 等其他配置。
已经写过 desc 的条目会跳过，可重复运行。
"""
import io
import re

PATH = "js/data.js"

src = io.open(PATH, encoding="utf-8").read()
had_bom = src.startswith("\ufeff")
if had_bom:
    src = src[1:]

lines = src.split("\n")
out = []
added = 0
skipped = 0

for i, line in enumerate(lines):
    out.append(line)
    m = re.match(r'^(\s+)city:\s*"', line)
    if not m:
        continue
    indent = m.group(1)
    # 往后看几行，若已有 desc 就跳过（避免重复插入）
    look = "\n".join(lines[i + 1:i + 6])
    if re.search(r'^\s*desc:', look, re.M):
        skipped += 1
        continue
    out.append('%sdesc: "",' % indent)
    added += 1

text = "\n".join(out)
if had_bom:
    text = "\ufeff" + text
io.open(PATH, "w", encoding="utf-8", newline="\n").write(text)

print("added=%d skipped=%d" % (added, skipped))

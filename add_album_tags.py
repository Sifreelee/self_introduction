# -*- coding: utf-8 -*-
"""
给 js/data.js 里每个相册写入自定义标签（tags 字段）。

用法：
    1. 修改下方 TAGS 字典：键 = 相册名（city），值 = 标签数组
    2. 运行本脚本（可反复运行：已存在的 tags 行会被覆盖，不会重复插入）

标签的匹配规则（见 js/main.js）：照片名（title 或文件名）中包含该标签即命中，
所以标签要写成照片名里真正出现过的字，例如「青铜器」「颐和园」。
"""
import io
import re

# ── 在这里增删标签 ──────────────────────────────────────────────
# 键要和 data.js 里的 city 完全一致（含空格）
TAGS = {
    "文物介绍及科普": ["镇馆之宝", "青铜器", "陶瓷", "金银器", "佛教文物", "玉器"],
    "中国 北京": ["颐和园", "北海", "雍和宫", "天安门", "天坛", "中山公园"],
    "北京 圆明园遗址公园": ["大水法", "海晏堂", "鸿慈永秙", "遗址", "鸳鸯", "荷"],
    "古建筑构建盘点": ["脊兽"],
    "北京 九坛八庙": ["天坛", "太庙", "社稷坛", "地坛", "先蚕坛"],
    "中国 重庆": ["老君洞", "华岩寺", "风吹岭", "夜", "江"],
    "吉林 长春": ["净月潭", "红旗街", "同志街", "电车"],
    "长春伪满和建国初期建筑": ["伪满皇宫", "伪满", "建国", "东本愿寺", "鸣放宫"],
    "山东 淄博": ["四宝山", "桓台", "周村", "淄川", "海岱楼"],
    "辽宁 沈阳": ["清故宫", "北陵公园", "中街", "工业博物馆", "教堂", "扫街"],
    "辽宁 大连": ["星海广场", "莲花山", "渔人码头", "东港", "威尼斯"],
    "华东四市": ["上海", "杭州", "乌镇", "苏州"],
    "陕西 西安": ["华山", "兵马俑", "不夜城", "骊山", "华清池"],
    "山东 泰安": ["泰山"],
    "名胜古迹 三山五岳": ["泰山", "华山"],
}
# ──────────────────────────────────────────────────────────────

CITY_RE = re.compile(r'^(\s*)city:\s*"([^"]*)",\s*$')
PHOTOS_RE = re.compile(r'^\s*photos:\s*\[\s*$')
# 图集级字段：同一本图集里出现多次只保留第一次（可用来清理重复行）
META_RE = re.compile(r'^\s*(desc|seal|star|tags|cover):')


def js_list(items):
    return "[" + ", ".join('"%s"' % t for t in items) + "]"


def main():
    path = "js/data.js"
    with io.open(path, "r", encoding="utf-8") as f:
        lines = f.read().split("\n")

    out, i, touched = [], 0, 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        i += 1

        m = CITY_RE.match(line)
        if not m:
            continue
        indent, city = m.group(1), m.group(2)
        seen = set()

        # 扫 city 之后、photos 之前这一段：重复的字段行丢掉，tags 行重写
        while i < len(lines) and not PHOTOS_RE.match(lines[i]):
            cur = lines[i]
            km = META_RE.match(cur)
            if km:
                key = km.group(1)
                if key == "tags" and city in TAGS:
                    if "tags" in seen:          # 重复行，丢掉
                        i += 1
                        continue
                    seen.add("tags")
                    out.append('%stags: %s,' % (indent, js_list(TAGS[city])))
                    i += 1
                    continue
                if key in seen:                 # 重复行，丢掉
                    i += 1
                    continue
                seen.add(key)
                out.append(cur)
                i += 1
                continue
            out.append(cur)
            i += 1

        # 这段里没有 tags 行，而该相册配了标签 → 补一行
        if city in TAGS:
            if "tags" not in seen:
                out.append('%stags: %s,' % (indent, js_list(TAGS[city])))
            touched += 1

    with io.open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))

    print("已写入 %d 本图集的标签（共配置 %d 本）" % (touched, len(TAGS)))


if __name__ == "__main__":
    main()

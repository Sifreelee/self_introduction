# 项目长期记忆（大同图集 assets/images/dt）

## 照片命名规范（2026-10-12 定）
- 格式：`大标题 其一.png` / `大标题 其二.png`…，用空格分隔，中文序数从「其一」起算。
- 单张即代表一个分类的：只保留大标题，不编号（如 `悬空寺.png`、`云冈石窟第8窟.png`）。
- 大标题本身不改（前缀如「大同古城」「古城」「云冈石窟第N窟」保持原样）。
- 带描述后缀的保留描述（如 `善化寺 大雄宝殿.png`、`善化寺 框架之美.png`），不并入序号。

## 站点背景
- 站点根目录 F:/WorkBuddy/personal-website，照片在 assets/images/ 下按城市分子目录。
- js/data.js 的 photos 数组登记各城市图集；大同相册尚未登记。
- 已有工具：rename_album.py（英文前缀批量编号+生成对照表/清单/data.js 片段）、
  compress.py、add_album_tags.py、tools.bat。
- 其他相册文件夹惯例：附 `1_对照表.csv`、`1_照片清单.txt`，可选 `1_datajs片段.txt`。

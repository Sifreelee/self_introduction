"""山水清音桌面管家：文件事务、网站配置和发布。Python 3.8+."""
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import uuid
import zipfile
from urllib.parse import unquote, urlsplit, urlunsplit
from datetime import datetime

from PIL import Image, ImageOps
if not getattr(sys, 'frozen', False):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import rename_qi

IMAGES = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tif', '.tiff', '.gif', '.svg'}
IGNORE = {'.git', '.workbuddy', '.codex', '.agents', '__pycache__', 'node_modules', '_internal', 'desktop-tool', 'desktop-output'}
PALETTE = {'paper': '#EFE8D6', 'card': '#F6F0E2', 'ink': '#2B2B26', 'teal': '#2C4A52', 'cinnabar': '#A83A32', 'gold': '#A98545'}


def report_progress(callback, stage, done, total, detail=''):
    if callback is not None:
        callback(stage, done, total, detail)


def is_site(path):
    root = Path(path)
    return all((root / name).is_file() for name in ('index.html', 'js/data.js', 'css/style.css'))


def locate_site(settings, app_dir):
    """先读取用户选择，再尝试随程序一起移动后的相对位置和邻近目录。"""
    app_dir = Path(app_dir).resolve()
    candidates = []
    if settings.get('site'):
        candidates.append(Path(settings['site']))
    if settings.get('site_relative'):
        candidates.append(app_dir / settings['site_relative'])
    nearby = [app_dir] + list(app_dir.parents)[:4]
    candidates.extend(nearby)
    candidates.extend(p / 'personal-website' for p in nearby[:2])
    for path in candidates:
        if is_site(path):
            return str(path.resolve())
    return ''


def writable(path):
    p = Path(path).resolve()
    if p.drive.upper() == 'C:':
        raise ValueError('请使用非 C 盘目录，遵循你的磁盘写入规则。')
    return p


def within(path, root):
    try:
        Path(path).resolve().relative_to(Path(root).resolve())
        return True
    except ValueError:
        return False


def natural(s):
    return [int(p) if p.isdigit() else p.casefold() for p in re.split(r'(\d+)', str(s))]


def photo_sort_key(value):
    path = Path(str(value))
    stem, number = path.stem, 0
    match = re.match(r'^(.*?)\s*其([零一二三四五六七八九十百\d]+)$', stem)
    if match and rename_qi.cn_parse(match.group(2)):
        stem, number = match.group(1).rstrip(' _-'), rename_qi.cn_parse(match.group(2))
    else:
        match = re.match(r'^(.*?)[ _-]*(\d+)$', stem)
        if match:
            stem, number = match.group(1).rstrip(' _-'), int(match.group(2))
        else:
            match = re.match(r'^(.*?)[ _-]*([零一二三四五六七八九十百]+)$', stem)
            if match and match.group(1) and (rename_qi.cn_parse(match.group(2)) or 0) >= 11:
                stem, number = match.group(1).rstrip(' _-'), rename_qi.cn_parse(match.group(2))
    return (natural(path.parent.as_posix()), natural(stem), number, natural(path.name))


def sorted_upload_items(items):
    return sorted(items, key=lambda item: photo_sort_key(item[1]))


def reveal_file(path):
    path = Path(path).resolve()
    if not path.exists():
        raise ValueError('文件已移动或改名，请先点击“刷新列表”再试。')
    explorer = str(Path(os.environ.get('WINDIR', 'C:/Windows')) / 'explorer.exe')
    return subprocess.Popen([explorer, '/select,', str(path)])


def file_identities(items):
    result = {}
    for source, _ in items:
        try:
            info = Path(source).stat()
            result[str(source)] = (info.st_dev, info.st_ino)
        except OSError:
            pass
    return result


def refresh_selected_files(items, identities):
    """只更新已选文件；同目录内改名通过文件 ID 识别，不把未选文件混进来。"""
    refreshed, parents = [], {}
    for source, relative in items:
        old = Path(source)
        current = old
        if not current.is_file():
            identity = identities.get(str(source))
            current = None
            if identity and identity[1] and old.parent.is_dir():
                if old.parent not in parents:
                    candidates = collect(old.parent, recursive=False)
                    parents[old.parent] = {identity: Path(p) for p, identity in file_identities([(str(p), p.name) for p in candidates]).items()}
                current = parents[old.parent].get(identity)
        if current is not None:
            refreshed.append((str(current), (Path(relative).parent / current.name).as_posix()))
    return sorted_upload_items(refreshed)


def collect(folder, recursive=True, images_only=False):
    folder = Path(folder).resolve()
    if not folder.is_dir():
        raise ValueError('文件夹不存在：' + str(folder))
    out = []
    for base, dirs, names in os.walk(str(folder), followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in IGNORE and not d.startswith('.') and not (Path(base) / d).is_symlink())
        for name in names:
            p = Path(base) / name
            if name.startswith('.') or p.is_symlink() or not within(p, folder):
                continue
            if not images_only or p.suffix.lower() in IMAGES:
                out.append(p)
        if not recursive:
            break
    return sorted(out, key=lambda p: photo_sort_key(p.relative_to(folder).as_posix()))


def digest(p):
    if not p.exists():
        return None
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def atomic(path, data):
    path = writable(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.ssqy-', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
        for attempt in range(8):
            try:
                os.replace(tmp, str(path))
                break
            except PermissionError:
                if attempt == 7:
                    raise
                time.sleep(0.05 * (attempt + 1))
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


class Transaction:
    def __init__(self, state, label):
        self.temp_root = writable(state) / 'temp'
        self.folder = self.temp_root / ('work-' + uuid.uuid4().hex)
        self.folder.mkdir(parents=True)

    def remember(self, path):
        # 兼容调用方的写入前校验，不复制原文件、不生成 .bak 或 history。
        writable(path)

    def write(self, path, data):
        self.remember(path)
        atomic(path, data)

    def remove(self, path):
        self.remember(path)
        Path(path).unlink()

    def __enter__(self):
        return self

    def __exit__(self, typ, value, tb):
        if self.folder.exists():
            if not within(self.folder.resolve(), self.temp_root.resolve()) or self.folder.is_symlink():
                raise ValueError('临时目录超出程序缓存范围，已停止清理。')
            shutil.rmtree(str(self.folder))
        return False




def push_script_resource():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS) / 'resources/push.bat'
    return Path(__file__).resolve().parent.parent / 'push.bat'


def clear_cache(state):
    """清理程序临时文件和旧版残留备份，不扫描网站、原图或设置。"""
    state = Path(state).absolute()
    result = {'files': 0, 'freed_bytes': 0, 'skipped': 0}
    reparse = getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)
    def linked(path):
        return path.is_symlink() or bool(getattr(path.lstat(), 'st_file_attributes', 0) & reparse)
    if not state.exists() or linked(state):
        return result
    state = writable(state)
    for name in ('temp', 'preview-cache', 'history'):
        cache = state / name
        if not cache.exists():
            continue
        if linked(cache) or not within(cache, state):
            result['skipped'] += 1
            continue
        folders = []
        for base, dirs, files in os.walk(str(cache), followlinks=False):
            parent = Path(base)
            safe_dirs = []
            for child in dirs:
                path = parent / child
                if not linked(path) and within(path, cache):
                    safe_dirs.append(child)
                else:
                    result['skipped'] += 1
            dirs[:] = safe_dirs
            folders.append(parent)
            for filename in files:
                path = parent / filename
                try:
                    if linked(path) or not within(path, cache):
                        result['skipped'] += 1
                        continue
                    size = path.stat().st_size
                    path.unlink()
                    result['files'] += 1
                    result['freed_bytes'] += size
                except OSError:
                    result['skipped'] += 1
        for folder in reversed(folders):
            if folder != cache and within(folder, cache) and not linked(folder):
                try:
                    folder.rmdir()
                except OSError:
                    pass
    return result


def launch_push_script(root, state, resource_path=None):
    root, state = writable(root), writable(state)
    if not is_site(root):
        raise ValueError('请选择正确的网站文件夹后再上传。')
    if resource_path is None:
        resource_path = push_script_resource()
    content = Path(resource_path).read_text(encoding='utf-8-sig')
    if content.count('cd /d "%~dp0"') != 1:
        raise ValueError('push.bat 的工作目录格式发生变化，无法安全指定当前网站。')
    content = content.replace('setlocal enabledelayedexpansion', 'setlocal DisableDelayedExpansion', 1)
    content = content.replace('cd /d "%~dp0"', 'cd /d "%SSQY_SITE_ROOT%"\nif errorlevel 1 exit /b 1\nsetlocal EnableDelayedExpansion', 1)
    session = state / 'upload-sessions' / uuid.uuid4().hex
    session.mkdir(parents=True)
    script = session / 'upload.bat'
    atomic(script, content.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf-8'))
    temp = state / 'temp'
    temp.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, SSQY_SITE_ROOT=str(root), TEMP=str(temp), TMP=str(temp))
    # Git 的网络传输连续 60 秒几乎无数据时退出，用户可直接在窗口里重试。
    env.setdefault('GIT_HTTP_LOW_SPEED_LIMIT', '1')
    env.setdefault('GIT_HTTP_LOW_SPEED_TIME', '60')
    cmd = os.environ.get('COMSPEC', str(Path(os.environ.get('WINDIR', 'C:/Windows')) / 'System32/cmd.exe'))
    # 固定脚本名 + cwd 避免把用户路径拼成 shell 代码。用户明确要求可见交互窗口。
    process = subprocess.Popen([cmd, '/D', '/V:OFF', '/K', 'upload.bat'], cwd=str(session), env=env,
                               creationflags=getattr(subprocess, 'CREATE_NEW_CONSOLE', 0))
    return process, script




# 词法扫描保留原 JS 注释和排版；不执行用户代码，不把中文转成转义乱码。
TOKEN = re.compile(r'''//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`|[A-Za-z_$][\w$]*|[^\s]''')


class Document:
    def __init__(self, text):
        self.text = text
        self.tokens = [(m.group(), m.start(), m.end()) for m in TOKEN.finditer(text) if not m.group().startswith(('//', '/*'))]
        self.pairs = {}
        stack = []
        for i, (v, _, _) in enumerate(self.tokens):
            if v in ('{', '['):
                stack.append(i)
            elif v in ('}', ']'):
                if not stack:
                    raise ValueError('data.js 括号不完整。')
                a = stack.pop()
                if self.tokens[a][0] != ('{' if v == '}' else '['):
                    raise ValueError('data.js 括号不匹配。')
                self.pairs[a] = i
        if stack:
            raise ValueError('data.js 括号不完整。')
        names = [i for i, t in enumerate(self.tokens) if t[0] == 'SITE_DATA']
        if not names:
            raise ValueError('找不到 SITE_DATA，请选择网站根目录。')
        self.root = names[0] + 2
        if self.tokens[self.root][0] != '{':
            raise ValueError('不支持当前 SITE_DATA 格式。')

    def prop(self, obj, name):
        i = obj + 1
        while i < self.pairs[obj]:
            if self.tokens[i][0].strip('"\'') == name and self.tokens[i + 1][0] == ':':
                return i + 2
            i = self.pairs[i] + 1 if i in self.pairs else i + 1
        return None

    def string(self, i):
        if i is None:
            return ''
        raw = self.tokens[i][0]
        if raw.startswith('"'):
            return json.loads(raw)
        if raw.startswith("'"):
            return re.sub(r'\\([\\\'"/])', r'\1', raw[1:-1])
        raise ValueError('需要普通字符串：' + raw)

    def value(self, i):
        if i is None:
            return None
        raw = self.tokens[i][0]
        if raw.startswith(('"', "'")):
            return self.string(i)
        if raw in ('true', 'false'):
            return raw == 'true'
        if raw == '[':
            values, j = [], i + 1
            while j < self.pairs[i]:
                if self.tokens[j][0] != ',':
                    values.append(self.value(j))
                j = self.pairs[j] + 1 if j in self.pairs else j + 1
            return values
        raise ValueError('不支持编辑此字段的动态表达式，请在源码中修改。')

    def objects(self, array):
        i = array + 1
        while i < self.pairs[array]:
            if self.tokens[i][0] == '{':
                yield i
            i = self.pairs[i] + 1 if i in self.pairs else i + 1

    def albums(self):
        array = self.prop(self.root, 'photos')
        if array is None or self.tokens[array][0] != '[':
            raise ValueError('找不到照片集 photos 数组。')
        out = []
        for obj in self.objects(array):
            title = self.string(self.prop(obj, 'city'))
            photos = self.prop(obj, 'photos')
            refs = []
            if photos is not None:
                refs = [self.string(self.prop(p, 'src')) for p in self.objects(photos)]
            out.append({'name': title, 'object': obj, 'array': photos, 'refs': refs})
        return out

    def append(self, array, values):
        if not values:
            return self.text
        end = self.pairs[array]
        close = self.tokens[end][1]
        nonempty = end > array + 1
        comma = ',' if nonempty and self.tokens[end - 1][0] != ',' else ''
        # 逗号放在最后一个实际 token 后，避免被行注释吞掉。
        insert_at = self.tokens[end - 1][2] if nonempty else self.tokens[array][2]
        text = self.text[:insert_at] + comma + self.text[insert_at:close]
        return text + '\n      ' + ',\n      '.join(values) + '\n    ' + self.text[close:]


def q(value):
    return json.dumps(value, ensure_ascii=False)


def sync_album(text, title, entries):
    doc = Document(text)
    matches = [a for a in doc.albums() if a['name'] == title]
    if len(matches) > 1:
        raise ValueError('存在同名相册，请先在 data.js 区分：' + title)
    if matches:
        album = matches[0]
        if album['array'] is None:
            raise ValueError('该相册缺少 photos 数组。')
        existing = set(album['refs'])
        return doc.append(album['array'], [json.dumps(e, ensure_ascii=False) for e in entries if e['src'] not in existing])
    album = {'city': title, 'seal': title[:1], 'photos': entries}
    return doc.append(doc.prop(doc.root, 'photos'), [json.dumps(album, ensure_ascii=False, indent=2)])


def album_by_name(doc, name):
    found = [a for a in doc.albums() if a['name'] == name]
    if len(found) != 1:
        raise ValueError('相册不存在或有重名，请重新读取：' + name)
    return found[0]


def set_album_property(text, name, key, value):
    doc = Document(text)
    obj = album_by_name(doc, name)['object']
    index = doc.prop(obj, key)
    if index is None:
        return doc.append(obj, [key + ': ' + q(value)])
    end = doc.pairs.get(index, index)
    return text[:doc.tokens[index][1]] + q(value) + text[doc.tokens[end][2]:]


def edit_album(text, original, metadata):
    name = metadata.get('city', '').strip()
    if not name or any(c in name for c in '\r\n'):
        raise ValueError('请输入单行相册名称。')
    doc = Document(text)
    if any(re.sub(r'\s+', '', a['name']) == re.sub(r'\s+', '', name) and a['name'] != original for a in doc.albums()):
        raise ValueError('相册名称已存在，请选择它进行修改，或使用其他名称。')
    tags = metadata.get('tags', [])
    if not isinstance(tags, list) or any(not isinstance(t, str) for t in tags):
        raise ValueError('关键词应为文字列表。')
    desc = metadata.get('desc', '').strip()
    if any(re.match(r'^\s*#{1,3}\s*\S', line) for line in desc.splitlines()):
        raise ValueError('简介中请勿用 # 开头的标题行，它会被网站识别为其他相册。')
    cover = metadata.get('cover', '').strip().replace('\\', '/')
    if cover and (not cover.startswith('assets/') or '..' in Path(cover).parts):
        raise ValueError('封面请填写网站 assets 内的图片路径，或留空使用第一张照片。')
    values = {'seal': metadata.get('seal', '').strip(), 'star': bool(metadata.get('star')), 'tags': list(dict.fromkeys(t.strip() for t in tags if t.strip())), 'desc': desc, 'cover': cover}
    if original is None:
        obj = dict(city=name, **values, photos=[])
        text = doc.append(doc.prop(doc.root, 'photos'), [json.dumps(obj, ensure_ascii=False, indent=2)])
    else:
        album_by_name(doc, original)
        for key, value in values.items():
            text = set_album_property(text, original, key, value)
        text = set_album_property(text, original, 'city', name)
        # 按网站的“全名优先、否则名称包含”规则识别快捷入口。
        tokens = Document(text).tokens
        edits = []
        for i, token in enumerate(tokens[:-2]):
            if token[0].strip('"\'') == 'openAlbum' and tokens[i + 1][0] == ':':
                raw = tokens[i + 2][0]
                if raw.startswith(('"', "'")):
                    val = json.loads(raw) if raw.startswith('"') else raw[1:-1]
                    key = val.strip()
                    old_albums = doc.albums()
                    exact = next((a['name'] for a in old_albums if a['name'] == key), None)
                    resolved = exact or next((a['name'] for a in old_albums if key and key in a['name']), None)
                    if resolved == original:
                        edits.append((tokens[i + 2][1], tokens[i + 2][2]))
        for a, b in reversed(edits):
            text = text[:a] + q(name) + text[b:]
    if metadata.get('position') not in (None, ''):
        text = move_album(text, name, metadata['position'])
    Document(text).albums()
    return text


def move_album(text, name, position):
    doc = Document(text)
    albums = doc.albums()
    position = int(position)
    if not 1 <= position <= len(albums):
        raise ValueError('显示顺序需在第 1～%d 个之间。' % len(albums))
    current = next(i for i, album in enumerate(albums) if album['name'] == name)
    if current == position - 1:
        return text
    # 对调对象所在的槽位，保留数组分隔符、尾逗号与所有槽位之间的注释。
    spans = [(doc.tokens[a['object']][1], doc.tokens[doc.pairs[a['object']]][2]) for a in albums]
    objects = [text[a:b] for a, b in spans]
    objects.insert(position - 1, objects.pop(current))
    for (a, b), obj in reversed(list(zip(spans, objects))):
        text = text[:a] + obj + text[b:]
    return text


DESC_ASSIGN = re.compile(r'window\s*\.\s*ALBUM_DESC_TEXT\s*=\s*(`(?:\\[\s\S]|[^`\\])*`)', re.S)


def description_sections(text):
    match = DESC_ASSIGN.search(text)
    if not match:
        raise ValueError('无法读取 album-desc.js 的 ALBUM_DESC_TEXT，已停止以保护原文件。')
    raw = match.group(1)[1:-1]
    if re.search(r'(?<!\\)\$\{', raw):
        raise ValueError('album-desc.js 含有动态表达式，请先在源码中处理。')
    raw = re.sub(r'\\([\\`$])', r'\1', raw)
    sections, current, body = [], None, []
    preamble = []
    for line in raw.splitlines():
        heading = re.match(r'^\s*#{1,3}\s*(.+?)\s*$', line)
        if heading:
            if current is not None:
                sections.append((current, '\n'.join(body).strip()))
            current, body = heading.group(1), []
        elif current is None:
            preamble.append(line)
        else:
            body.append(line)
    if current is not None:
        sections.append((current, '\n'.join(body).strip()))
    return match, '\n'.join(preamble).strip(), sections


def edit_description(text, original, name, desc):
    if text is None:
        text = 'window.ALBUM_DESC_TEXT = ``;\n'
    match, preamble, sections = description_sections(text)
    fold = lambda s: re.sub(r'\s+', '', s)
    keys = {fold(name)}
    if original:
        keys.add(fold(original))
    kept, inserted = [], False
    for title, body in sections:
        if fold(title) in keys:
            if not inserted:
                kept.append((name, desc.strip()))
                inserted = True
        else:
            kept.append((title, body))
    if not inserted:
        kept.append((name, desc.strip()))
    content = '\n' + ((preamble + '\n\n') if preamble else '') + '\n\n'.join('### ' + title + '\n' + body for title, body in kept) + '\n'
    content = content.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
    return text[:match.start(1)] + '`' + content + '`' + text[match.end(1):]


def read_album(root, name):
    root = Path(root)
    doc = Document((root / 'js/data.js').read_text(encoding='utf-8-sig'))
    album = album_by_name(doc, name)
    obj = album['object']
    values = {key: doc.value(doc.prop(obj, key)) for key in ('city', 'seal', 'star', 'tags', 'desc', 'cover')}
    values['position'] = next(i for i, a in enumerate(doc.albums(), 1) if a['name'] == name)
    if isinstance(values['desc'], list):
        values['desc'] = '\n'.join(values['desc'])
    desc_file = root / 'js/album-desc.js'
    if desc_file.exists():
        _, _, sections = description_sections(desc_file.read_text(encoding='utf-8-sig'))
        fold = lambda s: re.sub(r'\s+', '', s)
        exact = [body for title, body in sections if title == name and body]
        folded = [body for title, body in sections if fold(title) == fold(name) and body]
        if exact or folded:
            values['desc'] = (exact or folded)[-1]
    return values


def album_code(root, original, metadata):
    root = Path(root)
    text = (root / 'js/data.js').read_text(encoding='utf-8-sig')
    updated = edit_album(text, original, metadata)
    desc_file = root / 'js/album-desc.js'
    desc = edit_description(desc_file.read_text(encoding='utf-8-sig') if desc_file.exists() else None, original, metadata['city'].strip(), metadata.get('desc', '').strip())
    doc = Document(updated)
    obj = album_by_name(doc, metadata['city'].strip())['object']
    snippet = updated[doc.tokens[obj][1]:doc.tokens[doc.pairs[obj]][2]]
    return {'data.js': updated, 'album-desc.js': desc, '相册代码片段': snippet}


def save_album(root, state, original, metadata, expected=None):
    root = writable(root)
    if expected:
        for name, old_hash in expected.items():
            if digest(root / 'js' / name) != old_hash:
                raise ValueError('网站代码已被其他操作修改，请重新读取相册再保存。')
    code = album_code(root, original, metadata)
    with Transaction(state, '修改相册：' + metadata['city'].strip()) as tx:
        for name in ('data.js', 'album-desc.js'):
            tx.write(root / 'js' / name, code[name].encode('utf-8'))
    return metadata['city'].strip()


def replace_refs(text, mapping):
    replacements = []
    for m in TOKEN.finditer(text):
        raw = m.group()
        if not raw.startswith(('"', "'")):
            continue
        try:
            val = json.loads(raw) if raw.startswith('"') else re.sub(r'\\([\\\'"/])', r'\1', raw[1:-1])
        except ValueError:
            continue
        if val in mapping:
            replacements.append((m.start(), m.end(), q(mapping[val])))
    for a, b, value in reversed(replacements):
        text = text[:a] + value + text[b:]
    return text


def site_info(root):
    root = Path(root).resolve()
    text = (root / 'js/data.js').read_text(encoding='utf-8-sig')
    albums = Document(text).albums()
    dirs = {'assets/images'}
    base = root / 'assets/images'
    for folder, subdirs, _ in os.walk(str(base)):
        subdirs[:] = [d for d in subdirs if not d.startswith('.') and not (Path(folder) / d).is_symlink()]
        dirs.add(Path(folder).relative_to(root).as_posix())
    css = (root / 'css/style.css').read_text(encoding='utf-8')
    palette = dict(PALETTE)
    for key, color in re.findall(r'--([\w-]+)\s*:\s*(#[\da-fA-F]{6})', css):
        palette[key] = color
    return albums, sorted(dirs, key=natural), palette


def inspect_image_references(root, progress=None):
    """只读核对 data.js 和 assets 图片，报告保留快照以供安全修复。"""
    root = Path(root).resolve()
    report_progress(progress, '扫描图片文件', 0, 0, '正在读取网站图片和 data.js')
    data = root / 'js/data.js'
    raw = data.read_bytes()
    doc = Document(raw.decode('utf-8-sig'))
    albums = doc.albums()
    reference_count = sum(len(album['refs']) + bool(doc.string(doc.prop(album['object'], 'cover'))) for album in albums)
    inventory = {p.relative_to(root).as_posix(): p for p in collect(root / 'assets', images_only=True)} if (root / 'assets').is_dir() else {}
    folded = {path.casefold(): path for path in inventory}
    used, issues, external, checked = set(), [], 0, 0
    album_reference_tokens = set()
    total_work = reference_count + len(inventory) + 1

    def resolve_reference(value):
        parsed = urlsplit(value.replace('\\', '/'))
        if parsed.scheme in ('http', 'https', 'data', 'blob') or parsed.netloc:
            return 'external', None, None
        path = unquote(parsed.path)
        candidate = root / path
        if parsed.scheme or not path.casefold().startswith('assets/') or not within(candidate, root / 'assets'):
            return 'invalid', None, None
        canonical = folded.get(path.casefold())
        if canonical:
            used.add(canonical)
            if canonical != path:
                replacement = urlunsplit(('', '', canonical, parsed.query, parsed.fragment))
                return 'case', canonical, replacement
            return 'exists', canonical, None
        if candidate.is_file():
            used.add(path)
            return 'exists', path, None
        return 'missing', path, None

    def check(value, album_index, photo_index, role, title=''):
        nonlocal external, checked
        checked += 1
        report_progress(progress, '核对照片代码', min(checked, reference_count), total_work, '%d/%d 条引用 · %s' % (min(checked, reference_count), reference_count, Path(value).name))
        state, canonical, replacement = resolve_reference(value)
        if state == 'external':
            external += 1
            return state, value
        if state == 'exists':
            return state, canonical
        kind = state + '_' + role
        labels = {'missing': '文件已不存在', 'case': '路径大小写不一致', 'invalid': '图片路径不合法'}
        notes = {'missing': '文件可能被删除或改名；可选择删除这条照片代码', 'case': '本地 Windows 可能正常，GitHub 上可能打不开；需手动核对路径大小写', 'invalid': '请手动修改为网站 assets 内的相对路径'}
        issue = {'id': '%s:%s:%s:%s' % (kind, album_index, photo_index, value), 'kind': kind, 'type': labels[state] + ('（封面）' if role == 'cover' else ''), 'album': albums[album_index]['name'], 'album_index': album_index, 'photo_index': photo_index, 'title': title, 'path': value, 'suggestion': notes[state], 'repairable': state in ('missing', 'case'), 'replacement': replacement}
        if state == 'missing' and canonical:
            candidates = [path for path in inventory if Path(path).parent == Path(canonical).parent and Path(path).stem.casefold() == Path(canonical).stem.casefold()]
            if len(candidates) == 1:
                issue['suggestion'] += '；发现同名不同格式文件：' + candidates[0]
        issues.append(issue)
        return state, canonical

    for album_index, album in enumerate(albums):
        seen = set()
        if album['array'] is not None:
            for photo_index, obj in enumerate(doc.objects(album['array'])):
                src = doc.string(doc.prop(obj, 'src'))
                album_reference_tokens.add(doc.prop(obj, 'src'))
                try:
                    title = doc.string(doc.prop(obj, 'title'))
                except ValueError:
                    title = ''
                state, canonical = check(src, album_index, photo_index, 'photo', title)
                identity = canonical if canonical else src
                if identity in seen:
                    issues.append({'id': 'duplicate:%s:%s' % (album_index, photo_index), 'kind': 'duplicate_photo', 'type': '同相册重复照片', 'album': album['name'], 'album_index': album_index, 'photo_index': photo_index, 'title': title, 'path': src, 'suggestion': '可删除重复条目，保留第一次登记；不删除图片文件', 'repairable': True})
                seen.add(identity)
        cover = doc.string(doc.prop(album['object'], 'cover'))
        album_reference_tokens.add(doc.prop(album['object'], 'cover'))
        if cover:
            check(cover, album_index, None, 'cover')

    # 肖像、游记封面等 data.js 中的其他图片不误报为“未登记”。
    for index, token in enumerate(doc.tokens):
        if token[0].startswith(('"', "'")):
            try:
                value = doc.string(index)
                if value.replace('\\', '/').casefold().startswith('assets/'):
                    state, canonical, replacement = resolve_reference(value)
                    if index not in album_reference_tokens and state in ('missing', 'case', 'invalid'):
                        checked += 1
                        issues.append({'id': 'other:%d' % index, 'kind': state + '_other', 'type': '其他栏目图片：' + {'missing': '文件缺失', 'case': '大小写不一致', 'invalid': '路径不合法'}[state], 'album': '其他栏目', 'title': '', 'path': value, 'suggestion': '请在 data.js 相应栏目中手动修改；不会自动删除非相册内容', 'repairable': False})
            except (ValueError, OSError):
                pass
    other = []
    for scanned, path in enumerate(sorted(inventory, key=photo_sort_key), 1):
        report_progress(progress, '核对未登记图片', reference_count + scanned, total_work, '%d/%d 个文件 · %s' % (scanned, len(inventory), Path(path).name))
        if path not in used and Path(path).suffix.lower() != '.svg':
            other.append({'path': path, 'size': inventory[path].stat().st_size, 'suggestion': '未在 data.js 中使用，可能是新增照片或页面其他素材；请确认后再登记，不会自动删文件'})
    counts = {'albums': len(albums), 'references': checked, 'files': len(inventory), 'missing': sum(i['kind'].startswith('missing_') for i in issues), 'case': sum(i['kind'].startswith('case_') for i in issues), 'duplicates': sum(i['kind'] == 'duplicate_photo' for i in issues), 'invalid': sum(i['kind'].startswith('invalid_') for i in issues), 'unlisted': len(other), 'external': external}
    report_progress(progress, '检查完成', total_work, total_work, '%d 个相册，%d 个图片文件' % (len(albums), len(inventory)))
    return {'root': str(root), 'data_hash': hashlib.sha256(raw).hexdigest(), 'issues': issues, 'unlisted': other, 'counts': counts, 'album_names': [a['name'] for a in albums]}


def reference_local_file(root, value):
    parsed = urlsplit(value.replace('\\', '/'))
    path = Path(root) / unquote(parsed.path)
    if parsed.scheme or parsed.netloc or not unquote(parsed.path).casefold().startswith('assets/') or not within(path, Path(root) / 'assets'):
        return None
    return path


def repair_image_references(root, state, report, selected, operation_label='调整照片与代码对应关系'):
    root = writable(root)
    data = root / 'js/data.js'
    if root != Path(report['root']).resolve() or digest(data) != report['data_hash']:
        raise ValueError('网站或 data.js 已发生变化，请先重新检查，再操作。')
    text = data.read_text(encoding='utf-8-sig')
    doc = Document(text)
    albums = doc.albums()
    chosen = [issue for issue in report['issues'] if issue['id'] in set(selected) and issue['repairable']]
    if not chosen:
        raise ValueError('请先选中需要操作的照片代码；未登记的图片不会自动删除。')
    removed, edits, fixed = set(), [], 0
    for issue in chosen:
        album = albums[issue['album_index']]
        role = 'cover' if issue['kind'].endswith('_cover') else 'photo'
        if role == 'photo':
            obj = list(doc.objects(album['array']))[issue['photo_index']]
            index = doc.prop(obj, 'src')
        else:
            obj = album['object']
            index = doc.prop(obj, 'cover')
        value = doc.string(index)
        local = reference_local_file(root, value)
        if issue['kind'].startswith('missing_') and (local is None or local.is_file()):
            raise ValueError('文件已经恢复或路径变化，请重新检查：' + value)
        if issue['kind'].startswith('case_'):
            correct = reference_local_file(root, issue['replacement'])
            if correct is None or not correct.is_file():
                raise ValueError('建议路径已发生变化，请重新检查。')
            edits.append((doc.tokens[index][1], doc.tokens[index][2], q(issue['replacement'])))
        elif role == 'cover':
            edits.append((doc.tokens[index][1], doc.tokens[index][2], '""'))
        else:
            if obj in removed:
                continue
            removed.add(obj)
            end = doc.pairs[obj]
            a, b = doc.tokens[obj][1], doc.tokens[end][2]
            if doc.tokens[end + 1][0] == ',':
                b = doc.tokens[end + 1][2]
            elif doc.tokens[obj - 1][0] == ',':
                a = doc.tokens[obj - 1][1]
            edits.append((a, b, ''))
        fixed += 1
    # 相邻删除可能共用分隔逗号；合并范围，避免误删保留的照片或产生语法错误。
    deletion = sorted((a, b) for a, b, value in edits if value == '')
    merged = []
    for a, b in deletion:
        if merged and a <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(b, merged[-1][1]))
        else:
            merged.append((a, b))
    replacements = [(a, b, value) for a, b, value in edits if value != '' and not any(start <= a < stop for start, stop in merged)]
    all_edits = replacements + [(a, b, '') for a, b in merged]
    for a, b, value in sorted(all_edits, reverse=True):
        text = text[:a] + value + text[b:]
    Document(text).albums()
    if digest(data) != report['data_hash']:
        raise ValueError('保存前发现代码已被修改，请重新检查。')
    with Transaction(state, operation_label) as tx:
        tx.write(data, text.encode('utf-8'))
    return fixed


def delete_image_entries(root, state, report, selected):
    selected = set(selected)
    choices = [issue for issue in report['issues'] if issue['id'] in selected]
    allowed = {'missing_photo', 'missing_cover', 'duplicate_photo'}
    if not choices or any(issue['kind'] not in allowed for issue in choices):
        raise ValueError('请选择可删除的缺失照片、失效封面或重复照片代码；其他路径提示请手动核对。')
    return repair_image_references(root, state, report, selected, operation_label='删除选中的照片代码')


def register_unlisted_images(root, state, report, paths, album):
    root = writable(root)
    data = root / 'js/data.js'
    if root != Path(report['root']).resolve() or digest(data) != report['data_hash']:
        raise ValueError('网站代码已变化，请重新检查。')
    album = album.strip()
    if not album:
        raise ValueError('请选择或输入相册名称。')
    allowed = {item['path'] for item in report['unlisted']}
    entries = []
    for path in sorted(set(paths), key=photo_sort_key):
        local = root / path
        if path not in allowed or not within(local, root / 'assets') or not local.is_file():
            raise ValueError('图片已变化，请重新检查：' + path)
        entries.append({'src': path, 'title': local.stem})
    if not entries:
        raise ValueError('请先选择需要登记到相册的图片。')
    text = sync_album(data.read_text(encoding='utf-8-sig'), album, entries)
    if digest(data) != report['data_hash']:
        raise ValueError('保存前发现代码已修改，请重新检查。')
    with Transaction(state, '登记新增图片到相册') as tx:
        tx.write(data, text.encode('utf-8'))
    return len(entries)


def image_bytes(path, options):
    ext = path.suffix.lower()
    if not options.get('compress') or ext not in IMAGES - {'.gif', '.svg'}:
        return path.name, path.read_bytes()
    side = int(options.get('side', 1600))
    quality = int(options.get('quality', 82))
    if not 64 <= side <= 20000 or not 10 <= quality <= 100:
        raise ValueError('最长边需在 64～20000，质量需在 10～100。')
    bg = options.get('bg', '#F6F0E2')
    if not re.fullmatch(r'#[\da-fA-F]{6}', bg):
        raise ValueError('底色请填写 #RRGGBB。')
    preserve = options.get('keep_png', False) and ext == '.png'
    with Image.open(str(path)) as original:
        if getattr(original, 'n_frames', 1) > 1:
            return path.name, path.read_bytes()
        img = ImageOps.exif_transpose(original)
        if ext in ('.jpg', '.jpeg') and max(img.size) <= side and path.stat().st_size <= 800 * 1024:
            return path.name, path.read_bytes()
        img.thumbnail((side, side), Image.LANCZOS)
        if preserve:
            out = io.BytesIO()
            img.save(out, format='PNG', optimize=True)
            return path.name, out.getvalue()
        rgba = img.convert('RGBA')
        canvas = Image.new('RGB', img.size, bg)
        canvas.paste(rgba, mask=rgba.getchannel('A'))
        out = io.BytesIO()
        canvas.save(out, format='JPEG', quality=quality, optimize=True, progressive=True)
        return path.stem + '.jpg', out.getvalue()


def image_output_name(path, options):
    """只读图片头预测输出名，预览代码与实际导入使用相同的格式规则。"""
    path = Path(path)
    ext = path.suffix.lower()
    if not options.get('compress') or ext not in IMAGES - {'.gif', '.svg'}:
        return path.name
    if options.get('keep_png') and ext == '.png':
        return path.name
    with Image.open(str(path)) as image:
        if getattr(image, 'n_frames', 1) > 1:
            return path.name
        if ext in ('.jpg', '.jpeg') and max(image.size) <= int(options.get('side', 1600)) and path.stat().st_size <= 800 * 1024:
            return path.name
    return path.stem + '.jpg'


def upload_plan(root, jobs, options):
    root = Path(root).resolve()
    plan, occupied = [], set()
    for job in jobs:
        dest = root / job['target']
        if not within(dest, root / 'assets'):
            raise ValueError('照片存放文件夹必须位于网站 assets 内。')
        for source, relative in sorted_upload_items(job['items']):
            source = Path(source)
            target = dest / relative
            if not within(target, dest):
                raise ValueError('无效相对路径：' + relative)
            target = target.with_name(image_output_name(source, options))
            key = str(target.resolve()).casefold()
            if key in occupied:
                raise ValueError('两张文件会保存到同一个位置，请调整文件名或文件夹：' + str(target))
            occupied.add(key)
            plan.append({'source': source, 'target': target, 'album': job.get('album', '').strip(), 'title': source.stem})
    return plan


def upload_code(root, jobs, options):
    root = Path(root).resolve()
    text = (root / 'js/data.js').read_text(encoding='utf-8-sig')
    groups = {}
    for item in upload_plan(root, jobs, options):
        if item['album'] and item['target'].suffix.lower() in IMAGES:
            groups.setdefault(item['album'], []).append({'src': item['target'].relative_to(root).as_posix(), 'title': item['title']})
    parts = []
    for name, entries in groups.items():
        entries.sort(key=lambda entry: photo_sort_key(entry['src']))
        doc = Document(text)
        found = [a for a in doc.albums() if a['name'] == name]
        existing = set(found[0]['refs']) if found else set()
        entries = [e for e in entries if e['src'] not in existing]
        if entries:
            parts.append('// 相册：' + q(name) + '\n// 以下条目加入这本相册的 photos 数组\n' + ',\n'.join(q(e) for e in entries) + ',')
            text = sync_album(text, name, entries)
    snippet = '\n\n'.join(parts) or '// 本次没有需要新增的照片代码（已存在相同路径，或尚未选择相册）。'
    return {'本次照片 data.js 片段': snippet, 'data.js': text}


def import_jobs(root, state, jobs, options, log, progress=None):
    root = writable(root)
    config = root / 'js/data.js'
    text = config.read_text(encoding='utf-8-sig')
    tasks, occupied = [], set()
    total_files = sum(len(job['items']) for job in jobs)
    total_work = total_files * 2 + len({job.get('album') for job in jobs if job.get('album')}) + 2
    report_progress(progress, '准备添加照片', 0, total_work, '共 %d 个文件' % total_files)
    with Transaction(state, '添加照片并更新相册') as tx:
        staging = tx.folder / 'staging'
        staging.mkdir()
        for job in jobs:
            dest = writable(root / job['target'])
            if not within(dest, root / 'assets'):
                raise ValueError('模块文件的目标目录必须位于网站 assets 内。')
            if not job['items']:
                raise ValueError('这批任务没有文件。')
            for source, rel in sorted_upload_items(job['items']):
                source = Path(source)
                target = dest / rel
                if not within(target, dest):
                    raise ValueError('无效相对路径：' + rel)
                name, data = image_bytes(source, options)
                target = target.with_name(name)
                key = str(target).casefold()
                if key in occupied:
                    raise ValueError('批次之间出现同名目标，请拆分或改名：' + str(target))
                occupied.add(key)
                if target.exists() and not options.get('overwrite'):
                    if digest(target) != hashlib.sha256(data).hexdigest():
                        raise ValueError('同名文件内容不同，请启用“同名文件自动覆盖”或改名：' + str(target))
                    log('已存在相同文件，保留：' + target.name)
                staged = staging / str(len(tasks))
                atomic(staged, data)
                tasks.append((target, staged, job.get('album', ''), source.stem))
                report_progress(progress, '处理并暂存照片', len(tasks), total_work, '%d/%d 个 · %s' % (len(tasks), total_files, source.name))
        grouped = {}
        for target, staged, album, title in tasks:
            if album and target.suffix.lower() in IMAGES:
                grouped.setdefault(album, []).append({'src': target.relative_to(root).as_posix(), 'title': title})
        for title, entries in grouped.items():
            entries.sort(key=lambda entry: photo_sort_key(entry['src']))
            text = sync_album(text, title, entries)
        Document(text).albums()
        for copied, (target, staged, album, title) in enumerate(tasks, 1):
            tx.write(target, staged.read_bytes())
            log('已保存照片或文件 → ' + target.relative_to(root).as_posix())
            report_progress(progress, '保存照片到网站', total_files + copied, total_work, '%d/%d 个 · %s' % (copied, total_files, target.name))
        if text != config.read_text(encoding='utf-8-sig'):
            tx.write(config, text.encode('utf-8'))
        # 只保留成功输出，暂存结果立即删除。
        for p in staging.iterdir():
            p.unlink()
        staging.rmdir()
        report_progress(progress, '保存相册代码', total_work - 1, total_work, '正在完成本次添加')
    report_progress(progress, '添加照片完成', total_work, total_work, '已添加 %d 个文件' % len(tasks))
    return len(tasks)


def rename_plan(folder, mode, prefix, start, pad, recursive=False, filter_mode='全部', include_unchanged=False):
    folder = Path(folder).resolve()
    files = collect(folder, recursive)
    if filter_mode == '仅中文':
        files = [p for p in files if re.search(r'[\u3400-\u9fff]', p.stem)]
    elif filter_mode == '仅英文':
        files = [p for p in files if not re.search(r'[\u3400-\u9fff]', p.stem)]
    if mode == '其一／其二（按标题分组）':
        plan = []
        for parent in sorted({p.parent for p in files}):
            rows = rename_qi.build_plan(str(parent), [p.name for p in files if p.parent == parent], 4, 'strip', 'number')
            plan.extend((parent / a, parent / b) for a, b, _, _ in rows)
    else:
        if not prefix.strip() or re.search(r'[<>:"/\\|?*\x00-\x1f]', prefix) or prefix.endswith((' ', '.')):
            raise ValueError('请输入有效的文件名前缀。')
        if int(start) < 1 or not 0 <= int(pad) <= 8:
            raise ValueError('起始编号至少为 1，补零位数为 0～8。')
        plan = [(p, p.with_name(prefix + str(i).zfill(int(pad)) + p.suffix.lower())) for i, p in enumerate(files, int(start))]
    targets = [str(b).casefold() for _, b in plan]
    if len(targets) != len(set(targets)):
        raise ValueError('重命名会产生重复文件名，请更换规则。')
    old = {str(a).casefold() for a, _ in plan}
    for a, b in plan:
        if b.exists() and str(b).casefold() not in old:
            raise ValueError('目标名称已被其他文件占用：' + b.name)
    return plan if include_unchanged else [(a, b) for a, b in plan if a != b]


def apply_rename(root, state, plan, log, progress=None):
    root = Path(root).resolve()
    config = root / 'js/data.js'
    count, total_work = len(plan), len(plan) * 3 + 1
    report_progress(progress, '准备批量改名', 0, total_work, '共 %d 个文件' % count)
    sources = {str(a.resolve()).casefold() for a, _ in plan}
    targets = [str(b.resolve()).casefold() for _, b in plan]
    if len(targets) != len(set(targets)):
        raise ValueError('重命名目标重复，请重新预览。')
    for i, (a, b) in enumerate(plan, 1):
        writable(a)
        writable(b)
        if not a.is_file() or (b.exists() and str(b.resolve()).casefold() not in sources):
            raise ValueError('文件状态已变化，请重新生成改名预览。')
        report_progress(progress, '检查文件', i, total_work, '%d/%d 个 · %s' % (i, count, a.name))
    mapping = {a.relative_to(root).as_posix(): b.relative_to(root).as_posix() for a, b in plan if within(a, root)}
    before = config.read_bytes() if mapping and config.is_file() else None
    updated = replace_refs(before.decode('utf-8-sig'), mapping) if before is not None else None
    moves = []
    try:
        for i, (original, target) in enumerate(plan):
            temporary = original.with_name('.ssqy-rename-' + uuid.uuid4().hex + '.tmp')
            original.rename(temporary)
            moves.append([original, temporary, target, False])
            report_progress(progress, '暂时改名', count + i + 1, total_work, '%d/%d 个 · %s' % (i + 1, count, original.name))
        for i, move in enumerate(moves):
            original, temporary, target, _ = move
            temporary.rename(target)
            move[3] = True
            log(original.name + ' → ' + target.name)
            report_progress(progress, '保存新名称', count * 2 + i + 1, total_work, '%d/%d 个 · %s' % (i + 1, count, target.name))
        if before is not None and updated != before.decode('utf-8-sig'):
            if config.read_bytes() != before:
                raise ValueError('改名期间代码发生变化，请重试。')
            atomic(config, updated.encode('utf-8'))
    except Exception:
        # 失败时只移动文件名回原位置，不复制照片，不产生原图缓存。
        for move in moves:
            if move[3]:
                move[2].rename(move[1])
                move[3] = False
        for original, temporary, _, _ in moves:
            if temporary.exists():
                temporary.rename(original)
        raise
    report_progress(progress, '批量改名完成', total_work, total_work, '已改名 %d 个文件' % count)


def compress_folder(source, dest, state, options, log, progress=None):
    source, dest = Path(source).resolve(), writable(dest)
    in_place = source == dest
    if not in_place and (within(dest, source) or within(source, dest)):
        raise ValueError('源目录和输出目录可以完全相同，或互相独立；请不要选择彼此包含的不同目录。')
    files = collect(source, options.get('recursive', True), images_only=True)
    if not files:
        raise ValueError('未发现图片。')
    if in_place:
        total_work = len(files) * 3 + 2
        report_progress(progress, '准备原地压缩', 0, total_work, '共 %d 个文件，处理后保留压缩结果' % len(files))
        root = Path(options['site_root']).resolve() if options.get('site_root') else None
        data_file = root / 'js/data.js' if root and within(source, root / 'assets') else None
        data_snapshot = data_file.read_bytes() if data_file and data_file.is_file() else None
        with Transaction(state, '原地压缩图片（保留压缩结果）') as tx:
            staging = tx.folder / 'staging'
            staging.mkdir()
            tasks = []
            # 先生成所有处理结果，不复制原图备份，避免同名输入互相影响。
            for processed, path in enumerate(files, 1):
                tx.remember(path)
                name, content = image_bytes(path, dict(options, compress=True))
                staged = staging / str(processed)
                atomic(staged, content)
                tasks.append((path, path.with_name(name), staged))
                report_progress(progress, '压缩图片', processed, total_work, '%d/%d 个 · %s' % (processed, len(files), path.name))
            final_paths = {str(target.resolve()).casefold() for _, target, _ in tasks}
            changes = {}
            for processed, (original, target, staged) in enumerate(tasks, 1):
                tx.write(target, staged.read_bytes())
                log('原地压缩 → ' + target.name)
                if original != target and data_snapshot is not None:
                    changes[original.relative_to(root).as_posix()] = target.relative_to(root).as_posix()
                report_progress(progress, '保存压缩结果', len(files) + processed, total_work, '%d/%d 个 · %s' % (processed, len(files), target.name))
            if data_snapshot is not None and changes:
                if data_file.read_bytes() != data_snapshot:
                    raise ValueError('压缩期间 data.js 已被修改，原文件尚未删除，请重新检查。')
                before = data_snapshot.decode('utf-8-sig')
                updated = replace_refs(before, changes)
                if updated != before:
                    Document(updated).albums()
                    tx.write(data_file, updated.encode('utf-8'))
                    log('已同步 data.js 中转换后的图片路径。')
            for processed, (original, target, _) in enumerate(tasks, 1):
                if original != target and str(original.resolve()).casefold() not in final_paths:
                    tx.remove(original)
                    log('已移除转换前文件 → ' + original.name)
                report_progress(progress, '整理原目录', len(files) * 2 + processed, total_work, '%d/%d 个文件' % (processed, len(files)))
            for _, _, staged in tasks:
                staged.unlink()
            staging.rmdir()
            report_progress(progress, '完成原地压缩', total_work - 1, total_work, '目录内仅保留处理后的文件')
        report_progress(progress, '原地压缩完成', total_work, total_work, '已处理 %d 个文件' % len(files))
        return len(files)
    total_work = len(files) * 2 + 1
    report_progress(progress, '准备压缩图片', 0, total_work, '共 %d 个文件' % len(files))
    with Transaction(state, '压缩图片导出') as tx:
        tasks = []
        for processed, p in enumerate(files, 1):
            name, data = image_bytes(p, dict(options, compress=True))
            target = (dest / p.relative_to(source)).with_name(name)
            staged = tx.folder / str(processed)
            atomic(staged, data)
            tasks.append((target, staged))
            report_progress(progress, '压缩图片', processed, total_work, '%d/%d 个 · %s' % (processed, len(files), target.name))
        for processed, (target, staged) in enumerate(tasks, 1):
            overwritten = target.exists()
            tx.write(target, staged.read_bytes())
            log(('覆盖 → ' if overwritten else '导出 → ') + target.name)
            report_progress(progress, '导出图片', len(files) + processed, total_work, '%d/%d 个 · %s' % (processed, len(files), target.name))
        report_progress(progress, '保存输出结果', len(files) * 2, total_work, '已处理 %d/%d 个文件' % (len(files), len(files)))
    report_progress(progress, '图片压缩完成', total_work, total_work, '已导出 %d 个文件' % len(files))
    return len(files)


def make_zip(source, dest, log, progress=None):
    source, dest = Path(source).resolve(), writable(dest)
    if within(dest, source):
        raise ValueError('压缩包请保存到源目录之外，避免把输出打包进去。')
    files = collect(source)
    total_bytes = sum(p.stat().st_size for p in files)
    completed_bytes = 0
    report_progress(progress, '准备 ZIP 打包', 0, total_bytes + 1, '共 %d 个文件' % len(files))
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.ssqy-zip-', suffix='.tmp', dir=str(dest.parent))
    os.close(fd)
    tmp = Path(temporary)
    try:
        with zipfile.ZipFile(str(tmp), 'w', zipfile.ZIP_DEFLATED) as z:
            for processed, p in enumerate(files, 1):
                z.write(str(p), p.relative_to(source).as_posix())
                completed_bytes += p.stat().st_size
                report_progress(progress, '打包文件', min(completed_bytes, total_bytes), total_bytes + 1, '%d/%d 个 · %s' % (processed, len(files), p.name))
        report_progress(progress, '保存压缩包', min(completed_bytes, total_bytes), total_bytes + 1, dest.name)
        os.replace(str(tmp), str(dest))
    finally:
        if tmp.exists():
            tmp.unlink()
    log('ZIP 已保存：' + str(dest))
    report_progress(progress, 'ZIP 打包完成', total_bytes + 1, total_bytes + 1, '已打包 %d 个文件' % len(files))
    return len(files)


def git(root, args, timeout=90):
    env = dict(os.environ, GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='never', GIT_OPTIONAL_LOCKS='0')
    exe = shutil.which('git')
    if not exe:
        for p in ('C:/Program Files/Git/cmd/git.exe', 'C:/Program Files/Git/bin/git.exe'):
            if Path(p).exists():
                exe = p
                break
    if not exe:
        raise ValueError('找不到 Git，请先安装 Git 并完成账号登录。')
    proc = subprocess.run([exe, '-C', str(root)] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          encoding='utf-8', errors='replace', timeout=timeout, env=env,
                          creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    if proc.returncode:
        raise ValueError((proc.stderr or proc.stdout).strip() + '\n操作已停止；未强制覆盖远端。')
    return proc.stdout.strip()


def publish(root, message, log):
    writable(root)
    branch = git(root, ['symbolic-ref', '--short', 'HEAD'])
    url = git(root, ['remote', 'get-url', 'origin'])
    if not re.match(r'^(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)[\w.-]+/[\w.-]+(?:\.git)?$', url):
        raise ValueError('origin 不是有效的 GitHub 仓库地址：' + url)
    if git(root, ['diff', '--cached', '--name-only']):
        raise ValueError('Git 暂存区已有内容，请先处理原有暂存操作，再使用一键上传。')
    if git(root, ['diff', '--name-only', '--diff-filter=U']):
        raise ValueError('仓库存在未解决的合并冲突。')
    # 仅发布网站文件，不把桌面应用、备份、构建产物和账号文件上传。
    allow = ['index.html', 'add-tool.html', 'favicon.svg', 'css', 'js', 'assets']
    tracked = git(root, ['ls-files', '-z', '--'] + allow).split('\0')
    untracked = git(root, ['ls-files', '--others', '--exclude-standard', '-z', '--'] + allow).split('\0')
    paths = sorted(set(p for p in tracked + untracked if p and not any(part.startswith('.') for part in Path(p).parts)))
    for rel in paths:
        p = Path(root) / rel
        if not within(p, root) or p.is_symlink():
            raise ValueError('不能发布链接到网站以外的文件：' + rel)
        if p.exists() and p.stat().st_size > 25 * 1024 * 1024:
            raise ValueError('文件超过工具的 25MB 上传阈值，请先压缩：' + rel)
    for offset in range(0, len(paths), 100):
        git(root, ['add', '--'] + paths[offset:offset + 100])
    if git(root, ['diff', '--cached', '--name-only']):
        log(git(root, ['commit', '-m', message.strip() or '更新网站内容']))
    log('正在上传 ' + branch + ' → ' + url)
    log(git(root, ['push', '-u', 'origin', branch], timeout=180) or 'GitHub 上传成功。')
    return branch

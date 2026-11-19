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
from datetime import datetime

from PIL import Image, ImageOps
if not getattr(sys, 'frozen', False):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import rename_qi

IMAGES = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tif', '.tiff', '.gif', '.svg'}
IGNORE = {'.git', '.workbuddy', '.codex', '.agents', '__pycache__', 'node_modules', '_internal', 'desktop-tool', 'desktop-output'}
PALETTE = {'paper': '#EFE8D6', 'card': '#F6F0E2', 'ink': '#2B2B26', 'teal': '#2C4A52', 'cinnabar': '#A83A32', 'gold': '#A98545'}


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
        self.folder = writable(state) / 'history' / (datetime.now().strftime('%Y%m%d-%H%M%S-') + uuid.uuid4().hex[:8])
        self.folder.mkdir(parents=True)
        self.meta = {'label': label, 'status': 'running', 'files': [], 'created_at': time.time()}
        self.save()

    def save(self):
        atomic(self.folder / 'manifest.json', json.dumps(self.meta, ensure_ascii=False, indent=2).encode('utf-8'))

    def remember(self, path):
        p = writable(path)
        if any(x['path'] == str(p) for x in self.meta['files']):
            return
        item = {'path': str(p), 'before': digest(p), 'backup': None}
        if p.exists():
            item['backup'] = str(len(self.meta['files'])) + '.bak'
            shutil.copy2(str(p), str(self.folder / item['backup']))
        self.meta['files'].append(item)
        self.save()

    def write(self, path, data):
        self.remember(path)
        atomic(path, data)

    def remove(self, path):
        self.remember(path)
        Path(path).unlink()

    def __enter__(self):
        return self

    def __exit__(self, typ, value, tb):
        if typ:
            for item in reversed(self.meta['files']):
                p = Path(item['path'])
                if item['backup']:
                    atomic(p, (self.folder / item['backup']).read_bytes())
                elif p.exists():
                    p.unlink()
            self.meta['status'] = 'failed-rolled-back'
        else:
            for item in self.meta['files']:
                item['after'] = digest(Path(item['path']))
            self.meta['status'] = 'complete'
        self.meta['finished_at'] = time.time()
        self.save()
        return False


def cleanup_history(state, now=None, retention_seconds=24 * 3600):
    """只删除本工具 history 中超过保留期的已完成事务，不访问 manifest 的原图路径。"""
    state = Path(state).absolute()
    now = time.time() if now is None else now
    result = {'removed': 0, 'freed_bytes': 0}
    reparse = getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)
    def linked(path):
        return path.is_symlink() or bool(getattr(path.lstat(), 'st_file_attributes', 0) & reparse)
    if not state.exists() or linked(state):
        return result
    history = writable(state) / 'history'
    if not history.exists() or linked(history):
        return result
    for folder in history.iterdir():
        if not re.fullmatch(r'\d{8}-\d{6}-[a-f0-9]{8}', folder.name) or not folder.is_dir() or linked(folder) or not within(folder, history):
            continue
        manifest = folder / 'manifest.json'
        try:
            if linked(manifest):
                continue
            meta = json.loads(manifest.read_text(encoding='utf-8'))
            if meta.get('status') not in ('complete', 'undone') or not isinstance(meta.get('files'), list):
                continue
            finished = float(meta.get('finished_at', manifest.stat().st_mtime))
            if not math.isfinite(finished) or now - finished < retention_seconds:
                continue
            size, safe = 0, True
            for base, dirs, names in os.walk(str(folder), followlinks=False):
                for name in dirs + names:
                    p = Path(base) / name
                    if linked(p) or not within(p, folder):
                        safe = False
                        break
                    if p.is_file():
                        size += p.stat().st_size
                if not safe:
                    break
            if not safe:
                continue
            def readonly_retry(func, path, error):
                if not within(path, folder):
                    raise ValueError('备份清理路径超出历史目录。')
                os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
                func(path)
            # 递归删除前再次确认最终绝对路径仍然属于当前 history。
            if not within(folder.resolve(), history.resolve()) or linked(folder):
                continue
            shutil.rmtree(str(folder), onerror=readonly_retry)
            result['removed'] += 1
            result['freed_bytes'] += size
        except (OSError, ValueError, TypeError):
            continue
    return result


def push_script_resource():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS) / 'resources/push.bat'
    return Path(__file__).resolve().parent.parent / 'push.bat'


def clear_cache(state):
    """仅清理程序自己的临时目录；不扫描网站、原图、设置或未到期备份。"""
    state = Path(state).absolute()
    result = {'files': 0, 'freed_bytes': 0, 'skipped': 0, 'expired_backups': 0}
    reparse = getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)
    def linked(path):
        return path.is_symlink() or bool(getattr(path.lstat(), 'st_file_attributes', 0) & reparse)
    if not state.exists() or linked(state):
        return result
    state = writable(state)
    for name in ('temp', 'preview-cache'):
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
    expired = cleanup_history(state)
    result['expired_backups'] = expired['removed']
    result['freed_bytes'] += expired['freed_bytes']
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


def undo(state):
    for folder in sorted((Path(state) / 'history').glob('*'), reverse=True):
        f = folder / 'manifest.json'
        meta = json.loads(f.read_text(encoding='utf-8'))
        if meta['status'] != 'complete' or not meta['files']:
            continue
        for item in meta['files']:
            if digest(Path(item['path'])) != item['after']:
                raise ValueError('操作后文件已被修改，不能直接撤销：' + item['path'])
        for item in reversed(meta['files']):
            p = writable(item['path'])
            if item['backup']:
                atomic(p, (folder / item['backup']).read_bytes())
            elif p.exists():
                p.unlink()
        meta['status'] = 'undone'
        atomic(f, json.dumps(meta, ensure_ascii=False, indent=2).encode('utf-8'))
        return meta['label']
    raise ValueError('没有可以撤销的文件操作。')


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


def import_jobs(root, state, jobs, options, log):
    root = writable(root)
    config = root / 'js/data.js'
    text = config.read_text(encoding='utf-8-sig')
    tasks, occupied = [], set()
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
                        raise ValueError('同名文件内容不同，请启用“备份后覆盖”或改名：' + str(target))
                    log('已存在相同文件，保留：' + target.name)
                staged = staging / str(len(tasks))
                atomic(staged, data)
                tasks.append((target, staged, job.get('album', ''), source.stem))
        grouped = {}
        for target, staged, album, title in tasks:
            tx.write(target, staged.read_bytes())
            log('已保存照片或文件 → ' + target.relative_to(root).as_posix())
            if album and target.suffix.lower() in IMAGES:
                grouped.setdefault(album, []).append({'src': target.relative_to(root).as_posix(), 'title': title})
        for title, entries in grouped.items():
            entries.sort(key=lambda entry: photo_sort_key(entry['src']))
            text = sync_album(text, title, entries)
        Document(text).albums()
        if text != config.read_text(encoding='utf-8-sig'):
            tx.write(config, text.encode('utf-8'))
        # 暂存件已写回，历史记录只保留撤销所需的原文件。
        for p in staging.iterdir():
            p.unlink()
        staging.rmdir()
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


def apply_rename(root, state, plan, log):
    root = Path(root).resolve()
    config = root / 'js/data.js'
    sources = {str(a.resolve()).casefold() for a, _ in plan}
    targets = [str(b.resolve()).casefold() for _, b in plan]
    if len(targets) != len(set(targets)):
        raise ValueError('重命名目标重复，请重新预览。')
    for a, b in plan:
        writable(a)
        writable(b)
        if not a.is_file():
            raise ValueError('源文件不存在，请重新预览：' + str(a))
        if b.exists() and str(b.resolve()).casefold() not in sources:
            raise ValueError('目标已被其他文件占用，请重新预览：' + str(b))
    with Transaction(state, '批量重命名') as tx:
        for a, b in plan:
            tx.remember(a)
            tx.remember(b)
        # 先写入独立暂存目录，再写回正式名称，支持互换文件名。
        staging = tx.folder / 'staging'
        staging.mkdir()
        for i, (a, _) in enumerate(plan):
            shutil.copy2(str(a), str(staging / str(i)))
        for a, _ in plan:
            a.unlink()
        for i, (a, b) in enumerate(plan):
            atomic(b, (staging / str(i)).read_bytes())
            log(a.name + ' → ' + b.name)
        for p in staging.iterdir():
            p.unlink()
        staging.rmdir()
        mapping = {a.relative_to(root).as_posix(): b.relative_to(root).as_posix() for a, b in plan if within(a, root)}
        if mapping:
            text = config.read_text(encoding='utf-8-sig')
            new = replace_refs(text, mapping)
            if new != text:
                tx.write(config, new.encode('utf-8'))
        output = io.StringIO(newline='')
        writer = csv.writer(output)
        writer.writerow(['原路径', '新路径'])
        writer.writerows((str(a), str(b)) for a, b in plan)
        atomic(tx.folder / '重命名对照表.csv', output.getvalue().encode('utf-8-sig'))


def compress_folder(source, dest, state, options, log):
    source, dest = Path(source).resolve(), writable(dest)
    if within(dest, source) or within(source, dest):
        raise ValueError('输出目录与源目录应互相独立，原图会保留。')
    files = collect(source, options.get('recursive', True), images_only=True)
    if not files:
        raise ValueError('未发现图片。')
    occupied = set()
    with Transaction(state, '压缩图片导出') as tx:
        for p in files:
            name, data = image_bytes(p, dict(options, compress=True))
            target = (dest / p.relative_to(source)).with_name(name)
            key = str(target).casefold()
            if key in occupied or target.exists():
                raise ValueError('输出文件重名，请选择空目录或调整命名：' + str(target))
            occupied.add(key)
            tx.write(target, data)
            log('导出 → ' + target.name)
    return len(files)


def make_zip(source, dest, log):
    source, dest = Path(source).resolve(), writable(dest)
    if dest.exists():
        raise ValueError('压缩包已存在，请选择新文件名。')
    if within(dest, source):
        raise ValueError('压缩包请保存到源目录之外，避免把输出打包进去。')
    files = collect(source)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name('.' + dest.name + '.tmp')
    try:
        with zipfile.ZipFile(str(tmp), 'w', zipfile.ZIP_DEFLATED) as z:
            for p in files:
                z.write(str(p), p.relative_to(source).as_posix())
        os.replace(str(tmp), str(dest))
    finally:
        if tmp.exists():
            tmp.unlink()
    log('ZIP 已保存：' + str(dest))
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

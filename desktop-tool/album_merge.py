"""相册合并：只读预览、快照校验、暂存后覆盖并更新引用。"""
import hashlib
import re
import shutil
from pathlib import Path
from urllib.parse import unquote, urlsplit

import core


def _local(root, reference):
    parsed = urlsplit(reference.replace('\\', '/'))
    if parsed.scheme in ('http', 'https') or parsed.netloc:
        return None
    if parsed.scheme or parsed.query or parsed.fragment:
        raise ValueError('请先处理不支持的图片地址：' + reference)
    relative = Path(unquote(parsed.path))
    result = (root / relative).resolve()
    if relative.is_absolute() or not core.within(result, root / 'assets') or not core.within(result, root):
        raise ValueError('照片路径必须位于网站 assets 内：' + reference)
    return result


def _remove_album(text, name):
    doc = core.Document(text)
    obj = core.album_by_name(doc, name)['object']
    end = doc.pairs[obj]
    start_pos, end_pos = doc.tokens[obj][1], doc.tokens[end][2]
    if doc.tokens[end + 1][0] == ',':
        end_pos = doc.tokens[end + 1][2]
    elif doc.tokens[obj - 1][0] == ',':
        start_pos = doc.tokens[obj - 1][1]
    return text[:start_pos] + text[end_pos:]


def _shortcut_refs(text, albums, sources, mother):
    doc = core.Document(text)
    edits = []
    for i, token in enumerate(doc.tokens[:-2]):
        if token[0].strip('"\'') != 'openAlbum' or doc.tokens[i + 1][0] != ':':
            continue
        value = doc.string(i + 2).strip()
        resolved = next((a['name'] for a in albums if a['name'] == value), None)
        resolved = resolved or next((a['name'] for a in albums if value and value in a['name']), None)
        if resolved in sources:
            edits.append((doc.tokens[i + 2][1], doc.tokens[i + 2][2], core.q(mother)))
    for start, end, value in reversed(edits):
        text = text[:start] + value + text[end:]
    return text


def plan_merge(root, mother, sources, folder, progress=None):
    root = Path(root).resolve()
    sources = list(dict.fromkeys(sources))
    if not sources or mother in sources:
        raise ValueError('请选择至少一本并入相册，母相册不能同时被并入。')
    target_dir = (root / folder).resolve()
    if not folder.strip() or not core.within(target_dir, root / 'assets') or not core.within(target_dir, root):
        raise ValueError('请选择网站 assets 内的母文件夹。')
    if target_dir.exists() and not target_dir.is_dir():
        raise ValueError('母文件夹路径不是文件夹。')
    config = root / 'js/data.js'
    raw = config.read_bytes()
    text = raw.decode('utf-8-sig')
    doc = core.Document(text)
    albums = doc.albums()
    selected = [core.album_by_name(doc, name) for name in [mother] + sources]
    tags, merged, mapping, copies, originals, collisions = [], {}, {}, {}, set(), []
    checks = {str(config): hashlib.sha256(raw).hexdigest()}
    desc_path = root / 'js/album-desc.js'
    checks[str(desc_path)] = core.digest(desc_path)
    total = sum(len(a['refs']) for a in selected)
    target_names = {p.name.casefold(): p.name for p in target_dir.iterdir() if p.is_file()} if target_dir.exists() else {}
    done = 0
    for album in selected:
        for tag in doc.value(doc.prop(album['object'], 'tags')) or []:
            if tag not in tags:
                tags.append(tag)
        if album['array'] is None:
            continue
        for obj in doc.objects(album['array']):
            src = doc.string(doc.prop(obj, 'src'))
            if not src:
                raise ValueError('照片缺少 src，请先检查相册：' + album['name'])
            local = _local(root, src)
            target_ref = src
            if local is not None:
                if not local.is_file():
                    raise ValueError('照片不存在，请先检查图片与代码：' + src)
                canonical = target_names.setdefault(local.name.casefold(), local.name)
                target = target_dir / canonical
                if not core.within(target.resolve(), root / 'assets') or not core.within(target.resolve(), root):
                    raise ValueError('目标照片路径超出 assets：' + str(target))
                target_ref = target.relative_to(root).as_posix()
                originals.add(str(local))
                checks[str(local)] = core.digest(local)
                checks[str(target)] = core.digest(target)
                key = str(target).casefold()
                if key in copies and copies[key]['source'] != str(local):
                    collisions.append(target_ref)
                elif target.exists() and target.resolve() != local:
                    collisions.append(target_ref)
                copies[key] = {'source': str(local), 'target': str(target)}
                mapping[src] = target_ref
            raw_obj = text[doc.tokens[obj][1]:doc.tokens[doc.pairs[obj]][2]]
            merged[target_ref.casefold()] = raw_obj
            done += 1
            core.report_progress(progress, '预览相册合并', done, total, album['name'])
    # 每个目标只保留最后并入的照片条目；母相册的其他字段不重建。
    updated = _shortcut_refs(text, albums, set(sources), mother)
    for source in sources:
        updated = _remove_album(updated, source)
    current = core.Document(updated)
    parent = core.album_by_name(current, mother)
    array = parent['array']
    if array is None:
        raise ValueError('母相册缺少 photos 数组。')
    start, end = current.tokens[array][1], current.tokens[current.pairs[array]][2]
    updated = updated[:start] + '[\n' + ',\n'.join(merged.values()) + '\n]' + updated[end:]
    updated = core.replace_refs(updated, mapping)
    updated = core.set_album_property(updated, mother, 'tags', tags)
    updated = core.sort_album_photos(updated, mother)
    core.Document(updated).albums()
    description = None
    if desc_path.exists():
        description = desc_path.read_text(encoding='utf-8-sig')
        match, _, _ = core.description_sections(description)
        body = match.group(1)[1:-1]
        headings = list(re.finditer(r'^\s*#{1,3}[^\S\n]*(.+?)[^\S\n]*$', body, re.M))
        fold = lambda value: re.sub(r'\s+', '', value)
        source_keys = {fold(name) for name in sources}
        for i in range(len(headings) - 1, -1, -1):
            heading = headings[i]
            if fold(heading.group(1)) in source_keys:
                end = headings[i + 1].start() if i + 1 < len(headings) else len(body)
                body = body[:heading.start()] + body[end:]
        description = description[:match.start(1)] + '`' + body + '`' + description[match.end(1):]
    return {'root': str(root), 'mother': mother, 'sources': sources,
            'folder': target_dir.relative_to(root).as_posix(), 'tags': tags,
            'photos': len(merged), 'overwrites': sorted(set(collisions)),
            'files': list(copies.values()), 'originals': sorted(originals),
            'checks': checks, 'data': updated, 'description': description}


def apply_merge(root, state, plan, progress=None):
    root = core.writable(root)
    if str(root) != plan['root']:
        raise ValueError('网站目录已切换，请重新生成合并预览。')
    config = root / 'js/data.js'
    desc = root / 'js/album-desc.js'
    for name, expected in plan['checks'].items():
        path = Path(name)
        if path not in (config, desc) and (not core.within(path, root / 'assets') or not core.within(path, root)):
            raise ValueError('合并路径超出网站 assets。')
        if core.digest(path) != expected:
            raise ValueError('照片或网站代码已变化，请重新生成合并预览。')
    destinations = {str(Path(item['target']).resolve()).casefold() for item in plan['files']}
    removals = [Path(name) for name in plan['originals'] if str(Path(name).resolve()).casefold() not in destinations]
    writes = [Path(item['target']) for item in plan['files']] + [config]
    if plan['description'] is not None:
        writes.append(desc)
    for path in writes + removals:
        core.writable(path)
        if path not in (config, desc) and (not core.within(path, root / 'assets') or not core.within(path, root)):
            raise ValueError('合并目标超出网站 assets。')
    with core.Transaction(state, '合并相册：' + plan['mother']) as tx:
        stage, snapshots, touched = [], {}, []
        for i, item in enumerate(plan['files']):
            staged = tx.folder / ('photo-%d' % i)
            shutil.copyfile(item['source'], staged)
            if core.digest(staged) != plan['checks'][item['source']]:
                raise ValueError('照片已变化，请重新生成合并预览。')
            stage.append((Path(item['target']), staged))
        # 暂存原内容仅用于本次失败恢复，成功后随临时目录清理。
        for i, path in enumerate(dict.fromkeys(writes + removals)):
            snapshot = tx.folder / ('original-%d' % i) if path.exists() else None
            if snapshot is not None:
                shutil.copyfile(path, snapshot)
            snapshots[path] = snapshot
        for name, expected in plan['checks'].items():
            if core.digest(Path(name)) != expected:
                raise ValueError('照片或网站代码已变化，请重新生成合并预览。')
        try:
            for i, (target, staged) in enumerate(stage, 1):
                touched.append(target)
                tx.write(target, staged.read_bytes())
                core.report_progress(progress, '合并照片文件', i, len(stage) + 1, target.name)
            touched.append(config)
            tx.write(config, plan['data'].encode('utf-8'))
            if plan['description'] is not None:
                touched.append(desc)
                tx.write(desc, plan['description'].encode('utf-8'))
            for path in removals:
                touched.append(path)
                tx.remove(path)
        except Exception:
            for path in reversed(list(dict.fromkeys(touched))):
                original = snapshots[path]
                if original is None:
                    if path.exists():
                        path.unlink()
                else:
                    core.atomic(path, original.read_bytes())
            raise
    core.report_progress(progress, '相册合并完成', 1, 1, plan['mother'])
    return plan['mother']

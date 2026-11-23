"""荔荔精选编辑与照片替换。"""
import hashlib
import json
from pathlib import Path
import re

from PIL import Image
import core


def read(root):
    root = Path(root)
    config = root / 'js/journey-config.js'
    data = {}
    if config.exists():
        text = config.read_text(encoding='utf-8-sig')
        match = re.search(r'window\.JOURNEY_CONFIG\s*=\s*', text)
        if not match:
            raise ValueError('无法识别精选配置，请保留 window.JOURNEY_CONFIG 格式。')
        data, end = json.JSONDecoder().raw_decode(text[match.end():])
        if text[match.end() + end:].strip() not in ('', ';') or not isinstance(data, dict):
            raise ValueError('精选配置需要使用标准 JSON 对象。')
    return {'config': data, 'recent': data.get('recent', {}),
            'expected': {name: core.digest(root / name) for name in ('js/journey-config.js', 'js/data.js', 'index.html')}}


def save(root, state, values, expected, source=None):
    root = core.writable(root)
    for name, fingerprint in expected.items():
        if core.digest(root / name) != fingerprint:
            raise ValueError('网站内容已变化，请重新读取精选后保存。')
    config = read(root)['config']
    doc = core.Document((root / 'js/data.js').read_text(encoding='utf-8-sig'))
    core.album_by_name(doc, values['album'])
    if not values.get('title', '').strip():
        raise ValueError('请输入精选照片标题。')
    relative = values.get('src', '').replace('\\', '/')
    target = (root / relative).resolve()
    if not relative.startswith('assets/') or not core.within(target, root / 'assets') or not core.within(target, root):
        raise ValueError('精选照片需要放在网站 assets 内。')
    image = Path(source) if source else target
    if not image.is_file():
        raise ValueError('请选择存在的精选照片。')
    with Image.open(str(image)) as photo:
        photo.verify()
    image_bytes = image.read_bytes() if source else None
    config['recent'] = {key: values.get(key, '').strip() for key in ('album', 'src', 'title', 'note')}
    config['recent']['src'] = relative
    output = '// 荔荔精选由桌面管家编辑。\nwindow.JOURNEY_CONFIG = ' + json.dumps(config, ensure_ascii=False, indent=2) + ';\n'
    index = root / 'index.html'
    html = index.read_text(encoding='utf-8-sig')
    version = hashlib.sha256(output.encode('utf-8')).hexdigest()[:12]
    html = re.sub(r'(src=["\']js/journey-config\.js)(?:\?[^"\']*)?(["\'])', lambda m: m[1] + '?v=' + version + m[2], html)
    old_image = target.read_bytes() if image_bytes is not None and target.exists() else None
    config_path = root / 'js/journey-config.js'
    original_config = config_path.read_bytes() if config_path.exists() else None
    original_index = index.read_bytes()
    with core.Transaction(state, '替换荔荔精选') as tx:
        try:
            if image_bytes is not None:
                tx.write(target, image_bytes)
            tx.write(root / 'js/journey-config.js', output.encode('utf-8'))
            tx.write(index, html.encode('utf-8'))
        except Exception:
            if original_config is None:
                if config_path.exists():
                    config_path.unlink()
            else:
                core.atomic(config_path, original_config)
            core.atomic(index, original_index)
            if image_bytes is not None:
                if old_image is None:
                    if target.exists():
                        target.unlink()
                else:
                    core.atomic(target, old_image)
            raise
    return config['recent']['title']


def map_places(root):
    root = Path(root)
    doc = core.Document((root / 'js/data.js').read_text(encoding='utf-8-sig'))
    source = root / 'js/main.js'
    text = source.read_text(encoding='utf-8-sig') if source.exists() else ''
    match = re.search(r'const CITY_PROVINCE\s*=\s*\{([\s\S]*?)\};', text)
    provinces = dict(re.findall(r'"([^"]+)"\s*:\s*"([^"]+)"', match[1])) if match else {}
    places = []
    for entry in doc.value(doc.prop(doc.root, 'cities')) or []:
        city, _, province = entry.partition('@')
        province = province or provinces.get(city, '')
        places.append({'city': city, 'province': province})
    return places


def read_map_city(root, city):
    data = read(root)
    config = data['config']
    doc = core.Document((Path(root) / 'js/data.js').read_text(encoding='utf-8-sig'))
    if city in config.get('cityAlbums', {}):
        albums = config['cityAlbums'][city]
    else:
        albums = []
        for album in doc.albums():
            titles = [doc.string(doc.prop(obj, 'title')) for obj in doc.objects(album['array'])] if album['array'] is not None else []
            if city in album['name'] or any(city in title for title in titles):
                albums.append(album['name'])
    return {'albums': albums, 'match': config.get('cityPhotoMatch', {}).get(city, 'auto'),
            'photos': config.get('cityPhotos', {}).get(city, []),
            'slots': config.get('cityPhotoSlots', {}).get(city, []), 'expected': data['expected']}


def map_photo_options(root, albums, city='', match='auto'):
    doc = core.Document((Path(root) / 'js/data.js').read_text(encoding='utf-8-sig'))
    options, seen = [], set()
    for name in albums:
        album = core.album_by_name(doc, name)
        if album['array'] is None:
            continue
        for obj in doc.objects(album['array']):
            src = doc.string(doc.prop(obj, 'src'))
            title = doc.string(doc.prop(obj, 'title')) or Path(src).stem
            if src and src not in seen and (match != 'title' or city in title):
                options.append({'src': src, 'title': title, 'album': name})
                seen.add(src)
    return options


def save_map_city(root, state, city, albums, match, expected, photos=None, slots=None):
    root = core.writable(root)
    for name, fingerprint in expected.items():
        if core.digest(root / name) != fingerprint:
            raise ValueError('网站内容已变化，请重新读取地图配置。')
    if city not in [place['city'] for place in map_places(root)]:
        raise ValueError('请选择网站城市列表中的城市。')
    doc = core.Document((root / 'js/data.js').read_text(encoding='utf-8-sig'))
    for name in albums:
        core.album_by_name(doc, name)
    config = read(root)['config']
    config.setdefault('cityAlbums', {})[city] = list(dict.fromkeys(albums))
    config.setdefault('cityPhotoMatch', {})[city] = 'title' if match == 'title' else 'auto'
    if photos is not None:
        if len(set(photos)) > 9:
            raise ValueError('每个城市最多勾选 9 张照片。')
        available = {item['src'] for item in map_photo_options(root, albums, city, match)}
        if any(photo not in available for photo in photos):
            raise ValueError('指定照片不在已选相册中，请重新选择。')
        config.setdefault('cityPhotos', {})[city] = list(dict.fromkeys(photos))
    if slots is not None:
        available = {item['src'] for item in map_photo_options(root, albums, city, match)}
        chosen = [photo for photo in slots if photo]
        if city not in ('北京', '天津', '上海', '重庆') or len(slots) != 9 or len(set(chosen)) != len(chosen) or any(photo not in available for photo in chosen):
            raise ValueError('直辖市需要 9 个位置，指定照片不能重复或超出已选相册。')
        config.setdefault('cityPhotoSlots', {})[city] = slots
    output = '// 地图与荔荔精选由桌面管家编辑。\nwindow.JOURNEY_CONFIG = ' + json.dumps(config, ensure_ascii=False, indent=2) + ';\n'
    file = root / 'js/journey-config.js'
    index = root / 'index.html'
    before = file.read_bytes() if file.exists() else None
    old_html = index.read_bytes()
    version = hashlib.sha256(output.encode('utf-8')).hexdigest()[:12]
    html = re.sub(r'(src=["\']js/journey-config\.js)(?:\?[^"\']*)?(["\'])', lambda m: m[1] + '?v=' + version + m[2], old_html.decode('utf-8-sig'))
    with core.Transaction(state, '编辑地图城市照片') as tx:
        try:
            tx.write(file, output.encode('utf-8'))
            tx.write(index, html.encode('utf-8'))
        except Exception:
            if before is None:
                if file.exists():
                    file.unlink()
            else:
                core.atomic(file, before)
            core.atomic(index, old_html)
            raise
    return city


def delete_map_city(root, state, city, expected):
    root = core.writable(root)
    for name, fingerprint in expected.items():
        if core.digest(root / name) != fingerprint:
            raise ValueError('网站内容已变化，请重新读取地点后再删除。')
    data_path = root / 'js/data.js'
    text = data_path.read_text(encoding='utf-8-sig')
    removed = 0
    while True:
        doc = core.Document(text)
        array = doc.prop(doc.root, 'cities')
        if array is None:
            break
        item = next((i for i in range(array + 1, doc.pairs[array])
                     if doc.tokens[i][0].startswith(('"', "'")) and doc.string(i).split('@', 1)[0].strip() == city), None)
        if item is None:
            break
        start, end = doc.tokens[item][1], doc.tokens[item][2]
        if doc.tokens[item + 1][0] == ',':
            end = doc.tokens[item + 1][2]
        elif doc.tokens[item - 1][0] == ',':
            start = doc.tokens[item - 1][1]
        text = text[:start] + text[end:]
        removed += 1
    if not removed:
        raise ValueError('该地点已不存在，请重新读取。')
    config = read(root)['config']
    for key in ('cityAlbums', 'cityPhotos', 'cityPhotoMatch', 'cityPhotoSlots'):
        config.get(key, {}).pop(city, None)
    output = '// 地图与荔荔精选由桌面管家编辑。\nwindow.JOURNEY_CONFIG = ' + json.dumps(config, ensure_ascii=False, indent=2) + ';\n'
    config_path, index = root / 'js/journey-config.js', root / 'index.html'
    html = index.read_text(encoding='utf-8-sig')
    for script, content in [('data', text), ('journey-config', output)]:
        version = hashlib.sha256(content.encode('utf-8')).hexdigest()[:12]
        html = re.sub(r'(src=["\']js/' + script + r'\.js)(?:\?[^"\']*)?(["\'])', lambda m: m[1] + '?v=' + version + m[2], html)
    writes = {data_path: text, config_path: output, index: html}
    before = {path: path.read_bytes() if path.exists() else None for path in writes}
    with core.Transaction(state, '删除地图地点：' + city) as tx:
        try:
            for path, content in writes.items():
                tx.write(path, content.encode('utf-8'))
        except Exception:
            for path, original in before.items():
                if original is None:
                    if path.exists():
                        path.unlink()
                else:
                    core.atomic(path, original)
            raise
    return city

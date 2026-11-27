"""网页视频转码与零碎日月配置；源文件始终只读。"""
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

import core

MAX_BYTES = 25_000_000
CONFIG = 'js/video-config.js'


def find_ffmpeg(base=None):
    base = Path(base or (Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent))
    candidates = [base / '_data/tools/ffmpeg.exe']
    if getattr(sys, 'frozen', False):
        candidates.append(Path(sys._MEIPASS) / 'resources/ffmpeg.exe')
    if shutil.which('ffmpeg'):
        candidates.append(Path(shutil.which('ffmpeg')))
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate.resolve())
    raise ValueError('缺少视频编码器，请保留程序的 _internal 文件夹，或将 ffmpeg.exe 放入程序旁 _data/tools。')


def process_options(work):
    return {'creationflags': getattr(subprocess, 'CREATE_NO_WINDOW', 0),
            'env': dict(os.environ, TEMP=str(work), TMP=str(work))}


def probe(source, ffmpeg, work):
    result = subprocess.run([ffmpeg, '-hide_banner', '-i', str(source)], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, **process_options(work))
    info = result.stderr.decode('utf-8', errors='replace')
    duration = re.search(r'Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)', info)
    video = re.search(r'Stream[^\r\n]*Video:\s*([^\r\n]+)', info)
    if not duration or not video:
        raise ValueError('无法读取视频信息，请确认文件包含可解码的视频画面。')
    h, m, s = map(float, duration.groups())
    seconds = h * 3600 + m * 60 + s
    dimensions = re.search(r'(?<!\d)(\d{2,5})x(\d{2,5})(?!\d)', video[1])
    if seconds <= 0 or not math.isfinite(seconds) or not dimensions:
        raise ValueError('视频时长或画面尺寸无效。')
    audio = re.search(r'Stream[^\r\n]*Audio:\s*([^\r\n]+)', info)
    return {'duration': seconds, 'width': int(dimensions[1]), 'height': int(dimensions[2]),
            'codec': video[1].split(',')[0].split()[0], 'video': video[1],
            'audio': audio[1].split(',')[0].split()[0] if audio else ''}


def encode(ffmpeg, arguments, work, duration, progress, stage, start, span):
    log = Path(work) / 'ffmpeg-error.log'
    with log.open('wb') as errors:
        command = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-nostdin',
                   '-progress', 'pipe:1', '-nostats'] + list(map(str, arguments))
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=errors, **process_options(work))
        try:
            for line in iter(process.stdout.readline, b''):
                if line.startswith(b'out_time_ms='):
                    try:
                        fraction = max(0, min(1, int(line.split(b'=')[1]) / 1_000_000 / duration))
                        core.report_progress(progress, stage, start + span * fraction, 100, 'H.264 / AAC MP4')
                    except ValueError:
                        pass
            code = process.wait()
        finally:
            process.stdout.close()
            if process.poll() is None:
                process.kill()
                process.wait()
    if code:
        raise ValueError('视频处理失败：' + log.read_text(encoding='utf-8', errors='replace')[-1800:])


def compress(source, destination, state, ffmpeg=None, progress=None, max_bytes=MAX_BYTES):
    source, destination = Path(source).resolve(), core.writable(destination).resolve()
    if not source.is_file():
        raise ValueError('请选择存在的视频文件。')
    if destination == source or destination.exists():
        raise ValueError('输出文件已存在或与原视频相同，请更换名字；已有文件不会被覆盖。')
    if destination.suffix.lower() != '.mp4' or max_bytes < 32768:
        raise ValueError('输出需为 MP4，目标体积需至少 32KB。')
    ffmpeg = ffmpeg or find_ffmpeg()
    scratch = core.writable(Path(state) / 'temp')
    scratch.mkdir(parents=True, exist_ok=True)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='video-', dir=str(scratch)) as temporary:
        work = Path(temporary)
        info = probe(source, ffmpeg, work)
        output = work / 'web.mp4'
        mapping = ['-i', source, '-map', '0:v:0', '-map', '0:a:0?', '-map_metadata', '-1']
        browser_ready = (info['codec'] == 'h264' and re.search(r'\byuv420p\b', info['video'])
                         and info['audio'] in ('', 'aac'))
        if browser_ready and source.stat().st_size < max_bytes:
            encode(ffmpeg, mapping + ['-c', 'copy', '-movflags', '+faststart', output], work,
                   info['duration'], progress, '保留原画质并优化网页播放', 0, 35)
        else:
            encode(ffmpeg, mapping + ['-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
                   '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2', '-pix_fmt', 'yuv420p',
                   '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', output], work,
                   info['duration'], progress, '优先保留画质', 0, 35)
        # 仅在超限时按时长计算预算，使用两遍编码把码率留给复杂画面。
        if output.stat().st_size >= max_bytes:
            audio_rate = 96 if info['audio'] else 0
            target = int(max_bytes * .94)
            for attempt in range(3):
                video_rate = math.floor(target * 8 / info['duration'] / 1000 - audio_rate)
                if video_rate < 16:
                    raise ValueError('视频过长，25MB 内已无法保留可用画质；请先缩短或拆分视频。')
                base = ['-i', source, '-map', '0:v:0', '-c:v', 'libx264', '-preset', 'medium',
                        '-b:v', str(video_rate) + 'k', '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',
                        '-pix_fmt', 'yuv420p', '-passlogfile', work / ('pass-' + str(attempt))]
                encode(ffmpeg, base + ['-pass', '1', '-an', '-f', 'null', '-'], work,
                       info['duration'], progress, '分析画面复杂度 · 第一次编码', 35, 25)
                audio = ['-map', '0:a:0?', '-c:a', 'aac', '-b:a', str(audio_rate) + 'k'] if audio_rate else ['-an']
                encode(ffmpeg, base + ['-pass', '2'] + audio + ['-map_metadata', '-1', '-movflags', '+faststart', output],
                       work, info['duration'], progress, '控制成品体积 · 第二次编码', 60, 34)
                if output.stat().st_size < max_bytes:
                    break
                target = int(target * min(.88, max_bytes / output.stat().st_size * .92))
        if output.stat().st_size >= max_bytes:
            raise ValueError('编码后仍超过体积上限，没有保存超限成品；请缩短视频后重试。')
        verified = probe(output, ffmpeg, work)
        if verified['codec'] != 'h264' or not re.search(r'\byuv420p\b', verified['video']):
            raise ValueError('成品未通过网页视频编码检查。')
        os.rename(str(output), str(destination))
        core.report_progress(progress, '视频处理完成', 100, 100, destination.name)
        return {'path': str(destination), 'size': destination.stat().st_size, 'source_size': source.stat().st_size,
                'duration': verified['duration'], 'width': verified['width'], 'height': verified['height']}


def poster(source, destination, state, ffmpeg=None):
    ffmpeg = ffmpeg or find_ffmpeg()
    destination = core.writable(destination)
    scratch = core.writable(Path(state) / 'temp')
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='poster-', dir=str(scratch)) as temporary:
        output = Path(temporary) / 'poster.jpg'
        encode(ffmpeg, ['-ss', '0.1', '-i', source, '-frames:v', '1', '-vf', 'scale=640:-2', '-q:v', '3', output],
               temporary, 1, None, '', 0, 1)
        core.atomic(destination, output.read_bytes())


def read_catalog(root):
    file = Path(root) / CONFIG
    data = {'videos': []}
    if file.exists():
        content = file.read_text(encoding='utf-8-sig')
        match = re.search(r'window\.VIDEO_CONFIG\s*=\s*', content)
        if not match:
            raise ValueError('无法识别 js/video-config.js。')
        data, end = json.JSONDecoder().raw_decode(content[match.end():])
        if content[match.end() + end:].strip() not in ('', ';') or not isinstance(data, dict) or not isinstance(data.get('videos', []), list):
            raise ValueError('视频配置需要使用标准 JSON 对象和 videos 数组。')
    return {'config': data, 'expected': core.digest(file)}


def save_catalog(root, catalog, videos):
    root = core.writable(root)
    file = root / CONFIG
    if core.digest(file) != catalog['expected']:
        raise ValueError('视频列表已被其他操作修改，请重新读取后再保存。')
    for item in videos:
        if not str(item.get('title', '')).strip():
            raise ValueError('每段视频都需要填写名字。')
        target = (root / item.get('src', '')).resolve()
        if not core.within(target, root / 'assets') or not target.is_file() or target.stat().st_size >= MAX_BYTES:
            raise ValueError('视频需要位于当前网站 assets 内且小于 25MB。')
    data = dict(catalog['config'], videos=videos)
    output = '// 零碎日月由桌面管家编辑。\nwindow.VIDEO_CONFIG = ' + json.dumps(data, ensure_ascii=False, indent=2) + ';\n'
    html_file = root / 'index.html'
    original_html = html_file.read_bytes()
    original_config = file.read_bytes() if file.exists() else None
    version = hashlib.sha256(output.encode('utf-8')).hexdigest()[:12]
    html = re.sub(r'(src=["\']js/video-config\.js)(?:\?[^"\']*)?(["\'])',
                  lambda match: match[1] + '?v=' + version + match[2], original_html.decode('utf-8-sig'))
    if 'js/video-config.js' not in html:
        raise ValueError('当前网站尚未接入零碎日月视频模块。')
    try:
        core.atomic(file, output.encode('utf-8'))
        core.atomic(html_file, html.encode('utf-8'))
    except Exception:
        if original_config is not None:
            core.atomic(file, original_config)
        elif file.exists():
            file.unlink()
        core.atomic(html_file, original_html)
        raise
    return read_catalog(root)

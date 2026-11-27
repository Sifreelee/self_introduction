"""桌面管家的独立视频页面。"""
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog
import uuid

import core
import video_tools


class VideoPage(ttk.Frame):
    def __init__(self, parent, app, state):
        super().__init__(parent)
        self.pack(fill='both', expand=True)
        self.app, self.state = app, Path(state)
        self.selected = None
        self.catalog = None
        self.source = tk.StringVar()
        self.output = tk.StringVar(value=str(self.state / 'video-output'))
        self.title = tk.StringVar()
        self.description = tk.StringVar()
        self.location = tk.StringVar()
        self.result = tk.StringVar(value='网页 MP4 · 保留原视频 · 成品小于 25MB')
        ttk.Label(self, text='零碎日月 · 视频压缩与添加', style='Title.TLabel').pack(anchor='w', pady=(0, 10))
        row, _ = app.field(self, '原视频', self.source)
        ttk.Button(row, text='选择视频…', command=self.choose).pack(side='left', padx=8)
        row, _ = app.field(self, '单独导出目录', self.output)
        ttk.Button(row, text='选择目录…', command=lambda: app.choose_dir(self.output)).pack(side='left', padx=8)
        app.field(self, '视频名字', self.title)
        app.field(self, '简介', self.description)
        app.field(self, '拍摄地', self.location)
        ttk.Label(self, text='先尝试保留原分辨率和画质；超限后采用两遍编码控制体积。H.264 + AAC，适合网页播放。\n较长的视频需要降低码率；很长的视频建议分段。视频比例保持原样，在网页 4∶3 框内完整展示。', style='Hint.TLabel', wraplength=970).pack(anchor='w', pady=10)
        buttons = ttk.Frame(self)
        buttons.pack(fill='x', pady=6)
        ttk.Button(buttons, text='仅压缩并导出 MP4', command=lambda: self.start(False)).pack(side='left')
        ttk.Button(buttons, text='压缩并加入零碎日月', style='Accent.TButton', command=lambda: self.start(True)).pack(side='left', padx=10)
        ttk.Label(self, textvariable=self.result, wraplength=970).pack(anchor='w', pady=8)
        ttk.Separator(self).pack(fill='x', pady=10)
        row = ttk.Frame(self)
        row.pack(fill='x')
        ttk.Label(row, text='网站现有视频 · 选中后编辑名字、简介和拍摄地').pack(side='left')
        ttk.Button(row, text='重新读取', command=self.reload).pack(side='right')
        ttk.Button(row, text='保存资料', command=self.save).pack(side='right', padx=8)
        self.list = ttk.Treeview(self, columns=('title', 'location'), show='headings', height=4)
        self.list.heading('title', text='视频名字')
        self.list.heading('location', text='拍摄地')
        self.list.pack(fill='both', expand=True, pady=7)
        self.list.bind('<<TreeviewSelect>>', self.select)

    def choose(self):
        if self.app.busy:
            return
        file = filedialog.askopenfilename(parent=self.app, title='选择视频，原文件会保留', filetypes=[('视频', '*.mp4 *.mov *.mkv *.webm *.avi *.m4v'), ('所有文件', '*.*')])
        if file:
            self.selected = None
            self.list.selection_remove(self.list.selection())
            self.source.set(file)
            self.title.set(Path(file).stem)
            self.description.set('')
            self.location.set('')

    def reload(self):
        try:
            self.app.guard_idle()
            self.catalog = video_tools.read_catalog(self.app.root_path())
            self.selected = None
            self.list.delete(*self.list.get_children())
            for i, item in enumerate(self.catalog['config'].get('videos', [])):
                self.list.insert('', 'end', iid=str(i), values=(item.get('title', ''), item.get('location', '')))
        except Exception as error:
            self.app.error(error)

    def select(self, event=None):
        if self.app.busy or not self.list.selection() or not self.catalog:
            return
        self.selected = int(self.list.selection()[0])
        item = self.catalog['config']['videos'][self.selected]
        self.title.set(item.get('title', ''))
        self.description.set(item.get('description', ''))
        self.location.set(item.get('location', ''))
        self.source.set(str(self.app.root_path() / item['src']))

    def values(self):
        if not self.title.get().strip():
            raise ValueError('请填写视频名字。')
        return {'title': self.title.get().strip(), 'description': self.description.get().strip(), 'location': self.location.get().strip()}

    def save(self):
        try:
            self.app.guard_idle()
            if self.selected is None or self.catalog is None:
                raise ValueError('请先选中网站现有视频。')
            entries = [dict(item) for item in self.catalog['config'].get('videos', [])]
            entries[self.selected].update(self.values())
            video_tools.save_catalog(self.app.root_path(), self.catalog, entries)
            self.reload()
            self.result.set('视频资料已保存；上传 GitHub 后线上生效。')
        except Exception as error:
            self.app.error(error)

    def start(self, add):
        try:
            self.app.guard_idle()
            source = Path(self.source.get()).resolve()
            if not source.is_file():
                raise ValueError('请先选择视频。')
            ffmpeg = video_tools.find_ffmpeg()
            root = self.app.root_path() if add else None
            catalog = self.catalog if add and self.catalog is not None else video_tools.read_catalog(root) if add else None
            metadata = self.values() if add else {}
            selected = self.selected
            token = uuid.uuid4().hex[:12]
            folder = root / 'assets/videos' if add else core.writable(self.output.get())
            destination = folder / ('video-' + token + '.mp4')
            def work():
                result = video_tools.compress(source, destination, self.state, ffmpeg, self.app.worker_progress)
                if add:
                    cover = folder / ('video-' + token + '.jpg')
                    video_tools.poster(destination, cover, self.state, ffmpeg)
                    entry = dict(metadata, src=destination.relative_to(root).as_posix(), poster=cover.relative_to(root).as_posix(), duration=result['duration'])
                    entries = [dict(item) for item in catalog['config'].get('videos', [])]
                    if selected is None:
                        entries.append(entry)
                    else:
                        entries[selected] = entry
                    video_tools.save_catalog(root, catalog, entries)
                return result
            def done(result):
                self.result.set('已导出 %.2f MB，%d × %d：%s%s' % (result['size'] / 1_000_000, result['width'], result['height'], result['path'], '\n已写入零碎日月并生成封面；点击 GitHub 上传后线上生效。' if add else ''))
                self.app.log(self.result.get())
                if add:
                    self.reload()
            self.app.run('网页视频压缩' + ('并添加到网站' if add else ''), work, done)
        except Exception as error:
            self.app.error(error)

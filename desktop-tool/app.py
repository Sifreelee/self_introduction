"""山水清音 · 桌面管家。所有用户数据保存在程序旁的 _data 目录。"""
import json
import os
from pathlib import Path
import queue
import re
import shutil
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, simpledialog
import webbrowser

from PIL import Image, ImageTk, ImageOps
import core
import album_merge
import featured

BASE = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent
STATE = BASE / '_data'


class App(tk.Tk):
    def __init__(self, maintenance=True):
        super().__init__()
        self.title('山水清音 · 桌面管家 · 精选与地图编辑版')
        self.geometry('1180x860')
        self.minsize(1040, 780)
        self.configure(bg=core.PALETTE['paper'])
        self.config_file = STATE / 'settings.json'
        self.settings = {}
        if self.config_file.exists():
            try:
                self.settings = json.loads(self.config_file.read_text(encoding='utf-8'))
            except (OSError, ValueError):
                pass
        self.site = tk.StringVar(value=core.locate_site(self.settings, BASE))
        self.events = queue.Queue()
        self.progress_lock = threading.Lock()
        self.pending_progress = None
        self.operation_started = None
        self.last_progress_at = None
        self.operation_timer = None
        self.active_label = ''
        self.busy = False
        self.upload_process = None
        self.jobs = []
        self.files = []
        self.selected_folder = None
        self.selected_file_ids = {}
        self.last_file_ids = {}
        self.last_upload_code = None
        self.last_upload_files = []
        self.upload_rows = {}
        self.upload_refresh_timer = None
        self.upload_name_cache = {}
        self.plan = []
        self.palette = dict(core.PALETTE)
        self.setup_style()
        self.build()
        self.refresh_site(initial=True)
        self.after(100, self.pump)
        self.protocol('WM_DELETE_WINDOW', self.close)

    def setup_style(self):
        s = ttk.Style(self)
        s.theme_use('clam')
        p = self.palette
        s.configure('.', font=('Microsoft YaHei UI', 10), background=p['paper'], foreground=p['ink'])
        s.configure('TFrame', background=p['paper'])
        s.configure('Card.TFrame', background=p['card'])
        s.configure('TLabel', background=p['paper'], foreground=p['ink'])
        s.configure('Hint.TLabel', foreground='#777064', font=('Microsoft YaHei UI', 9))
        s.configure('Title.TLabel', font=('KaiTi', 25), foreground=p['teal'])
        s.configure('TButton', padding=(13, 8), background=p['card'], bordercolor='#D3C8AC')
        s.map('TButton', background=[('active', '#E7DFC8')])
        s.configure('Accent.TButton', background=p['cinnabar'], foreground=p['card'], padding=(18, 10))
        s.map('Accent.TButton', background=[('active', '#8C2F28'), ('disabled', '#BAADA0')])
        s.configure('TEntry', fieldbackground='#FCF9F1', padding=6)
        s.configure('TCombobox', fieldbackground='#FCF9F1', padding=5)
        s.configure('Treeview', background=p['card'], fieldbackground=p['card'], rowheight=29, borderwidth=0)
        s.configure('Treeview.Heading', background='#E7DFC8', padding=7)
        s.configure('Work.Horizontal.TProgressbar', background=p['teal'], troughcolor='#E7DFC8', thickness=12)
        s.map('Treeview', background=[('selected', p['teal'])], foreground=[('selected', '#FFFFFF')])
        s.configure('TNotebook', tabmargins=(0, 10, 0, 0))
        s.configure('TNotebook.Tab', padding=(8, 11), background='#E7DFC8')
        s.map('TNotebook.Tab', background=[('selected', p['card'])], foreground=[('selected', p['cinnabar'])])

    def build(self):
        header = ttk.Frame(self, padding=(28, 14))
        header.pack(fill='x')
        self.logo = tk.Label(header, text='荔', font=('KaiTi', 29), bg=self.palette['cinnabar'], fg=self.palette['card'], width=2)
        self.logo.pack(side='left', padx=(0, 14))
        title = ttk.Frame(header)
        title.pack(side='left')
        ttk.Label(title, text='山水清音 · 桌面管家', style='Title.TLabel').pack(anchor='w')
        ttk.Label(title, text='整理一册山水，留存一路行迹 · 精选与地图编辑版', style='Hint.TLabel').pack(anchor='w', pady=(3, 0))
        self.art = tk.Label(header, bg=self.palette['paper'])
        self.art.pack(side='right')
        bar = ttk.Frame(self, padding=(28, 0, 28, 8))
        bar.pack(fill='x')
        ttk.Label(bar, text='网站目录').pack(side='left', padx=(0, 10))
        ttk.Entry(bar, textvariable=self.site).pack(side='left', fill='x', expand=True)
        ttk.Button(bar, text='选择网站文件夹…', command=self.choose_site).pack(side='left', padx=7)
        ttk.Button(bar, text='读取网站内容', command=self.refresh_site).pack(side='left')
        ttk.Button(bar, text='预览本地网站', style='Accent.TButton', command=self.preview).pack(side='left', padx=7)
        self.status = tk.StringVar(value='就绪')
        ttk.Label(self, textvariable=self.status, style='Hint.TLabel', padding=(28, 2)).pack(fill='x')
        progress_panel = ttk.Frame(self, padding=(28, 1, 28, 4))
        progress_panel.pack(fill='x')
        progress_panel.columnconfigure(0, weight=1)
        self.progress_text = tk.StringVar(value='任务进度：就绪')
        self.elapsed_text = tk.StringVar(value='已用 00:00')
        ttk.Label(progress_panel, textvariable=self.progress_text, style='Hint.TLabel').grid(row=0, column=0, sticky='w')
        ttk.Label(progress_panel, textvariable=self.elapsed_text, style='Hint.TLabel').grid(row=0, column=1, sticky='e', padx=(10, 0))
        self.progress = ttk.Progressbar(progress_panel, mode='determinate', maximum=100, value=0, style='Work.Horizontal.TProgressbar')
        self.progress.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(4, 0))
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill='both', expand=True, padx=28, pady=4)
        pages = []
        for name in ('壹  添加照片', '贰  相册与代码', '叁  批量改名', '肆  压缩打包', '伍  GitHub', '陆  我的设计', '柒  相册合并', '捌  荔荔精选', '玖  地图照片'):
            page = ttk.Frame(self.tabs, padding=18)
            self.tabs.add(page, text=name)
            pages.append(page)
        self.import_page(pages[0])
        self.editor_page(pages[1])
        self.rename_page(pages[2])
        self.compress_page(pages[3])
        self.github_page(pages[4])
        self.design_page(pages[5])
        self.merge_page(pages[6])
        self.featured_page(pages[7])
        self.map_photos_page(pages[8])
        bottom = ttk.Frame(self, padding=(28, 7, 28, 14))
        bottom.pack(fill='x')
        row = ttk.Frame(bottom)
        row.pack(fill='x', pady=(0, 5))
        ttk.Label(row, text='操作记录', foreground=self.palette['teal']).pack(side='left')
        ttk.Button(row, text='清除缓存', command=self.clear_cache).pack(side='right')
        self.logbox = tk.Text(bottom, height=4, relief='flat', bg='#F6F0E2', fg='#55524A', font=('Microsoft YaHei UI', 9), padx=10, pady=7, state='disabled')
        self.logbox.pack(fill='x')
        self.apply_design()
        for variable in (self.target, self.album, self.do_compress, self.keep_png, self.overwrite, self.side, self.quality):
            variable.trace_add('write', lambda *_: self.schedule_upload_list())

    def field(self, parent, label, variable, width=None):
        row = ttk.Frame(parent)
        row.pack(fill='x', pady=5)
        ttk.Label(row, text=label, width=15).pack(side='left')
        ent = ttk.Entry(row, textvariable=variable, width=width)
        ent.pack(side='left', fill='x', expand=True)
        return row, ent

    def table(self, parent, columns, height=5):
        frame = ttk.Frame(parent)
        frame.pack(fill='both', expand=True, pady=7)
        tree = ttk.Treeview(frame, columns=[str(i) for i in range(len(columns))], show='headings', height=height)
        for i, (label, width) in enumerate(columns):
            tree.heading(str(i), text=label)
            tree.column(str(i), width=width, minwidth=70)
        scroll = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')
        return tree

    def options(self, parent):
        self.do_compress = tk.BooleanVar(value=True)
        self.keep_png = tk.BooleanVar(value=False)
        self.overwrite = tk.BooleanVar(value=True)
        row = ttk.Frame(parent)
        row.pack(fill='x', pady=5)
        ttk.Checkbutton(row, text='导入时压缩图片', variable=self.do_compress).pack(side='left')
        ttk.Checkbutton(row, text='PNG 保留透明和格式', variable=self.keep_png).pack(side='left', padx=15)
        ttk.Checkbutton(row, text='同名文件自动覆盖', variable=self.overwrite).pack(side='left')

    def map_photos_page(self, page):
        self.map_city = tk.StringVar()
        self.map_match = tk.BooleanVar()
        self.map_expected = None
        ttk.Label(page, text='点亮中国 · 地图照片', style='Title.TLabel').pack(anchor='w', pady=(0, 12))
        ttk.Label(page, text='地图按省份展示，照片上的城市说明从这里读取。给每个城市选择对应相册；每座城市随机展示一张。\n照片区固定在地图与地点列表之间。选择跨城市相册时，可勾选仅使用标题含该城市名的照片。', style='Hint.TLabel', wraplength=900).pack(anchor='w', pady=(0, 14))
        row = ttk.Frame(page)
        row.pack(fill='x', pady=5)
        ttk.Label(row, text='编辑城市', width=15).pack(side='left')
        self.map_city_combo = ttk.Combobox(row, textvariable=self.map_city, state='readonly')
        self.map_city_combo.pack(side='left', fill='x', expand=True)
        self.map_city_combo.bind('<<ComboboxSelected>>', lambda e: self.load_map_city())
        self.map_hint = tk.StringVar()
        ttk.Label(page, textvariable=self.map_hint, style='Hint.TLabel').pack(anchor='w', pady=8)
        ttk.Label(page, text='对应相册（可多选；清空选择可暂停该城市的照片）').pack(anchor='w')
        area = ttk.Frame(page)
        area.pack(fill='both', expand=True, pady=8)
        area.columnconfigure(0, weight=1)
        area.columnconfigure(1, weight=2)
        area.columnconfigure(2, weight=1)
        area.rowconfigure(1, weight=1)
        for col, text in enumerate(('相册', '指定照片（多选可随机；不选为全部）', '照片预览')):
            ttk.Label(area, text=text).grid(row=0, column=col, sticky='w', padx=5)
        album_area = ttk.Frame(area)
        album_area.grid(row=1, column=0, sticky='nsew', padx=(0, 8))
        self.map_albums = tk.Listbox(album_area, width=20, selectmode='extended', exportselection=False, font=('Microsoft YaHei UI', 10), bg=self.palette['card'], relief='flat')
        scroll = ttk.Scrollbar(album_area, command=self.map_albums.yview)
        scroll.pack(side='right', fill='y')
        self.map_albums.pack(fill='both', expand=True)
        self.map_albums.configure(yscrollcommand=scroll.set)
        self.map_albums.bind('<<ListboxSelect>>', lambda e: self.load_map_photos())
        photo_area = ttk.Frame(area)
        photo_area.grid(row=1, column=1, sticky='nsew', padx=(0, 8))
        self.map_photos = tk.Listbox(photo_area, width=30, selectmode='extended', exportselection=False, font=('Microsoft YaHei UI', 10), bg=self.palette['card'], relief='flat')
        photo_scroll = ttk.Scrollbar(photo_area, command=self.map_photos.yview)
        photo_scroll.pack(side='right', fill='y')
        self.map_photos.pack(fill='both', expand=True)
        self.map_photos.configure(yscrollcommand=photo_scroll.set)
        self.map_photos.bind('<<ListboxSelect>>', lambda e: self.preview_map_photo())
        self.map_photo_preview = ttk.Label(area, text='选择照片后预览', anchor='center', width=22)
        self.map_photo_preview.grid(row=1, column=2, sticky='nsew')
        self.map_photo_options = []
        self.map_selected_photos = []
        ttk.Checkbutton(page, text='只使用照片标题中包含该城市名的照片', variable=self.map_match, command=self.load_map_photos).pack(anchor='w')
        row = ttk.Frame(page)
        row.pack(fill='x', pady=12)
        ttk.Button(row, text='重新读取', command=self.load_map_city).pack(side='left')
        ttk.Button(row, text='预览本地网站', command=self.preview).pack(side='left', padx=8)
        ttk.Button(row, text='删除所选地点', command=self.delete_map_city).pack(side='left', padx=8)
        ttk.Button(row, text='保存地图照片配置', style='Accent.TButton', command=self.save_map_city).pack(side='right')

    def delete_map_city(self):
        try:
            root = self.root_path()
            city = self.map_city.get()
            if not city or self.map_expected is None:
                raise ValueError('请先选择要删除的地点。')
            expected = dict(self.map_expected)
            def done(name):
                self.refresh_site()
                self.status.set('已删除地点“%s”，相册和照片文件均保留。' % name)
            self.run('删除所选地点（保留相册照片）', lambda: featured.delete_map_city(root, STATE, city, expected), done)
        except Exception as e:
            self.error(e)

    def load_map_city(self):
        try:
            if not self.map_city.get():
                self.map_expected = None
                self.map_albums.delete(0, 'end')
                self.map_photos.delete(0, 'end')
                self.map_photo_options = []
                self.map_photo_preview.configure(image='', text='请先选择城市')
                self.map_hint.set('删除地点仅移除地图足迹，相册和照片保留。')
                return
            root = self.root_path()
            data = featured.read_map_city(root, self.map_city.get())
            self.map_expected = data['expected']
            self.map_albums.delete(0, 'end')
            for i, album in enumerate(self.albums):
                self.map_albums.insert('end', album['name'])
                if album['name'] in data['albums']:
                    self.map_albums.selection_set(i)
            self.map_match.set(data['match'] == 'title')
            self.map_selected_photos = data['photos']
            self.map_photo_options = []
            self.load_map_photos()
            place = next((p for p in featured.map_places(root) if p['city'] == self.map_city.get()), {})
            self.map_hint.set('所属省份：' + (place.get('province') or '待补录') + ' · 保存后预览，再上传 GitHub。')
        except Exception as e:
            self.error(e)

    def load_map_photos(self):
        try:
            albums = [self.map_albums.get(i) for i in self.map_albums.curselection()]
            selected = [self.map_photo_options[i]['src'] for i in self.map_photos.curselection()] if self.map_photo_options else self.map_selected_photos
            self.map_photo_options = featured.map_photo_options(self.root_path(), albums, self.map_city.get(), 'title' if self.map_match.get() else 'auto')
            self.map_photos.delete(0, 'end')
            for i, item in enumerate(self.map_photo_options):
                self.map_photos.insert('end', item['title'] + ' · ' + item['album'])
                if item['src'] in selected:
                    self.map_photos.selection_set(i)
            self.preview_map_photo()
        except Exception as e:
            self.error(e)

    def preview_map_photo(self):
        try:
            chosen = self.map_photos.curselection()
            if not chosen:
                self.map_photo_preview.configure(image='', text='未指定照片：从相册随机展示')
                return
            item = self.map_photo_options[chosen[-1]]
            root = self.root_path()
            path = root / item['src']
            if not core.within(path, root / 'assets') or not path.is_file():
                self.map_photo_preview.configure(image='', text='此照片暂不能本地预览')
                return
            with Image.open(str(path)) as image:
                photo = ImageOps.exif_transpose(image).convert('RGB')
                photo.thumbnail((180, 160))
                self.map_photo_image = ImageTk.PhotoImage(photo)
            self.map_photo_preview.configure(image=self.map_photo_image, text='')
        except Exception:
            self.map_photo_preview.configure(image='', text='暂不能预览这张照片')

    def save_map_city(self):
        try:
            root = self.root_path()
            if self.map_expected is None:
                raise ValueError('请先选择城市并读取配置。')
            city = self.map_city.get()
            albums = [self.map_albums.get(i) for i in self.map_albums.curselection()]
            match = 'title' if self.map_match.get() else 'auto'
            photos = [self.map_photo_options[i]['src'] for i in self.map_photos.curselection()]
            def done(name):
                self.load_map_city()
                self.load_featured()
                self.status.set('已保存地图城市照片：' + name)
            self.run('保存地图照片配置', lambda: featured.save_map_city(root, STATE, city, albums, match, self.map_expected, photos), done)
        except Exception as e:
            self.error(e)

    def featured_page(self, page):
        self.featured_source = None
        self.featured_expected = None
        self.featured_album = tk.StringVar()
        self.featured_src = tk.StringVar()
        self.featured_title = tk.StringVar()
        self.featured_note = tk.StringVar()
        self.featured_photo_options = []
        ttk.Label(page, text='荔荔精选', style='Title.TLabel').pack(anchor='w', pady=(0, 12))
        ttk.Label(page, text='选择精选相册后自动带出封面，点击网页精选卡片直接进入这本相册。\n也可从相册里另选照片，或自行上传替换；保存后预览，再上传 GitHub。', style='Hint.TLabel', wraplength=900).pack(anchor='w', pady=(0, 18))
        body = ttk.Frame(page)
        body.pack(fill='both', expand=True)
        body.columnconfigure(0, weight=1)
        left = ttk.Frame(body)
        left.grid(row=0, column=0, sticky='nsew', padx=(0, 20))
        right = ttk.Frame(body)
        right.grid(row=0, column=1, sticky='ne')
        ttk.Label(right, text='当前精选照片', style='Hint.TLabel').pack(anchor='w', pady=(4, 8))
        self.featured_thumbnail = tk.Canvas(right, width=220, height=180, bg=self.palette['card'], highlightthickness=1, highlightbackground='#D3C8AC')
        self.featured_thumbnail.pack()
        self.featured_preview_image = None
        row = ttk.Frame(left)
        row.pack(fill='x', pady=5)
        ttk.Label(row, text='跳转相册', width=15).pack(side='left')
        self.featured_combo = ttk.Combobox(row, textvariable=self.featured_album, state='readonly')
        self.featured_combo.pack(side='left', fill='x', expand=True)
        self.featured_combo.bind('<<ComboboxSelected>>', lambda e: self.load_featured_photos(True))
        row = ttk.Frame(left)
        row.pack(fill='x', pady=5)
        ttk.Label(row, text='相册中的照片', width=15).pack(side='left')
        self.featured_photo_combo = ttk.Combobox(row, state='readonly')
        self.featured_photo_combo.pack(side='left', fill='x', expand=True)
        self.featured_photo_combo.bind('<<ComboboxSelected>>', lambda e: self.choose_featured_album_photo())
        self.field(left, '照片标题', self.featured_title)
        row, _ = self.field(left, '精选照片路径', self.featured_src)
        ttk.Button(row, text='更换照片…', command=self.pick_featured_photo).pack(side='left', padx=7)
        self.field(left, '配文', self.featured_note)
        self.featured_hint = tk.StringVar(value='点击重新读取，可载入现有精选。')
        ttk.Label(left, textvariable=self.featured_hint, style='Hint.TLabel', wraplength=900).pack(anchor='w', pady=14)
        row = ttk.Frame(page)
        row.pack(fill='x', pady=12)
        ttk.Button(row, text='重新读取精选', command=self.load_featured).pack(side='left')
        ttk.Button(row, text='预览本地网站', command=self.preview).pack(side='left', padx=8)
        ttk.Button(row, text='保存荔荔精选', style='Accent.TButton', command=self.save_featured).pack(side='right')

        self.featured_src.trace_add('write', lambda *_: self.preview_featured_photo())

    def preview_featured_photo(self):
        self.featured_thumbnail.delete('all')
        self.featured_preview_image = None
        try:
            if self.featured_source:
                path = Path(self.featured_source)
            else:
                root = self.root_path()
                path = root / self.featured_src.get()
                if not self.featured_src.get() or not core.within(path, root / 'assets'):
                    raise ValueError('No local image')
            with Image.open(str(path)) as image:
                photo = ImageOps.exif_transpose(image).convert('RGB')
                photo.thumbnail((210, 170))
                self.featured_preview_image = ImageTk.PhotoImage(photo)
            self.featured_thumbnail.create_image(110, 90, image=self.featured_preview_image)
        except Exception:
            self.featured_thumbnail.create_text(110, 90, text='暂无可预览的照片', fill='#777064', font=('Microsoft YaHei UI', 10))

    def load_featured(self):
        try:
            data = featured.read(self.root_path())
            self.featured_expected = data['expected']
            self.featured_source = None
            for key, var in [('album', self.featured_album), ('src', self.featured_src), ('title', self.featured_title), ('note', self.featured_note)]:
                var.set(data['recent'].get(key, ''))
            self.load_featured_photos()
            self.featured_hint.set('已读取当前精选。更换照片和编辑文字后，点击保存才会修改网站。')
        except Exception as e:
            self.error(e)

    def load_featured_photos(self, use_cover=False):
        try:
            name = self.featured_album.get()
            self.featured_photo_options = featured.map_photo_options(self.root_path(), [name]) if name else []
            cover = core.read_album(self.root_path(), name).get('cover') if name else ''
            if cover and not any(item['src'] == cover for item in self.featured_photo_options):
                self.featured_photo_options.insert(0, {'src': cover, 'title': Path(cover).stem, 'album': name})
            if use_cover:
                self.featured_source = None
                first = next((item for item in self.featured_photo_options if item['src'] == cover), None)
                first = first or (self.featured_photo_options[0] if self.featured_photo_options else None)
                self.featured_src.set(first['src'] if first else '')
                self.featured_title.set(first['title'] if first else name)
                self.featured_hint.set('已绑定相册“%s”，可另选照片或自行上传替换。' % name)
            current = self.featured_src.get()
            if current and not any(item['src'] == current for item in self.featured_photo_options):
                self.featured_photo_options.insert(0, {'src': current, 'title': self.featured_title.get() or '自行选择的照片', 'album': name})
            self.featured_photo_combo['values'] = [item['title'] + ' · ' + item['src'] for item in self.featured_photo_options]
            chosen = next((i for i, item in enumerate(self.featured_photo_options) if item['src'] == current), -1)
            if chosen >= 0:
                self.featured_photo_combo.current(chosen)
            else:
                self.featured_photo_combo.set('')
        except Exception as e:
            self.error(e)

    def choose_featured_album_photo(self):
        index = self.featured_photo_combo.current()
        if index >= 0:
            item = self.featured_photo_options[index]
            if item['src'] != self.featured_src.get():
                self.featured_source = None
            self.featured_src.set(item['src'])
            self.featured_title.set(item['title'])

    def pick_featured_photo(self):
        try:
            root = self.root_path()
            name = filedialog.askopenfilename(title='选择荔荔精选照片', initialdir=str(root / 'assets/images'), filetypes=[('照片', '*.jpg *.jpeg *.png *.webp')])
            if not name:
                return
            source = Path(name).resolve()
            if core.within(source, root / 'assets'):
                self.featured_source = None
                self.featured_src.set(source.relative_to(root).as_posix())
                matches = [album['name'] for album in self.albums if self.featured_src.get() in album['refs']]
                if matches and self.featured_album.get() not in matches:
                    self.featured_album.set(matches[0])
            else:
                self.featured_source = str(source)
                self.featured_src.set('assets/images/featured/' + source.name)
            self.featured_title.set(source.stem)
            self.load_featured_photos()
            self.featured_hint.set('已选择：' + str(source) + '；保存时复制到网站，原文件保留。')
        except Exception as e:
            self.error(e)

    def save_featured(self):
        try:
            root = self.root_path()
            if self.featured_expected is None:
                raise ValueError('请先重新读取精选。')
            values = {'album': self.featured_album.get(), 'src': self.featured_src.get(), 'title': self.featured_title.get(), 'note': self.featured_note.get()}
            source = self.featured_source
            if source and values['src'] != 'assets/images/featured/' + Path(source).name:
                raise ValueError('待复制照片与路径不一致，请重新选择照片。')
            def done(title):
                self.load_featured()
                self.status.set('已更新荔荔精选：' + title + '；可预览并上传 GitHub。')
            self.run('保存荔荔精选', lambda: featured.save(root, STATE, values, self.featured_expected, source), done)
        except Exception as e:
            self.error(e)

    def merge_page(self, page):
        self.merge_plan = None
        self.merge_mother = tk.StringVar()
        self.merge_folder = tk.StringVar()
        row, _ = self.field(page, '母相册', self.merge_mother)
        # 只允许从现有相册选择；照片目标文件夹可与相册名不同。
        for widget in row.winfo_children():
            if isinstance(widget, ttk.Entry):
                widget.destroy()
        self.merge_mother_combo = ttk.Combobox(row, textvariable=self.merge_mother, state='readonly')
        self.merge_mother_combo.pack(side='left', fill='x', expand=True)
        self.merge_mother_combo.bind('<<ComboboxSelected>>', self.merge_mother_selected)
        row, _ = self.field(page, '母文件夹', self.merge_folder)
        ttk.Button(row, text='选择文件夹…', command=self.pick_merge_folder).pack(side='left', padx=7)
        ttk.Label(page, text='保留母相册名称、简介、星标、印章简写和封面；关键词合并去重。\n仅移动相册里已登记的照片。同名照片用并入相册覆盖；多本冲突时，列表中靠后的相册优先。', style='Hint.TLabel', wraplength=940).pack(anchor='w', pady=7)
        body = ttk.Frame(page)
        body.pack(fill='both', expand=True)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(1, weight=1)
        ttk.Label(body, text='选择要并入的相册（可多选）').grid(row=0, column=0, sticky='w', pady=4)
        ttk.Label(body, text='合并预览').grid(row=0, column=1, sticky='w', padx=(14, 0), pady=4)
        choices = ttk.Frame(body)
        choices.grid(row=1, column=0, sticky='nsew')
        self.merge_sources = tk.Listbox(choices, selectmode='extended', exportselection=False, bg=self.palette['card'], relief='flat', font=('Microsoft YaHei UI', 10))
        scrollbar = ttk.Scrollbar(choices, orient='vertical', command=self.merge_sources.yview)
        scrollbar.pack(side='right', fill='y')
        self.merge_sources.pack(fill='both', expand=True)
        self.merge_sources.configure(yscrollcommand=scrollbar.set)
        self.merge_sources.bind('<<ListboxSelect>>', lambda e: self.invalidate_merge())
        self.merge_preview = tk.Text(body, width=40, height=7, wrap='word', state='disabled', relief='flat', bg=self.palette['card'], padx=12, pady=10, font=('Microsoft YaHei UI', 10))
        self.merge_preview.grid(row=1, column=1, sticky='nsew', padx=(14, 0))
        row = ttk.Frame(page)
        row.pack(fill='x', pady=(12, 0))
        ttk.Button(row, text='生成合并预览', command=self.preview_merge).pack(side='left')
        ttk.Button(row, text='预览本地网站', command=self.preview).pack(side='left', padx=8)
        self.merge_apply = ttk.Button(row, text='确认合并相册', style='Accent.TButton', state='disabled', command=self.apply_album_merge)
        self.merge_apply.pack(side='right')
        self.merge_mother.trace_add('write', lambda *_: self.invalidate_merge())
        self.merge_folder.trace_add('write', lambda *_: self.invalidate_merge())

    def invalidate_merge(self):
        self.merge_plan = None
        self.merge_apply.configure(state='disabled')
        self.merge_preview.configure(state='normal')
        self.merge_preview.delete('1.0', 'end')
        self.merge_preview.insert('1.0', '选择母相册、母文件夹和要并入的相册，然后生成预览。确认后才会修改文件；合并后被并入的相册条目会移除。')
        self.merge_preview.configure(state='disabled')

    def merge_mother_selected(self, _=None):
        try:
            album = next(a for a in self.albums if a['name'] == self.merge_mother.get())
            folders = [str(Path(ref).parent).replace('\\', '/') for ref in album['refs'] if ref.startswith('assets/')]
            self.merge_folder.set(folders[0] if folders else '')
            self.merge_sources.selection_clear(0, 'end')
            self.invalidate_merge()
        except Exception as e:
            self.error(e)

    def pick_merge_folder(self):
        try:
            root = self.root_path()
            folder = filedialog.askdirectory(title='选择母相册照片文件夹', initialdir=str(root / (self.merge_folder.get() or 'assets/images')))
            if folder:
                path = Path(folder).resolve()
                if not core.within(path, root / 'assets'):
                    raise ValueError('请选择当前网站 assets 内的文件夹。')
                self.merge_folder.set(path.relative_to(root).as_posix())
        except Exception as e:
            self.error(e)

    def preview_merge(self):
        try:
            root = self.root_path()
            mother, folder = self.merge_mother.get(), self.merge_folder.get()
            sources = [self.merge_sources.get(i) for i in self.merge_sources.curselection()]
            self.invalidate_merge()
            def done(plan):
                current = [self.merge_sources.get(i) for i in self.merge_sources.curselection()]
                if (self.merge_mother.get(), self.merge_folder.get(), current) != (mother, folder, sources):
                    return
                self.merge_plan = plan
                lines = ['母相册：' + mother, '母文件夹：' + plan['folder'], '并入相册：' + '、'.join(sources),
                         '合并后照片：%d 张' % plan['photos'], '简介 / 星标 / 印章简写 / 封面：沿用母相册',
                         '合并关键词：' + '，'.join(plan['tags']), '同名覆盖：%d 个' % len(plan['overwrites'])]
                lines.extend(plan['overwrites'])
                lines.append('确认后移动已登记照片并移除并入相册；不提供撤销，请先核对。')
                self.merge_preview.configure(state='normal')
                self.merge_preview.delete('1.0', 'end')
                self.merge_preview.insert('1.0', '\n\n'.join(lines))
                self.merge_preview.configure(state='disabled')
                self.merge_apply.configure(state='normal')
            self.run('生成相册合并预览', lambda: album_merge.plan_merge(root, mother, sources, folder, self.worker_progress), done)
        except Exception as e:
            self.error(e)

    def apply_album_merge(self):
        try:
            root = self.root_path()
            if not self.merge_plan:
                raise ValueError('请先生成合并预览。')
            plan = self.merge_plan
            def done(name):
                self.refresh_site()
                self.edit_choice.set(name)
                self.album.set(name)
                self.load_editor()
                self.status.set('已合并到“%s”，可预览网站后上传 GitHub。' % name)
            self.run('合并相册', lambda: album_merge.apply_merge(root, STATE, plan, self.worker_progress), done)
        except Exception as e:
            self.error(e)

    def import_page(self, page):
        ttk.Label(page, text='选照片 → 选网站里的存放文件夹 → 选展示相册 → 点击添加。程序会复制照片并自动改好网站代码，原图保留。', style='Hint.TLabel', wraplength=950).pack(anchor='w')
        self.source_label = tk.StringVar(value='尚未选择文件')
        row = ttk.Frame(page)
        row.pack(fill='x', pady=8)
        ttk.Button(row, text='选择多个文件', command=self.pick_files).pack(side='left')
        ttk.Button(row, text='选择整个文件夹', command=self.pick_folder).pack(side='left', padx=9)
        ttk.Button(row, text='预览文件 / 照片', command=self.preview_upload_files).pack(side='left', padx=(0, 9))
        ttk.Label(row, textvariable=self.source_label, style='Hint.TLabel').pack(side='left')
        self.target = tk.StringVar(value='assets/images')
        row = ttk.Frame(page)
        row.pack(fill='x', pady=5)
        ttk.Label(row, text='新照片上传到哪个文件夹', width=24).pack(side='left')
        self.target_combo = ttk.Combobox(row, textvariable=self.target)
        self.target_combo.pack(side='left', fill='x', expand=True)
        ttk.Button(row, text='选择存放文件夹', command=self.pick_target).pack(side='left', padx=(8, 0))
        self.album = tk.StringVar()
        row = ttk.Frame(page)
        row.pack(fill='x', pady=5)
        ttk.Label(row, text='照片添加到哪个相册', width=24).pack(side='left')
        self.album_combo = ttk.Combobox(row, textvariable=self.album)
        self.album_combo.pack(side='left', fill='x', expand=True)
        self.album_combo.bind('<<ComboboxSelected>>', self.album_selected)
        ttk.Button(row, text='新建 / 修改相册', command=self.open_album_editor).pack(side='left', padx=(8, 0))
        ttk.Label(page, text='这里的“上传”先保存到电脑里的网站文件夹；传到网上请点 GitHub。相册留空则只复制文件，不改相册代码。', style='Hint.TLabel', wraplength=950).pack(anchor='w', pady=(2, 4))
        self.options(page)
        row = ttk.Frame(page)
        row.pack(fill='x', pady=5)
        ttk.Button(row, text='＋ 加入待添加列表', command=self.add_job).pack(side='left')
        ttk.Button(row, text='移除选中文件', command=self.remove_job).pack(side='left', padx=8)
        ttk.Button(row, text='刷新列表', command=self.rescan_upload_files).pack(side='left')
        ttk.Label(row, text='选完照片自动显示下表；双击文件可看图片。', style='Hint.TLabel').pack(side='left', padx=8)
        self.jobs_tree = self.table(page, [('文件名', 220), ('格式', 65), ('大小', 85), ('保存位置', 240), ('添加到相册', 145), ('状态', 115)], 4)
        self.jobs_tree.bind('<Double-1>', lambda _: self.preview_upload_files(selected_batch=True))
        self.upload_menu = tk.Menu(self, tearoff=False)
        self.upload_menu.add_command(label='在文件管理器中显示', command=self.reveal_selected_upload_file)
        self.upload_menu.add_command(label='查看图片预览', command=lambda: self.preview_upload_files(selected_batch=True))
        self.upload_menu.add_separator()
        self.upload_menu.add_command(label='刷新列表', command=self.rescan_upload_files)
        self.jobs_tree.bind('<Button-3>', self.show_upload_menu)
        row = ttk.Frame(page)
        row.pack(fill='x', pady=(4, 0))
        ttk.Button(row, text='获取本次照片 data.js 代码', command=self.current_upload_code).pack(side='left')
        ttk.Button(row, text='预览本地网站', command=self.preview).pack(side='left', padx=8)
        ttk.Button(row, text='检查图片与代码', command=self.start_image_check).pack(side='left')
        ttk.Button(row, text='添加全部照片并更新网站代码', style='Accent.TButton', command=self.start_import).pack(side='right')

    def editor_page(self, page):
        self.editor_original = None
        self.editor_snapshot = None
        self.edit_choice = tk.StringVar()
        row = ttk.Frame(page)
        row.pack(fill='x', pady=(0, 8))
        ttk.Label(row, text='选择要修改的相册').pack(side='left', padx=(0, 10))
        self.edit_combo = ttk.Combobox(row, textvariable=self.edit_choice, state='readonly')
        self.edit_combo.pack(side='left', fill='x', expand=True)
        self.edit_combo.bind('<<ComboboxSelected>>', lambda _: self.load_editor())
        ttk.Button(row, text='重新读取', command=self.load_editor).pack(side='left', padx=8)
        ttk.Button(row, text='＋ 创建新相册…', command=self.create_album_now).pack(side='left')
        self.edit_note = tk.StringVar(value='新建相册：填写下方资料后保存。已有相册可在上方选择并直接修改。')
        ttk.Label(page, textvariable=self.edit_note, style='Hint.TLabel', wraplength=950).pack(anchor='w', pady=(0, 8))
        body = ttk.Frame(page)
        body.pack(fill='both', expand=True)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)
        left = ttk.Frame(body)
        left.grid(row=0, column=0, sticky='nsew', padx=(0, 18))
        right = ttk.Frame(body)
        right.grid(row=0, column=1, sticky='nsew')
        self.edit_name = tk.StringVar()
        self.edit_seal = tk.StringVar()
        self.edit_star = tk.BooleanVar(value=False)
        self.edit_tags = tk.StringVar()
        self.edit_cover = tk.StringVar()
        self.edit_position = tk.StringVar(value='1')
        for label, var in [('相册名称', self.edit_name), ('印章文字', self.edit_seal), ('关键词 / 分类', self.edit_tags), ('封面图片路径', self.edit_cover)]:
            row, _ = self.field(left, label, var)
            if var is self.edit_cover:
                ttk.Button(row, text='选图', command=self.pick_cover).pack(side='left', padx=(7, 0))
        tags_row = ttk.Frame(left)
        tags_row.pack(fill='x', pady=3)
        ttk.Button(tags_row, text='识别当前相册', command=self.detect_editor_tags).pack(side='left')
        ttk.Button(tags_row, text='识别全部相册关键词', command=self.detect_all_tags).pack(side='left', padx=8)
        row = ttk.Frame(left)
        row.pack(fill='x', pady=5)
        ttk.Label(row, text='相册显示顺序', width=15).pack(side='left')
        ttk.Label(row, text='第').pack(side='left')
        self.position_spin = ttk.Spinbox(row, from_=1, to=999, textvariable=self.edit_position, width=5)
        self.position_spin.pack(side='left', padx=6)
        ttk.Label(row, text='个').pack(side='left')
        ttk.Button(row, text='前移', command=lambda: self.shift_position(-1)).pack(side='left', padx=(8, 5))
        ttk.Button(row, text='后移', command=lambda: self.shift_position(1)).pack(side='left')
        ttk.Checkbutton(left, text='给这个相册打星标', variable=self.edit_star).pack(anchor='w', pady=7)
        ttk.Label(left, text='按相册内全部照片识别，包含以前上传的照片；至少 3 张重复。\n可识别当前或全部相册，手动增删后保存。新增照片也会自动识别。\n关键词用逗号分隔；封面留空使用第一张照片。', style='Hint.TLabel', wraplength=490).pack(anchor='w', pady=4)
        ttk.Label(right, text='相册简介（可分段）').pack(anchor='w', pady=(5, 7))
        self.edit_desc = tk.Text(right, height=7, width=25, wrap='word', relief='flat', bg='#FCF9F1', fg=self.palette['ink'], font=('Microsoft YaHei UI', 10), padx=9, pady=8, undo=True)
        self.edit_desc.pack(fill='both', expand=True)
        ttk.Label(right, text='保存会同时更新 data.js 和 album-desc.js。\n修改现有相册会保留照片与其他未编辑字段。', style='Hint.TLabel').pack(anchor='w', pady=7)
        row = ttk.Frame(page)
        row.pack(fill='x', pady=(12, 0))
        ttk.Button(row, text='生成 / 获取 data.js 代码…', command=self.preview_album_code).pack(side='left')
        ttk.Button(row, text='预览本地网站', command=self.preview).pack(side='left', padx=8)
        self.editor_save_label = tk.StringVar(value='创建相册并加入列表')
        ttk.Button(row, textvariable=self.editor_save_label, style='Accent.TButton', command=self.save_editor).pack(side='right')

    def create_album_now(self):
        try:
            self.guard_idle()
            self.root_path()
            name = simpledialog.askstring('创建新相册', '请输入相册名称，点确定后立即创建并加入相册列表。\n星标、关键词和简介可创建后再修改。', parent=self)
            if name is None:
                return
            metadata = {'city': name.strip(), 'seal': '', 'star': False, 'tags': [], 'desc': '', 'cover': ''}
            root = self.root_path()
            self.run('创建新相册', lambda: core.save_album(root, STATE, None, metadata), lambda title: self.album_saved(title, None, True))
        except Exception as e:
            self.error(e)

    def album_saved(self, name, original, created):
        for job in self.jobs:
            if original and job['album'] == original:
                job['album'] = name
        self.refresh_site(preserve_jobs=True)
        self.edit_choice.set(name)
        self.album.set(name)
        self.load_editor()
        if created:
            self.tabs.select(0)
            if not self.files:
                self.source_label.set('请为新相册“%s”选择照片' % name)
            text = '已创建“%s”，已进入“添加照片”并选中此相册。请选择照片、存放文件夹，再点击添加。' % name
        else:
            text = '已保存“%s”的资料，原有照片保留，简介已更新。' % name
        self.edit_note.set(text)
        self.status.set(text)
        self.log(text)

    def snapshot_editor(self):
        root = self.root_path()
        self.editor_snapshot = {name: core.digest(root / 'js' / name) for name in ('data.js', 'album-desc.js')}

    def shift_position(self, delta):
        try:
            limit = len(getattr(self, 'albums', [])) + (1 if self.editor_original is None else 0)
            self.edit_position.set(str(max(1, min(limit, int(self.edit_position.get()) + delta))))
        except ValueError:
            self.error(ValueError('显示顺序请输入整数，例如 1 表示第一个显示。'))

    def new_album(self):
        try:
            self.guard_idle()
            self.snapshot_editor()
            self.editor_original = None
            self.edit_position.set(str(len(getattr(self, 'albums', [])) + 1))
            self.position_spin.configure(to=len(getattr(self, 'albums', [])) + 1)
            self.edit_choice.set('')
            for var in (self.edit_name, self.edit_seal, self.edit_tags, self.edit_cover):
                var.set('')
            self.edit_star.set(False)
            self.edit_desc.delete('1.0', 'end')
            self.editor_save_label.set('创建相册并加入列表')
            self.edit_note.set('当前是未创建的表单：填写名称后点右下“创建相册并加入列表”，才会出现在相册列表中。')
        except Exception as e:
            self.error(e)

    def load_editor(self):
        try:
            self.guard_idle()
            name = self.edit_choice.get()
            if not name:
                raise ValueError('请先选择要修改的相册，或点击“新建相册”。')
            root = self.root_path()
            data = core.read_album(root, name)
            self.snapshot_editor()
            self.editor_original = name
            self.edit_position.set(str(data['position']))
            self.position_spin.configure(to=len(self.albums))
            self.editor_save_label.set('保存相册修改')
            self.edit_name.set(data['city'])
            self.edit_seal.set(data['seal'] or '')
            self.edit_star.set(bool(data['star']))
            self.edit_tags.set('，'.join(data['tags'] or []))
            self.edit_cover.set(data['cover'] or '')
            self.edit_desc.delete('1.0', 'end')
            self.edit_desc.insert('1.0', data['desc'] or '')
            doc = core.Document((root / 'js/data.js').read_text(encoding='utf-8-sig'))
            count = len(core.album_by_name(doc, name)['refs'])
            self.edit_note.set('正在修改“%s” · 原有 %d 张照片会保留 · 简介已读取网页实际使用的内容' % (name, count))
        except Exception as e:
            self.error(e)

    def detect_all_tags(self):
        try:
            root = self.root_path()
            self.run('识别全部相册关键词', lambda: core.album_tags_plan(root),
                     lambda plan: self.show_all_tags(root, plan))
        except Exception as e:
            self.error(e)

    def show_all_tags(self, root, plan):
        window = tk.Toplevel(self)
        window.title('全部相册关键词 · 包含以前上传的照片')
        window.geometry('960x640')
        window.minsize(720, 420)
        window.transient(self)
        window.grab_set()
        ttk.Label(window, text='已按每个相册的全部照片识别至少 3 张重复出现的词，并保留原有分类。\n可直接修改每行，用逗号分隔；点击“保存全部关键词”后写入网站。', style='Hint.TLabel', padding=12).pack(fill='x')
        area = ttk.Frame(window)
        area.pack(fill='both', expand=True, padx=12)
        canvas = tk.Canvas(area, highlightthickness=0)
        scroll = ttk.Scrollbar(area, orient='vertical', command=canvas.yview)
        scroll.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        canvas.configure(yscrollcommand=scroll.set)
        body = ttk.Frame(canvas)
        slot = canvas.create_window((0, 0), window=body, anchor='nw')
        canvas.bind('<Configure>', lambda e: canvas.itemconfigure(slot, width=e.width))
        body.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        body.columnconfigure(0, weight=1)
        fields = []
        for i, album in enumerate(plan['albums']):
            ttk.Label(body, text='%s · 新识别 %d 个' % (album['name'], album['added'])).grid(row=i * 2, column=0, sticky='w', pady=(10, 3))
            value = tk.StringVar(value='，'.join(album['tags']))
            ttk.Entry(body, textvariable=value).grid(row=i * 2 + 1, column=0, sticky='ew', padx=(0, 10))
            fields.append((album['name'], value))
        row = ttk.Frame(window, padding=12)
        row.pack(fill='x')
        ttk.Button(row, text='取消', command=window.destroy).pack(side='left')
        def save():
            rows = [{'name': name, 'tags': [t.strip() for t in re.split(r'[,，;；、\n]+', value.get()) if t.strip()]} for name, value in fields]
            def done(count):
                window.destroy()
                if self.editor_original:
                    self.load_editor()
                self.status.set('已保存 %d 个相册的关键词，可预览网站后上传 GitHub。' % count)
            self.run('保存全部相册关键词', lambda: core.save_album_tags(root, STATE, rows, plan['hash']), done)
        ttk.Button(row, text='保存全部关键词', style='Accent.TButton', command=save).pack(side='right')

    def detect_editor_tags(self):
        try:
            self.guard_idle()
            if not self.editor_original:
                raise ValueError('请先选择已有相册；新相册添加照片时会自动识别关键词。')
            root = self.root_path()
            text = (root / 'js/data.js').read_text(encoding='utf-8-sig')
            tags = core.suggest_album_tags(text, self.editor_original)
            current = [t.strip() for t in re.split(r'[,，;；、\n]+', self.edit_tags.get()) if t.strip()]
            merged = list(dict.fromkeys(current + tags))
            self.edit_tags.set('，'.join(merged))
            self.edit_note.set('已识别 %d 个关键词，新增 %d 个；可继续手动增删，点击“保存相册修改”后生效。' % (len(tags), len(merged) - len(set(current))))
        except Exception as e:
            self.error(e)

    def open_album_editor(self):
        self.tabs.select(1)
        if self.album.get() in [a['name'] for a in getattr(self, 'albums', [])]:
            self.edit_choice.set(self.album.get())
            self.load_editor()
        else:
            name = self.album.get().strip()
            self.new_album()
            self.edit_name.set(name)

    def editor_metadata(self):
        return {'city': self.edit_name.get().strip(), 'seal': self.edit_seal.get().strip(), 'star': self.edit_star.get(), 'tags': [t.strip() for t in re.split(r'[,，;；、\n]+', self.edit_tags.get()) if t.strip()], 'desc': self.edit_desc.get('1.0', 'end-1c').strip(), 'cover': self.edit_cover.get().strip(), 'position': int(self.edit_position.get())}

    def pick_cover(self):
        try:
            root = self.root_path()
            path = filedialog.askopenfilename(title='选择网站 assets 内的封面照片', initialdir=str(root / 'assets/images'), filetypes=[('图片', '*.jpg *.jpeg *.png *.webp *.gif *.svg')])
            if path:
                if not core.within(path, root / 'assets'):
                    raise ValueError('封面需要先放到网站 assets 文件夹内，也可以先添加照片后再设置封面。')
                self.edit_cover.set(Path(path).resolve().relative_to(root).as_posix())
        except Exception as e:
            self.error(e)

    def save_editor(self):
        try:
            root = self.root_path()
            metadata, original, expected = self.editor_metadata(), self.editor_original, self.editor_snapshot
            def done(name):
                self.album_saved(name, original, original is None)
            self.run('保存相册', lambda: core.save_album(root, STATE, original, metadata, expected), done)
        except Exception as e:
            self.error(e)

    def preview_album_code(self):
        try:
            self.guard_idle()
            code = core.album_code(self.root_path(), self.editor_original, self.editor_metadata())
            self.show_code(code, '相册资料生成的代码（尚未保存到网站）')
        except Exception as e:
            self.error(e)

    def current_code(self):
        try:
            root = self.root_path()
            code = {name: (root / 'js' / name).read_text(encoding='utf-8-sig') for name in ('data.js', 'album-desc.js') if (root / 'js' / name).exists()}
            self.show_code(code, '网站当前保存的代码')
        except Exception as e:
            self.error(e)

    def start_image_check(self):
        try:
            root = self.root_path()
            self.run('检查图片与代码', lambda: core.inspect_image_references(root, self.worker_progress), self.show_image_check)
        except Exception as e:
            self.error(e)

    def show_image_check(self, report):
        window = tk.Toplevel(self)
        window.title('图片与代码核对 · ' + report['root'])
        window.geometry('1160x760')
        window.minsize(1000, 670)
        model = {'report': report}
        summary = tk.StringVar()
        ttk.Label(window, textvariable=summary, foreground=self.palette['teal'], wraplength=1090, padding=12).pack(fill='x')
        ttk.Label(window, text='由你选择：删除失效 / 重复的照片代码，或增加新图片到相册。选中后点击相应按钮才会保存；图片文件保留。', style='Hint.TLabel', wraplength=1090, padding=(12, 0, 12, 8)).pack(fill='x')
        tabs = ttk.Notebook(window)
        tabs.pack(fill='both', expand=True, padx=12)
        problems, unlisted = ttk.Frame(tabs, padding=8), ttk.Frame(tabs, padding=8)
        tabs.add(problems, text='删除照片代码')
        tabs.add(unlisted, text='增加图片')
        issue_tree = self.table(problems, [('情况', 170), ('相册 / 栏目', 150), ('照片标题', 155), ('代码中的路径', 400), ('操作', 100)], 10)
        issue_note = tk.StringVar(value='选择一行查看具体建议；可用 Ctrl 或 Shift 多选。')
        ttk.Label(problems, textvariable=issue_note, style='Hint.TLabel', wraplength=1020).pack(fill='x', pady=8)
        row = ttk.Frame(problems)
        row.pack(fill='x', pady=5)
        files_tree = self.table(unlisted, [('图片路径', 710), ('大小', 100)], 10)
        ttk.Label(unlisted, text='这些图片尚未在 data.js 使用。请自己选择需要增加到相册的图片；图片文件不移动、不删除。', style='Hint.TLabel', wraplength=1000).pack(fill='x', pady=7)
        add_row = ttk.Frame(unlisted)
        add_row.pack(fill='x', pady=5)
        ttk.Label(add_row, text='增加到相册').pack(side='left', padx=(0, 8))
        chosen_album = tk.StringVar(value=self.album.get())
        album_box = ttk.Combobox(add_row, textvariable=chosen_album, width=30)
        album_box.pack(side='left')
        notice = tk.StringVar(value='只执行你选中的删除或增加，不生成备份；请核对选择后操作。')
        ttk.Label(window, textvariable=notice, style='Hint.TLabel', wraplength=1090, padding=12).pack(fill='x')
        footer = ttk.Frame(window, padding=(12, 0, 12, 12))
        footer.pack(fill='x')

        def fill(current):
            if not window.winfo_exists():
                return
            model['report'] = current
            issue_tree.delete(*issue_tree.get_children())
            files_tree.delete(*files_tree.get_children())
            for i, issue in enumerate(current['issues']):
                can_delete = issue['kind'] in ('missing_photo', 'missing_cover', 'duplicate_photo')
                issue_tree.insert('', 'end', iid=str(i), values=(issue['type'], issue['album'], issue['title'], issue['path'], '可选删除' if can_delete else '手动核对'))
            for i, item in enumerate(current['unlisted']):
                files_tree.insert('', 'end', iid=str(i), values=(item['path'], self.format_file_size(item['size'])))
            album_box['values'] = current['album_names']
            c = current['counts']
            summary.set('检查了 %d 个相册、%d 条引用、%d 个图片文件 · 缺失 %d · 重复 %d · 大小写 %d · 路径异常 %d · 未登记 %d' % (c['albums'], c['references'], c['files'], c['missing'], c['duplicates'], c['case'], c['invalid'], c['unlisted']))
            issue_note.set('选择一行查看具体建议；可用 Ctrl 或 Shift 多选。')

        def reload_report():
            root = Path(model['report']['root'])
            self.run('重新检查图片与代码', lambda: core.inspect_image_references(root, self.worker_progress), fill)

        def after_change(message):
            def done(current):
                fill(current)
                self.refresh_site(preserve_jobs=True)
                self.refresh_upload_list()
                notice.set(message + ' 已重新检查，可继续处理或预览网站。')
            return done

        def delete_selected():
            try:
                self.guard_idle()
                current = model['report']
                selected = [current['issues'][int(i)]['id'] for i in issue_tree.selection()]
                if not selected:
                    raise ValueError('请先选中需要删除的照片代码。')
                root = Path(current['root'])
                if root != self.root_path():
                    raise ValueError('主窗口已经切换网站，请关闭此窗口后重新检查。')
                def work():
                    core.delete_image_entries(root, STATE, current, selected)
                    return core.inspect_image_references(root, self.worker_progress)
                self.run('删除选中的照片代码', work, after_change('选中的照片代码已删除，图片文件保留。'))
            except Exception as e:
                self.error(e)

        def register():
            try:
                self.guard_idle()
                current = model['report']
                paths = [current['unlisted'][int(i)]['path'] for i in files_tree.selection()]
                album = chosen_album.get().strip()
                if not paths or not album:
                    raise ValueError('请选择要增加的图片，并选择或输入相册名称。')
                root = Path(current['root'])
                if root != self.root_path():
                    raise ValueError('主窗口已经切换网站，请关闭此窗口后重新检查。')
                def work():
                    core.register_unlisted_images(root, STATE, current, paths, album)
                    return core.inspect_image_references(root, self.worker_progress)
                self.run('增加选中的图片到相册', work, after_change('选中的图片已增加到“%s”。' % album))
            except Exception as e:
                self.error(e)

        def suggestion(_=None):
            selected = issue_tree.selection()
            if selected:
                issue = model['report']['issues'][int(selected[0])]
                can_delete = issue['kind'] in ('missing_photo', 'missing_cover', 'duplicate_photo')
                issue_note.set(issue['suggestion'] + (' · 可选择删除这条照片代码' if can_delete else ' · 只提示，需手动核对，不执行删除'))

        def select_deletable():
            issue_tree.selection_set([str(i) for i, issue in enumerate(model['report']['issues']) if issue['kind'] in ('missing_photo', 'missing_cover', 'duplicate_photo')])

        def locate():
            try:
                selected = files_tree.selection()
                if selected:
                    path = Path(model['report']['root']) / model['report']['unlisted'][int(selected[0])]['path']
                    core.reveal_file(path)
            except Exception as e:
                self.error(e)

        def export():
            dest = filedialog.asksaveasfilename(parent=window, title='导出检查报告', initialdir=str(BASE), initialfile='图片与代码检查报告.csv', defaultextension='.csv', filetypes=[('CSV 检查报告', '*.csv')])
            if dest:
                try:
                    import csv, io
                    output = io.StringIO(newline='')
                    writer = csv.writer(output)
                    writer.writerow(['问题类型', '相册或栏目', '照片标题', '图片路径', '建议'])
                    for issue in model['report']['issues']:
                        writer.writerow([issue['type'], issue['album'], issue['title'], issue['path'], issue['suggestion']])
                    for item in model['report']['unlisted']:
                        writer.writerow(['未登记图片', '', '', item['path'], item['suggestion']])
                    core.atomic(dest, output.getvalue().encode('utf-8-sig'))
                    notice.set('检查报告已导出。')
                except Exception as e:
                    self.error(e)

        issue_tree.bind('<<TreeviewSelect>>', suggestion)
        ttk.Button(row, text='全选可删除项', command=select_deletable).pack(side='left')
        ttk.Button(row, text='删除选中的照片代码', style='Accent.TButton', command=delete_selected).pack(side='right')
        ttk.Button(add_row, text='增加选中的图片到相册', command=register).pack(side='left', padx=10)
        ttk.Button(add_row, text='在文件管理器中显示', command=locate).pack(side='left')
        ttk.Button(footer, text='重新检查', command=reload_report).pack(side='left')
        ttk.Button(footer, text='导出报告…', command=export).pack(side='left', padx=8)
        ttk.Button(footer, text='预览本地网站', command=lambda: webbrowser.open((Path(model['report']['root']) / 'index.html').as_uri(), new=2)).pack(side='left')
        ttk.Button(footer, text='关闭', command=window.destroy).pack(side='right')
        fill(report)
        return window

    def pending_job(self):
        root = self.root_path()
        target = self.target.get().strip().replace('\\', '/')
        if not core.within(root / target, root / 'assets'):
            raise ValueError('照片存放文件夹必须在当前网站 assets 内。')
        return {'items': list(self.files), 'target': target, 'album': self.album.get().strip()}

    def upload_jobs(self):
        jobs = list(self.jobs)
        if self.files:
            jobs.append(self.pending_job())
        return jobs

    def current_upload_code(self):
        try:
            self.guard_idle()
            jobs = self.upload_jobs()
            if jobs:
                code = core.upload_code(self.root_path(), jobs, self.get_options())
            elif self.last_upload_code:
                code = self.last_upload_code
            else:
                raise ValueError('请先选择照片和相册，这里生成的是本次添加照片的代码。')
            self.show_code(code, '本次添加照片的 data.js 代码')
        except Exception as e:
            self.error(e)

    def preview_upload_files(self, selected_batch=False):
        try:
            self.guard_idle()
            jobs = self.upload_jobs()
            selection = self.jobs_tree.selection()
            if selected_batch and selection:
                rows = [self.upload_rows[i] for i in selection if i in self.upload_rows]
                if rows:
                    entries = [row['entry'] for row in rows]
                    options = dict(self.get_options(), compress=False) if all(row['kind'] == 'saved' for row in rows) else self.get_options()
                    self.show_upload_preview(entries, options)
                    return
            if jobs:
                entries = core.upload_plan(self.root_path(), jobs, self.get_options())
                options = self.get_options()
            else:
                entries = self.last_upload_files
                options = dict(self.get_options(), compress=False)
            if not entries:
                raise ValueError('请先选择文件或文件夹，或双击待添加列表中的一批文件。')
            self.show_upload_preview(entries, options)
        except Exception as e:
            self.error(e)

    def schedule_upload_list(self):
        if self.upload_refresh_timer is not None:
            self.after_cancel(self.upload_refresh_timer)
        self.upload_refresh_timer = self.after_idle(self.refresh_upload_list)

    def show_upload_menu(self, event):
        row = self.jobs_tree.identify_row(event.y)
        if not row:
            return
        if row not in self.jobs_tree.selection():
            self.jobs_tree.selection_set(row)
        self.jobs_tree.focus(row)
        try:
            self.upload_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.upload_menu.grab_release()

    def reveal_selected_upload_file(self):
        try:
            selection = self.jobs_tree.selection()
            focused = self.jobs_tree.focus()
            row = focused if focused in selection else (selection[0] if selection else None)
            if row not in self.upload_rows:
                raise ValueError('请先在文件列表中选中一张照片。')
            entry = self.upload_rows[row]['entry']
            path = entry['source'] if entry['source'].exists() else entry['target']
            core.reveal_file(path)
        except Exception as e:
            self.error(e)

    def rescan_upload_files(self):
        try:
            self.guard_idle()
            self.upload_name_cache.clear()
            for job in self.jobs:
                if job.get('source_folder'):
                    folder = Path(job['source_folder'])
                    job['items'] = [(str(p), p.relative_to(folder).as_posix()) for p in core.collect(folder)]
                else:
                    job['items'] = core.refresh_selected_files(job['items'], job.get('file_ids', {}))
                job['file_ids'] = core.file_identities(job['items'])
            self.jobs = [job for job in self.jobs if job['items']]
            if self.selected_folder:
                folder = Path(self.selected_folder)
                self.files = [(str(p), p.relative_to(folder).as_posix()) for p in core.collect(folder)]
            elif self.files:
                self.files = core.refresh_selected_files(self.files, self.selected_file_ids)
            self.selected_file_ids = core.file_identities(self.files)
            if not self.jobs and not self.files and self.selected_folder is None and self.last_upload_files:
                old = self.last_upload_files
                by_path = {str(item['source']): item for item in old}
                by_id = {self.last_file_ids.get(str(item['source'])): item for item in old}
                updated = core.refresh_selected_files([(str(item['source']), item['source'].name) for item in old], self.last_file_ids)
                new_ids = core.file_identities(updated)
                self.last_upload_files = []
                for source, _ in updated:
                    original = by_path.get(source) or by_id.get(new_ids.get(source))
                    if original:
                        self.last_upload_files.append(dict(original, source=Path(source), target=Path(source)))
                self.last_file_ids = new_ids
            self.refresh_upload_list()
            count = len(self.upload_rows)
            self.source_label.set('列表已刷新 · %d 个文件 · 按数字 / 其几排序' % count)
            self.status.set('文件列表已重新读取，可查看改名后的文件、大小和保存位置。')
        except Exception as e:
            self.error(e)

    def refresh_upload_list(self):
        if self.upload_refresh_timer is not None:
            self.after_cancel(self.upload_refresh_timer)
            self.upload_refresh_timer = None
        if not hasattr(self, 'jobs_tree'):
            return
        self.jobs_tree.delete(*self.jobs_tree.get_children())
        self.upload_rows = {}
        root = getattr(self, 'loaded_site', BASE)
        batches = [('queued', i, job) for i, job in enumerate(self.jobs)]
        if self.files:
            batches.append(('pending', None, {'items': self.files, 'target': self.target.get().strip(), 'album': self.album.get().strip()}))
        try:
            options = self.get_options()
        except ValueError:
            options = {'compress': self.do_compress.get(), 'keep_png': self.keep_png.get(), 'side': 1600}
        for kind, job_index, job in batches:
            for file_index, (source, relative) in enumerate(job['items']):
                source = Path(source)
                state = '待添加'
                try:
                    info = source.stat()
                    key = (str(source), info.st_mtime_ns, info.st_size, options.get('compress'), options.get('keep_png'), options.get('side'))
                    if key not in self.upload_name_cache:
                        if len(self.upload_name_cache) > 5000:
                            self.upload_name_cache.clear()
                        self.upload_name_cache[key] = core.image_output_name(source, options)
                    name = self.upload_name_cache[key]
                    size = self.format_file_size(info.st_size)
                except Exception:
                    name, size, state = source.name, '无法读取', '文件待检查'
                target = (root / job['target'] / relative).with_name(name)
                if state == '待添加' and target.exists():
                    state = '自动覆盖' if self.overwrite.get() else '已存在，需检查'
                entry = {'source': source, 'target': target, 'album': job.get('album', ''), 'title': source.stem}
                self.insert_upload_row(entry, relative, size, state, kind, job_index, file_index)
        if not batches and self.selected_folder is None:
            for file_index, entry in enumerate(self.last_upload_files):
                try:
                    size = self.format_file_size(entry['source'].stat().st_size)
                except OSError:
                    size = '无法读取'
                self.insert_upload_row(entry, entry['source'].name, size, '已添加', 'saved', None, file_index)

    @staticmethod
    def format_file_size(size):
        return '%.1f MB' % (size / 1024 / 1024) if size >= 1024 * 1024 else '%.1f KB' % (size / 1024)

    def insert_upload_row(self, entry, filename, size, state, kind, job_index, file_index):
        root = getattr(self, 'loaded_site', BASE)
        target = entry['target']
        display = target.relative_to(root).as_posix() if core.within(target, root) else str(target)
        row = self.jobs_tree.insert('', 'end', values=(filename, entry['source'].suffix.lstrip('.').upper() or '文件', size, display, entry['album'] or '只复制文件', state))
        self.upload_rows[row] = {'kind': kind, 'job': job_index, 'file': file_index, 'entry': entry}

    def show_upload_preview(self, entries, options):
        window = tk.Toplevel(self)
        window.title('上传文件预览 · %d 个文件' % len(entries))
        window.geometry('1080x720')
        window.minsize(850, 600)
        ttk.Label(window, text='左侧选文件，右侧查看图片。勾选“处理后效果”可检查压缩、格式转换和 PNG 底色。', style='Hint.TLabel', wraplength=1000, padding=12).pack(fill='x')
        body = ttk.Frame(window, padding=(12, 0, 12, 0))
        body.pack(fill='both', expand=True)
        body.columnconfigure(0, weight=2)
        body.columnconfigure(1, weight=3)
        body.rowconfigure(0, weight=1)
        left, right = ttk.Frame(body), ttk.Frame(body)
        left.grid(row=0, column=0, sticky='nsew', padx=(0, 12))
        right.grid(row=0, column=1, sticky='nsew')
        files = self.table(left, [('文件名', 220), ('大小', 80)], 14)
        for i, item in enumerate(entries):
            source = item['source']
            size = source.stat().st_size
            files.insert('', 'end', iid=str(i), values=(source.name, '%.1f MB' % (size / 1024 / 1024) if size >= 1024 * 1024 else '%.1f KB' % (size / 1024)))
        processed = tk.BooleanVar(value=bool(options.get('compress')))
        ttk.Checkbutton(right, text='查看处理后效果（仅预览，尚不保存）', variable=processed).pack(anchor='w', pady=8)
        picture = tk.Label(right, bg='#E7DFC8', text='', anchor='center')
        picture.pack(fill='both', expand=True)
        detail = tk.StringVar()
        ttk.Label(right, textvariable=detail, wraplength=540, style='Hint.TLabel', padding=(0, 10)).pack(fill='x')
        def render(_=None):
            chosen = files.selection()
            if not chosen:
                return
            item = entries[int(chosen[0])]
            source = item['source']
            info = '原文件：%s\n保存到：%s\n相册：%s' % (source, item['target'], item['album'] or '仅复制文件')
            try:
                import io
                if processed.get():
                    _, data = core.image_bytes(source, options)
                    image_source = io.BytesIO(data)
                else:
                    image_source = str(source)
                with Image.open(image_source) as original:
                    image = ImageOps.exif_transpose(original).convert('RGBA')
                    dimensions = image.size
                    image.thumbnail((560, 435), Image.LANCZOS)
                paper = Image.new('RGBA', image.size, '#F6F0E2')
                paper.alpha_composite(image)
                bitmap = ImageTk.PhotoImage(paper, master=window)
                picture.configure(image=bitmap, text='')
                picture.image = bitmap
                info += '\n预览尺寸：%d × %d px' % dimensions
            except Exception as e:
                picture.configure(image='', text='此文件暂无图片预览\n' + source.name)
                picture.image = None
                info += '\n说明：' + str(e)
            detail.set(info)
        files.bind('<<TreeviewSelect>>', render)
        processed.trace_add('write', lambda *_: render())
        row = ttk.Frame(window, padding=12)
        row.pack(fill='x')
        def step(offset):
            current = int(files.selection()[0]) if files.selection() else 0
            index = max(0, min(len(entries) - 1, current + offset))
            files.selection_set(str(index))
            files.see(str(index))
        ttk.Button(row, text='上一张', command=lambda: step(-1)).pack(side='left')
        ttk.Button(row, text='下一张', command=lambda: step(1)).pack(side='left', padx=8)
        ttk.Button(row, text='关闭预览', command=window.destroy).pack(side='right')
        files.selection_set('0')
        render()
        return window

    def show_code(self, code, title):
        window = tk.Toplevel(self)
        window.title(title)
        window.geometry('1000x680')
        window.minsize(720, 460)
        hint = '第一个标签仅包含本次新增照片的代码，放入对应相册的 photos 数组；data.js 标签是合并后的完整文件。' if '本次照片 data.js 片段' in code else '可复制或导出完整文件，也可仅取相册片段。预览和复制不会改网站；应用资料请点击创建或保存相册。'
        ttk.Label(window, text=hint, style='Hint.TLabel', wraplength=930, padding=12).pack(fill='x')
        tabs = ttk.Notebook(window)
        tabs.pack(fill='both', expand=True, padx=12)
        names = list(code)
        for name in names:
            frame = ttk.Frame(tabs)
            tabs.add(frame, text=name)
            frame.rowconfigure(0, weight=1)
            frame.columnconfigure(0, weight=1)
            text = tk.Text(frame, wrap='none', bg='#FCF9F1', font=('Consolas', 11), padx=10, pady=8)
            text.insert('1.0', code[name])
            text.configure(state='disabled')
            text.grid(row=0, column=0, sticky='nsew')
            ys = ttk.Scrollbar(frame, orient='vertical', command=text.yview)
            xs = ttk.Scrollbar(frame, orient='horizontal', command=text.xview)
            ys.grid(row=0, column=1, sticky='ns')
            xs.grid(row=1, column=0, sticky='ew')
            text.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)
        row = ttk.Frame(window, padding=12)
        row.pack(fill='x')
        info = tk.StringVar(value='完整 data.js 请替换 js/data.js；简介对应 album-desc.js。')
        ttk.Label(row, textvariable=info, style='Hint.TLabel').pack(side='left')
        def copy():
            name = names[tabs.index('current')]
            window.clipboard_clear()
            window.clipboard_append(code[name])
            info.set('已复制：' + name)
        def export():
            name = names[tabs.index('current')]
            filename = name if name.endswith('.js') else name + '.txt'
            dest = filedialog.asksaveasfilename(parent=window, title='导出 ' + name, initialdir=str(BASE), initialfile=filename, defaultextension=Path(filename).suffix)
            if dest:
                try:
                    self.guard_idle()
                    with core.Transaction(STATE, '导出代码：' + name) as tx:
                        tx.write(dest, code[name].encode('utf-8'))
                    info.set('已导出：' + filename)
                except Exception as e:
                    self.error(e)
        ttk.Button(row, text='导出当前代码…', command=export).pack(side='right')
        ttk.Button(row, text='复制当前代码', command=copy).pack(side='right', padx=8)

    def rename_page(self, page):
        self.rename_dir = tk.StringVar()
        self.rename_files = None
        self.rename_selection_text = tk.StringVar(value='文件夹模式：处理目录内文件，点击“生成预览”检查。')
        row, _ = self.field(page, '文件夹', self.rename_dir)
        ttk.Button(row, text='选择照片…', command=self.choose_rename_files).pack(side='left', padx=(8, 0))
        ttk.Button(row, text='选择文件夹…', command=self.choose_rename_folder).pack(side='left', padx=(8, 0))
        ttk.Label(page, textvariable=self.rename_selection_text, style='Hint.TLabel').pack(anchor='w', pady=(0, 3))
        self.rename_mode = tk.StringVar(value='其一／其二（按标题分组）')
        row = ttk.Frame(page)
        row.pack(fill='x', pady=5)
        ttk.Label(row, text='命名规则', width=15).pack(side='left')
        ttk.Combobox(row, textvariable=self.rename_mode, state='readonly', values=['其一／其二（按标题分组）', '数字编号']).pack(side='left', fill='x', expand=True)
        self.filter_mode = tk.StringVar(value='全部')
        ttk.Combobox(row, textvariable=self.filter_mode, state='readonly', values=['全部', '仅中文', '仅英文'], width=10).pack(side='left', padx=(8, 0))
        self.prefix = tk.StringVar(value='')
        self.rename_add_prefix = tk.BooleanVar(value=False)
        self.start = tk.StringVar(value='1')
        self.pad = tk.StringVar(value='0')
        row = ttk.Frame(page)
        row.pack(fill='x', pady=5)
        ttk.Checkbutton(row, text='添加前缀', variable=self.rename_add_prefix).pack(side='left', padx=(0, 7))
        self.rename_prefix_entry = ttk.Entry(row, textvariable=self.prefix, width=22, state='disabled')
        self.rename_prefix_entry.pack(side='left', padx=(0, 18))
        self.rename_add_prefix.trace_add('write', lambda *_: self.rename_prefix_entry.configure(state='normal' if self.rename_add_prefix.get() else 'disabled'))
        for label, var, width in [('起始编号', self.start, 8), ('补零位数', self.pad, 8)]:
            ttk.Label(row, text=label).pack(side='left', padx=(0, 7))
            ttk.Entry(row, textvariable=var, width=width).pack(side='left', padx=(0, 18))
        self.rename_recursive = tk.BooleanVar(value=False)
        self.rename_recursive_check = ttk.Checkbutton(row, text='包含子文件夹', variable=self.rename_recursive)
        self.rename_recursive_check.pack(side='left')
        ttk.Label(page, text='两种规则均可勾选添加前缀，用一个空格连接，例如“圆明园 海晏堂”“圆明园 海晏堂 其一”。\n“其一”每组独立编号，十一开始不加“其”；单张只留标题。数字编号不保留原标题。网站内图片同步更新 data.js 路径和 title。', style='Hint.TLabel', wraplength=970).pack(anchor='w', pady=5)
        self.rename_tree = self.table(page, [('原文件名', 395), ('新文件名', 395), ('状态', 110)], 5)
        row = ttk.Frame(page)
        row.pack(fill='x', pady=3)
        ttk.Button(row, text='生成预览', command=self.preview_rename).pack(side='left')
        self.rename_apply = ttk.Button(row, text='按预览执行重命名', style='Accent.TButton', command=self.start_rename, state='disabled')
        self.rename_apply.pack(side='right')
        for var in (self.rename_dir, self.rename_mode, self.filter_mode, self.prefix, self.rename_add_prefix, self.start, self.pad, self.rename_recursive):
            var.trace_add('write', lambda *_: self.invalidate_plan())
        self.rename_dir.trace_add('write', lambda *_: self.rename_folder_changed())

    def compress_page(self, page):
        self.comp_source = tk.StringVar()
        self.comp_dest = tk.StringVar(value=str(Path(self.site.get()) / 'assets/images') if self.site.get() else '')
        for label, var in [('图片源文件夹', self.comp_source), ('图片输出目录', self.comp_dest)]:
            row, _ = self.field(page, label, var)
            ttk.Button(row, text='选择', command=lambda v=var: self.choose_dir(v)).pack(side='left', padx=(8, 0))
        self.side = tk.StringVar(value='1600')
        self.quality = tk.StringVar(value='82')
        self.bg = tk.StringVar(value='#F6F0E2')
        row = ttk.Frame(page)
        row.pack(fill='x', pady=7)
        for label, var, width in [('最长边 px', self.side, 8), ('JPEG 质量', self.quality, 7), ('透明 PNG 转 JPG 底色', self.bg, 12)]:
            ttk.Label(row, text=label).pack(side='left', padx=(0, 6))
            ttk.Entry(row, textvariable=var, width=width).pack(side='left', padx=(0, 14))
        ttk.Button(row, text='取色', command=self.pick_bg).pack(side='left')
        row = ttk.Frame(page)
        row.pack(fill='x', pady=4)
        for label, color in [('卡片纸色', '#F6F0E2'), ('页面宣纸', '#EFE8D6'), ('老纸', '#E7DFC8')]:
            ttk.Button(row, text=label, command=lambda c=color: self.bg.set(c)).pack(side='left', padx=(0, 8))
        ttk.Checkbutton(row, text='PNG 保留透明和格式', variable=self.keep_png).pack(side='left', padx=12)
        ttk.Label(page, text='默认 JPG：最长边 1600、质量 82；小 JPG、GIF / SVG / 动画保持原样。透明 PNG 按所选底色合成。\n源和输出目录相同：只保留处理后的文件；目录不同：保留原图。同名直接覆盖，不生成备份。', style='Hint.TLabel', wraplength=970).pack(anchor='w', pady=7)
        ttk.Button(page, text='压缩并导出图片', style='Accent.TButton', command=self.start_compress).pack(anchor='e')
        ttk.Separator(page).pack(fill='x', pady=14)
        self.zip_source = tk.StringVar()
        row, _ = self.field(page, 'ZIP 源文件夹', self.zip_source)
        ttk.Button(row, text='选择', command=lambda: self.choose_dir(self.zip_source)).pack(side='left', padx=(8, 0))
        ttk.Label(page, text='ZIP 打包会排除 .git、隐藏目录、桌面工具及其备份和构建目录。', style='Hint.TLabel').pack(anchor='w')
        ttk.Button(page, text='打包为 ZIP…', command=self.start_zip).pack(anchor='e', pady=7)

    def github_page(self, page):
        ttk.Label(page, text='把整理好的行迹，送回你的 GitHub。', style='Title.TLabel').pack(anchor='w', pady=(5, 15))
        self.git_summary = tk.StringVar(value='点击“查看待上传内容”读取当前分支与仓库。')
        ttk.Label(page, textvariable=self.git_summary, wraplength=950).pack(anchor='w', pady=5)
        self.commit_message = tk.StringVar(value='更新网站照片与内容')
        ttk.Label(page, text='点击上传会打开内置 push.bat 的命令窗口，使用当前选中的网站文件夹。\n更新说明、登录和仓库选项都在该窗口操作，Git 的真实传输进度也显示在那里。\n沿用你原来的脚本逻辑；本机仍需安装 Git。网络过慢时可在窗口按 Ctrl+C 中止，再重新上传。', style='Hint.TLabel', wraplength=960).pack(anchor='w', pady=12)
        self.git_text = tk.Text(page, height=7, bg='#F6F0E2', relief='flat', font=('Consolas', 10), padx=10, pady=8, state='disabled')
        self.git_text.pack(fill='both', expand=True, pady=6)
        row = ttk.Frame(page)
        row.pack(fill='x', pady=5)
        ttk.Button(row, text='查看待上传内容', command=self.git_status).pack(side='left')
        ttk.Button(row, text='一键上传 GitHub', style='Accent.TButton', command=self.start_publish).pack(side='right')

    def design_page(self, page):
        ttk.Label(page, text='图由你画，山水由你定。', style='Title.TLabel').pack(anchor='w', pady=(5, 18))
        ttk.Label(page, text='可以直接选择你设计的 PNG / JPG / ICO：程序会复制到自己的素材目录，原图保留。\n图标建议使用方形透明 PNG（256×256 或更大）；横幅建议 720×180，显示在右上角。', style='Hint.TLabel').pack(anchor='w', pady=8)
        row = ttk.Frame(page)
        row.pack(fill='x', pady=12)
        ttk.Button(row, text='设置窗口图标…', command=lambda: self.set_design('icon')).pack(side='left')
        ttk.Button(row, text='设置顶部横幅…', command=lambda: self.set_design('banner')).pack(side='left', padx=10)
        ttk.Button(row, text='恢复默认设计', command=self.reset_design).pack(side='left')
        ttk.Label(page, text='界面配色取自网站', font=('KaiTi', 18)).pack(anchor='w', pady=(15, 9))
        row = ttk.Frame(page)
        row.pack(fill='x')
        for label, color in [('宣纸', '#EFE8D6'), ('卡纸', '#F6F0E2'), ('松烟墨', '#2B2B26'), ('黛青', '#2C4A52'), ('朱砂', '#A83A32'), ('鎏金', '#A98545')]:
            cell = ttk.Frame(row)
            cell.pack(side='left', padx=(0, 20))
            tk.Label(cell, bg=color, width=10, height=3).pack()
            ttk.Label(cell, text=label + '\n' + color, justify='center').pack(pady=5)
        ttk.Label(page, text='更换 EXE 文件本身的图标：把你的图片命名为 custom-icon.png 放入 desktop-tool，再运行 build.ps1 重新打包。\n窗口内更换图标无需重新打包。配置与日志在程序旁的 _data 目录，不保存原图备份。', style='Hint.TLabel', wraplength=960).pack(anchor='w', pady=20)

    def error(self, e):
        self.log('未完成：' + str(e))
        messagebox.showerror('操作未完成', str(e), parent=self)

    def guard_idle(self):
        if self.busy:
            raise ValueError('当前任务仍在执行，请完成后再操作。')

    def choose_site(self):
        if self.busy:
            return
        initial = self.site.get() if self.site.get() and Path(self.site.get()).is_dir() else str(BASE)
        folder = filedialog.askdirectory(title='选择个人网站文件夹（包含 index.html、js 和 css）', initialdir=initial, mustexist=True)
        if folder:
            self.site.set(folder)
            self.refresh_site()

    def refresh_site(self, initial=False, preserve_jobs=False):
        try:
            self.guard_idle()
            if not self.site.get().strip():
                raise ValueError('请点击“选择网站文件夹…”定位你的个人网站。')
            root = Path(self.site.get()).resolve()
            core.writable(root)
            if not core.is_site(root):
                raise ValueError('这不是网站根目录：请选择同时包含 index.html、js/data.js 和 css/style.css 的文件夹。')
            albums, dirs, palette = core.site_info(root)
            if root != getattr(self, 'loaded_site', None):
                self.comp_dest.set(str(root / 'assets/images'))
                self.files = []
                self.selected_folder = None
                self.selected_file_ids = {}
                self.last_file_ids = {}
                self.last_upload_code = None
                self.last_upload_files = []
            self.loaded_site = root
            self.albums = albums
            if not preserve_jobs:
                self.jobs.clear()
                self.jobs_tree.delete(*self.jobs_tree.get_children())
            self.album_combo['values'] = [''] + [a['name'] for a in albums]
            self.edit_combo['values'] = [a['name'] for a in albums]
            self.featured_combo['values'] = [a['name'] for a in albums]
            self.load_featured()
            places = featured.map_places(root)
            self.map_city_combo['values'] = list(dict.fromkeys(place['city'] for place in places))
            if self.map_city.get() not in self.map_city_combo['values']:
                self.map_city.set(places[0]['city'] if places else '')
            self.load_map_city()
            self.merge_mother_combo['values'] = [a['name'] for a in albums]
            self.merge_sources.delete(0, 'end')
            for item in albums:
                self.merge_sources.insert('end', item['name'])
            if self.merge_mother.get() not in self.merge_mother_combo['values']:
                self.merge_mother.set('')
                self.merge_folder.set('')
            self.invalidate_merge()
            if not preserve_jobs:
                self.new_album()
            self.target_combo['values'] = dirs
            history = self.path_history()
            remembered = history.get('target', 'assets/images')
            self.target.set(remembered if core.within(root / remembered, root / 'assets') else 'assets/images')
            self.rename_dir.set(str(root / 'assets/images'))
            self.zip_source.set(str(root))
            self.bg.set(palette['card'])
            self.settings['site'] = str(root)
            try:
                self.settings['site_relative'] = os.path.relpath(str(root), str(BASE))
            except ValueError:
                self.settings.pop('site_relative', None)
            self.save_settings()
            self.refresh_upload_list()
            self.status.set('已读取网站 · %d 个相册 · %d 个照片文件夹' % (len(albums), len(dirs)))
        except Exception as e:
            self.status.set('未找到网站或原路径已失效 · 请点击“选择网站文件夹…”重新定位，程序会记住新位置。')
            if not initial:
                self.error(e)

    def root_path(self):
        root = Path(self.site.get()).resolve()
        if root != getattr(self, 'loaded_site', None):
            raise ValueError('网站路径已更改，请先点击“读取网站内容”。')
        return root

    def choose_dir(self, var):
        folder = filedialog.askdirectory(initialdir=var.get() if Path(var.get()).is_dir() else str(BASE))
        if folder:
            var.set(folder)

    def path_history(self):
        root = str(self.root_path())
        return self.settings.setdefault('photo_path_history', {}).setdefault(root, {})

    def remember_photo_paths(self, source=None):
        history = self.path_history()
        if source:
            history['source'] = str(Path(source).resolve())
        target = self.target.get().strip().replace('\\', '/')
        if core.within(self.root_path() / target, self.root_path() / 'assets'):
            history['target'] = target
        self.save_settings()

    def photo_dialog_start(self):
        previous = self.path_history().get('source', '')
        return previous if previous and Path(previous).is_dir() else str(self.root_path())

    def use_source_folder(self, folder):
        root, folder = self.root_path(), Path(folder).resolve()
        if core.within(folder, root / 'assets'):
            self.target.set(folder.relative_to(root).as_posix())
            self.log('已自动使用照片所在文件夹：' + str(folder))
        else:
            target = Path('assets/images') / folder.name
            self.target.set(target.as_posix())
            self.log('原图在网站外，将复制到网站内的同名文件夹：' + str(root / target))
        self.remember_photo_paths(source=folder)

    def pick_files(self):
        if self.busy:
            return
        files = filedialog.askopenfilenames(title='选择这批要导入的文件', initialdir=self.photo_dialog_start())
        if files:
            self.files = core.sorted_upload_items([(str(Path(f).resolve()), Path(f).name) for f in files])
            self.selected_folder = None
            self.selected_file_ids = core.file_identities(self.files)
            self.source_label.set('%d 个文件' % len(files))
            self.batch_label = Path(files[0]).parent.name
            self.use_source_folder(Path(files[0]).parent)
            self.refresh_upload_list()

    def pick_folder(self):
        if self.busy:
            return
        folder = filedialog.askdirectory(title='选择一批文件，保留子目录结构', initialdir=self.photo_dialog_start())
        if folder:
            folder = str(Path(folder).resolve())
            paths = core.collect(folder)
            self.files = [(str(p), p.relative_to(folder).as_posix()) for p in paths]
            self.selected_folder = folder
            self.selected_file_ids = core.file_identities(self.files)
            self.batch_label = Path(folder).name
            self.source_label.set(self.batch_label + ' · %d 个文件' % len(paths))
            self.use_source_folder(folder)
            self.refresh_upload_list()

    def pick_target(self):
        try:
            root = self.root_path()
            current = root / self.target.get()
            folder = filedialog.askdirectory(initialdir=str(current if current.is_dir() else root))
            if folder:
                if not core.within(folder, root / 'assets'):
                    raise ValueError('请选择网站 assets 内的文件夹。也可以直接在目录框填写新的子目录。')
                self.target.set(Path(folder).resolve().relative_to(root).as_posix())
                self.remember_photo_paths()
        except Exception as e:
            self.error(e)

    def album_selected(self, _=None):
        if self.files or self.path_history().get('target'):
            return
        for a in self.albums:
            if a['name'] == self.album.get() and a['refs']:
                parents = [str(Path(ref).parent) for ref in a['refs'] if ref.startswith('assets/')]
                if parents:
                    self.target.set(Path(os.path.commonpath(parents)).as_posix())

    def add_job(self):
        try:
            self.guard_idle()
            root = self.root_path()
            target = self.target.get().strip().replace('\\', '/')
            if not core.within(root / target, root / 'assets'):
                raise ValueError('目标文件夹必须位于网站 assets 内。')
            if not self.files:
                raise ValueError('请先选择文件或文件夹。')
            job = {'items': list(self.files), 'target': target, 'album': self.album.get().strip()}
            job['source_folder'] = self.selected_folder
            job['file_ids'] = dict(self.selected_file_ids)
            self.jobs.append(job)
            self.remember_photo_paths()
            self.files = []
            self.selected_folder = None
            self.selected_file_ids = {}
            self.refresh_upload_list()
            self.source_label.set('已加入待添加列表，可以选择下一批照片')
        except Exception as e:
            self.error(e)

    def remove_job(self):
        if self.busy:
            return
        selected = self.jobs_tree.selection()
        rows = [self.upload_rows[i] for i in selected if i in self.upload_rows]
        pending = {row['file'] for row in rows if row['kind'] == 'pending'}
        self.files = [item for i, item in enumerate(self.files) if i not in pending]
        for index, job in enumerate(self.jobs):
            removed = {row['file'] for row in rows if row['kind'] == 'queued' and row['job'] == index}
            job['items'] = [item for i, item in enumerate(job['items']) if i not in removed]
        self.jobs = [job for job in self.jobs if job['items']]
        self.refresh_upload_list()

    def get_options(self):
        return {'compress': self.do_compress.get(), 'keep_png': self.keep_png.get(), 'overwrite': self.overwrite.get(), 'side': int(self.side.get()), 'quality': int(self.quality.get()), 'bg': self.bg.get().strip(), 'recursive': True}

    def start_import(self):
        try:
            root, options = self.root_path(), self.get_options()
            jobs = self.upload_jobs()
            if not jobs:
                raise ValueError('请先选择照片或文件夹，然后选择相册。可直接点击添加，多批照片才需要加入列表。')
            self.remember_photo_paths()
            def work():
                self.worker_progress('准备本次照片代码', 0, 0, '正在核对图片格式与目标路径')
                code = core.upload_code(root, jobs, options)
                plan = core.upload_plan(root, jobs, options)
                count = core.import_jobs(root, STATE, jobs, options, self.worker_log, self.worker_progress)
                return count, code, plan
            self.run('添加照片并更新网站代码', work, self.import_done)
        except Exception as e:
            self.error(e)

    def import_done(self, result):
        count, code, plan = result
        self.last_upload_code = code
        self.last_upload_files = [dict(item, source=item['target']) for item in plan]
        self.last_file_ids = core.file_identities([(str(item['source']), item['source'].name) for item in self.last_upload_files])
        self.files = []
        self.selected_folder = None
        self.selected_file_ids = {}
        self.jobs.clear()
        self.jobs_tree.delete(*self.jobs_tree.get_children())
        self.refresh_site()
        self.source_label.set('已完成，可预览已保存的文件或获取本次照片代码')
        self.log('已添加 %d 个文件，相册照片和自动关键词已更新；可到“相册与代码”继续增删关键词。' % count)

    def invalidate_plan(self):
        self.plan = []
        self.rename_apply.configure(state='disabled')

    def rename_folder_changed(self):
        self.rename_files = None
        self.rename_recursive_check.configure(state='normal')
        self.rename_selection_text.set('文件夹模式：处理目录内文件，点击“生成预览”检查。')
        self.rename_tree.delete(*self.rename_tree.get_children())

    def choose_rename_folder(self):
        try:
            self.guard_idle()
            self.choose_dir(self.rename_dir)
        except Exception as e:
            self.error(e)

    def choose_rename_files(self):
        try:
            self.guard_idle()
            initial = self.rename_dir.get()
            paths = filedialog.askopenfilenames(parent=self, title='选择要批量改名的照片（可多选）',
                initialdir=initial if Path(initial).is_dir() else str(BASE),
                filetypes=[('照片', '*.jpg *.jpeg *.png *.webp *.bmp *.tif *.tiff *.gif *.svg'), ('所有文件', '*.*')])
            if not paths:
                return
            selected = list(dict.fromkeys(str(Path(p).resolve()) for p in paths))
            folder = os.path.commonpath([str(Path(p).parent) for p in selected])
            self.rename_dir.set(folder)
            self.rename_files = selected
            self.rename_recursive_check.configure(state='disabled')
            self.rename_selection_text.set('已选择 %d 个文件：仅处理所选照片，点击“生成预览”检查；选择文件夹可切回整目录。' % len(selected))
            self.invalidate_plan()
        except Exception as e:
            self.error(e)

    def rename_options(self):
        selected = tuple(self.rename_files) if self.rename_files is not None else None
        return (self.rename_dir.get(), self.rename_mode.get(), self.prefix.get(), self.start.get(), self.pad.get(), self.rename_recursive.get(), self.filter_mode.get(), selected, self.rename_add_prefix.get())

    def preview_rename(self):
        try:
            self.guard_idle()
            options = self.rename_options()
            folder, mode, prefix, start, pad, recursive, filter_mode, selected, add_prefix = options
            start, pad = int(start), int(pad)
            self.invalidate_plan()
            def work():
                self.worker_progress('生成改名预览', 0, 0, '正在读取所选照片' if selected is not None else '正在扫描文件夹')
                preview = core.rename_plan(folder, mode, prefix, start, pad, recursive, filter_mode, include_unchanged=True, add_prefix=add_prefix, selected_files=selected)
                changes = [(a, b) for a, b in preview if a != b]
                hashes = {}
                for i, (a, _) in enumerate(changes, 1):
                    hashes[str(a)] = core.digest(a)
                    self.worker_progress('核对待改名文件', i, len(changes) + 1, '%d/%d 个 · %s' % (i, len(changes), a.name))
                return preview, changes, hashes
            def done(result):
                if self.rename_options() != options:
                    self.invalidate_plan()
                    self.status.set('改名规则已变化，请重新生成预览。')
                    return
                preview, self.plan, self.plan_hashes = result
                self.rename_tree.delete(*self.rename_tree.get_children())
                base = Path(folder).resolve()
                for a, b in preview:
                    self.rename_tree.insert('', 'end', values=(a.relative_to(base).as_posix(), b.relative_to(base).as_posix(), '名称不变' if a == b else '将修改'))
                self.rename_apply.configure(state='normal' if self.plan else 'disabled')
                self.log('预览：共 %d 个文件，%d 个会改名，%d 个名称不变。' % (len(preview), len(self.plan), len(preview) - len(self.plan)))
            self.run('生成重命名预览', work, done)
        except Exception as e:
            self.error(e)

    def start_rename(self):
        try:
            self.guard_idle()
            root = self.root_path()
            plan = list(self.plan)
            if not plan:
                raise ValueError('请先生成重命名预览。')
            hashes = dict(self.plan_hashes)
            def work():
                for i, (a, _) in enumerate(plan, 1):
                    self.worker_progress('检查预览是否仍有效', 0, 0, '%d/%d 个 · %s' % (i, len(plan), a.name))
                    if core.digest(a) != hashes[str(a)]:
                        raise ValueError('文件在预览后发生变化，请重新生成预览。')
                core.apply_rename(root, STATE, plan, self.worker_log, self.worker_progress)
            def done(_):
                if self.rename_files is not None:
                    renamed = {str(a): str(b) for a, b in plan}
                    self.rename_files = [renamed.get(p, p) for p in self.rename_files]
                self.preview_rename()
            self.run('批量重命名', work, done)
        except Exception as e:
            self.error(e)

    def pick_bg(self):
        color = colorchooser.askcolor(color=self.bg.get(), parent=self)[1]
        if color:
            self.bg.set(color)

    def start_compress(self):
        try:
            if not self.comp_source.get().strip():
                raise ValueError('请选择图片源文件夹。')
            source, dest, opts = self.comp_source.get(), self.comp_dest.get(), dict(self.get_options(), site_root=str(self.root_path()))
            self.run('图片压缩', lambda: core.compress_folder(source, dest, STATE, opts, self.worker_log, self.worker_progress))
        except Exception as e:
            self.error(e)

    def start_zip(self):
        source = self.zip_source.get()
        if not Path(source).is_dir():
            self.error(ValueError('请选择 ZIP 源文件夹。'))
            return
        dest = filedialog.asksaveasfilename(title='保存 ZIP（选择源目录之外）', initialdir=str(BASE), initialfile=Path(source).name + '.zip', defaultextension='.zip', filetypes=[('ZIP 压缩包', '*.zip')], confirmoverwrite=False)
        if dest:
            self.run('ZIP 打包', lambda: core.make_zip(source, dest, self.worker_log, self.worker_progress))

    def git_status(self):
        try:
            root = self.root_path()
            def work():
                return (core.git(root, ['remote', 'get-url', 'origin']), core.git(root, ['branch', '--show-current']), core.git(root, ['status', '--short']))
            def done(result):
                url, branch, status = result
                self.git_summary.set(url + '  ·  ' + branch)
                self.git_text.configure(state='normal')
                self.git_text.delete('1.0', 'end')
                self.git_text.insert('end', status or '网站文件无未提交修改；仍可上传此前尚未推送的提交。')
                self.git_text.configure(state='disabled')
            self.run('读取 Git 状态', work, done)
        except Exception as e:
            self.error(e)

    def start_publish(self):
        try:
            self.guard_idle()
            if self.upload_process is not None and self.upload_process.poll() is None:
                self.status.set('GitHub 上传窗口已经打开，请在该窗口继续操作；关闭后可以重新打开。')
                return
            root = self.root_path()
            self.upload_process, script = core.launch_push_script(root, STATE)
            self.status.set('已打开内置 push.bat 上传窗口，请在窗口中填写说明并查看真实进度。')
            self.log('已打开 GitHub 上传窗口 · 网站：' + str(root) + '\n上传结果以命令窗口内的 Git 提示为准。')
        except Exception as e:
            self.error(e)


    def run(self, label, work, done=None):
        try:
            self.guard_idle()
        except Exception as e:
            self.error(e)
            return
        self.busy = True
        self.active_label = label
        self.operation_started = time.monotonic()
        self.last_progress_at = self.operation_started
        with self.progress_lock:
            self.pending_progress = None
        if self.operation_timer is not None:
            self.after_cancel(self.operation_timer)
            self.operation_timer = None
        self.status.set('正在' + label + '…')
        self.progress.stop()
        self.progress.configure(mode='indeterminate', value=0)
        self.progress_text.set(label + ' · 正在准备…')
        self.progress.start(12)
        self.tick_operation()
        self.log('开始' + label)
        def worker():
            try:
                result = work()
                self.events.put(('done', (label, result, done)))
            except Exception as e:
                self.events.put(('error', e))
        threading.Thread(target=worker, daemon=True).start()

    def worker_log(self, text):
        self.events.put(('log', text))

    def worker_progress(self, stage, done, total, detail=''):
        # 快速处理成千上万个文件时只保留最新进度，不让消息队列撑满。
        with self.progress_lock:
            self.pending_progress = (stage, done, total, detail, time.monotonic())

    def tick_operation(self):
        self.operation_timer = None
        if not self.busy or self.operation_started is None:
            return
        seconds = int(time.monotonic() - self.operation_started)
        text = '已用 %02d:%02d' % divmod(seconds, 60)
        if self.last_progress_at is not None and time.monotonic() - self.last_progress_at >= 10:
            text += ' · 当前步骤仍在处理中'
        self.elapsed_text.set(text)
        self.operation_timer = self.after(500, self.tick_operation)

    def update_operation_progress(self):
        with self.progress_lock:
            progress, self.pending_progress = self.pending_progress, None
        if progress is None or not self.busy:
            return
        stage, done, total, detail, stamp = progress
        self.last_progress_at = stamp
        if total and total > 0:
            value = max(0, min(100, done * 100.0 / total))
            self.progress.stop()
            self.progress.configure(mode='determinate', maximum=100, value=value)
            suffix = ' · %d%%' % value
        else:
            if str(self.progress.cget('mode')) != 'indeterminate':
                self.progress.configure(mode='indeterminate', value=0)
                self.progress.start(12)
            suffix = ''
        detail = str(detail)
        if len(detail) > 78:
            detail = detail[:75] + '…'
        self.progress_text.set(stage + (' · ' + detail if detail else '') + suffix)

    def pump(self):
        self.update_operation_progress()
        try:
            # 每轮限制数量，批量图片的日志不会阻塞窗口响应。
            for _ in range(150):
                kind, value = self.events.get_nowait()
                if kind == 'log':
                    self.log(value)
                else:
                    self.busy = False
                    was_indeterminate = str(self.progress.cget('mode')) == 'indeterminate'
                    self.progress.stop()
                    if self.operation_timer is not None:
                        self.after_cancel(self.operation_timer)
                        self.operation_timer = None
                    if self.operation_started is not None:
                        self.elapsed_text.set('已用 %02d:%02d' % divmod(int(time.monotonic() - self.operation_started), 60))
                    if kind == 'error':
                        self.progress.configure(mode='determinate', value=0 if was_indeterminate else self.progress.cget('value'))
                        self.progress_text.set(self.active_label + ' · 未完成，请查看操作记录')
                        self.status.set('操作未完成，详情见操作记录。')
                        self.error(value)
                    else:
                        label, result, done = value
                        self.progress.configure(mode='determinate', value=100)
                        self.progress_text.set(label + '完成 · 100%')
                        self.status.set(label + '完成')
                        self.log(label + '完成')
                        if done:
                            try:
                                done(result)
                            except Exception as e:
                                self.error(e)
        except queue.Empty:
            pass
        self.after(100, self.pump)

    def log(self, text):
        self.logbox.configure(state='normal')
        self.logbox.insert('end', str(text) + '\n')
        self.logbox.see('end')
        if int(self.logbox.index('end-1c').split('.')[0]) > 1500:
            self.logbox.delete('1.0', '500.0')
        self.logbox.configure(state='disabled')
        try:
            core.writable(STATE).mkdir(parents=True, exist_ok=True)
            with (STATE / 'operations.log').open('a', encoding='utf-8') as f:
                f.write(str(text) + '\n')
        except OSError:
            pass


    def clear_cache(self):
        try:
            self.guard_idle()
            if self.upload_process is not None and self.upload_process.poll() is None:
                self.status.set('GitHub 上传窗口仍在运行，请关闭该窗口后再清理缓存，避免影响上传。')
                return
            self.upload_name_cache.clear()
            def done(result):
                text = '缓存已清理：%d 个文件，释放 %.1f MB；网站照片、原图和设置保留。' % (result['files'], result['freed_bytes'] / 1024 / 1024)
                if result['skipped']:
                    text += ' %d 项被占用或为链接，已跳过。' % result['skipped']
                self.status.set(text)
                self.log(text)
            self.run('清除缓存', lambda: core.clear_cache(STATE), done)
        except Exception as e:
            self.error(e)


    def save_settings(self):
        core.atomic(self.config_file, json.dumps(self.settings, ensure_ascii=False, indent=2).encode('utf-8'))

    def set_design(self, key):
        try:
            self.guard_idle()
            path = filedialog.askopenfilename(filetypes=[('图片', '*.png *.jpg *.jpeg *.ico')], initialdir=str(BASE))
            if not path:
                return
            with Image.open(path) as src:
                src.verify()
            target = STATE / 'design' / (key + Path(path).suffix.lower())
            core.atomic(target, Path(path).read_bytes())
            self.settings[key] = str(target)
            self.save_settings()
            self.apply_design()
        except Exception as e:
            self.error(e)

    def reset_design(self):
        self.settings.pop('icon', None)
        self.settings.pop('banner', None)
        self.save_settings()
        self.apply_design()

    def apply_design(self):
        try:
            if self.settings.get('icon') and Path(self.settings['icon']).exists():
                with Image.open(self.settings['icon']) as src:
                    image = src.convert('RGBA')
                    image.thumbnail((128, 128), Image.LANCZOS)
                self.icon_img = ImageTk.PhotoImage(image)
            else:
                self.icon_img = tk.PhotoImage(width=64, height=64)
                self.icon_img.put(self.palette['cinnabar'], to=(0, 0, 64, 64))
            self.iconphoto(True, self.icon_img)
            self.art.configure(image='')
            if self.settings.get('banner') and Path(self.settings['banner']).exists():
                with Image.open(self.settings['banner']) as src:
                    image = src.convert('RGBA')
                    image.thumbnail((330, 82), Image.LANCZOS)
                self.banner_img = ImageTk.PhotoImage(image)
                self.art.configure(image=self.banner_img)
        except Exception as e:
            self.status.set('设计图片未能加载：' + str(e))

    def preview(self):
        try:
            self.guard_idle()
            index = self.root_path() / 'index.html'
            if not index.is_file():
                raise ValueError('网站首页 index.html 不存在，请重新选择网站文件夹。')
            if not webbrowser.open(index.as_uri(), new=2):
                os.startfile(str(index))
            self.status.set('已打开本地网站 · 显示已保存的修改；之后可在浏览器按 Ctrl+F5 刷新查看。')
            self.log('已打开本地预览：' + str(index) + '\n预览显示本地已保存的内容；表单修改请先点“保存相册到网站”。')
        except Exception as e:
            self.error(e)

    def close(self):
        if self.busy:
            messagebox.showinfo('任务进行中', '请等待当前任务完成后再关闭，保证文件写入完整。', parent=self)
        else:
            self.destroy()


if __name__ == '__main__':
    # 拒绝在 C 盘落配置、日志、备份或临时文件。
    core.writable(BASE)
    os.environ['TEMP'] = str(STATE / 'temp')
    os.environ['TMP'] = str(STATE / 'temp')
    (STATE / 'temp').mkdir(parents=True, exist_ok=True)
    ui = App(maintenance='--smoke-test' not in sys.argv)
    if '--smoke-test' in sys.argv:
        from PIL import ImageGrab
        ui.update()
        for i in range(len(ui.tabs.tabs())):
            ui.tabs.select(i)
            ui.update()
        ui.tabs.select(0)
        ui.update()
        if '--smoke-report' in sys.argv:
            import io
            sample = io.BytesIO()
            Image.new('RGBA', (4, 4), (0, 0, 0, 0)).save(sample, format='PNG')
            test_file = STATE / 'temp' / 'smoke.png'
            core.atomic(test_file, sample.getvalue())
            name, result = core.image_bytes(test_file, {'compress': True})
            assert name == 'smoke.jpg' and result[:2] == b'\xff\xd8'
            test_file.unlink()
            assert core.push_script_resource().is_file()
            report = {'pages': len(ui.tabs.tabs()), 'albums': len(getattr(ui, 'albums', [])), 'title': ui.title(), 'site': ui.site.get(), 'frozen': bool(getattr(sys, 'frozen', False)), 'image_conversion': 'passed', 'embedded_push_script': core.push_script_resource().is_file(), 'temporary_directory': os.environ['TEMP']}
            core.atomic(sys.argv[sys.argv.index('--smoke-report') + 1], json.dumps(report, ensure_ascii=False, indent=2).encode('utf-8'))
        if '--screenshot' in sys.argv:
            output = core.writable(sys.argv[sys.argv.index('--screenshot') + 1])
            def finish_smoke():
                try:
                    ImageGrab.grab(bbox=(ui.winfo_rootx(), ui.winfo_rooty(), ui.winfo_rootx() + ui.winfo_width(), ui.winfo_rooty() + ui.winfo_height())).save(str(output))
                finally:
                    ui.destroy()
            ui.after(700, finish_smoke)
        else:
            ui.after(500, ui.destroy)
    ui.mainloop()

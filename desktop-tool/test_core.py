import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from PIL import Image
import core

HERE = Path(__file__).resolve().parent
WORK = HERE / '.test-work'


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        WORK.mkdir(exist_ok=True)
        self.base = Path(tempfile.mkdtemp(dir=str(WORK)))
        self.root = self.base / '网站 中文'
        self.state = self.base / 'state'
        (self.root / 'js').mkdir(parents=True)
        (self.root / 'assets/images/北京').mkdir(parents=True)
        (self.root / 'css').mkdir()
        self.doc = '''// photos: [ misleading comment ]
const SITE_DATA = {
  site: {name: "山水"},
  photos: [
    {city: "北京", photos: [
      {src: "assets/images/北京/故宫01.png", title: "故宫"} // 最后一项注释
    ]}, // 相册注释
  ],
  cities: ["北京"],
};'''
        (self.root / 'js/data.js').write_text(self.doc, encoding='utf-8')
        (self.root / 'css/style.css').write_text(':root {--card: #F6F0E2;}', encoding='utf-8')
        (self.root / 'index.html').write_text('<html>山水</html>', encoding='utf-8')
        self.source = self.base / '原图'
        self.source.mkdir()
        Image.new('RGBA', (40, 30), (255, 0, 0, 0)).save(str(self.source / '透明.png'))
        self.opts = {'compress': True, 'bg': '#F6F0E2', 'side': 1600, 'quality': 82}

    def tearDown(self):
        assert core.within(self.base, WORK) and self.base != WORK
        def retry_readonly(func, path, exc):
            os.chmod(path, stat.S_IWRITE)
            func(path)
        shutil.rmtree(str(self.base), onerror=retry_readonly)

    def job(self, album='北京', target='assets/images/北京'):
        return [{'target': target, 'album': album, 'items': [(str(self.source / '透明.png'), '透明.png')]}]

    def test_real_site_parser_and_folder_discovery(self):
        albums, dirs, colors = core.site_info(HERE.parent)
        self.assertGreater(len(albums), 5)
        self.assertIn('assets/images/bowu/qtq', dirs)
        self.assertEqual(colors['paper'], '#EFE8D6')

    def meta(self, name='北京'):
        return {'city': name, 'seal': '京', 'star': True, 'tags': ['青铜器', '镇馆之宝', '青铜器'], 'desc': '新的简介\n\n第二段，含 `引号` 和 ${文字} 与 \\ 路径。', 'cover': ''}

    def test_new_album_preview_and_save(self):
        before = (self.root / 'js/data.js').read_bytes()
        code = core.album_code(self.root, None, self.meta('新相册'))
        self.assertEqual((self.root / 'js/data.js').read_bytes(), before)
        self.assertIn('新相册', code['相册代码片段'])
        self.assertIn('"star": true', code['相册代码片段'])
        self.assertIn('\\${文字}', code['album-desc.js'])
        core.save_album(self.root, self.state, None, self.meta('新相册'))
        data = core.read_album(self.root, '新相册')
        self.assertTrue(data['star'])
        self.assertEqual(data['tags'], ['青铜器', '镇馆之宝'])
        self.assertEqual(data['desc'], self.meta()['desc'])
        self.assertFalse((self.state / "history").exists())
        self.assertEqual(list(self.state.rglob("*.bak")), [])

    def test_edit_album_keeps_photos_comments_and_unknown_fields(self):
        text = self.doc.replace('city: "北京"', 'city: "北京", custom: {keep: "原有字段"}')
        updated = core.edit_album(text, '北京', self.meta())
        self.assertIn('custom: {keep: "原有字段"}', updated)
        self.assertIn('// 最后一项注释', updated)
        self.assertEqual(core.Document(updated).albums()[0]['refs'], ['assets/images/北京/故宫01.png'])
        data = core.Document(updated)
        self.assertTrue(data.value(data.prop(data.albums()[0]['object'], 'star')))

    def test_rename_album_description_and_exact_shortcut(self):
        text = self.doc.replace('site: {name: "山水"}', 'site: {name: "山水", openAlbum: "北京"}')
        (self.root / 'js/data.js').write_text(text, encoding='utf-8')
        desc = '// 保留注释\nwindow.ALBUM_DESC_TEXT = `\n### 北京\n正式简介\n\n### 其他\n不要改我\n`;'
        (self.root / 'js/album-desc.js').write_text(desc, encoding='utf-8')
        self.assertEqual(core.read_album(self.root, '北京')['desc'], '正式简介')
        core.save_album(self.root, self.state, '北京', self.meta('北京新名'))
        changed = (self.root / 'js/data.js').read_text(encoding='utf-8')
        self.assertIn('openAlbum: "北京新名"', changed)
        self.assertNotIn('city: "北京"', changed)
        description = (self.root / 'js/album-desc.js').read_text(encoding='utf-8')
        _, _, sections = core.description_sections(description)
        self.assertIn(('其他', '不要改我'), sections)
        self.assertNotIn(('北京', '正式简介'), sections)
        self.assertEqual(core.read_album(self.root, '北京新名')['desc'], self.meta()['desc'])

    def test_clear_star_tags_and_description(self):
        core.save_album(self.root, self.state, '北京', self.meta())
        empty = dict(self.meta(), star=False, tags=[], desc='')
        core.save_album(self.root, self.state, '北京', empty)
        data = core.read_album(self.root, '北京')
        self.assertFalse(data['star'])
        self.assertEqual(data['tags'], [])
        self.assertEqual(data['desc'], '')

    def test_rename_partial_shortcut_resolves_same_as_website(self):
        text = self.doc.replace('city: "北京"', 'city: "中国 北京"').replace('site: {name: "山水"}', 'site: {name: "山水", openAlbum: "北京", other: {openAlbum: "不存在"}}')
        changed = core.edit_album(text, '中国 北京', self.meta('京城行迹'))
        self.assertIn('openAlbum: "京城行迹"', changed)
        self.assertIn('openAlbum: "不存在"', changed)

    def test_stale_editor_and_invalid_metadata_protected(self):
        expected = {'data.js': core.digest(self.root / 'js/data.js')}
        (self.root / 'js/data.js').write_text(self.doc + '\n// external edit', encoding='utf-8')
        with self.assertRaises(ValueError):
            core.save_album(self.root, self.state, '北京', self.meta(), expected)
        with self.assertRaises(ValueError):
            core.album_code(self.root, None, self.meta())
        with self.assertRaises(ValueError):
            core.album_code(self.root, None, self.meta('北 京'))
        with self.assertRaises(ValueError):
            core.album_code(self.root, '北京', dict(self.meta(), desc='### 不允许的新标题'))
        with self.assertRaises(ValueError):
            core.album_code(self.root, '北京', dict(self.meta(), cover='../outside.png'))

    def test_bad_description_preserves_both_files(self):
        before = (self.root / 'js/data.js').read_bytes()
        desc = self.root / 'js/album-desc.js'
        desc.write_text('unsupported format', encoding='utf-8')
        with self.assertRaises(ValueError):
            core.save_album(self.root, self.state, '北京', self.meta())
        self.assertEqual((self.root / 'js/data.js').read_bytes(), before)
        self.assertEqual(desc.read_text(encoding='utf-8'), 'unsupported format')

    def test_generated_code_executes_as_javascript(self):
        node = shutil.which('node')
        if not node:
            self.skipTest('Node is not installed')
        code = core.album_code(self.root, '北京', self.meta())
        script = 'const window={};\n' + code['data.js'] + '\n' + code['album-desc.js'] + '\nconsole.log(JSON.stringify({photos:SITE_DATA.photos,desc:window.ALBUM_DESC_TEXT}));'
        result = subprocess.run([node], input=script, encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertTrue(data['photos'][0]['star'])
        self.assertIn(self.meta()['desc'], data['desc'])

    def test_album_position_moves_object_and_preserves_photos_comments(self):
        text = core.sync_album(self.doc, '西安', [{'src': 'assets/images/西安.jpg', 'title': '西安'}])
        text = core.sync_album(text, '重庆', [])
        moved = core.edit_album(text, '重庆', dict(self.meta('重庆'), position=1))
        self.assertEqual([a['name'] for a in core.Document(moved).albums()], ['重庆', '北京', '西安'])
        self.assertIn('// 最后一项注释', moved)
        self.assertEqual(core.album_by_name(core.Document(moved), '北京')['refs'], ['assets/images/北京/故宫01.png'])
        moved = core.move_album(moved, '重庆', 3)
        self.assertEqual([a['name'] for a in core.Document(moved).albums()], ['北京', '西安', '重庆'])
        with self.assertRaises(ValueError):
            core.move_album(text, '北京', 0)
        with self.assertRaises(ValueError):
            core.move_album(text, '北京', 4)

    def test_create_at_position_and_undo_reordering(self):
        core.save_album(self.root, self.state, None, dict(self.meta('新相册'), position=1))
        self.assertEqual(core.read_album(self.root, '新相册')['position'], 1)
        self.assertEqual(core.read_album(self.root, '北京')['position'], 2)
        self.assertFalse((self.state / "history").exists())
        self.assertEqual(list(self.state.rglob("*.bak")), [])

    def test_upload_fragment_contains_only_batch_and_matches_actual(self):
        before = (self.root / 'js/data.js').read_bytes()
        code = core.upload_code(self.root, self.job(), self.opts)
        fragment = code['本次照片 data.js 片段']
        self.assertIn('assets/images/北京/透明.jpg', fragment)
        self.assertNotIn('故宫01', fragment)
        self.assertNotIn('SITE_DATA', fragment)
        self.assertEqual((self.root / 'js/data.js').read_bytes(), before)
        plan = core.upload_plan(self.root, self.job(), self.opts)
        self.assertEqual(plan[0]['target'].name, '透明.jpg')
        core.import_jobs(self.root, self.state, self.job(), self.opts, lambda _: None)
        self.assertEqual((self.root / 'js/data.js').read_text(encoding='utf-8'), code['data.js'])
        code_after = core.upload_code(self.root, self.job(), self.opts)
        self.assertNotIn('"src"', code_after['本次照片 data.js 片段'])

    def test_upload_prediction_png_and_jpeg(self):
        png = self.source / '透明.png'
        self.assertEqual(core.image_output_name(png, dict(self.opts, keep_png=True)), '透明.png')
        jpeg = self.source / '小图.jpeg'
        Image.new('RGB', (30, 30), 'white').save(str(jpeg))
        self.assertEqual(core.image_output_name(jpeg, self.opts), core.image_bytes(jpeg, self.opts)[0])
        self.assertEqual(core.image_output_name(png, dict(self.opts, compress=False)), '透明.png')
        with self.assertRaises(ValueError):
            core.upload_plan(self.root, self.job() * 2, self.opts)

    def test_renamed_files_remain_in_preview(self):
        folder = self.root / 'assets/images/北京'
        for name in ('景点01.jpg', '景点05.jpg'):
            (folder / name).write_bytes(b'picture')
        plan = core.rename_plan(folder, '其一／其二（按标题分组）', '', 1, 0)
        core.apply_rename(self.root, self.state, plan, lambda _: None)
        self.assertEqual(core.rename_plan(folder, '其一／其二（按标题分组）', '', 1, 0), [])
        preview = core.rename_plan(folder, '其一／其二（按标题分组）', '', 1, 0, include_unchanged=True)
        self.assertEqual(len(preview), 2)
        self.assertTrue(all(a == b for a, b in preview))

    def test_upload_orders_numbers_and_chinese_ordinals(self):
        names = ['皇极殿 十二.jpg', 'photo10.jpg', '皇极殿 其十.jpg', '皇极殿 其二.jpg', 'photo2.jpg', '皇极殿 十一.jpg', '皇极殿 其一.jpg', 'photo1.jpg']
        for name in names:
            Image.new('RGB', (4, 4), 'white').save(str(self.source / name))
        job = {'items': [(str(self.source / name), name) for name in names], 'target': 'assets/images/北京', 'album': '北京'}
        expected = ['photo1.jpg', 'photo2.jpg', 'photo10.jpg', '皇极殿 其一.jpg', '皇极殿 其二.jpg', '皇极殿 其十.jpg', '皇极殿 十一.jpg', '皇极殿 十二.jpg']
        self.assertEqual([p['source'].name for p in core.upload_plan(self.root, [job], self.opts)], expected)
        code = core.upload_code(self.root, [job], self.opts)
        core.import_jobs(self.root, self.state, [job], self.opts, lambda _: None)
        actual = (self.root / 'js/data.js').read_text(encoding='utf-8')
        self.assertEqual(actual, code['data.js'])
        self.assertEqual([Path(ref).name for ref in core.Document(actual).albums()[0]['refs'][1:]], expected)

    def test_existing_album_and_generated_code_regroup_ordinals(self):
        names = ['午门 其十', '别的照片', '午门 其二', '午门 十二', '午门 其一', '午门 十一']
        entries = [{'src': 'assets/images/北京/' + name + '.jpg', 'title': name, 'extra': i} for i, name in enumerate(names)]
        text = 'const SITE_DATA = ' + core.q({'photos': [{'city': '测试', 'photos': entries}]}) + ';'
        text = text.replace('"extra": 0', '"extra": /* 自定义字段 */ 0')
        expected = [names[i] for i in [4, 2, 0, 5, 3, 1]]
        actual = core.sync_album(text, '测试', [])
        refs = core.Document(actual).albums()[0]['refs']
        self.assertEqual([Path(ref).stem for ref in refs], expected)
        self.assertIn('/* 自定义字段 */', actual)
        self.assertEqual(core.sort_album_photos(actual, '测试'), actual)
        (self.root / 'js/data.js').write_text(text, encoding='utf-8')
        p = self.source / (names[0] + '.jpg')
        Image.new('RGB', (4, 4), 'white').save(str(p))
        job = {'items': [(str(p), p.name)], 'target': 'assets/images/北京', 'album': '测试'}
        code = core.upload_code(self.root, [job], self.opts)
        self.assertEqual(core.Document(code['data.js']).albums()[0]['refs'], refs)

    def test_refresh_selected_file_renamed_and_deleted(self):
        a, b = self.source / '选中.jpg', self.source / '删除.jpg'
        a.write_bytes(b'a')
        b.write_bytes(b'b')
        (self.source / '未选中.jpg').write_bytes(b'other')
        items = [(str(a), a.name), (str(b), b.name)]
        identities = core.file_identities(items)
        renamed = a.with_name('改好名字.jpg')
        a.rename(renamed)
        b.unlink()
        self.assertEqual(core.refresh_selected_files(items, identities), [(str(renamed), renamed.name)])

    def test_reveal_file_uses_explorer_select_argument(self):
        path = self.source / '文件 有空格.png'
        path.write_bytes(b'file')
        with patch.object(core.subprocess, 'Popen') as open_process:
            core.reveal_file(path)
            args = open_process.call_args[0][0]
            self.assertEqual(args[1:], ['/select,', str(path.resolve())])
            self.assertTrue(args[0].endswith('explorer.exe'))

    def test_bundled_batch_launch_opens_console_in_selected_site(self):
        with patch.object(core.subprocess, 'Popen') as popen:
            process, script = core.launch_push_script(self.root, self.state)
            self.assertEqual(process, popen.return_value)
            args, kwargs = popen.call_args
            self.assertEqual(args[0][-4:], ['/D', '/V:OFF', '/K', 'upload.bat'])
            self.assertEqual(Path(kwargs['cwd']), script.parent)
            self.assertEqual(kwargs['env']['SSQY_SITE_ROOT'], str(self.root.resolve()))
            self.assertTrue(core.within(kwargs['env']['TEMP'], self.state))
            self.assertEqual(kwargs['creationflags'], getattr(core.subprocess, 'CREATE_NEW_CONSOLE', 0))
            content = script.read_text(encoding='utf-8')
            self.assertIn('cd /d "%SSQY_SITE_ROOT%"', content)
            self.assertNotIn('cd /d "%~dp0"', content)
            self.assertIn('setlocal DisableDelayedExpansion', content)
            self.assertIn('push -u origin', content)

    def test_batch_really_uses_selected_site_with_special_characters(self):
        if os.name != 'nt':
            self.skipTest('Windows batch integration test')
        root = self.base / '网站 ! & 空格'
        for name in ('js', 'css'):
            (root / name).mkdir(parents=True, exist_ok=True)
        for name in ('index.html', 'js/data.js', 'css/style.css'):
            (root / name).write_text('test', encoding='utf-8')
        resource = self.base / 'stub.bat'
        resource.write_bytes(b'@echo off\r\nsetlocal enabledelayedexpansion\r\ncd /d "%~dp0"\r\nsetlocal DisableDelayedExpansion\r\nchcp 65001 >nul\r\necho "%CD%">"%SSQY_TEST_OUTPUT%"\r\nexit 0\r\n')
        output = self.base / 'cwd.txt'
        real_popen = core.subprocess.Popen
        def hidden(*args, **kwargs):
            kwargs['creationflags'] = core.subprocess.CREATE_NO_WINDOW
            kwargs['stdout'] = core.subprocess.PIPE
            kwargs['stderr'] = core.subprocess.PIPE
            return real_popen(*args, **kwargs)
        with patch.dict(os.environ, {'SSQY_TEST_OUTPUT': str(output)}), patch.object(core.subprocess, 'Popen', side_effect=hidden):
            process, _ = core.launch_push_script(root, self.state, resource)
            try:
                _, error = process.communicate(timeout=8)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
                raise
            self.assertEqual(process.returncode, 0, error)
        self.assertEqual(output.read_text(encoding='utf-8').strip().strip('"'), str(root.resolve()))




    def test_clear_cache_removes_legacy_backups_but_keeps_settings_and_originals(self):
        for name in ('temp/nested/cache.tmp','preview-cache/thumb.png','history/old/1.bak','settings.json','design/icon.png','upload-sessions/session/upload.bat'):
            path=self.state/name; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(b'content')
        original=self.source/'原图.jpg'; original.write_bytes(b'original')
        with core.Transaction(self.state,'no backup') as tx:
            tx.write(original,b'changed')
        self.assertFalse(tx.folder.exists())
        report=core.clear_cache(self.state)
        self.assertEqual(report['files'],3)
        for name in ('settings.json','design/icon.png','upload-sessions/session/upload.bat'):
            self.assertTrue((self.state/name).exists())
        self.assertEqual(original.read_bytes(),b'changed')
        self.assertEqual(list(self.state.rglob('*.bak')),[])

    def reference_fixture(self):
        folder = self.root / 'assets/images/北京'
        for name in ('a.jpg', '新增.jpg', '肖像.jpg'):
            (folder / name).write_bytes(b'original image')
        text = '''const SITE_DATA = {
          profile: {portrait: "assets/images/北京/肖像.jpg"},
          photos: [{city: "北京", star: true, cover: "assets/images/北京/封面已删.jpg", photos: [
            {src: "assets/images/北京/a.jpg", title: "保留"}, // 保留备注
            {src: "assets/images/北京/已删.jpg", title: "已删"},
            {src: "assets/images/北京/a.jpg", title: "重复"},
          ]}], cities: ["北京"]};'''
        (self.root / 'js/data.js').write_text(text, encoding='utf-8')
        return text

    def test_image_inspection_read_only_and_classifies_relationships(self):
        text = self.reference_fixture()
        report = core.inspect_image_references(self.root)
        self.assertEqual((self.root / 'js/data.js').read_text(encoding='utf-8'), text)
        self.assertEqual(report['counts']['missing'], 2)
        self.assertEqual(report['counts']['duplicates'], 1)
        self.assertEqual([item['path'] for item in report['unlisted']], ['assets/images/北京/新增.jpg'])

    def test_selected_reference_repair_preserves_images_and_supports_undo(self):
        before = self.reference_fixture()
        report = core.inspect_image_references(self.root)
        selected = [issue['id'] for issue in report['issues'] if issue['repairable']]
        core.repair_image_references(self.root, self.state, report, selected)
        after = (self.root / 'js/data.js').read_text(encoding='utf-8')
        self.assertIn('// 保留备注', after)
        self.assertIn('star: true', after)
        self.assertEqual(core.Document(after).albums()[0]['refs'], ['assets/images/北京/a.jpg'])
        self.assertEqual(core.read_album(self.root, '北京')['cover'], '')
        self.assertEqual(core.inspect_image_references(self.root)['counts']['missing'], 0)
        self.assertEqual((self.root / 'assets/images/北京/a.jpg').read_bytes(), b'original image')
        self.assertTrue((self.root / 'assets/images/北京/新增.jpg').exists())
        self.assertFalse((self.state / "history").exists())
        self.assertEqual(list(self.state.rglob("*.bak")), [])

    def test_reference_repair_rechecks_data_snapshot_and_restored_file(self):
        self.reference_fixture()
        report = core.inspect_image_references(self.root)
        issue = next(i for i in report['issues'] if i['kind'] == 'missing_photo')
        restored = self.root / 'assets/images/北京/已删.jpg'
        restored.write_bytes(b'restored')
        with self.assertRaises(ValueError):
            core.repair_image_references(self.root, self.state, report, [issue['id']])
        restored.unlink()
        data = self.root / 'js/data.js'
        data.write_text(data.read_text(encoding='utf-8') + '\n// external edit', encoding='utf-8')
        with self.assertRaises(ValueError):
            core.repair_image_references(self.root, self.state, report, [issue['id']])

    def test_reference_case_fix_and_remote_reference(self):
        (self.root / 'assets/images/北京/a.jpg').write_bytes(b'local')
        text = 'const SITE_DATA = {photos:[{city:"北京",photos:[{src:"ASSETS/images/北京/A.jpg?v=1#x"},{src:"https://example.invalid/image.jpg"}]}]};'
        (self.root / 'js/data.js').write_text(text, encoding='utf-8')
        report = core.inspect_image_references(self.root)
        self.assertEqual(report['counts']['case'], 1)
        self.assertEqual(report['counts']['external'], 1)
        self.assertEqual(report['counts']['missing'], 0)
        issue = report['issues'][0]
        core.repair_image_references(self.root, self.state, report, [issue['id']])
        result = (self.root / 'js/data.js').read_text(encoding='utf-8')
        self.assertIn('assets/images/北京/a.jpg?v=1#x', result)
        self.assertIn('https://example.invalid/image.jpg', result)

    def test_delete_selected_is_explicit_and_does_not_fix_other_paths(self):
        (self.root / 'assets/images/北京/a.jpg').write_bytes(b'keep')
        text = 'const SITE_DATA={photos:[{city:"北京",photos:[{src:"assets/images/北京/A.jpg"},{src:"assets/images/已删除.jpg"}]}]};'
        data = self.root / 'js/data.js'
        data.write_text(text, encoding='utf-8')
        report = core.inspect_image_references(self.root)
        case = next(i for i in report['issues'] if i['kind'] == 'case_photo')
        missing = next(i for i in report['issues'] if i['kind'] == 'missing_photo')
        with self.assertRaises(ValueError):
            core.delete_image_entries(self.root, self.state, report, [case['id']])
        self.assertEqual(data.read_text(encoding='utf-8'), text)
        core.delete_image_entries(self.root, self.state, report, [missing['id']])
        after = data.read_text(encoding='utf-8')
        self.assertIn('北京/A.jpg', after)
        self.assertNotIn('已删除.jpg', after)
        self.assertEqual((self.root / 'assets/images/北京/a.jpg').read_bytes(), b'keep')

    def test_unlisted_registration_only_writes_code(self):
        self.reference_fixture()
        report = core.inspect_image_references(self.root)
        path = 'assets/images/北京/新增.jpg'
        before = (self.root / path).read_bytes()
        core.register_unlisted_images(self.root, self.state, report, [path], '新相册')
        self.assertEqual((self.root / path).read_bytes(), before)
        self.assertIn('新相册', [a['name'] for a in core.Document((self.root / 'js/data.js').read_text(encoding='utf-8')).albums()])
        self.assertEqual(core.inspect_image_references(self.root)['counts']['unlisted'], 0)

    def test_reference_removals_first_middle_last_and_all_valid_js(self):
        node = shutil.which('node')
        if not node:
            self.skipTest('Node is required to verify generated JavaScript')
        for trailing in (False, True):
            for mask in range(1, 16):
                photos = ['{src:"assets/images/missing%d.jpg",title:"%d"}' % (i, i) for i in range(4)]
                text = 'const SITE_DATA={photos:[{city:"测试",photos:[\n' + ', // 注释\n'.join(photos) + (',' if trailing else '') + '\n]}]};'
                data = self.root / 'js/data.js'
                data.write_text(text, encoding='utf-8')
                report = core.inspect_image_references(self.root)
                selected = [issue['id'] for issue in report['issues'] if issue['kind'] == 'missing_photo' and mask & (1 << issue['photo_index'])]
                core.repair_image_references(self.root, self.state, report, selected)
                code = data.read_text(encoding='utf-8') + '\nconsole.log(JSON.stringify(SITE_DATA.photos[0].photos.map(p=>p&&p.title)));'
                proc = subprocess.run([node], input=code, encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertEqual(json.loads(proc.stdout), [str(i) for i in range(4) if not mask & (1 << i)])

    def test_portable_location_remembered_and_relative(self):
        app_dir = self.base / '管家'
        app_dir.mkdir()
        self.assertEqual(core.locate_site({'site': str(self.root)}, app_dir), str(self.root.resolve()))
        old_settings = {'site': 'Z:/旧电脑/网站', 'site_relative': '../网站 中文'}
        self.assertEqual(core.locate_site(old_settings, app_dir), str(self.root.resolve()))

    def test_portable_location_nearby_and_missing(self):
        app_dir = self.root / '管理工具'
        app_dir.mkdir()
        self.assertEqual(core.locate_site({}, app_dir), str(self.root.resolve()))
        self.assertFalse(core.is_site(self.source))
        self.assertEqual(core.locate_site({'site': 'Z:/旧电脑/网站'}, self.base / '独立目录/a/b/c/d/e'), '')

    def test_append_existing_new_and_idempotent_with_comments(self):
        entry = {'src': 'assets/images/北京/新图.jpg', 'title': '中文 " 引号'}
        text = core.sync_album(self.doc, '北京', [entry])
        self.assertIn('// 最后一项注释', text)
        self.assertIn('png", title: "故宫"}, //', text)
        self.assertEqual(core.sync_album(text, '北京', [entry]), text)
        text = core.sync_album(text, '西安', [entry])
        self.assertEqual([a['name'] for a in core.Document(text).albums()], ['北京', '西安'])

    def test_transparent_paper_color_and_keep_png(self):
        name, data = core.image_bytes(self.source / '透明.png', self.opts)
        self.assertEqual(name, '透明.jpg')
        import io
        with Image.open(io.BytesIO(data)) as im:
            self.assertTrue(all(abs(a - b) <= 2 for a, b in zip(im.getpixel((0, 0)), (246, 240, 226))))
        name, data = core.image_bytes(self.source / '透明.png', dict(self.opts, keep_png=True))
        with Image.open(io.BytesIO(data)) as im:
            self.assertEqual(im.getpixel((0, 0))[3], 0)

    def test_small_jpeg_unchanged(self):
        p = self.source / '小.jpg'
        Image.new('RGB', (60, 60), 'white').save(str(p))
        self.assertEqual(core.image_bytes(p, self.opts)[1], p.read_bytes())

    def test_import_sync_and_undo(self):
        core.import_jobs(self.root, self.state, self.job(), self.opts, lambda _: None)
        dest = self.root / 'assets/images/北京/透明.jpg'
        self.assertTrue(dest.exists())
        self.assertTrue((self.source / '透明.png').exists())
        self.assertIn('assets/images/北京/透明.jpg', (self.root / 'js/data.js').read_text(encoding='utf-8'))
        self.assertFalse((self.state / "history").exists())
        self.assertEqual(list(self.state.rglob("*.bak")), [])

    def test_conflict_fails_before_writing_and_queue_collision(self):
        dest = self.root / 'assets/images/北京/透明.jpg'
        dest.write_bytes(b'original')
        with self.assertRaises(ValueError):
            core.import_jobs(self.root, self.state, self.job(), self.opts, lambda _: None)
        self.assertEqual(dest.read_bytes(), b'original')
        dest.unlink()
        with self.assertRaises(ValueError):
            core.import_jobs(self.root, self.state, self.job() * 2, self.opts, lambda _: None)
        self.assertFalse(dest.exists())

    def test_overwrite_and_undo(self):
        dest = self.root / 'assets/images/北京/透明.jpg'
        dest.write_bytes(b'original')
        core.import_jobs(self.root, self.state, self.job(), dict(self.opts, overwrite=True), lambda _: None)
        self.assertFalse((self.state / "history").exists())
        self.assertEqual(list(self.state.rglob("*.bak")), [])

    def test_abort_rolls_back_files_when_bad_album(self):
        (self.root / 'js/data.js').write_text(self.doc.replace('city: "北京"', 'city: "北京", photos2: []').replace('photos: [\n      ', 'pictures: [\n      '), encoding='utf-8')
        with self.assertRaises(ValueError):
            core.import_jobs(self.root, self.state, self.job(), self.opts, lambda _: None)
        self.assertFalse((self.root / 'assets/images/北京/透明.jpg').exists())

    def test_path_escape_rejected(self):
        with self.assertRaises(ValueError):
            core.import_jobs(self.root, self.state, self.job(target='../escape'), self.opts, lambda _: None)
        with self.assertRaises(ValueError):
            core.writable('C:/Temp/unwanted')

    def test_references_replace_only_whole_string(self):
        old = 'assets/images/北京/故宫01.png'
        text = core.replace_refs(self.doc, {old: 'assets/images/北京/故宫.png'})
        self.assertIn('故宫.png', text)
        self.assertIn('// photos:', text)

    def test_rename_groups_and_sync(self):
        folder = self.root / 'assets/images/北京'
        for name in ('故宫01.png', '故宫05.png'):
            shutil.copy2(str(self.source / '透明.png'), str(folder / name))
        plan = core.rename_plan(folder, '其一／其二（按标题分组）', '', 1, 0)
        self.assertEqual([b.name for a, b in plan], ['故宫 其一.png', '故宫 其二.png'])
        core.apply_rename(self.root, self.state, plan, lambda _: None)
        self.assertIn('故宫 其一.png', (self.root / 'js/data.js').read_text(encoding='utf-8'))
        self.assertFalse((self.state / "history").exists())
        self.assertEqual(list(self.state.rglob("*.bak")), [])

    def test_two_phase_swap_without_copying_photos(self):
        a, b = self.source / 'a.txt', self.source / 'b.txt'
        a.write_bytes(b'A'); b.write_bytes(b'B')
        with patch.object(core.shutil, 'copy2', side_effect=AssertionError('must not copy originals')):
            core.apply_rename(self.root, self.state, [(a,b),(b,a)], lambda _: None)
        self.assertEqual(a.read_bytes(), b'B')
        self.assertEqual(b.read_bytes(), b'A')
        self.assertFalse((self.state/'history').exists())

    def test_prefix_natural_sort_filter(self):
        for name in ('IMG10.jpg', 'IMG2.jpg', '中文.jpg'):
            (self.source / name).write_bytes(b'x')
        plan = core.rename_plan(self.source, '前缀＋数字', 'bj', 1, 3, False, '仅英文')
        self.assertEqual([(a.name, b.name) for a, b in plan], [('IMG2.jpg', 'bj001.jpg'), ('IMG10.jpg', 'bj002.jpg')])

    def test_optional_prefix_on_title_rule_is_repeatable_and_syncs_code(self):
        folder = self.root / 'assets/images/北京'
        for name in ('海晏堂.jpg', '长春园2.jpg', '长春园1.jpg'):
            (folder / name).write_bytes(b'photo')
        mode = '其一／其二（按标题分组）'
        plan = core.rename_plan(folder, mode, '圆明园', 1, 0, add_prefix=True)
        names = {b.name for a, b in plan}
        self.assertIn('圆明园 海晏堂.jpg', names)
        self.assertIn('圆明园 长春园 其一.jpg', names)
        self.assertIn('圆明园 长春园 其二.jpg', names)
        # 不勾选时忽略前缀内容。
        plain = core.rename_plan(folder, mode, 'invalid/prefix', 1, 0, include_unchanged=True, add_prefix=False)
        self.assertIn('海晏堂.jpg', {b.name for a, b in plain})
        code = self.root / 'js/data.js'
        text = code.read_text(encoding='utf-8').replace('故宫01.png', '海晏堂.jpg')
        code.write_text(text, encoding='utf-8')
        core.apply_rename(self.root, self.state, plan, lambda _: None)
        self.assertIn('assets/images/北京/圆明园 海晏堂.jpg', code.read_text(encoding='utf-8'))
        self.assertEqual(core.rename_plan(folder, mode, '圆明园', 1, 0, add_prefix=True), [])
        preview = core.rename_plan(folder, mode, '圆明园', 1, 0, include_unchanged=True, add_prefix=True)
        self.assertTrue(all(a == b for a, b in preview))

    def test_optional_prefix_on_number_rule_and_invalid_prefix(self):
        for name in ('IMG2.jpg', 'IMG10.jpg'):
            (self.source / name).write_bytes(b'photo')
        plain = core.rename_plan(self.source, '数字编号', 'ignored', 1, 3, filter_mode='仅英文', add_prefix=False)
        self.assertEqual([b.name for a, b in plain], ['001.jpg', '002.jpg'])
        prefixed = core.rename_plan(self.source, '数字编号', ' 圆明园 ', 1, 3, filter_mode='仅英文', add_prefix=True)
        self.assertEqual([b.name for a, b in prefixed], ['圆明园 001.jpg', '圆明园 002.jpg'])
        for mode in ('数字编号', '其一／其二（按标题分组）'):
            for prefix in ('', ' ', 'bad/prefix', 'bad.'):
                with self.assertRaises(ValueError):
                    core.rename_plan(self.source, mode, prefix, 1, 0, add_prefix=True)

    def test_rename_selected_photos_only_and_keeps_unselected_files(self):
        a, b, untouched = [self.source / name for name in ('海晏堂1.jpg', '海晏堂2.jpg', '海晏堂3.jpg')]
        for p in (a, b, untouched):
            p.write_bytes(p.name.encode('utf-8'))
        selected = [str(b), str(a), str(a)]
        plan = core.rename_plan(self.source, '其一／其二（按标题分组）', '圆明园', 1, 0,
            recursive=True, add_prefix=True, selected_files=selected)
        self.assertEqual(len(plan), 2)
        self.assertEqual({a for a, b in plan}, {a, b})
        self.assertEqual({b.name for a, b in plan}, {'圆明园 海晏堂 其一.jpg', '圆明园 海晏堂 其二.jpg'})
        core.apply_rename(self.root, self.state, plan, lambda _: None)
        self.assertTrue(untouched.is_file())
        self.assertTrue((self.source / '透明.png').is_file())
        updated = [str(b) for a, b in plan]
        again = core.rename_plan(self.source, '其一／其二（按标题分组）', '圆明园', 1, 0,
            add_prefix=True, selected_files=updated, include_unchanged=True)
        self.assertEqual(len(again), 2)
        self.assertTrue(all(a == b for a, b in again))

    def test_rename_selected_validation_and_existing_unselected_target(self):
        photo = self.source / 'photo.jpg'
        photo.write_bytes(b'photo')
        kwargs = dict(add_prefix=False, selected_files=[str(photo)])
        (self.source / '1.jpg').write_bytes(b'unselected')
        with self.assertRaises(ValueError):
            core.rename_plan(self.source, '数字编号', '', 1, 0, **kwargs)
        for selected in ([], [str(self.source / 'missing.jpg')], [str(self.root / 'js/data.js')]):
            with self.assertRaises(ValueError):
                core.rename_plan(self.source, '数字编号', '', 1, 0, add_prefix=False, selected_files=selected)
        self.assertEqual(photo.read_bytes(), b'photo')
        self.assertEqual((self.source / '1.jpg').read_bytes(), b'unselected')

    def test_rename_syncs_photo_titles_across_albums_and_keeps_other_fields(self):
        old = 'assets/images/北京/故宫01.png'
        new = 'assets/images/北京/圆明园 海晏堂.png'
        text = '''const SITE_DATA = {photos: [
          {city: '保留相册名', cover: 'assets/images/北京/故宫01.png', photos: [
            {src: 'assets/images/北京/故宫01.png', title: '旧标题', tags: ['保留'], desc: '原简介'},
            {src: 'assets/images/untouched.jpg', title: '自定义标题'}]},
          {city: '另一本', photos: [
            {title: '另一个旧标题', src: 'assets/images/北京/故宫01.png'},
            {src: 'assets/images/北京/故宫01.png' // 保留行注释
            },
            {src: 'assets/images/北京/故宫01.png', /* 保留注释 */},
          ]}
        ]};'''
        updated = core.rename_photo_refs(text, {old: new})
        doc = core.Document(updated)
        titles = [doc.string(doc.prop(obj, 'title')) for album in doc.albums() for obj in doc.objects(album['array'])]
        self.assertEqual(titles, ['圆明园 海晏堂', '自定义标题', '圆明园 海晏堂', '圆明园 海晏堂', '圆明园 海晏堂'])
        self.assertIn("city: '保留相册名'", updated)
        self.assertIn("tags: ['保留'], desc: '原简介'", updated)
        self.assertIn('// 保留行注释', updated)
        self.assertIn('/* 保留注释 */', updated)
        self.assertNotIn(old, updated)
        config = self.root / 'js/data.js'
        config.write_text(text, encoding='utf-8')
        a, b = self.root / old, self.root / new
        a.write_bytes(b'photo')
        core.apply_rename(self.root, self.state, [(a, b)], lambda _: None)
        self.assertEqual(config.read_text(encoding='utf-8'), updated)
        self.assertFalse(a.exists())
        self.assertEqual(b.read_bytes(), b'photo')

    def test_dynamic_photo_title_stops_before_renaming_file(self):
        old = 'assets/images/北京/故宫01.png'
        a, b = self.root / old, self.root / 'assets/images/北京/改后.png'
        a.write_bytes(b'photo')
        config = self.root / 'js/data.js'
        for dynamic in ('makeTitle()', "'旧标题' + extra"):
            text = self.doc.replace('title: "故宫"', 'title: ' + dynamic)
            config.write_text(text, encoding='utf-8')
            with self.assertRaises(ValueError):
                core.apply_rename(self.root, self.state, [(a, b)], lambda _: None)
            self.assertEqual(a.read_bytes(), b'photo')
            self.assertFalse(b.exists())
            self.assertEqual(config.read_text(encoding='utf-8'), text)

    def test_compression_prepares_all_inputs_before_writing_outputs(self):
        dest=self.base/'导出'
        core.compress_folder(self.source,dest,self.state,self.opts,lambda _:None)
        before=(dest/'透明.jpg').read_bytes()
        (self.source/'透明.jpg').write_bytes(b'bad image')
        with self.assertRaises(Exception):
            core.compress_folder(self.source,dest,self.state,self.opts,lambda _:None)
        self.assertEqual((dest/'透明.jpg').read_bytes(),before)
        self.assertFalse((self.state/'history').exists())
        with self.assertRaises(ValueError):
            core.compress_folder(self.source,self.source/'child',self.state,self.opts,lambda _:None)

    def test_zip_exclusions(self):
        (self.source / '.workbuddy').mkdir()
        (self.source / '.workbuddy/secret').write_bytes(b'private')
        dest = self.base / '相册.zip'
        core.make_zip(self.source, dest, lambda _: None)
        with zipfile.ZipFile(str(dest)) as z:
            self.assertEqual(z.namelist(), ['透明.png'])
        with self.assertRaises(ValueError):
            core.make_zip(self.source, self.source / 'self.zip', lambda _: None)

    def test_compression_overwrites_existing_output_and_undo_restores_it(self):
        dest = self.base / '导出'
        dest.mkdir()
        target = dest / '透明.jpg'
        target.write_bytes(b'previous output')
        messages = []
        core.compress_folder(self.source, dest, self.state, self.opts, messages.append)
        self.assertNotEqual(target.read_bytes(), b'previous output')
        self.assertTrue(any('覆盖' in message for message in messages))
        self.assertTrue((self.source / '透明.png').exists())
        self.assertFalse((self.state / "history").exists())
        self.assertEqual(list(self.state.rglob("*.bak")), [])

    def test_compression_same_batch_output_name_last_wins(self):
        Image.new('RGB', (16, 16), 'blue').save(str(self.source / 'same.jpg'))
        Image.new('RGB', (16, 16), 'red').save(str(self.source / 'same.png'))
        dest = self.base / '导出'
        dest.mkdir()
        target = dest / 'same.jpg'
        target.write_bytes(b'old')
        core.compress_folder(self.source, dest, self.state, self.opts, lambda _: None)
        expected = core.image_bytes(self.source / 'same.png', self.opts)[1]
        self.assertEqual(target.read_bytes(), expected)
        self.assertFalse((self.state / "history").exists())
        self.assertEqual(list(self.state.rglob("*.bak")), [])

    def test_compression_failure_restores_overwritten_file(self):
        Image.new('RGB', (16, 16), 'red').save(str(self.source / 'a.png'))
        (self.source / 'z_bad.jpg').write_bytes(b'not an image')
        dest = self.base / '导出'
        dest.mkdir()
        target = dest / 'a.jpg'
        target.write_bytes(b'old')
        with self.assertRaises(Exception):
            core.compress_folder(self.source, dest, self.state, self.opts, lambda _: None)
        self.assertEqual(target.read_bytes(), b'old')

    def test_zip_overwrites_existing_archive_only_after_success(self):
        dest = self.base / '相册.zip'
        dest.write_bytes(b'old archive')
        core.make_zip(self.source, dest, lambda _: None)
        with zipfile.ZipFile(str(dest)) as archive:
            self.assertIn('透明.png', archive.namelist())
        before = dest.read_bytes()
        with patch.object(core.zipfile.ZipFile, 'write', side_effect=OSError('failed')):
            with self.assertRaises(OSError):
                core.make_zip(self.source, dest, lambda _: None)
        self.assertEqual(dest.read_bytes(), before)
        self.assertEqual(list(self.base.glob('.ssqy-zip-*')), [])

    def test_file_operations_report_real_monotonic_progress(self):
        events = []
        progress = lambda *event: events.append(event)
        def check():
            bounded = [event for event in events if event[2] > 0]
            self.assertTrue(bounded)
            self.assertTrue(all(0 <= done <= total for _, done, total, _ in bounded))
            self.assertEqual([event[1] for event in bounded], sorted(event[1] for event in bounded))
            self.assertEqual(bounded[-1][1], bounded[-1][2])
            events.clear()
        core.compress_folder(self.source, self.base / '导出', self.state, self.opts, lambda _: None, progress)
        check()
        core.import_jobs(self.root, self.state, self.job(), self.opts, lambda _: None, progress)
        check()
        plan = core.rename_plan(self.root / 'assets/images/北京', '前缀＋数字', 'new', 1, 0)
        core.apply_rename(self.root, self.state, plan, lambda _: None, progress)
        check()
        core.make_zip(self.source, self.base / '进度.zip', lambda _: None, progress)
        check()
        core.inspect_image_references(self.root, progress)
        check()

    def test_failed_compression_does_not_report_complete(self):
        (self.source / 'a_bad.jpg').write_bytes(b'bad image')
        events = []
        with self.assertRaises(Exception):
            core.compress_folder(self.source, self.base / '导出', self.state, self.opts, lambda _: None, lambda *event: events.append(event))
        self.assertTrue(events)
        self.assertTrue(all(done < total for _, done, total, _ in events if total > 0))

    def test_in_place_compress_removes_converted_original_and_undo_restores(self):
        original = (self.source / '透明.png').read_bytes()
        events = []
        core.compress_folder(self.source, self.source, self.state, self.opts, lambda _: None, lambda *event: events.append(event))
        self.assertFalse((self.source / '透明.png').exists())
        self.assertTrue((self.source / '透明.jpg').exists())
        self.assertEqual(events[-1][1], events[-1][2])
        self.assertFalse((self.state / "history").exists())
        self.assertEqual(list(self.state.rglob("*.bak")), [])

    def test_in_place_stages_same_name_inputs_before_overwrite(self):
        jpg, png = self.source / 'same.jpg', self.source / 'same.png'
        Image.new('RGB', (32, 32), 'blue').save(str(jpg))
        Image.new('RGB', (32, 32), 'red').save(str(png))
        before_jpg, before_png = jpg.read_bytes(), png.read_bytes()
        expected = core.image_bytes(png, self.opts)[1]
        core.compress_folder(self.source, self.source, self.state, self.opts, lambda _: None)
        self.assertEqual(jpg.read_bytes(), expected)
        self.assertFalse(png.exists())
        self.assertFalse((self.state / "history").exists())
        self.assertEqual(list(self.state.rglob("*.bak")), [])

    def test_in_place_write_failure_keeps_unremoved_originals_without_backups(self):
        for name in ('a.png','b.png'):
            Image.new('RGB',(32,32),'red').save(str(self.source/name))
        originals={p.name:p.read_bytes() for p in self.source.iterdir()}
        real_atomic,raised=core.atomic,[]
        def fail_once(path,data):
            if Path(path)==self.source/'b.jpg' and not raised:
                raised.append(True); raise OSError('test failure')
            return real_atomic(path,data)
        with patch.object(core,'atomic',side_effect=fail_once):
            with self.assertRaises(OSError):
                core.compress_folder(self.source,self.source,self.state,self.opts,lambda _:None)
        for name,data in originals.items(): self.assertEqual((self.source/name).read_bytes(),data)
        self.assertTrue((self.source/'a.jpg').exists())
        self.assertFalse((self.state/'history').exists())
        self.assertEqual(list((self.state/'temp').glob('work-*')),[])

    def test_in_place_updates_current_site_references_in_same_transaction(self):
        folder = self.root / 'assets/images/北京'
        original = folder / '故宫01.png'
        shutil.copy2(str(self.source / '透明.png'), str(original))
        before_js = (self.root / 'js/data.js').read_bytes()
        core.compress_folder(folder, folder, self.state, dict(self.opts, site_root=str(self.root)), lambda _: None)
        self.assertFalse(original.exists())
        self.assertTrue((folder / '故宫01.jpg').exists())
        self.assertIn('assets/images/北京/故宫01.jpg', (self.root / 'js/data.js').read_text(encoding='utf-8'))
        self.assertFalse((self.state / "history").exists())
        self.assertEqual(list(self.state.rglob("*.bak")), [])

    def test_in_place_external_source_does_not_change_site_data(self):
        before = (self.root / 'js/data.js').read_bytes()
        core.compress_folder(self.source, self.source, self.state, dict(self.opts, site_root=str(self.root)), lambda _: None)
        self.assertEqual((self.root / 'js/data.js').read_bytes(), before)

    def test_in_place_keep_png_retains_transparency_and_animation_files(self):
        Image.new('RGBA', (512, 256), (255, 0, 0, 0)).save(str(self.source / '透明.png'))
        svg = self.source / '不变.svg'
        svg.write_bytes(b'<svg xmlns="http://www.w3.org/2000/svg"/>')
        core.compress_folder(self.source, self.source, self.state, dict(self.opts, keep_png=True, side=64), lambda _: None)
        with Image.open(str(self.source / '透明.png')) as image:
            self.assertEqual(image.size, (64, 32))
            self.assertEqual(image.getpixel((0, 0))[3], 0)
        self.assertFalse((self.source / '透明.jpg').exists())
        self.assertEqual(svg.read_bytes(), b'<svg xmlns="http://www.w3.org/2000/svg"/>')

    def test_publish_local_commit_scope_no_network(self):
        core.git(self.root, ['init'])
        core.git(self.root, ['config', 'user.name', 'Test'])
        core.git(self.root, ['config', 'user.email', 'test@example.invalid'])
        core.git(self.root, ['remote', 'add', 'origin', 'https://github.com/example/test.git'])
        (self.root / 'desktop-tool').mkdir()
        (self.root / 'desktop-tool/backup.bin').write_bytes(b'private')
        (self.root / 'assets/.workbuddy').mkdir()
        (self.root / 'assets/.workbuddy/secret').write_bytes(b'private')
        real_git = core.git
        calls = []
        def local_git(root, args, **kwargs):
            calls.append(args)
            if args[0] == 'push':
                return 'mock push success'
            return real_git(root, args, **kwargs)
        with patch.object(core, 'git', side_effect=local_git):
            core.publish(self.root, '测试提交', lambda _: None)
        staged = real_git(self.root, ['ls-tree', '-r', '--name-only', 'HEAD'])
        self.assertIn('index.html', staged)
        self.assertNotIn('backup.bin', staged)
        self.assertNotIn('secret', staged)
        self.assertEqual(len([a for a in calls if a[0] == 'push']), 1)
        (self.root / 'index.html').write_text('changed', encoding='utf-8')
        real_git(self.root, ['add', 'index.html'])
        with patch.object(core, 'git', side_effect=local_git):
            with self.assertRaises(ValueError):
                core.publish(self.root, 'blocked', lambda _: None)

    def test_compression_never_copies_or_retains_original_photo_backups(self):
        with patch.object(core.shutil, 'copy2', side_effect=AssertionError('no photo backups')):
            core.compress_folder(self.source, self.source, self.state, self.opts, lambda _: None)
        self.assertFalse((self.source/'透明.png').exists())
        self.assertTrue((self.source/'透明.jpg').exists())
        self.assertFalse((self.state/'history').exists())
        self.assertEqual(list(self.state.rglob('*.bak')), [])
        self.assertEqual(list((self.state/'temp').glob('work-*')), [])

    def test_upload_size_check_ignores_gitignored_large_caches(self):
        if os.name != 'nt':
            self.skipTest('PowerShell integration test')
        import re
        core.git(self.root,['init'])
        (self.root/'.gitignore').write_text('desktop-tool/dist/\n',encoding='utf-8')
        cache=self.root/'desktop-tool/dist/test/_data/history/old/1.bak'
        cache.parent.mkdir(parents=True)
        with cache.open('wb') as f: f.truncate(60*1024*1024)
        script=(HERE.parent/'push.bat').read_text(encoding='utf-8-sig')
        command=re.search(r'^powershell .*?-Command "(.*)"$',script,re.M).group(1)
        env=dict(os.environ,GITEXE=shutil.which('git'))
        def check():
            return subprocess.run(['powershell','-NoProfile','-Command',command],cwd=str(self.root),env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding='utf-8',errors='replace',timeout=20)
        result=check()
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        large=self.root/'assets/images/大照片.jpg'
        with large.open('wb') as f: f.truncate(30*1024*1024)
        result=check()
        self.assertEqual(result.returncode,1,result.stdout+result.stderr)
        self.assertIn('大照片.jpg',result.stdout)
        self.assertNotIn('1.bak',result.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)

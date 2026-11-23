import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import album_merge
import core


class AlbumMergeTests(unittest.TestCase):
    def setUp(self):
        self.work = Path(__file__).parent / '.test-work'
        self.work.mkdir(exist_ok=True)
        self.base = Path(tempfile.mkdtemp(dir=str(self.work)))
        self.root = self.base / '网站'
        for name in ('js', 'assets/mother', 'assets/child', 'assets/second'):
            (self.root / name).mkdir(parents=True)
        self.file('mother/same.jpg', b'mother')
        self.file('child/same.jpg', b'child')
        self.file('child/new.jpg', b'new')
        self.albums = [
            {'city': '母相册', 'seal': '母', 'star': True, 'desc': '母简介', 'cover': 'assets/mother/same.jpg',
             'custom': {'keep': True}, 'tags': ['母词', '重复'], 'photos': [
                 {'src': 'assets/mother/same.jpg', 'title': '原照片', 'keep': '母'}]},
            {'city': '子相册', 'seal': '子', 'star': False, 'desc': '子简介', 'tags': ['重复', '子词'], 'photos': [
                {'src': 'assets/child/same.jpg', 'title': '覆盖照片', 'custom': {'child': True}},
                {'src': 'assets/child/new.jpg', 'title': '新增照片'}]},
            {'city': '不合并', 'photos': [{'src': 'assets/child/new.jpg', 'title': '共享照片'}]}
        ]
        self.config = self.root / 'js/data.js'
        self.desc = self.root / 'js/album-desc.js'
        self.write_data()
        self.desc.write_text('window.ALBUM_DESC_TEXT = `\n### 母相册\n母正式简介\n\n### 子相册\n子正式简介\n\n### 不合并\n保留简介\n`;', encoding='utf-8')

    def tearDown(self):
        assert core.within(self.base, self.work)
        shutil.rmtree(str(self.base))

    def file(self, relative, content):
        (self.root / 'assets' / relative).write_bytes(content)

    def write_data(self):
        self.config.write_text('const SITE_DATA = ' + json.dumps({
            'photos': self.albums, 'profile': {'shortcut': {'openAlbum': '子'}},
            'travel': [{'cover': 'assets/child/new.jpg'}]}, ensure_ascii=False) + ';', encoding='utf-8')

    def read(self):
        return json.loads(self.config.read_text(encoding='utf-8').split('=', 1)[1].strip().rstrip(';'))

    def plan(self):
        return album_merge.plan_merge(self.root, '母相册', ['子相册'], 'assets/mother')

    def apply(self, plan):
        return album_merge.apply_merge(self.root, self.base / 'state', plan)

    def test_preview_is_readonly_then_merge_keeps_mother_and_unions_tags(self):
        before = self.config.read_bytes()
        plan = self.plan()
        self.assertEqual(self.config.read_bytes(), before)
        self.assertEqual((self.root / 'assets/mother/same.jpg').read_bytes(), b'mother')
        self.assertEqual(plan['photos'], 2)
        self.assertIn('assets/mother/same.jpg', plan['overwrites'])
        self.apply(plan)
        data = self.read()
        self.assertEqual([a['city'] for a in data['photos']], ['母相册', '不合并'])
        mother = data['photos'][0]
        for key in ('city', 'seal', 'star', 'desc', 'cover', 'custom'):
            self.assertEqual(mother[key], self.albums[0][key])
        self.assertEqual(mother['tags'], ['母词', '重复', '子词'])
        same = next(p for p in mother['photos'] if p['src'].endswith('same.jpg'))
        self.assertEqual(same['title'], '覆盖照片')
        self.assertEqual(same['custom'], {'child': True})
        self.assertEqual((self.root / 'assets/mother/same.jpg').read_bytes(), b'child')
        self.assertEqual((self.root / 'assets/mother/new.jpg').read_bytes(), b'new')
        self.assertFalse((self.root / 'assets/child/new.jpg').exists())
        self.assertEqual(data['photos'][1]['photos'][0]['src'], 'assets/mother/new.jpg')
        self.assertEqual(data['travel'][0]['cover'], 'assets/mother/new.jpg')
        self.assertEqual(data['profile']['shortcut']['openAlbum'], '母相册')
        description = self.desc.read_text(encoding='utf-8')
        self.assertIn('### 母相册\n母正式简介', description)
        self.assertIn('### 不合并\n保留简介', description)
        self.assertNotIn('### 子相册', description)

    def test_multiple_sources_overwrite_in_selected_order(self):
        self.file('second/same.jpg', b'last')
        self.albums.append({'city': '第二子', 'tags': ['末词'], 'photos': [
            {'src': 'assets/second/same.jpg', 'title': '最后照片'}]})
        self.write_data()
        plan = album_merge.plan_merge(self.root, '母相册', ['子相册', '第二子'], 'assets/mother')
        self.apply(plan)
        self.assertEqual((self.root / 'assets/mother/same.jpg').read_bytes(), b'last')
        self.assertEqual(self.read()['photos'][0]['tags'], ['母词', '重复', '子词', '末词'])

    def test_changed_input_or_destination_rejects_before_writing(self):
        for changed in (self.config, self.desc, self.root / 'assets/child/new.jpg', self.root / 'assets/mother/same.jpg'):
            plan = self.plan()
            before = changed.read_bytes()
            changed.write_bytes(before + b' ')
            snapshot = self.config.read_bytes()
            with self.assertRaisesRegex(ValueError, '已变化'):
                self.apply(plan)
            self.assertEqual(self.config.read_bytes(), snapshot)
            changed.write_bytes(before)

    def test_failure_after_removal_restores_files_and_metadata(self):
        plan = self.plan()
        before = {path: path.read_bytes() for path in self.root.rglob('*') if path.is_file()}
        remove = core.Transaction.remove
        def fail(tx, path):
            remove(tx, path)
            raise OSError('模拟移动失败')
        with patch.object(core.Transaction, 'remove', fail):
            with self.assertRaisesRegex(OSError, '模拟移动失败'):
                self.apply(plan)
        after = {path: path.read_bytes() for path in self.root.rglob('*') if path.is_file()}
        self.assertEqual(after, before)

    def test_invalid_selection_missing_file_and_outside_target(self):
        for sources, folder in (([], 'assets/mother'), (['母相册'], 'assets/mother'), (['子相册'], '../outside')):
            with self.assertRaises(ValueError):
                album_merge.plan_merge(self.root, '母相册', sources, folder)
        (self.root / 'assets/child/new.jpg').unlink()
        with self.assertRaisesRegex(ValueError, '照片不存在'):
            self.plan()

    def test_empty_mother_and_remote_photos(self):
        self.albums[0]['photos'] = []
        self.albums[1]['photos'] = [{'src': 'https://example.com/photo.jpg', 'title': '远程照片'}]
        self.write_data()
        self.apply(self.plan())
        self.assertEqual(self.read()['photos'][0]['photos'][0]['src'], 'https://example.com/photo.jpg')

    def test_case_variant_conflict_uses_one_canonical_destination(self):
        (self.root / 'assets/child/same.jpg').rename(self.root / 'assets/child/SAME.jpg')
        self.albums[1]['photos'][0]['src'] = 'assets/child/SAME.jpg'
        self.write_data()
        plan = self.plan()
        self.apply(plan)
        mother = self.read()['photos'][0]
        self.assertEqual(mother['cover'], 'assets/mother/same.jpg')
        self.assertEqual([p['src'] for p in mother['photos'] if p['src'].lower().endswith('same.jpg')], ['assets/mother/same.jpg'])


if __name__ == '__main__':
    unittest.main()

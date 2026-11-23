import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image
import featured


class FeaturedTests(unittest.TestCase):
    def test_edit_copy_preserve_other_config_and_stale_check(self):
        work = Path(__file__).parent / '.test-work'
        work.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=str(work)) as temp:
            base = Path(temp)
            root = base / '网站'
            (root / 'js').mkdir(parents=True)
            (root / 'assets').mkdir()
            (root / 'js/data.js').write_text('const SITE_DATA={photos:[{city:"相册",photos:[]}]};', encoding='utf-8')
            (root / 'index.html').write_text('<script src="js/journey-config.js?v=old"></script>', encoding='utf-8')
            config = root / 'js/journey-config.js'
            config.write_text('window.JOURNEY_CONFIG = ' + json.dumps({'cityAlbums': {'城市': ['相册']}}) + ';', encoding='utf-8')
            image = base / '新照片.jpg'
            Image.new('RGB', (20, 20)).save(str(image))
            before = featured.read(root)
            values = {'album': '相册', 'title': '新精选', 'src': 'assets/images/featured/新照片.jpg', 'note': '新配文'}
            self.assertNotIn('recent', before['config'])
            featured.save(root, base / 'state', values, before['expected'], str(image))
            updated = featured.read(root)
            self.assertEqual(updated['recent'], values)
            self.assertEqual(updated['config']['cityAlbums'], {'城市': ['相册']})
            self.assertEqual((root / values['src']).read_bytes(), image.read_bytes())
            self.assertNotIn('?v=old', (root / 'index.html').read_text(encoding='utf-8'))
            with self.assertRaisesRegex(ValueError, '网站内容已变化'):
                featured.save(root, base / 'state', values, before['expected'])
            values['src'] = '../outside.jpg'
            with self.assertRaisesRegex(ValueError, 'assets'):
                featured.save(root, base / 'state', values, updated['expected'])

    def test_map_editor_preserves_featured_and_limits_to_selected_albums(self):
        work = Path(__file__).parent / '.test-work'
        work.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=str(work)) as temp:
            root = Path(temp)
            (root / 'js').mkdir()
            (root / 'index.html').write_text('<script src="js/journey-config.js"></script>', encoding='utf-8')
            (root / 'js/data.js').write_text('const SITE_DATA={cities:["大同@山西"],photos:[{city:"山西 大同",photos:[]},{city:"其他",photos:[{src:"assets/大同.jpg",title:"大同照片"},{src:"assets/另图.jpg",title:"大同城墙"}]}]};', encoding='utf-8')
            (root / 'js/journey-config.js').write_text('window.JOURNEY_CONFIG = {"recent":{"title":"保留精选"}};', encoding='utf-8')
            before = featured.read_map_city(root, '大同')
            self.assertEqual(before['albums'], ['山西 大同', '其他'])
            featured.save_map_city(root, root / 'state', '大同', ['其他'], 'title', before['expected'], ['assets/大同.jpg'])
            after = featured.read_map_city(root, '大同')
            self.assertEqual(after['albums'], ['其他'])
            self.assertEqual(after['match'], 'title')
            self.assertEqual(after['photos'], ['assets/大同.jpg'])
            self.assertEqual(len(featured.map_photo_options(root, ['其他'], '大同', 'title')), 2)
            self.assertEqual(featured.read(root)['recent']['title'], '保留精选')
            with self.assertRaisesRegex(ValueError, '网站内容已变化'):
                featured.save_map_city(root, root / 'state', '大同', [], 'auto', before['expected'])
            expected = featured.read(root)['expected']
            featured.delete_map_city(root, root / 'state', '大同', expected)
            self.assertEqual(featured.map_places(root), [])
            config = featured.read(root)['config']
            self.assertNotIn('大同', config['cityPhotos'])
            self.assertNotIn('大同', config['cityAlbums'])
            self.assertEqual(config['recent']['title'], '保留精选')
            self.assertIn('assets/大同.jpg', (root / 'js/data.js').read_text(encoding='utf-8'))

    def test_delete_city_positions_and_duplicates_preserves_albums(self):
        work = Path(__file__).parent / '.test-work'
        work.mkdir(exist_ok=True)
        for entries in (['大同', '长春'], ['长春', '大同'], ['大同', '大同@山西', '长春'], ['大同']):
            with tempfile.TemporaryDirectory(dir=str(work)) as temp:
                root = Path(temp)
                (root / 'js').mkdir()
                (root / 'index.html').write_text('<script src="js/data.js?v=old"></script>', encoding='utf-8')
                albums = [{'city': '大同', 'photos': [{'src': 'photo.jpg', 'title': '照片保留'}]}]
                (root / 'js/data.js').write_text('const SITE_DATA = ' + json.dumps({'cities': entries, 'photos': albums}) + ';', encoding='utf-8')
                featured.delete_map_city(root, root / 'state', '大同', featured.read(root)['expected'])
                data = json.loads((root / 'js/data.js').read_text(encoding='utf-8').split('=', 1)[1].strip().rstrip(';'))
                self.assertEqual(data['cities'], [entry for entry in entries if not entry.startswith('大同')])
                self.assertEqual(data['photos'], albums)


if __name__ == '__main__':
    unittest.main()

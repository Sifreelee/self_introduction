"""真实视频编码和配置写入回归检查，临时产物限定在非 C 盘。"""
import json
from pathlib import Path
import tempfile
import unittest

import core
import video_tools as video


class VideoTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent
        temporary = self.root / 'desktop-tool/.test-work'
        temporary.mkdir(exist_ok=True)
        self.work = tempfile.TemporaryDirectory(prefix='video-', dir=str(temporary))
        self.addCleanup(self.work.cleanup)
        self.folder = Path(self.work.name)
        self.source = self.root / 'assets/videos/moment-001-web.mp4'

    def test_preserve_browser_ready_source_and_generate_poster(self):
        before = core.digest(self.source)
        result = video.compress(self.source, self.folder / 'web.mp4', self.folder)
        self.assertLess(result['size'], video.MAX_BYTES)
        self.assertEqual(result['width'], 1280)
        self.assertEqual(core.digest(self.source), before)
        video.poster(result['path'], self.folder / 'poster.jpg', self.folder)
        self.assertGreater((self.folder / 'poster.jpg').stat().st_size, 1000)
        self.assertEqual(list((self.folder / 'temp').iterdir()), [])

    def test_two_pass_respects_actual_file_size(self):
        stages = []
        result = video.compress(self.source, self.folder / 'bounded.mp4', self.folder,
                                max_bytes=80_000, progress=lambda stage, *args: stages.append(stage))
        self.assertLess(result['size'], 80_000)
        self.assertTrue(any('第二次编码' in stage for stage in stages))

    def test_existing_file_never_overwritten(self):
        target = self.folder / 'existing.mp4'
        target.write_bytes(b'keep')
        with self.assertRaises(ValueError):
            video.compress(self.source, target, self.folder)
        self.assertEqual(target.read_bytes(), b'keep')

    def test_metadata_round_trip_and_concurrent_edit_guard(self):
        (self.folder / 'assets').mkdir()
        (self.folder / 'js').mkdir()
        (self.folder / 'assets/test.mp4').write_bytes(b'video')
        (self.folder / 'index.html').write_text('<script src="js/video-config.js?v=old"></script>', encoding='utf-8')
        old = video.read_catalog(self.folder)
        entry = {'title': '秋日', 'description': '一段日常', 'location': '拍摄地', 'src': 'assets/test.mp4'}
        video.save_catalog(self.folder, old, [entry])
        self.assertEqual(video.read_catalog(self.folder)['config']['videos'], [entry])
        self.assertNotIn('?v=old', (self.folder / 'index.html').read_text())
        before = (self.folder / video.CONFIG).read_bytes()
        with self.assertRaises(ValueError):
            video.save_catalog(self.folder, old, [])
        self.assertEqual((self.folder / video.CONFIG).read_bytes(), before)


if __name__ == '__main__':
    unittest.main()

"""从选择母相册到确认合并的真实 Tk 界面流程，只操作临时网站。"""
from pathlib import Path
import tempfile
import time
from unittest.mock import patch

import app
import core


def wait(ui):
    end = time.monotonic() + 10
    while ui.busy and time.monotonic() < end:
        ui.update()
        time.sleep(.02)
    assert not ui.busy


work = Path(__file__).parent / '.test-work'
work.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(dir=str(work)) as temp:
    folder = Path(temp)
    root = folder / '网站'
    for name in ('js', 'css', 'assets/images/母', 'assets/images/子'):
        (root / name).mkdir(parents=True)
    (root / 'index.html').write_text('<html></html>', encoding='utf-8')
    (root / 'css/style.css').write_text(':root{}', encoding='utf-8')
    (root / 'js/data.js').write_text('''const SITE_DATA = {photos: [
      {city: '母', seal: '母印', star: true, desc: '母简介', tags: ['甲'], photos: [
        {src: 'assets/images/母/照片.jpg', title: '母照片'}]},
      {city: '子', seal: '子印', star: false, tags: ['乙'], photos: [
        {src: 'assets/images/子/照片.jpg', title: '子照片'}]}
    ]};''', encoding='utf-8')
    (root / 'assets/images/母/照片.jpg').write_bytes(b'mother')
    (root / 'assets/images/子/照片.jpg').write_bytes(b'child')
    with patch.object(app, 'STATE', folder / 'state'):
        ui = app.App(maintenance=False)
        try:
            errors = []
            ui.error = lambda error: errors.append(str(error))
            ui.site.set(str(root))
            ui.refresh_site()
            ui.tabs.select(6)
            assert '相册合并' in ui.tabs.tab(6, 'text')
            ui.merge_mother.set('母')
            ui.merge_mother_selected()
            assert ui.merge_folder.get() == 'assets/images/母'
            child = list(ui.merge_sources.get(0, 'end')).index('子')
            ui.merge_sources.selection_set(child)
            ui.preview_merge()
            wait(ui)
            assert not errors, errors
            assert ui.merge_plan['photos'] == 1
            assert '同名覆盖：1 个' in ui.merge_preview.get('1.0', 'end')
            assert str(ui.merge_apply.cget('state')) == 'normal'
            ui.merge_folder.set('assets/images/别处')
            assert ui.merge_plan is None
            assert str(ui.merge_apply.cget('state')) == 'disabled'
            ui.merge_folder.set('assets/images/母')
            ui.preview_merge()
            wait(ui)
            ui.merge_apply.invoke()
            wait(ui)
            assert not errors, errors
            assert list(ui.merge_mother_combo['values']) == ['母']
            assert list(ui.merge_sources.get(0, 'end')) == ['母']
            data = core.read_album(root, '母')
            assert data['seal'] == '母印' and data['star']
            assert data['tags'] == ['甲', '乙']
            assert (root / 'assets/images/母/照片.jpg').read_bytes() == b'child'
            assert not (root / 'assets/images/子/照片.jpg').exists()
            assert ui.edit_choice.get() == '母'
        finally:
            ui.destroy()
print('Merge UI: separate module, selection, preview, invalidation, overwrite, mother metadata and refreshed album lists passed.')

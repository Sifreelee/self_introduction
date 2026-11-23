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
    (root / 'js/data.js').write_text('''const SITE_DATA = {cities: ['母@山西', '北京'], photos: [
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
            assert '荔荔精选' in ui.tabs.tab(7, 'text')
            ui.featured_album.set('母')
            ui.load_featured_photos(True)
            assert ui.featured_src.get() == 'assets/images/母/照片.jpg'
            assert ui.featured_photo_options
            ui.featured_photo_combo.current(0)
            ui.choose_featured_album_photo()
            assert ui.featured_album.get() == '母'
            photo = folder / '新的精选.jpg'
            app.Image.new('RGB', (20, 20)).save(str(photo))
            ui.tabs.select(7)
            with patch.object(app.filedialog, 'askopenfilename', return_value=str(photo)):
                ui.pick_featured_photo()
            ui.choose_featured_album_photo()
            assert ui.featured_source == str(photo.resolve())
            ui.featured_album.set('母')
            ui.featured_note.set('手动编辑的配文')
            ui.save_featured()
            wait(ui)
            assert not errors, errors
            assert app.featured.read(root)['recent']['note'] == '手动编辑的配文'
            assert (root / 'assets/images/featured/新的精选.jpg').exists()
            ui.tabs.select(8)
            ui.map_city.set('母')
            ui.load_map_city()
            assert ui.map_photo_options
            ui.map_photos.selection_set(0)
            ui.preview_map_photo()
            ui.map_confirm_selection.invoke()
            wait(ui)
            assert not errors, errors
            assert app.featured.read_map_city(root, '母')['photos'] == ['assets/images/母/照片.jpg']
            ui.delete_map_city()
            wait(ui)
            assert not errors, errors
            assert ui.map_city.get() == '北京'
            assert [place['city'] for place in app.featured.map_places(root)] == ['北京']
            assert core.read_album(root, '母')['city'] == '母'
            assert (root / 'assets/images/母/照片.jpg').exists()
            ui.map_albums.selection_set(0)
            ui.load_map_photos()
            from types import SimpleNamespace
            ui.update()
            bbox = ui.map_photos.bbox('0')
            assert bbox
            row_y = bbox[1] + bbox[3] // 2
            ui.map_photos.toggle_row(SimpleNamespace(keysym='??', x=90, y=row_y))
            assert ui.map_photos.curselection() == ()
            assert '已选 0 / 9 张' in ui.map_selection_status.get()
            ui.map_photos.toggle_row(SimpleNamespace(keysym='??', x=15, y=row_y))
            assert ui.map_photos.curselection() == (0,)
            assert '已选 1 / 9 张' in ui.map_selection_status.get()
            assert ui.map_selected_count.get() == '已选 1 张 / 9 张'
            assert ui.map_confirm_text.get() == '确认选取（已选 1 张）'
            assert ui.map_count_label.winfo_ismapped()
            assert ui.map_count_label.winfo_rooty() < ui.map_photos.winfo_rooty()
            assert '未保存' in ui.map_selection_status.get()
            ui.map_photos.toggle_row(SimpleNamespace(keysym='??', x=90, y=row_y))
            assert ui.map_photos.curselection() == (0,)
            ui.map_photos.toggle_row(SimpleNamespace(keysym='??', x=15, y=row_y))
            assert ui.map_photos.curselection() == ()
            ui.map_photos.focus('0')
            ui.map_photos.toggle_row(SimpleNamespace(keysym='space', y=0))
            assert ui.map_photos.curselection() == (0,)
            assert ui.map_photos.item('0', 'text').startswith('☑')
            ui.edit_map_slots()
            window = next(child for child in ui.winfo_children() if isinstance(child, app.tk.Toplevel))
            def descend(parent):
                for child in parent.winfo_children():
                    yield child
                    yield from descend(child)
            combos = [child for child in descend(window) if isinstance(child, app.ttk.Combobox)]
            assert len(combos) == 9
            for combo in combos:
                combo.current(0)
            combos[8].current(1)
            apply = next(child for child in descend(window) if isinstance(child, app.ttk.Button) and child.cget('text') == '应用位置选择')
            apply.invoke()
            assert ui.map_slots[:8] == [''] * 8
            assert ui.map_slots[8] == 'assets/images/母/照片.jpg'
            ui.save_map_city()
            wait(ui)
            assert not errors, errors
            assert app.featured.read_map_city(root, '北京')['slots'][8] == 'assets/images/母/照片.jpg'
            assert '已选 1 / 9 张' in ui.map_selection_status.get()
            assert '已保存' in ui.map_selection_status.get()
            ui.load_map_city()
            assert ui.map_photos.curselection() == (0,)
            reopened = app.App(maintenance=False)
            try:
                assert reopened.map_city.get() == '北京'
                assert reopened.map_photos.curselection() == (0,)
                assert '已选 1 / 9 张' in reopened.map_selection_status.get()
                assert '已保存' in reopened.map_selection_status.get()
            finally:
                reopened.destroy()
        finally:
            ui.destroy()
print('Merge UI: separate module, selection, preview, invalidation, overwrite, mother metadata and refreshed album lists passed.')

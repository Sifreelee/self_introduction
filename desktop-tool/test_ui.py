"""检查全部页面在默认及最小窗口尺寸下的控件边界。"""
import app
import core
from pathlib import Path
import shutil
import tempfile
import time
from unittest.mock import patch, Mock


if __name__ == '__main__':
    ui = app.App(maintenance=False)
    try:
        assert len(ui.albums) > 5
        # 真实网站的每本相册均能读取到表单，并生成代码；不保存、不修改网站。
        def fail(error):
            raise error
        ui.error = fail
        for album in ui.albums:
            ui.edit_choice.set(album['name'])
            ui.load_editor()
            code = core.album_code(ui.root_path(), ui.editor_original, ui.editor_metadata())
            assert album['name'] in code['相册代码片段']
        ui.show_code({'data.js': 'const SITE_DATA = {photos: []};'}, '代码窗口测试')
        ui.update()
        for child in ui.winfo_children():
            if isinstance(child, app.tk.Toplevel):
                child.destroy()
        def visible_children(parent):
            for widget in parent.winfo_children():
                if widget.winfo_ismapped():
                    yield widget
                    yield from visible_children(widget)
        for width, height in ((1180, 860), (1040, 780)):
            ui.geometry('%dx%d' % (width, height))
            for page in range(len(ui.tabs.tabs())):
                ui.tabs.select(page)
                ui.update()
                for widget in visible_children(ui):
                    x = widget.winfo_rootx() - ui.winfo_rootx()
                    y = widget.winfo_rooty() - ui.winfo_rooty()
                    assert x >= 0 and y >= 0 and x + widget.winfo_width() <= width + 2 and y + widget.winfo_height() <= height + 2, (page, str(widget), x, y, widget.winfo_width(), widget.winfo_height())
        ui.geometry('1180x860')
        ui.tabs.select(0)
        ui.update()

        # 重现用户流程：点击创建后，两个列表立即出现新相册，并跳到添加照片。
        work = Path(__file__).parent / '.test-work'
        work.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=str(work)) as tmp:
            folder = Path(tmp)
            site = folder / '网站'
            for name in ('js', 'css', 'assets/images'):
                (site / name).mkdir(parents=True, exist_ok=True)
            (site / 'index.html').write_text('<html></html>', encoding='utf-8')
            (site / 'css/style.css').write_text(':root {--card: #F6F0E2;}', encoding='utf-8')
            (site / 'js/data.js').write_text('const SITE_DATA = {photos: []};', encoding='utf-8')
            with patch.object(app, 'STATE', folder / 'state'):
                flow = app.App(maintenance=False)
                try:
                    errors = []
                    flow.error = lambda e: errors.append(str(e))
                    flow.site.set(str(site))
                    flow.refresh_site()
                    flow.tabs.select(1)
                    with patch.object(app.simpledialog, 'askstring', return_value='回归新相册'):
                        flow.create_album_now()
                    deadline = time.monotonic() + 8
                    while flow.busy and time.monotonic() < deadline:
                        flow.update()
                        time.sleep(.02)
                    assert not flow.busy and not errors, errors
                    assert '回归新相册' in flow.album_combo['values']
                    assert '回归新相册' in flow.edit_combo['values']
                    assert flow.album.get() == '回归新相册'
                    assert flow.edit_choice.get() == '回归新相册'
                    assert flow.tabs.index('current') == 0
                    assert core.Document((site / 'js/data.js').read_text(encoding='utf-8')).albums()[0]['name'] == '回归新相册'
                    # 选择整文件夹后自动使用该目录，单批直接导入，并保留本次照片代码。
                    photos = site / 'assets/images/测试集'
                    photos.mkdir()
                    app.Image.new('RGBA', (64, 48), (255, 0, 0, 0)).save(str(photos / '透明.png'))
                    with patch.object(app.filedialog, 'askdirectory', return_value=str(photos)):
                        flow.pick_folder()
                    assert flow.target.get() == 'assets/images/测试集'
                    assert flow.photo_dialog_start() == str(photos.resolve())
                    assert flow.overwrite.get() is True
                    assert len(flow.jobs_tree.get_children()) == 1
                    first = flow.jobs_tree.get_children()[0]
                    listed = flow.jobs_tree.item(first, 'values')
                    assert listed[0] == '透明.png' and listed[1] == 'PNG'
                    assert listed[2].endswith('KB') and listed[3].endswith('透明.jpg')
                    flow.add_job()
                    assert not flow.files and len(flow.jobs_tree.get_children()) == 1
                    flow.jobs_tree.selection_set(flow.jobs_tree.get_children()[0])
                    flow.remove_job()
                    assert not flow.jobs and not flow.jobs_tree.get_children()
                    with patch.object(app.filedialog, 'askdirectory', return_value=str(photos)):
                        flow.pick_folder()
                    app.Image.new('RGB', (8, 8), 'blue').save(str(photos / '透明.jpg'))
                    flow.refresh_upload_list()
                    assert flow.jobs_tree.item(flow.jobs_tree.get_children()[0], 'values')[-1] == '自动覆盖'
                    with patch.object(flow, 'show_code') as show:
                        flow.current_upload_code()
                        assert 'assets/images/测试集/透明.jpg' in show.call_args[0][0]['本次照片 data.js 片段']
                    previews = []
                    real_preview = flow.show_upload_preview
                    def preview(entries, opts):
                        result = real_preview(entries, opts)
                        previews.append(result)
                        return result
                    with patch.object(flow, 'show_upload_preview', side_effect=preview):
                        flow.preview_upload_files()
                        flow.update()
                    assert previews and previews[0].winfo_exists()
                    previews[0].destroy()
                    assert not flow.jobs
                    flow.start_import()
                    deadline = time.monotonic() + 8
                    while flow.busy and time.monotonic() < deadline:
                        flow.update()
                        time.sleep(.02)
                    assert not flow.busy and not errors, errors
                    assert (photos / '透明.jpg').exists()
                    with app.Image.open(str(photos / '透明.jpg')) as replaced:
                        assert replaced.size == (64, 48)
                    assert flow.jobs_tree.item(flow.jobs_tree.get_children()[0], 'values')[-1] == '已添加'
                    assert flow.last_upload_code and '透明.jpg' in flow.last_upload_code['本次照片 data.js 片段']
                    assert flow.target.get() == 'assets/images/测试集'
                    restored = app.App(maintenance=False)
                    try:
                        assert restored.target.get() == 'assets/images/测试集'
                        assert restored.photo_dialog_start() == str(photos.resolve())
                    finally:
                        restored.update()
                        for timer in restored.tk.call('after', 'info'):
                            restored.after_cancel(timer)
                        restored.destroy()
                    core.save_album(site, app.STATE, None, {'city': '第二本'})
                    flow.refresh_site()
                    flow.edit_choice.set('回归新相册')
                    flow.load_editor()
                    flow.edit_position.set('2')
                    flow.save_editor()
                    deadline = time.monotonic() + 8
                    while flow.busy and time.monotonic() < deadline:
                        flow.update()
                        time.sleep(.02)
                    assert not flow.busy and not errors, errors
                    assert tuple(flow.edit_combo['values']) == ('第二本', '回归新相册')
                    external = folder / '外部原图'
                    external.mkdir()
                    flow.use_source_folder(external)
                    assert flow.target.get() == 'assets/images/外部原图'
                    flow.album_selected()
                    assert flow.target.get() == 'assets/images/外部原图'
                    # 刷新确实重读目录，右键动作定位当前文件，不使用过时路径。
                    (external / '照片 其二.jpg').write_bytes(b'2')
                    (external / '照片 其一.jpg').write_bytes(b'1')
                    with patch.object(app.filedialog, 'askdirectory', return_value=str(external)):
                        flow.pick_folder()
                    (external / '照片 其一.jpg').rename(external / '照片 其三.jpg')
                    (external / '照片 十一.jpg').write_bytes(b'11')
                    flow.rescan_upload_files()
                    visible = [flow.jobs_tree.item(row, 'values')[0] for row in flow.jobs_tree.get_children()]
                    assert visible == ['照片 其二.jpg', '照片 其三.jpg', '照片 十一.jpg'], visible
                    first = flow.jobs_tree.get_children()[0]
                    flow.jobs_tree.selection_set(first)
                    flow.jobs_tree.focus(first)
                    with patch.object(core, 'reveal_file') as reveal:
                        flow.reveal_selected_upload_file()
                        assert reveal.call_args[0][0].name == '照片 其二.jpg'
                    renames = site / 'assets/images/改名测试'
                    renames.mkdir()
                    for name in ('景点01.jpg', '景点05.jpg'):
                        (renames / name).write_bytes(b'photo')
                    flow.rename_dir.set(str(renames))
                    flow.preview_rename()
                    assert len(flow.plan) == 2
                    flow.start_rename()
                    deadline = time.monotonic() + 8
                    while flow.busy and time.monotonic() < deadline:
                        flow.update()
                        time.sleep(.02)
                    assert not errors, errors
                    flow.preview_rename()
                    assert len(flow.rename_tree.get_children()) == 2
                    assert not flow.plan
                    assert all(flow.rename_tree.item(row, 'values')[-1] == '名称不变' for row in flow.rename_tree.get_children())
                    process = Mock()
                    process.poll.return_value = None
                    with patch.object(core, 'launch_push_script', return_value=(process, folder / 'upload.bat')) as launch:
                        flow.start_publish()
                        launch.assert_called_once_with(flow.root_path(), app.STATE)
                        assert '上传窗口' in flow.status.get()
                        flow.start_publish()
                        assert launch.call_count == 1
                finally:
                    flow.destroy()

        print('UI: %d pages x 2 sizes; create, file preview, direct import, batch code, path history and album ordering passed.' % len(ui.tabs.tabs()))
    finally:
        ui.destroy()


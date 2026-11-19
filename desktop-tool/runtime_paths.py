"""在 PyInstaller 内置运行钩子之前指定非 C 盘的临时目录。"""
import os
import sys
import tempfile

folder = os.path.dirname(sys.executable)
if os.path.splitdrive(os.path.abspath(folder))[0].upper() == 'C:':
    raise RuntimeError('请将整个程序文件夹移到非 C 盘后运行。')
task_temp = os.path.join(folder, '_data', 'temp')
os.makedirs(task_temp, exist_ok=True)
os.environ['TEMP'] = task_temp
os.environ['TMP'] = task_temp
tempfile.tempdir = task_temp
sys.dont_write_bytecode = True

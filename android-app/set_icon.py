# -*- coding: utf-8 -*-
"""一键换图标并重新打包。

由 set-icon.bat 调用，也可以直接命令行运行：
    python set_icon.py "D:\\some\\logo.png"

流程：归一化图片 → 重新生成全部图标资源 → Gradle 打包 → 复制到 dist/
"""
import glob
import os
import re
import shutil
import subprocess
import sys

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(APP_DIR, "dist")

# 本机构建环境，换机器时改这三行
JAVA_HOME = r"C:\Program Files\Java\jdk-17.0.2"
ANDROID_HOME = r"F:\android-sdk"
GRADLE_BAT = r"F:\android-build\gradle-8.9\bin\gradle.bat"

APK_REL = os.path.join("app", "build", "outputs", "apk", "release", "app-release.apk")


def step(msg):
    print("\n>>> " + msg, flush=True)


def fail(msg, code=1):
    print("\n[失败] " + msg, flush=True)
    sys.exit(code)


def build_env():
    env = os.environ.copy()
    env["JAVA_HOME"] = JAVA_HOME
    env["ANDROID_HOME"] = ANDROID_HOME
    env["ANDROID_SDK_ROOT"] = ANDROID_HOME
    env["PATH"] = os.path.join(JAVA_HOME, "bin") + os.pathsep + env.get("PATH", "")
    env["PYTHONUTF8"] = "1"
    return env


def read_version():
    """从 app/build.gradle 读出当前版本号。"""
    p = os.path.join(APP_DIR, "app", "build.gradle")
    txt = open(p, encoding="utf-8").read()
    name = re.search(r'versionName\s+"([^"]+)"', txt)
    code = re.search(r"versionCode\s+(\d+)", txt)
    return (name.group(1) if name else "0.0.0",
            code.group(1) if code else "1")


def normalize_image(src):
    """把任意图片统一存成 custom-icon.png，避免扩展名不一致读到旧文件。"""
    try:
        from PIL import Image
    except ImportError:
        fail("缺少 Pillow，请先运行：\n"
             r"  C:\Users\lenovo\.workbuddy\binaries\python\envs\default\Scripts\python.exe -m pip install pillow")

    try:
        im = Image.open(src)
        im.load()
    except Exception as e:
        fail("图片打不开：%s\n%s" % (src, e))

    # 丢掉历史的自定义图，避免 custom-icon.jpg 与 .png 同时存在
    for old in glob.glob(os.path.join(APP_DIR, "custom-icon.*")):
        try:
            os.remove(old)
        except OSError:
            pass

    out = os.path.join(APP_DIR, "custom-icon.png")
    im.convert("RGBA").save(out, "PNG")
    return out, im.size, im.mode


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd or APP_DIR, env=build_env())


def main():
    args = sys.argv[1:]
    if not args:
        fail("未提供图片路径。用法：python set_icon.py <图片路径>")

    if args[0] == "--pick":
        # 由 set-icon.bat 的文件选择框产出，路径含中文也能正确读取
        if len(args) < 2 or not os.path.isfile(args[1]):
            fail("未选择图片")
        with open(args[1], encoding="utf-8-sig") as f:
            src = f.read().strip()
        if not src:
            fail("未选择图片")
    else:
        src = args[0]

    src = os.path.abspath(src)
    if not os.path.isfile(src):
        fail("文件不存在：%s" % src)

    print("=" * 60, flush=True)
    print("换图标并重新打包", flush=True)
    print("图片：%s" % src, flush=True)
    print("=" * 60, flush=True)

    step("1/4 归一化图片")
    saved, size, mode = normalize_image(src)
    print("    尺寸 %dx%d  模式 %s" % (size[0], size[1], mode), flush=True)
    print("    已保存 %s" % saved, flush=True)

    step("2/4 生成图标资源（5 档密度 + 自适应图标）")
    r = run([sys.executable, os.path.join(APP_DIR, "make_icons.py")])
    if r.returncode != 0:
        fail("图标生成失败，看上面对应输出")

    step("3/4 Gradle 打包")
    if not os.path.isfile(GRADLE_BAT):
        fail("找不到 Gradle：%s" % GRADLE_BAT)
    r = run([GRADLE_BAT, "assembleRelease"])
    if r.returncode != 0:
        fail("打包失败，看上面 Gradle 输出")

    apk = os.path.join(APP_DIR, APK_REL)
    if not os.path.isfile(apk):
        fail("没有找到产物：%s" % apk)

    step("4/4 输出到 dist")
    ver, code = read_version()
    os.makedirs(DIST_DIR, exist_ok=True)
    ascii_name = "LuQingYueFei-v%s.apk" % ver
    cn_name = "洛晴跃飞-v%s.apk" % ver
    dst_ascii = os.path.join(DIST_DIR, ascii_name)
    dst_cn = os.path.join(DIST_DIR, cn_name)
    shutil.copy2(apk, dst_ascii)
    shutil.copy2(apk, dst_cn)

    size_kb = os.path.getsize(dst_cn) / 1024.0

    print("", flush=True)
    print("=" * 60, flush=True)
    print("完成", flush=True)
    print("  版本     %s  (versionCode %s)" % (ver, code), flush=True)
    print("  体积     %.0f KB" % size_kb, flush=True)
    print("  成品     %s" % dst_cn, flush=True)
    print("=" * 60, flush=True)

    # 自动打开输出目录，方便直接拖进微信发送
    if not os.environ.get("NO_OPEN"):
        try:
            os.startfile(DIST_DIR)
        except Exception:
            pass


if __name__ == "__main__":
    main()

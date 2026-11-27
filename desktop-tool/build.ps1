param([string]$Python = 'python')
$ErrorActionPreference = 'Stop'
$toolDir = $PSScriptRoot
if ([IO.Path]::GetPathRoot($toolDir) -eq 'C:\') { throw '请把项目放在非 C 盘再打包。' }
$buildRoot = Join-Path $toolDir '.build'
New-Item -ItemType Directory -Force -Path $buildRoot | Out-Null
$env:TEMP = Join-Path $buildRoot 'temp'
$env:TMP = $env:TEMP
$env:PYTHONPYCACHEPREFIX = Join-Path $buildRoot 'pycache'
$env:PYINSTALLER_CONFIG_DIR = Join-Path $buildRoot 'pyinstaller-cache'
$env:PIP_CACHE_DIR = Join-Path $buildRoot 'pip-cache'
$env:PYTHONUTF8 = '1'
New-Item -ItemType Directory -Force -Path $env:TEMP | Out-Null
$distDir = Join-Path $toolDir 'dist'
$profileDir = Join-Path $distDir 'ShanshuiManager'
$releaseRecord = Join-Path $buildRoot 'latest-release.txt'
if (Test-Path -LiteralPath $releaseRecord) {
    $recordedDir = (Get-Content -LiteralPath $releaseRecord -Raw).Trim()
    $distBoundary = [IO.Path]::GetFullPath($distDir).TrimEnd('\') + '\'
    if ($recordedDir -and [IO.Path]::GetFullPath($recordedDir).StartsWith($distBoundary, [StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $recordedDir)) {
        $profileDir = $recordedDir
    }
}
$iconPath = Join-Path $buildRoot 'app.ico'
$customIcon = Join-Path $toolDir 'custom-icon.png'
if (Test-Path -LiteralPath $customIcon) {
    & $Python -c 'from PIL import Image; import sys; im=Image.open(sys.argv[1]).convert("RGBA"); im.thumbnail((256,256)); out=Image.new("RGBA",(256,256)); out.paste(im,((256-im.width)//2,(256-im.height)//2)); out.save(sys.argv[2],sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])' $customIcon $iconPath
} else {
    & $Python -c 'from PIL import Image,ImageDraw; import sys; im=Image.new("RGBA",(256,256),"#EFE8D6"); d=ImageDraw.Draw(im); d.rectangle((24,24,232,232),fill="#A83A32"); d.line([(52,180),(100,96),(144,152),(174,110),(208,180)],fill="#F6F0E2",width=12); d.ellipse((166,53,196,83),fill="#F6F0E2"); im.save(sys.argv[1],sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])' $iconPath
}
if ($LASTEXITCODE -ne 0) { throw '生成图标失败。' }
# onedir 不会在启动时向系统临时目录解压，整个文件夹可直接移动到非 C 盘。
$stagedDist = Join-Path $buildRoot 'staged-dist'
$pushSource = Join-Path (Split-Path $toolDir -Parent) 'push.bat'
$ffmpegSource = Join-Path $toolDir '_data/tools/ffmpeg.exe'
if (-not (Test-Path -LiteralPath $ffmpegSource)) { throw '缺少视频编码器：请将 ffmpeg.exe 放入 desktop-tool/_data/tools 后打包。' }
& $Python -m PyInstaller --noconfirm --clean --windowed --onedir --name 'ShanshuiManager' --icon $iconPath --add-data "$pushSource;resources" --add-data "$ffmpegSource;resources" --runtime-hook (Join-Path $toolDir 'runtime_paths.py') --paths (Split-Path $toolDir -Parent) --distpath $stagedDist --workpath (Join-Path $buildRoot 'work') --specpath $buildRoot (Join-Path $toolDir 'app.py')
if ($LASTEXITCODE -ne 0) { throw 'EXE 打包失败。' }
$previousDir = Join-Path $distDir 'ShanshuiManager'
$releaseDir = $previousDir
$existingExe = Join-Path $releaseDir 'ShanshuiManager.exe'
if (Test-Path -LiteralPath $existingExe) {
    try {
        $probe = [IO.File]::Open($existingExe, 'Open', 'ReadWrite', 'None')
        $probe.Dispose()
    } catch {
        $releaseDir = Join-Path $distDir 'ShanshuiManager-v2'
        $releaseNumber = 2
        while (Test-Path -LiteralPath $releaseDir) {
            $releaseNumber++
            $releaseDir = Join-Path $distDir ('ShanshuiManager-v' + $releaseNumber)
        }
    }
}
New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null
# 从暂存构建复制程序文件，不删除用户 _data。旧版运行中时发布到新目录。
Get-ChildItem -LiteralPath (Join-Path $stagedDist 'ShanshuiManager') -Force | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $releaseDir -Recurse -Force
}
$oldData = Join-Path $profileDir '_data'
$newData = Join-Path $releaseDir '_data'
if ($releaseDir -ne $profileDir -and (Test-Path -LiteralPath $oldData)) {
    New-Item -ItemType Directory -Force -Path $newData | Out-Null
    Get-ChildItem -LiteralPath $oldData -Force | Where-Object { $_.Name -notin @('temp','history','upload-sessions','preview-cache','previous-version-logs') } | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $newData -Recurse -Force
    }
}
Copy-Item -LiteralPath (Join-Path $toolDir '使用说明.md') -Destination (Join-Path $releaseDir '使用说明.md') -Force
Set-Content -LiteralPath (Join-Path $buildRoot 'latest-release.txt') -Value $releaseDir -Encoding utf8
Write-Host "完成：$releaseDir\ShanshuiManager.exe"

param([switch]$CheckOnly)
$ErrorActionPreference = 'Stop'
$distRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot 'dist'))
$record = Join-Path $PSScriptRoot '.build/latest-release.txt'
$exe = $null
if (Test-Path -LiteralPath $record) {
    $release = (Get-Content -LiteralPath $record -Raw -Encoding UTF8).Trim()
    if ($release -and [IO.Path]::GetFullPath($release).StartsWith($distRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
        $candidate = Join-Path $release 'ShanshuiManager.exe'
        if (Test-Path -LiteralPath $candidate) { $exe = $candidate }
    }
}
if (-not $exe) {
    $latest = Get-ChildItem -LiteralPath $distRoot -Filter 'ShanshuiManager.exe' -File -Recurse |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latest) { $exe = $latest.FullName }
}
if (-not $exe) { throw '没有找到上传软件，请先运行 desktop-tool/build.ps1 打包。' }
if ($CheckOnly) { Write-Output $exe; exit 0 }
Start-Process -FilePath $exe -WorkingDirectory (Split-Path -Parent $exe) -WindowStyle Hidden

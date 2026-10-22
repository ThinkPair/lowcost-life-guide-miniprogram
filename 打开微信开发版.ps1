$ErrorActionPreference = 'Stop'
$lifeProject = Join-Path $PSScriptRoot 'miniprogram'
$lifeCliCandidates = @(
  (Join-Path ${env:ProgramFiles(x86)} 'Tencent\微信web开发者工具\cli.bat'),
  (Join-Path $env:ProgramFiles 'Tencent\微信web开发者工具\cli.bat')
)
$lifeCli = $lifeCliCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $lifeCli) { throw '没有找到微信开发者工具，请在工具中手动导入同目录下的 miniprogram 文件夹。' }
& $lifeCli open --project $lifeProject --lang zh
if ($LASTEXITCODE -ne 0) { throw '微信开发者工具未能打开工程，请手动导入 miniprogram。' }

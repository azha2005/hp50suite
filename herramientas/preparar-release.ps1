# Build a distribution from current sources. No ROM or third-party software.
$ErrorActionPreference = 'Stop'
$raizSuite = Split-Path $PSScriptRoot -Parent
Push-Location $raizSuite
try {
    # Child processes isolate scripts that use exit. Stop on any failed check.
    $motor = (Get-Process -Id $PID).Path
    & $motor -NoProfile -File ./verificar.ps1 './programas/*.txt' './programas/mat1/*.txt' './programas/datos/*.txt'
    if ($LASTEXITCODE -ne 0) { throw 'Source verification failed' }
    foreach ($script in @('armar-lab.ps1', 'armar-mat1.ps1')) {
        & $motor -NoProfile -File (Join-Path 'programas' $script)
        if ($LASTEXITCODE -ne 0) { throw "Build failed: $script" }
    }
    & $motor -NoProfile -File ./verificar.ps1 ./programas/LAB.txt ./programas/MAT1.txt
    if ($LASTEXITCODE -ne 0) { throw 'Package verification failed' }
    $destinoSuite = Join-Path $raizSuite 'dist'
    New-Item -ItemType Directory -Force $destinoSuite | Out-Null
    $archivosSuite = @('programas/LAB.txt', 'programas/MAT1.txt', 'programas/DINF.txt',
        'INICIO-RAPIDO.md', 'DICCIONARIO-LAB.md', 'DICCIONARIO-MAT1.md', 'LICENSE')
    $hashesSuite = foreach ($rutaSuite in $archivosSuite) {
        '{0}  {1}' -f (Get-FileHash -Algorithm SHA256 $rutaSuite).Hash.ToLowerInvariant(), (Split-Path $rutaSuite -Leaf)
    }
    $manifiestoSuite = Join-Path $destinoSuite 'SHA256SUMS'
    [IO.File]::WriteAllLines($manifiestoSuite, $hashesSuite, [Text.Encoding]::ASCII)
    Compress-Archive -LiteralPath ($archivosSuite + $manifiestoSuite) -DestinationPath (Join-Path $destinoSuite 'hp50suite.zip') -Force
    # The external manifest also verifies the downloadable ZIP. The manifest
    # inside the archive covers its seven payload files (no circular hash).
    $hashZipSuite = (Get-FileHash -Algorithm SHA256 (Join-Path $destinoSuite 'hp50suite.zip')).Hash.ToLowerInvariant()
    [IO.File]::AppendAllText($manifiestoSuite, "$hashZipSuite  hp50suite.zip`r`n", [Text.Encoding]::ASCII)
    Write-Host "Ready: $destinoSuite/hp50suite.zip (static checks only; no emulator run)"
} finally {
    Pop-Location
}

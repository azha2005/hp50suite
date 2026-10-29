# Original harness key channel: targets Emu48 only, without stealing focus.
param([int[]]$Teclas = @(), [string]$Foto = '', [int]$EsperaMs = 500)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'emu-ventana.ps1')
$bancoProcesos = @(Get-Process EMU48 -ErrorAction SilentlyContinue)
if ($bancoProcesos.Count -ne 1) { throw 'Expected exactly one EMU48 process' }
$bancoH = [EmuBanco]::Window($bancoProcesos[0].Id)
foreach ($bancoK in $Teclas) { [EmuBanco]::Key($bancoH,$bancoK) }
if ($EsperaMs -gt 0) { Start-Sleep -Milliseconds $EsperaMs }
if ($Foto) { [EmuBanco]::Capture($bancoH,[IO.Path]::GetFullPath($Foto)) }

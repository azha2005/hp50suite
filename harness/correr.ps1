# correr.ps1 - lado PC del harness: se trae el resultado de la pila del
#              emulador y lo compara contra los casos.
#
# Requisitos antes de correrlo:
#   1. El Emu48 de Debug4x abierto con el KML de 50g (R50g1024.kml, que usa
#      ROMG+.50G: es la ROM de la 50g de verdad, medido en el emulador).
#   2. BATERIA instalada en la calculadora (una vez; ver README.md de esta
#      carpeta).
#   3. BATERIA ejecutada, con la lista de resultados en el nivel 1.
#
# Lo que hace este script es el paso 4: DDE48 r + comparacion. El unico paso
# manual que queda es apretar la tecla que corre BATERIA.
#
# Uso:
#   .\correr.ps1
#   .\correr.ps1 -Casos casos-escapes.txt

[CmdletBinding()]
param(
    [string]$Casos = '',
    [string]$Salida = '',
    [string]$Dde48 = 'C:\Program Files (x86)\Hewlett-Packard\Debug4x\Emu\DDE48.exe'
)

$ErrorActionPreference = 'Stop'

$aqui = Split-Path -Parent $MyInvocation.MyCommand.Definition
if ([string]::IsNullOrEmpty($aqui)) { $aqui = (Get-Location).Path }
if ($Casos  -eq '') { $Casos  = Join-Path $aqui 'casos.txt' }
if ($Salida -eq '') { $Salida = Join-Path $aqui 'salida.bin' }

if (-not (Test-Path -LiteralPath $Dde48)) {
    throw "No encontre DDE48.exe en: $Dde48"
}

Write-Host "Pidiendo el nivel 1 de la pila del emulador..." -ForegroundColor Cyan
& $Dde48 'r' $Salida
if ($LASTEXITCODE -ne 0) {
    Write-Host "DDE48 no pudo traer el objeto." -ForegroundColor Red
    Write-Host "Revisar que el Emu48 este abierto y que haya algo en el nivel 1." -ForegroundColor Yellow
    exit 1
}

$bytes = (Get-Item -LiteralPath $Salida).Length
Write-Host "Recibidos $bytes bytes en $Salida" -ForegroundColor Green
Write-Host ""

python (Join-Path $aqui 'leer-resultado.py') $Salida $Casos
exit $LASTEXITCODE

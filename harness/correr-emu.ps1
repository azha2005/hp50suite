# correr-emu.ps1 - ciclo completo del harness contra el Emu48 de Debug4x,
#                  sin tocar el teclado.
#
#   1. DDE48 s   manda el objeto a la pila del emulador
#   2. PostMessage le manda la tecla EVAL a la ventana (no roba el foco:
#      va al handle, no al teclado del sistema)
#   3. espera
#   4. DDE48 r    se trae el nivel 1
#   5. leer-resultado.py lo decodifica y lo compara contra los casos
#
# El objeto se arma con herramientas\compilar.py, que envuelve el fuente en
# \<< "texto" STR\-> EVAL \>>: asi la calculadora compila con su propio STR\->
# y no hace falta ASCIIBIN ni el menu del emulador.
#
# Mapeo de teclas del KML de 50g: las teclas de la calculadora estan mapeadas
# en orden alfabetico a las del PC. EVAL es la tecla 42 = vk 78 ('N').
#
# Uso:
#   .\correr-emu.ps1
#   .\correr-emu.ps1 -Fuente BESC.txt -Casos casos-escapes.txt -EsperaMs 30000

[CmdletBinding()]
param(
    [string]$Fuente   = '',
    [string]$Casos    = '',
    [int]   $Vk       = 78,        # 'N' -> tecla 42 -> EVAL
    [int]   $EsperaMs = 20000,
    [int]   $EnterCadaMs = 4000,
    [int]   $Reintentos = 3,
    [switch]$SinComparar,          # deja el objeto crudo y no compara
    [string]$Bin = '',             # donde dejarlo
    [string]$Dde48 = 'C:\Program Files (x86)\Hewlett-Packard\Debug4x\Emu\DDE48.exe'
)

$ErrorActionPreference = 'Stop'

$aqui = Split-Path -Parent $MyInvocation.MyCommand.Definition
if ([string]::IsNullOrEmpty($aqui)) { $aqui = (Get-Location).Path }
if ($Fuente -eq '') { $Fuente = Join-Path $aqui 'BATERIA.txt' }
if ($Casos  -eq '') { $Casos  = Join-Path $aqui 'casos.txt' }
$objeto = [IO.Path]::ChangeExtension($Fuente, '.hp')
$salida = if ($Bin -ne '') { $Bin } else { Join-Path $aqui 'salida.bin' }

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class EmuTecla {
    [DllImport("user32.dll")] static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
    public static void Enviar(IntPtr h, int vk) {
        PostMessage(h, 0x0100, (IntPtr)vk, IntPtr.Zero);
        System.Threading.Thread.Sleep(80);
        PostMessage(h, 0x0101, (IntPtr)vk, IntPtr.Zero);
    }
}
'@

$proc = Get-Process -Name EMU48 -ErrorAction SilentlyContinue
if (-not $proc) { throw "No hay ningun EMU48 abierto. Abrirlo con el estado 'Default 50g.E49'." }
if (-not (Test-Path -LiteralPath $Dde48)) { throw "No encontre DDE48.exe en: $Dde48" }

Write-Host "1. compilando $([IO.Path]::GetFileName($Fuente)) a objeto..." -ForegroundColor Cyan
& python (Join-Path (Join-Path $aqui '..') 'herramientas\compilar.py') $Fuente $objeto
if ($LASTEXITCODE -ne 0) { throw "compilar.py fallo" }

Write-Host "2. mandando el objeto a la pila (DDE POKE)..." -ForegroundColor Cyan
$r = & $Dde48 's' $objeto
$r | ForEach-Object { Write-Host "   $_" -ForegroundColor DarkGray }
# DDE48 devuelve 0 aunque falle: hay que mirar el texto.
if ($r -join ' ' -notmatch 'OK') { throw "El POKE fallo. Emulador ocupado o sin responder." }

Write-Host "3. tecla EVAL (vk $Vk) a la ventana $($proc.MainWindowHandle)..." -ForegroundColor Cyan
[EmuTecla]::Enviar($proc.MainWindowHandle, $Vk)

# El CAS abre dialogos modales en medio del calculo (visto: "Unsigned inf.
# Solve?" con el limite de 1/X en 0). Sin contestarlos la bateria se queda
# colgada para siempre. Se manda ENTER cada tanto: si hay dialogo, contesta la
# opcion por defecto; si no hay, ENTER sobre un programa ya terminado es un DUP
# del nivel 1, que no cambia lo que vamos a leer.
Write-Host "4. esperando $EsperaMs ms, con ENTER cada $EnterCadaMs ms por si el CAS pregunta..." -ForegroundColor Cyan
$transcurrido = 0
while ($transcurrido -lt $EsperaMs) {
    Start-Sleep -Milliseconds $EnterCadaMs
    $transcurrido += $EnterCadaMs
    [EmuTecla]::Enviar($proc.MainWindowHandle, 13)   # ENTER
}

for ($i = 1; $i -le $Reintentos; $i++) {
    if (Test-Path -LiteralPath $salida) { Remove-Item -LiteralPath $salida -Force }
    $r = & $Dde48 'r' $salida
    if ((Test-Path -LiteralPath $salida) -and ((Get-Item -LiteralPath $salida).Length -gt 0)) {
        $n = (Get-Item -LiteralPath $salida).Length
        Write-Host "5. recibidos $n bytes (intento $i)" -ForegroundColor Green
        break
    }
    Write-Host "   nada todavia (intento $i de $Reintentos), espero 10 s mas..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
}
if (-not (Test-Path -LiteralPath $salida)) { throw "No volvio nada de la pila." }

Write-Host ""
if ($SinComparar) {
    Write-Host "Objeto crudo en: $salida" -ForegroundColor Green
    exit 0
}
& python (Join-Path $aqui 'leer-resultado.py') $salida $Casos
exit $LASTEXITCODE

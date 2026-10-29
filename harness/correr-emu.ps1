# correr-emu.ps1 - ciclo completo del harness contra el Emu48 de Debug4x,
#                  sin tocar el teclado.
#
#   1. DDE48 s   manda el objeto a la pila del emulador
#   2. PostMessage le manda la tecla EVAL a la ventana (no roba el foco:
#      va al handle, no al teclado del sistema)
#   3. espera
#   4. SoloRecibir, tras confirmar reposo: DDE48 r trae el nivel 1
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
    [int]   $Reintentos = 3,      # compatibilidad; no se reintenta DDE en vivo
    [switch]$SoloPreparar,        # compila/carga; EVAL queda a cargo del operador
    [switch]$SoloRecibir,         # no carga ni envia teclas; requiere marca final
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
if (@($proc).Count -ne 1) { throw "Hay varios EMU48: no se puede elegir un servidor DDE de forma segura." }
if (-not (Test-Path -LiteralPath $Dde48)) { throw "No encontre DDE48.exe en: $Dde48" }
if ($SoloPreparar -and $SoloRecibir) { throw 'Elegir SoloPreparar o SoloRecibir' }
. (Join-Path $aqui 'emu-ventana.ps1')
$ventanaBanco = [EmuBanco]::Window($proc.Id)
$meta = [IO.Path]::ChangeExtension($Fuente, '.json')
if (Test-Path -LiteralPath $meta) {
    $manifest = Get-Content -LiteralPath $meta -Raw | ConvertFrom-Json
    if ((Get-FileHash -LiteralPath $Fuente -Algorithm SHA256).Hash.ToLowerInvariant() -ne $manifest.sha256) {
        throw 'El fuente cambio despues de generar los metadatos: reconstruir la bateria.'
    }
} elseif ($SoloRecibir) { throw 'SoloRecibir requiere metadatos con marca final.' }

if (-not $SoloRecibir) {
Write-Host "1. compilando $([IO.Path]::GetFileName($Fuente)) a objeto..." -ForegroundColor Cyan
& python (Join-Path (Join-Path $aqui '..') 'herramientas\compilar.py') $Fuente $objeto
if ($LASTEXITCODE -ne 0) { throw "compilar.py fallo" }

Write-Host "2. mandando el objeto a la pila (DDE POKE)..." -ForegroundColor Cyan
$r = & $Dde48 's' $objeto
$r | ForEach-Object { Write-Host "   $_" -ForegroundColor DarkGray }
# DDE48 devuelve 0 aunque falle: hay que mirar el texto.
if ($r -join ' ' -notmatch 'OK') { throw "El POKE fallo. Emulador ocupado o sin responder." }
if ($SoloPreparar) { Write-Host 'Listo para EVAL; luego usar -SoloRecibir.'; exit 0 }

Write-Host "3. tecla EVAL (vk $Vk) a la ventana $($ventanaBanco)..." -ForegroundColor Cyan
[EmuTecla]::Enviar($ventanaBanco, $Vk)
}

if ($SoloRecibir) {
    # The operator must establish idle state BEFORE this call.
    # ON is not proof of cancellation: an inner IFERR can catch it and keep
    # running. Never REQUEST from a running batch or an unanswered CAS modal.
    # DDE REQUEST while UserRPL is running may corrupt emulator memory.
    # See Emu48.txt, DDE SERVER: applies to BOTH POKE and REQUEST.
    if (Test-Path -LiteralPath $salida) { Remove-Item -LiteralPath $salida -Force }
    $r = & $Dde48 'r' $salida
    if (($r -join ' ') -notmatch 'OK') { throw 'No se recibio resultado' }
    & python (Join-Path $aqui 'leer-resultado.py') $salida --meta $meta --comprobar-fin
    if ($LASTEXITCODE -ne 0) { throw 'Sin marca final. No repetir DDE mientras este ejecutando.' }
    if ($SinComparar) { exit 0 }
    & python (Join-Path $aqui 'leer-resultado.py') $salida --meta $meta
    exit $LASTEXITCODE
}

# El CAS abre dialogos modales en medio del calculo (visto: "Unsigned inf.
# Solve?" con el limite de 1/X en 0). Sin contestarlos la bateria se queda
# colgada para siempre. Se manda ENTER cada tanto: si hay dialogo, contesta la
# opcion por defecto; si no hay, ENTER sobre un programa ya terminado es un DUP
# del nivel 1, que no cambia lo que vamos a leer.
Write-Host "4. esperando $EsperaMs ms, con ENTER cada $EnterCadaMs ms por si el CAS pregunta..." -ForegroundColor Cyan
$transcurrido = 0
while ($transcurrido -lt $EsperaMs) {
    $pausa = if ($EnterCadaMs -gt 0) { [Math]::Min($EnterCadaMs, $EsperaMs - $transcurrido) } else { $EsperaMs - $transcurrido }
    Start-Sleep -Milliseconds $pausa
    $transcurrido += $pausa
    if ($EnterCadaMs -gt 0) { [EmuTecla]::Enviar($ventanaBanco, 13) }
}

# Fixed time is not proof of completion. ON can be caught by IFERR, so it
# cannot make DDE safe here. Leave reception as an explicit second phase.
Write-Host 'Tiempo de espera cumplido. No se consulto la pila por DDE.' -ForegroundColor Yellow
Write-Host 'Confirmar que termino (sin calculo ni dialogo CAS), luego ejecutar:'
Write-Host "  .\correr-emu.ps1 -Fuente '$Fuente' -SoloRecibir"
exit 0

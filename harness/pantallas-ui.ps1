# pantallas-ui.ps1 - maneja una INTERFAZ de la suite en el Emu48 con teclas
#                    y le saca fotos a la pantalla en cada paso.
#
# Las baterias prueban los nucleos XXXC. Esto mira lo que no pueden: el
# formulario INFORM y las cajas MSGBOX de XXX, tipeando lo mismo que un
# alumno y guardando un PNG de la pantalla de la calculadora en cada paso.
#
#   1. armar-ui.py arma un programa que carga los objetos y arranca XXX
#   2. compilar.py + DDE48 s lo ponen en la pila, la tecla EVAL lo corre
#   3. el guion manda teclas (PostMessage a la ventana: no roba el foco)
#   4. FOTO:nombre guarda la LCD en pantallas\nombre.png (PrintWindow,
#      funciona aunque la ventana este tapada; no si esta minimizada)
#
# Guion: tokens separados por espacios.
#   0-9 . SPC ENTER + - * /     las teclas de siempre
#   LS RS ALPHA                  shift izquierdo, derecho, alpha
#   UP DOWN LEFT RIGHT           flechas
#   F1..F6                       teclas de menu (F6 = OK en un INFORM)
#   ON BKSP                      cancelar, borrar
#   ESPERA:ms                    pausa
#   FOTO:nombre                  captura
#   "texto"                      tipea digitos, espacios y . - uno por uno
#
# Mapeo del KML de 50g (R50g1024.kml): las letras de la PC caen en la tecla
# de la calculadora que lleva esa letra en alpha (F = F6, N = EVAL); Tab es
# ALPHA, Shift es el shift izquierdo, Ctrl el derecho, Esc es ON.
#
# Uso:
#   .\pantallas-ui.ps1                         # DTABLA2 con el caso del examen
#   .\pantallas-ui.ps1 -Programa DZLISTA -Objetos DZLISTAC,DSTATSC,DCOMPZC -Guion '...'

[CmdletBinding()]
param(
    [string]  $Programa = 'DTABLA2',
    [string[]]$Objetos  = @('DTABLA2C','DCOVCORRC','DSTATSC'),
    [string]  $Guion    = '',
    [string]  $Prefijo  = '',
    [int]     $ArranqueMs = 8000,
    [string]  $Dde48 = 'C:\Program Files (x86)\Hewlett-Packard\Debug4x\Emu\DDE48.exe'
)

$ErrorActionPreference = 'Stop'
$aqui = Split-Path -Parent $MyInvocation.MyCommand.Definition
if ([string]::IsNullOrEmpty($aqui)) { $aqui = (Get-Location).Path }
if ($Prefijo -eq '') { $Prefijo = $Programa.ToLower() }
$dirFotos = Join-Path $aqui 'pantallas'
New-Item -ItemType Directory -Force $dirFotos | Out-Null

# El caso a) del examen intensivo: X = {1 2 3 4 5}, Y = {1 4 3 5 6}.
# LS + abre { } con el cursor adentro; el ENTER la cierra y pasa al campo
# siguiente. Despues F6 = OK y un ENTER por cada caja.
if ($Guion -eq '') {
    $Guion = 'FOTO:01-formulario LS + "1 2 3 4 5" FOTO:02-tipeando-x ENTER ' +
             'LS + "1 4 3 5 6" ENTER FOTO:03-formulario-lleno F6 ESPERA:4000 ' +
             'FOTO:04-caja-medias ENTER FOTO:05-caja-ss ENTER FOTO:06-caja-sxy ENTER ' +
             'FOTO:07-caja-var ENTER FOTO:08-caja-desvios ENTER FOTO:09-caja-cov-r ENTER ' +
             'FOTO:10-caja-columnas ENTER FOTO:11-caja-ver-tabla ENTER ESPERA:1500 ' +
             'FOTO:12-pila-matriz DOWN ESPERA:2500 FOTO:13-editor-matriz ' +
             'RIGHT RIGHT RIGHT FOTO:14-editor-col4 ON ESPERA:800 FOTO:15-fin'
}

Add-Type -AssemblyName System.Drawing
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System;
using System.Drawing;
using System.Runtime.InteropServices;
public class EmuUI {
    [DllImport("user32.dll")] static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
    [DllImport("user32.dll")] static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint f);
    [DllImport("user32.dll")] static extern bool GetClientRect(IntPtr h, out RECT r);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
    public static void Tecla(IntPtr h, int vk) {
        PostMessage(h, 0x0100, (IntPtr)vk, IntPtr.Zero);
        System.Threading.Thread.Sleep(90);
        PostMessage(h, 0x0101, (IntPtr)vk, IntPtr.Zero);
        System.Threading.Thread.Sleep(220);
    }
    // Captura el area cliente y recorta la LCD: Offset 49 84, Zoom 2,
    // 131x80 pixeles de la 50g -> 262x160. Se amplia x2 para leerla.
    public static void Foto(IntPtr h, string ruta) {
        RECT r; GetClientRect(h, out r);
        using (Bitmap b = new Bitmap(r.R - r.L, r.B - r.T)) {
            using (Graphics g = Graphics.FromImage(b)) {
                IntPtr hdc = g.GetHdc();
                PrintWindow(h, hdc, 1);   // PW_CLIENTONLY
                g.ReleaseHdc(hdc);
            }
            Rectangle lcd = new Rectangle(49, 84, 262, 160);
            using (Bitmap c = b.Clone(lcd, b.PixelFormat))
            using (Bitmap z = new Bitmap(524, 320)) {
                using (Graphics g2 = Graphics.FromImage(z)) {
                    g2.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.NearestNeighbor;
                    g2.PixelOffsetMode = System.Drawing.Drawing2D.PixelOffsetMode.Half;
                    g2.DrawImage(c, 0, 0, 524, 320);
                }
                z.Save(ruta, System.Drawing.Imaging.ImageFormat.Png);
            }
        }
    }
}
'@

$teclas = @{
    '0'=48; '1'=49; '2'=50; '3'=51; '4'=52; '5'=53; '6'=54; '7'=55; '8'=56; '9'=57
    '.'=190; 'SPC'=32; 'ENTER'=13; '+'=107; '-'=109; '*'=106; '/'=111
    'LS'=16; 'RS'=17; 'ALPHA'=9; 'ON'=27; 'BKSP'=8
    'UP'=38; 'DOWN'=40; 'LEFT'=37; 'RIGHT'=39
    'F1'=65; 'F2'=66; 'F3'=67; 'F4'=68; 'F5'=69; 'F6'=70
}

$proc = Get-Process -Name EMU48 -ErrorAction SilentlyContinue
if (-not $proc) { throw "No hay ningun EMU48 abierto." }
$h = $proc.MainWindowHandle

Write-Host "1. armando y compilando $Programa..." -ForegroundColor Cyan
$fuente = Join-Path $aqui ("UI-" + $Programa + ".txt")
$objeto = [IO.Path]::ChangeExtension($fuente, '.hp')
& python (Join-Path $aqui 'armar-ui.py') $fuente $Programa @Objetos
if ($LASTEXITCODE -ne 0) { throw "armar-ui.py fallo" }
& python (Join-Path (Join-Path $aqui '..') 'herramientas\compilar.py') $fuente $objeto
if ($LASTEXITCODE -ne 0) { throw "compilar.py fallo" }

Write-Host "2. a la pila y EVAL..." -ForegroundColor Cyan
$r = & $Dde48 's' $objeto
if ($r -join ' ' -notmatch 'OK') { throw "El POKE fallo." }
[EmuUI]::Tecla($h, 78)   # N = EVAL
Start-Sleep -Milliseconds $ArranqueMs

Write-Host "3. guion..." -ForegroundColor Cyan
$tokens = [regex]::Matches($Guion, '"[^"]*"|\S+') | ForEach-Object { $_.Value }
foreach ($t in $tokens) {
    if ($t.StartsWith('"')) {
        foreach ($ch in $t.Trim('"').ToCharArray()) {
            $k = if ($ch -eq ' ') { 'SPC' } else { [string]$ch }
            if (-not $teclas.ContainsKey($k)) { throw "No se tipear '$ch'" }
            [EmuUI]::Tecla($h, $teclas[$k])
        }
    } elseif ($t -like 'ESPERA:*') {
        Start-Sleep -Milliseconds ([int]$t.Substring(7))
    } elseif ($t -like 'FOTO:*') {
        Start-Sleep -Milliseconds 700
        $ruta = Join-Path $dirFotos ("{0}-{1}.png" -f $Prefijo, $t.Substring(5))
        [EmuUI]::Foto($h, $ruta)
        Write-Host "   foto: $ruta" -ForegroundColor DarkGray
    } elseif ($teclas.ContainsKey($t)) {
        [EmuUI]::Tecla($h, $teclas[$t])
    } else {
        throw "Token desconocido en el guion: $t"
    }
}
Write-Host "Listo. Fotos en $dirFotos" -ForegroundColor Green

# Prueba minima del canal de teclas: escribe 1, ENTER, y lee el nivel 1.
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class T {
    [DllImport("user32.dll")] static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
    public static void K(IntPtr h, int vk) {
        PostMessage(h, 0x0100, (IntPtr)vk, IntPtr.Zero);
        System.Threading.Thread.Sleep(80);
        PostMessage(h, 0x0101, (IntPtr)vk, IntPtr.Zero);
        System.Threading.Thread.Sleep(200);
    }
}
'@
$p = Get-Process -Name EMU48
Write-Host "ventana: $($p.MainWindowHandle)"
[T]::K($p.MainWindowHandle, 49)   # '1' -> tecla 92
[T]::K($p.MainWindowHandle, 13)   # ENTER -> tecla 105
Start-Sleep -Milliseconds 500
$dde = 'C:\Program Files (x86)\Hewlett-Packard\Debug4x\Emu\DDE48.exe'
$out = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Definition) 'tecla.bin'
if (Test-Path -LiteralPath $out) { Remove-Item -LiteralPath $out -Force }
& $dde 'r' $out | Out-Null
if (Test-Path -LiteralPath $out) {
    $b = [IO.File]::ReadAllBytes($out)
    Write-Host ("nivel 1: {0} bytes -> {1}" -f $b.Length, (($b | ForEach-Object { '{0:X2}' -f $_ }) -join ' '))
} else { Write-Host "no volvio nada" }

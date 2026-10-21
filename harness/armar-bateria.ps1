# armar-bateria.ps1 - genera el programa de bateria para el harness.
#
# Lee casos.txt (nombre | expresion | esperado) y emite un unico programa
# UserRPL que corre todos los casos y deja UNA lista de strings en la pila.
# Cada caso va dentro de su propio IFERR, asi que un fallo del CAS no tira
# abajo el resto de la corrida (misma politica que los programas de mat1/).
#
# La salida cumple AGENTS.md 1: header %%HP, CRLF y ASCII puro de 7 bits.
#
# Uso:
#   .\armar-bateria.ps1                          # casos.txt -> BATERIA.txt
#   .\armar-bateria.ps1 -Casos casos-escapes.txt -Nombre BESC

[CmdletBinding()]
param(
    [string]$Casos  = '',
    [string]$Nombre = 'BATERIA',
    [string]$Salida = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# $PSScriptRoot viene vacio al invocar con -File y ruta relativa en PS 5.1.
$aqui = Split-Path -Parent $MyInvocation.MyCommand.Definition
if ([string]::IsNullOrEmpty($aqui)) { $aqui = (Get-Location).Path }

if ($Casos  -eq '') { $Casos  = Join-Path $aqui 'casos.txt' }
if ($Salida -eq '') { $Salida = Join-Path $aqui "$Nombre.txt" }
if (-not (Test-Path -LiteralPath $Casos)) { throw "No existe: $Casos" }

$filas = @()
foreach ($l in [System.IO.File]::ReadAllLines($Casos)) {
    $t = $l.Trim()
    if ($t -eq '' -or $t.StartsWith('#')) { continue }
    $p = @($t -split '\|')
    if ($p.Count -lt 3) { Write-Host "Linea ignorada: $t" -ForegroundColor Yellow; continue }
    $filas += [pscustomobject]@{
        Nombre   = $p[0].Trim()
        Expr     = $p[1].Trim()
        Esperado = ($p[2..($p.Count-1)] -join '|').Trim()
    }
}
if (@($filas).Count -eq 0) { throw "Sin casos en $Casos" }

$lineas = New-Object System.Collections.Generic.List[string]
$lineas.Add('%%HP: T(3)A(R)F(.);')
$lineas.Add("@ $Nombre - generado por harness\armar-bateria.ps1 desde $(Split-Path $Casos -Leaf)")
$lineas.Add("@ $(@($filas).Count) casos. Deja UNA lista de strings en la pila, en el orden")
$lineas.Add('@ del archivo de casos. No editar a mano.')
$lineas.Add('\<<')
# Arranca limpiando: al evaluar, el programa ya salio de la pila, asi que CLEAR
# no se borra a si mismo. Hace falta porque cada ENTER que manda el harness para
# contestar los dialogos del CAS hace un DUP del nivel 1, y sin esto la pila se
# llena de duplicados corrida tras corrida (y DEPTH deja de significar algo).
$lineas.Add('  CLEAR')
# El acumulador va en un GLOBAL, no en la pila. Si un caso falla dejando basura
# apilada (el IFERR NO limpia lo que el cuerpo empujo antes del error: medido en
# el emulador), un acumulador de pila queda sepultado y los resultados
# anteriores se pierden. Con un global eso no puede pasar.
$lineas.Add("  { } 'BRES' STO")
foreach ($f in $filas) {
    $lineas.Add("  @ $($f.Nombre) -> espera: $($f.Esperado)")
    # Cada resultado sale como "NOMBRE|valor". Sin la etiqueta hay que alinear
    # por posicion, y alcanza con que un caso devuelva de mas o de menos para
    # que todo lo que sigue quede corrido (paso en la primera corrida real).
    $lineas.Add("  IFERR $($f.Expr) \->STR THEN ""ERROR"" END ""$($f.Nombre)|"" SWAP + 1 \->LIST BRES SWAP + 'BRES' STO")
}
$lineas.Add('  BRES')
$lineas.Add("  'BRES' PURGE")
$lineas.Add('\>>')

$texto = ($lineas -join "`r`n") + "`r`n"
[System.IO.File]::WriteAllText($Salida, $texto, (New-Object System.Text.ASCIIEncoding))

$bytes   = [System.IO.File]::ReadAllBytes($Salida)
$noAscii = @($bytes | Where-Object { $_ -gt 127 }).Count
Write-Host ("{0}: {1} casos, {2} bytes, {3} bytes no-ASCII" -f (Split-Path $Salida -Leaf), @($filas).Count, $bytes.Length, $noAscii) -ForegroundColor Green
if ($noAscii -gt 0) { Write-Host "  REVISAR: hay bytes no-ASCII" -ForegroundColor Red; exit 1 }
Write-Host "Verificar con:  ..\..\hp50suite\verificar.ps1 $Salida" -ForegroundColor DarkGray

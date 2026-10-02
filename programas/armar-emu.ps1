# armar-emu.ps1 - empaqueta programas\mat1\*.txt en un INSTALADOR de un paso
#                 para cargar en Emu48 (ver SUITE-MAT1.md seccion 9).
#
# Emu48 carga un archivo sin header binario "HPHP4x-" como un STRING en la pila
# (Sources\Emu48\FILES.C, WriteStack). Ese string se convierte al objeto real
# con ASCIIBIN, que necesita justamente el header %%HP: T(3)A(R)F(.); completo.
#
# ASCIIBIN falla a veces con directorios, asi que este empaquetado NO usa DIR:
# genera un unico PROGRAMA que, al evaluarse, crea los 17 globales. Cada cuerpo
# va como literal \<< ... \>> seguido de 'NOMBRE' STO. Ese \<< huerfano es
# deliberado: CLAUDE.md 2.2 dice que un \<< sin \-> adelante se empuja a la pila
# como dato inerte, que es exactamente lo que hace falta antes del STO.
#
# Resultado: un Load Object + un ASCIIBIN + un EVAL, en vez de 17 ciclos.
#
# MAT1-EMU.txt es salida generada. No editarlo a mano.
# verificar.ps1 va a marcarle huerfanos (son los 17 literales): verificar la
# fuente en mat1\, no este archivo.
#
# Uso:  .\armar-emu.ps1

$origen = Join-Path $PSScriptRoot 'mat1'
$salida = Join-Path $PSScriptRoot 'MAT1-EMU.txt'

# Los datos de prueba primero, para que existan antes que TD y TF.
$orden = @('TDSEP','TEFUN','TCHK','TD','TF',
           'DVFGC','DVFG','DDOMPC','DDOMP','DCONTC','DCONT','DCONTFC','DCONTF',
           'DDEFC','DDEF','DTANORC','DTANOR','DASVC','DASV',
           'DASHOC','DASHO','DOPFUNC','DOPFUN','DESTFUNC','DESTFUN',
           'LHOPC','LHOP','DSEPC','DSEP','DSEPIC','DSEPI',
           'LAGRC','LAGR',
           'DRUFC','DRUF','DWEIERC','DWEIER',
           'DBOLZC','DBOLZ','DWSUSC','DWSUS',
           'DCONDC','DSATC','DINTC','DRELC','DDOMC','DDOM','DINECC','DINEC',
           'DINVC','DINV','DCONTKC','DCONTK','DPARC','DPAR',
           'DASVTC','DASVT','DCEROC','DCERO')

$lineas = New-Object System.Collections.Generic.List[string]
$lineas.Add('%%HP: T(3)A(R)F(.);')
$lineas.Add('\<<')

foreach ($nombre in $orden) {
    $ruta = Join-Path $origen "$nombre.txt"
    if (-not (Test-Path $ruta)) {
        Write-Host "FALTA: $nombre.txt" -ForegroundColor Red
        exit 1
    }
    # Se descarta la primera linea (el header %%HP de cada archivo suelto).
    $cuerpo = [System.IO.File]::ReadAllText($ruta) -split "`r?`n" | Select-Object -Skip 1
    foreach ($l in $cuerpo) {
        if ($l.Trim().Length -gt 0) { $lineas.Add("  $l") }
    }
    $lineas.Add("  '$nombre' STO")
}

$lineas.Add('\>>')

$texto = ($lineas -join "`r`n") + "`r`n"
[System.IO.File]::WriteAllText($salida, $texto, (New-Object System.Text.ASCIIEncoding))

$bytes   = [System.IO.File]::ReadAllBytes($salida)
$noAscii = ($bytes | Where-Object { $_ -gt 127 }).Count
$ab  = ([regex]::Matches($texto, [regex]::Escape('\<<'))).Count
$ce  = ([regex]::Matches($texto, [regex]::Escape('\>>'))).Count
# Solo los STO de instalacion, que van con indentacion 2 y en su propia linea.
# Los 'DIF' STO / 'LI' STO de adentro de los programas van mas indentados.
$sto = ($lineas | Where-Object { $_ -match "^  '[A-Z0-9]+' STO$" }).Count

Write-Host "MAT1-EMU.txt: $sto STO, $ab/$ce bloques, $noAscii bytes no-ASCII, $($bytes.Length) bytes" -ForegroundColor Green
if ($ab -ne $ce -or $noAscii -gt 0 -or $sto -ne $orden.Count) {
    Write-Host "  REVISAR" -ForegroundColor Red; exit 1
}
Write-Host "Pasos en Emu48: Edit > Load Object (ASCIIBIN.49), 'ASCIIBIN' STO," -ForegroundColor DarkGray
Write-Host "                Edit > Load Object (MAT1-EMU.txt), ASCIIBIN, EVAL." -ForegroundColor DarkGray

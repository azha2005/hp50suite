# armar-mat1.ps1 - empaqueta programas\mat1\*.txt en un unico MAT1.txt
#
# Por que: TD y TF referencian TDSEP y TEFUN por nombre global, y entre
# carpetas hermanas NO hay visibilidad (CLAUDE.md seccion 5). Si cada .txt
# viajara con su propio DIR, cada uno caeria como subcarpeta hermana y los
# helpers quedarian invisibles. Un unico DIR resuelve eso: una transferencia,
# una subcarpeta, todos los nombres visibles entre si.
#
# Los archivos sueltos de mat1\ siguen siendo la fuente de verdad para editar
# y para verificar.ps1. MAT1.txt es salida generada: no editarlo a mano.
#
# Uso:  .\armar-mat1.ps1
# Si PowerShell bloquea: powershell -ExecutionPolicy Bypass -File .\armar-mat1.ps1

$origen  = Join-Path $PSScriptRoot 'mat1'
$salida  = Join-Path $PSScriptRoot 'MAT1.txt'

# Orden de carga: los datos de prueba antes que los programas que los leen.
$orden = @('TDSEP','TEFUN','TCHK','TD','TF',
           'DVFG','DDOMP','DCONT','DDEF','DTANOR','DASV','DASHO',
           'DOPFUN','DESTFUN',
           'LHOP','DSEP','DSEPI','LAGR')

$lineas = New-Object System.Collections.Generic.List[string]
$lineas.Add('%%HP: T(3)A(R)F(.);')
$lineas.Add('DIR')

foreach ($nombre in $orden) {
    $ruta = Join-Path $origen "$nombre.txt"
    if (-not (Test-Path $ruta)) {
        Write-Host "FALTA: $nombre.txt" -ForegroundColor Red
        exit 1
    }
    # Se descarta la primera linea (el header %%HP de cada archivo suelto).
    $cuerpo = [System.IO.File]::ReadAllText($ruta) -split "`r?`n" | Select-Object -Skip 1
    $lineas.Add("  $nombre")
    foreach ($l in $cuerpo) {
        if ($l.Trim().Length -gt 0) { $lineas.Add("  $l") }
    }
}
$lineas.Add('END')

# CRLF explicito, ASCII puro, sin BOM.
$texto = ($lineas -join "`r`n") + "`r`n"
[System.IO.File]::WriteAllText($salida, $texto, (New-Object System.Text.ASCIIEncoding))

$bytes   = [System.IO.File]::ReadAllBytes($salida)
$noAscii = ($bytes | Where-Object { $_ -gt 127 }).Count
$ab = ([regex]::Matches($texto, [regex]::Escape('\<<'))).Count
$ce = ([regex]::Matches($texto, [regex]::Escape('\>>'))).Count

Write-Host "MAT1.txt: $($orden.Count) objetos, $ab/$ce bloques, $noAscii bytes no-ASCII" -ForegroundColor Green
if ($ab -ne $ce -or $noAscii -gt 0) { Write-Host "  REVISAR" -ForegroundColor Red; exit 1 }
Write-Host "Verificar los archivos sueltos de mat1\, que son la fuente:" -ForegroundColor DarkGray
Write-Host "  ..\verificar.ps1 .\mat1\*.txt" -ForegroundColor DarkGray

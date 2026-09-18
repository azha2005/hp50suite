# a-crlf.ps1 — Convierte un .txt a formato transferible por Conn4x
# (terminaciones CRLF + verifica ASCII puro + verifica header)
#
# Uso:
#   .\a-crlf.ps1 entrada.txt salida.txt
#   .\a-crlf.ps1 entrada.txt            (sobreescribe el mismo archivo)

param(
    [Parameter(Mandatory=$true)][string]$Entrada,
    [string]$Salida
)

if (-not (Test-Path $Entrada)) {
    Write-Host "No existe: $Entrada" -ForegroundColor Red
    exit 1
}

if (-not $Salida) { $Salida = $Entrada }

# Leer, normalizar a LF primero, despues pasar todo a CRLF
$contenido = [System.IO.File]::ReadAllText($Entrada)
$contenido = $contenido -replace "`r`n", "`n"
$contenido = $contenido -replace "`n", "`r`n"

# Escribir SIN BOM y en ASCII — un BOM al inicio rompe la transferencia
$sinBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($Salida, $contenido, $sinBom)

# Verificaciones post-escritura
$bytes = [System.IO.File]::ReadAllBytes($Salida)
$noAscii = ($bytes | Where-Object { $_ -gt 127 }).Count
$primeraLinea = ($contenido -split "`r`n")[0]

Write-Host "Escrito: $Salida"

if ($primeraLinea -match '^%%HP:') {
    Write-Host "  Header %%HP: OK" -ForegroundColor Green
} else {
    Write-Host "  FALTA el header %%HP en la primera linea" -ForegroundColor Red
}

if ($noAscii -eq 0) {
    Write-Host "  ASCII puro: OK" -ForegroundColor Green
} else {
    Write-Host "  TIENE $noAscii bytes no-ASCII (va a fallar la transferencia)" -ForegroundColor Red
}

Write-Host "  CRLF: OK" -ForegroundColor Green

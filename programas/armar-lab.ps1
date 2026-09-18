# armar-lab.ps1 - empaqueta los programas de Laboratorio de Datos y
#                 Microeconomia I en un unico LAB.txt, igual que
#                 armar-mat1.ps1 hace con Matematica I.
#
# Por que un solo DIR: dentro de un mismo directorio todos los nombres se
# ven entre si, asi que DOLS y DCOVCORR encuentran a SIGFIG, y cada
# interfaz encuentra a su nucleo. Con una transferencia por programa,
# cada uno caeria en su propia subcarpeta y entre carpetas hermanas NO hay
# visibilidad (CLAUDE.md seccion 5): por eso antes SIGFIG TENIA que estar
# en HOME. Empaquetado, esa restriccion desaparece.
#
# Si SIGFIG falta, DOLS no da error: deja el nombre 'SIGFIG' SIN EVALUAR en
# la pila y muestra un resultado equivocado. Medido en el emulador.
#
# Tres capas por programa:
#   XXXC  el calculo, entra y sale por pila
#   XXXG  el dibujo, dibuja en PICT y no abre PICTURE
#   XXX   la interfaz: INFORM, PICTURE y las cajas
# Estan separados para que el harness pueda probarlos: INFORM es interactivo
# por definicion (una bateria no puede tipear en un formulario) y PICTURE
# espera una tecla. Con el dibujo aparte, la bateria dibuja en PICT y mide
# con PIX? en coordenadas reales.
#
# Los archivos sueltos de programas\ y programas\datos\ siguen siendo la
# fuente de verdad para editar y para verificar.ps1. LAB.txt es salida
# generada: no editarlo a mano.
#
# Uso:  .\armar-lab.ps1
# Si PowerShell bloquea: powershell -ExecutionPolicy Bypass -File .\armar-lab.ps1

$origen = $PSScriptRoot
$datos  = Join-Path $PSScriptRoot 'datos'
$salida = Join-Path $PSScriptRoot 'LAB.txt'

# Orden de carga: primero los datasets, despues la utilidad compartida,
# despues cada nucleo con su interfaz.
$orden = @(
    # Datasets de catedra (se pueden escribir por nombre en el campo "Datos")
    'BM5X','BM5Y','BMHIST','BMSCX','BMSCY','HORAS',
    # Utilidad compartida
    'SIGFIG',
    # Estadistica descriptiva
    'DSTATSC','DSTATS','DMODAC','DMODA','DPCTILC','DPCTIL',
    'DFRECTABLAC','DFRECTABLA','DHISTOG','DHISTO',
    'DBOXPLOTC','DBOXPLOTG','DBOXPLOT',
    # Dos variables
    'DCOVCORRC','DCOVCORRG','DCOVCORR','DOLSC','DOLS',
    # Economia
    'DMKTC','DMKTG','DMKT','DMKTFISCC','DMKTFISCG','DMKTFISC',
    'DCOMPFIRMC','DCOMPFIRMG','DCOMPFIRM',
    'DPIBPPAC','DPIBPPA','DTCAMBIOC','DTCAMBIO','DCOMPZC','DCOMPZ',
    # Matematica
    'DTROZOS',
    # Infinito del CAS (lo usa la suite de Matematica I)
    'DINF'
)

$lineas = New-Object System.Collections.Generic.List[string]
$lineas.Add('%%HP: T(3)A(R)F(.);')
$lineas.Add('DIR')

foreach ($nombre in $orden) {
    $ruta = Join-Path $origen "$nombre.txt"
    if (-not (Test-Path $ruta)) { $ruta = Join-Path $datos "$nombre.txt" }
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

$texto = ($lineas -join "`r`n") + "`r`n"
[System.IO.File]::WriteAllText($salida, $texto, (New-Object System.Text.ASCIIEncoding))

$bytes   = [System.IO.File]::ReadAllBytes($salida)
$noAscii = @($bytes | Where-Object { $_ -gt 127 }).Count
$ctrl    = @($bytes | Where-Object { $_ -lt 32 -and $_ -ne 9 -and $_ -ne 10 -and $_ -ne 13 }).Count
$ab = ([regex]::Matches($texto, [regex]::Escape('\<<'))).Count
$ce = ([regex]::Matches($texto, [regex]::Escape('\>>'))).Count
Write-Host ("LAB.txt: {0} objetos, {1}/{2} bloques, {3} bytes no-ASCII, {4} bytes de control, {5} bytes" -f $orden.Count, $ab, $ce, $noAscii, $ctrl, $bytes.Length) -ForegroundColor Green
if ($noAscii -gt 0 -or $ctrl -gt 0 -or $ab -ne $ce) { Write-Host "  REVISAR" -ForegroundColor Red; exit 1 }
Write-Host "Verificar los archivos sueltos, que son la fuente:" -ForegroundColor DarkGray
Write-Host "  ..\verificar.ps1 .\*.txt" -ForegroundColor DarkGray

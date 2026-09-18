# verificar.ps1 — Bateria de verificacion para programas UserRPL (HP 50g)
#
# Uso:
#   .\verificar.ps1 archivo.txt        (un archivo)
#   .\verificar.ps1 programas\*.txt    (varios)
#
# Si PowerShell bloquea el script:
#   powershell -ExecutionPolicy Bypass -File .\verificar.ps1 archivo.txt

param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Archivos)

if (-not $Archivos) {
    Write-Host "Uso: .\verificar.ps1 <archivo.txt> [mas archivos...]"
    exit 1
}

function Test-ArchivoRPL {
    param([string]$Ruta)

    if (-not (Test-Path $Ruta)) {
        Write-Host "NO EXISTE: $Ruta" -ForegroundColor Red
        return
    }

    $nombre    = Split-Path $Ruta -Leaf
    $bytes     = [System.IO.File]::ReadAllBytes($Ruta)
    $contenido = [System.IO.File]::ReadAllText($Ruta)
    $lineas    = $contenido -split "`r?`n"

    $problemas = @()

    # 1. Profundidad de anidacion acumulada (debe terminar en 0)
    $depth = 0; $maxd = 0
    foreach ($l in $lineas) {
        $ab = ([regex]::Matches($l, [regex]::Escape('\<<'))).Count
        $ce = ([regex]::Matches($l, [regex]::Escape('\>>'))).Count
        $depth += $ab - $ce
        if ($depth -gt $maxd) { $maxd = $depth }
    }
    if ($depth -ne 0) { $problemas += "Anidacion NO cierra (queda en $depth)" }

    # 2. Bloques \<< huerfanos (sin \-> en la linea anterior).
    #    El unico esperado es el que abre el programa.
    #    Excepcion: dentro de un DIR la linea previa es el NOMBRE del objeto
    #    (un identificador solo). Es legitimo y hay uno por programa, asi que
    #    un archivo con varios objetos no dispara falsos positivos.
    #    Excepcion 2: la declaracion puede estar en la MISMA linea, como
    #    `DUP \-> K \<< ... \>>`. Es legitimo y la suite no lo usa, pero el
    #    codigo de terceros si (analisis\calcnum en el fork): sin esto la
    #    bateria marcaba 8 archivos ajenos que estaban bien.
    #    Excepcion 3: la linea previa termina en STO. Es el formato de los
    #    INSTALADORES generados (`\<< ... \>> 'NOMBRE' STO` uno tras otro,
    #    ver armar-emu.ps1): despues del STO la pila quedo limpia y lo que
    #    empieza es el objeto siguiente, no un bloque suelto. Sin esto,
    #    MAT1-EMU.txt marcaba 26 falsos positivos en CADA corrida de la
    #    bateria, y una compuerta que siempre se queja ensenia a ignorarla.
    #    OJO con la excepcion del NOMBRE: aceptar cualquier identificador
    #    solo tambien acepta un comando suelto. `DROP` parece un nombre de
    #    objeto, asi que un `\<<` huerfano justo despues de un DROP pasaba
    #    sin ser visto. Se detecto con un archivo roto a proposito. Ahora la
    #    excepcion vale SOLO en archivos que tienen un DIR, que son los
    #    paquetes generados (MAT1.txt, LAB.txt): ahi la linea previa a un
    #    bloque si es el nombre del objeto. Los archivos de un solo programa
    #    -- que son los que se editan a mano -- quedan con el chequeo
    #    estricto, que es donde hace falta.
    $tieneDir = @($lineas | Where-Object { $_.Trim() -eq 'DIR' }).Count -gt 0
    $huerfanos = @()
    for ($i = 1; $i -lt $lineas.Count; $i++) {
        if ($lineas[$i] -notlike '*\<<*') { continue }
        $posBloque = $lineas[$i].IndexOf('\<<')
        $posFlecha = $lineas[$i].IndexOf('\->')
        if ($posFlecha -ge 0 -and $posFlecha -lt $posBloque) { continue }
        $prev = $lineas[$i-1].Trim()
        if ($prev -like '*\->*')                  { continue }
        if ($tieneDir -and $prev -match '^[A-Za-z][A-Za-z0-9]*$') { continue }
        if ($prev -eq 'DIR')                       { continue }
        if ($prev -match "STO$")                   { continue }
        $huerfanos += ($i + 1)
    }
    if ($huerfanos.Count -gt 1) {
        $problemas += "Posibles bloques huerfanos en lineas: $($huerfanos -join ', ')"
    }

    # 3. Bytes no-ASCII (rompen la transferencia por Conn4x)
    $noAscii = ($bytes | Where-Object { $_ -gt 127 }).Count
    if ($noAscii -gt 0) { $problemas += "Tiene $noAscii bytes no-ASCII" }

    # 3b. Bytes de CONTROL. Son ASCII de 7 bits, asi que el chequeo de arriba
    # NO los ve, y viajan invisibles hasta la calculadora. Aparecen cuando un
    # script de Python escribe el archivo y un literal lleva barra invertida
    # seguida de letra: "\v/" en un literal de Python no es la raiz
    # cuadrada, es TABULADOR VERTICAL mas "/". Paso tres veces en este
    # proyecto, y una de ellas invalido en silencio una tanda entera de
    # pruebas con raices: la raiz nunca llego a la calculadora, llegaban los
    # tres caracteres literales y compilaban como un nombre basura.
    $ctrl = ($bytes | Where-Object { $_ -lt 32 -and $_ -ne 9 -and $_ -ne 10 -and $_ -ne 13 }).Count
    if ($ctrl -gt 0) { $problemas += "Tiene $ctrl bytes de control (revisar literales con barra invertida)" }

    # 4. Comandos que no existen en UserRPL (ignorando comentarios @)
    $codigo = ($lineas | Where-Object { $_ -notmatch '^\s*@' }) -join "`n"

    #    Las palabras adentro de un string literal NO son codigo. Sin esto, un
    #    prompt como "Press the <NEXT> soft-key" desbalancea el conteo de
    #    bucles, y un texto que diga ROUND dispara un falso positivo.
    $codigoSinStr = [regex]::Replace($codigo, '"[^"]*"', '""')

    foreach ($cmd in @('SQRT', 'ROUND', '=/=')) {
        if ($codigoSinStr -match [regex]::Escape($cmd)) {
            $problemas += "Usa comando invalido: $cmd"
        }
    }
    #    >= y <= sueltos no existen; las formas con escape \>= y \<= si son
    #    validas (aparecen en codigo de terceros que funciona, ver CLAUDE.md
    #    2.1). El lookbehind deja pasar solo las escapadas.
    foreach ($cmp in @('>=', '<=')) {
        if ($codigoSinStr -match ('(?<!\\)' + [regex]::Escape($cmp))) {
            $problemas += "Usa comparador invalido: $cmp (la forma con escape es \$cmp)"
        }
    }

    # 5. Comillas dobles balanceadas
    $comillas = ([regex]::Matches($contenido, '"')).Count
    if ($comillas % 2 -ne 0) { $problemas += "Comillas dobles impares ($comillas)" }

    # 6. Header %%HP y terminaciones CRLF
    if ($lineas[0] -notmatch '^%%HP:') { $problemas += "Falta el header %%HP en la primera linea" }
    if ($contenido -notmatch "`r`n")   { $problemas += "No tiene terminaciones CRLF" }

    # 7. Conteos informativos
    $ab  = ([regex]::Matches($contenido, [regex]::Escape('\<<'))).Count
    $ce  = ([regex]::Matches($contenido, [regex]::Escape('\>>'))).Count
    #    Un bucle cierra con NEXT o con STEP. Se cuenta FOR pero NO START,
    #    aunque START..NEXT tambien sea un bucle valido: DHISTO y DFRECTABLA
    #    usan START como nombre de variable local, y contarlo daba dos falsos
    #    positivos. Limitacion asumida: un bucle START..NEXT en codigo propio
    #    desbalancea este conteo. La suite usa solo FOR.
    $for = ([regex]::Matches($codigoSinStr, '\bFOR\b')).Count
    $nxt = ([regex]::Matches($codigoSinStr, '\bNEXT\b')).Count + ([regex]::Matches($codigoSinStr, '\bSTEP\b')).Count
    if ($for -ne $nxt) {
        $problemas += "FOR ($for) y NEXT/STEP ($nxt) no coinciden (START..NEXT no se cuenta, ver comentario)"
    }

    # 8. Balance de END. Cada THEN (de IF o de IFERR, y cada rama de un CASE)
    #    cierra con un END; el CASE mismo agrega uno mas; DO..UNTIL..END,
    #    WHILE..REPEAT..END y el envoltorio DIR..END aportan uno cada uno.
    #    END = THEN + CASE + DO + WHILE + DIR
    #    Esto es lo que detecta un IFERR sin cerrar: el conteo de \<< no lo ve,
    #    porque IFERR no abre un programa.
    $nThen  = ([regex]::Matches($codigoSinStr, '\bTHEN\b')).Count
    $nIfErr = ([regex]::Matches($codigoSinStr, '\bIFERR\b')).Count
    $nCase  = ([regex]::Matches($codigoSinStr, '\bCASE\b')).Count
    $nDo    = ([regex]::Matches($codigoSinStr, '\bDO\b')).Count
    $nWhile = ([regex]::Matches($codigoSinStr, '\bWHILE\b')).Count
    $nDir   = ($lineas | Where-Object { $_.Trim() -eq 'DIR' }).Count
    $nEnd   = ([regex]::Matches($codigoSinStr, '\bEND\b')).Count
    $abren  = $nThen + $nCase + $nDo + $nWhile + $nDir
    if ($nEnd -ne $abren) {
        $problemas += "END ($nEnd) no cierra los bloques abiertos (esperados $abren = $nThen THEN + $nCase CASE + $nDo DO + $nWhile WHILE + $nDir DIR)"
    }

    if ($problemas.Count -eq 0) {
        Write-Host ("{0,-20} OK   (depth max {1}, {2}/{3} bloques, {4} FOR, {5} IFERR)" -f $nombre, $maxd, $ab, $ce, $for, $nIfErr) -ForegroundColor Green
    } else {
        Write-Host ("{0,-20} PROBLEMAS:" -f $nombre) -ForegroundColor Red
        foreach ($p in $problemas) { Write-Host "    - $p" -ForegroundColor Yellow }
    }
}

foreach ($patron in $Archivos) {
    $encontrados = Get-ChildItem -Path $patron -ErrorAction SilentlyContinue
    if ($encontrados) {
        foreach ($f in $encontrados) { Test-ArchivoRPL $f.FullName }
    } else {
        Test-ArchivoRPL $patron
    }
}

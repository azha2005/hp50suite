# Development package: self-contained DIR for the new guided programs.
# Keep separate from MAT1 until LCD/Conn4x/hardware acceptance is complete.
$ErrorActionPreference = 'Stop'
$ordenP2 = @('DFREEC','DREADC','DPOWC','DREALC','DVALC','DROOTC','DCUTSC','DORDC',
    'DCONDC','DSATC','DINTC','DRELC','DDOMC','DINFOC','DCLOSEC','DABRC',
    'DINSUMC','DINPRC','DINTEGC','DINPVIC','DPAGC','DPANTC','DPASOS','DINTEG','DIMPLC','DIMPL',
    'DINTDEFC','DINTDEF','DAREAC','DAREAG','DAREA','DBRKC','DANAC',
    'DLATC','DCONTFC','DASHOC','DASVC','DANAG','DESTFUNC','DESTFUN','DWEIERC','DWEIER')
$lineasP2 = [Collections.Generic.List[string]]::new()
$lineasP2.Add('%%HP: T(3)A(R)F(.);')
$lineasP2.Add('DIR')
foreach ($nombreP2 in $ordenP2) {
    $rutaP2 = Join-Path $PSScriptRoot "mat1/$nombreP2.txt"
    $bytesP2 = [IO.File]::ReadAllBytes($rutaP2)
    if (@($bytesP2 | Where-Object { $_ -gt 127 -or ($_ -lt 32 -and $_ -notin @(9,10,13)) }).Count) {
        throw "ASCII/control invalido: $rutaP2"
    }
    $textoP2 = [Text.Encoding]::ASCII.GetString($bytesP2)
    if (-not $textoP2.StartsWith("%%HP: T(3)A(R)F(.);`r`n")) { throw "Header/CRLF invalido: $rutaP2" }
    $lineasP2.Add($nombreP2)
    foreach ($lineaP2 in (($textoP2 -split "`r`n") | Select-Object -Skip 1)) {
        $compactaP2 = $lineaP2.Trim()
        if ($compactaP2 -and -not $compactaP2.StartsWith('@')) { $lineasP2.Add($compactaP2) }
    }
}
$lineasP2.Add('END')
$salidaP2 = Join-Path $PSScriptRoot 'MAT1-P2.txt'
[IO.File]::WriteAllText($salidaP2, ($lineasP2 -join "`r`n") + "`r`n", [Text.Encoding]::ASCII)
Write-Host "MAT1-P2.txt: $($ordenP2.Count) objetos, $((Get-Item $salidaP2).Length) bytes. Desarrollo: falta validar LCD/Conn4x/HP real."

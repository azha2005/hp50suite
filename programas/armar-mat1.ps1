# armar-mat1.ps1 - empaqueta programas\mat1\*.txt en un unico MAT1.txt
#
# Por que: TD y TF referencian TDSEP y TEFUN por nombre global, y entre
# carpetas hermanas NO hay visibilidad (AGENTS.md seccion 5). Si cada .txt
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
# Los objetos XXXC son los NUCLEOS de calculo; XXX es la interfaz que los
# llama. Estan separados para que el harness pueda probar el calculo: INFORM
# es interactivo por definicion y una bateria no puede tipear en un formulario.
# Cada nucleo va antes de su interfaz, aunque dentro de un DIR el orden no
# afecta la visibilidad de los nombres.
$orden = @('TDSEP','TEFUN','TCHK','TD','TF',
           'DVFGC','DVFG','DDOMPC','DDOMP','DLATC','DCONTC','DCONT','DCONTFC','DCONTF',
           'DDEFC','DDEF','DTANORC','DTANOR','DASVC','DASV',
           'DASHOC','DASHO','DOPFUNC','DOPFUN','DESTFUNC','DESTFUN',
           'LHOPC','LHOP','DSEPC','DSEP','DSEPIC','DSEPI',
           'LAGRC','LAGR',
           'DRUFC','DRUF','DWEIERC','DWEIER',
           'DBOLZC','DBOLZ','DWSUSC','DWSUS',
           'DCONDC','DSATC','DINTC','DRELC','DDOMC','DDOM','DINECC','DINEC',
           'DINVC','DINV','DCONTKC','DCONTK','DPARC','DPAR',
           'DASVTC','DASVT','DCEROC','DCERO',
           'DFREEC','DREADC','DPOWC','DREALC','DVALC','DROOTC','DCUTSC','DORDC','DINFOC','DCLOSEC','DABRC',
           'DINSUMC','DINPRC','DINTEGC','DINPVIC','DPAGC','DPANTC','DPASOS','DBRKC','DANAC','DANAG')

# Resolve every current transitive dependency, including the guided kernels.
& python (Join-Path (Split-Path $PSScriptRoot -Parent) 'herramientas/empaquetar-mat1.py') --base
if ($LASTEXITCODE -ne 0) { throw 'MAT1 packaging failed' }

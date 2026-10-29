# Independent guided topic packages; sources remain in mat1/.
# Each directory includes its own transitive helpers. No sibling visibility.
$ErrorActionPreference = 'Stop'
& python (Join-Path (Split-Path $PSScriptRoot -Parent) 'herramientas/empaquetar-mat1.py')
if ($LASTEXITCODE -ne 0) { throw 'Guided topic packaging failed' }

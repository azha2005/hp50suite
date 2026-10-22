# Contribuir / Contributing

## Probar un programa

No hace falta programar para ayudar. Descargar una [release](https://github.com/azha2005/hp50suite/releases),
seguir la [guía de inicio](INICIO-RAPIDO.md) y contar cómo salió en el
[formulario de prueba](https://github.com/azha2005/hp50suite/issues/new?template=prueba.yml).

Incluir la versión, el modelo, si fue hardware real o emulador, los datos de
entrada y el resultado esperado y obtenido. Si hubo un error, copiar su texto
y los pasos para repetirlo. También sirven las pruebas exitosas.

## Proponer un cambio

- Leer [AGENTS.md](AGENTS.md) antes de editar UserRPL.
- Editar los fuentes individuales de `programas/` o `programas/mat1/`.
  `LAB.txt` y `MAT1.txt` se generan; no se editan a mano.
- Conservar ASCII de 7 bits, CRLF y la cabecera HP en los fuentes de transferencia.
- Ejecutar `./herramientas/preparar-release.ps1` desde la raíz del repositorio.
  Verifica el formato y regenera los paquetes; no ejecuta pruebas en la ROM.
- Para cambios de cálculo, agregar un caso reproducible al harness y seguir
  [sus instrucciones](harness/README.md). Indicar qué se probó y en qué entorno.
  Una prueba en emulador se documenta como tal.

Abrir un pull request explicando el problema, el cambio y cómo se verificó.
No incluir ROMs, emuladores, estados de la calculadora ni material de terceros.

## English

Testing is welcome even if you do not write UserRPL. Download a release, follow
the first-run guide and submit a user-test issue in English or Spanish. Include
the version, model, hardware/emulator environment, inputs, expected and actual
output, and steps to reproduce any error. Successful tests are useful too.

For code contributions, read AGENTS.md, edit individual sources, preserve the
HP transfer format and run `./herramientas/preparar-release.ps1`. Calculation
changes should include a reproducible harness case. State exactly what was
tested; static checks, emulator tests and real hardware tests provide different
evidence. Please keep pull requests focused and exclude proprietary ROMs and
third-party material.

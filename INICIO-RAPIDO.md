# Primera prueba / First run — HP 50g

[Descargar ZIP / Download ZIP](https://github.com/azha2005/hp50suite/releases/latest/download/hp50suite.zip)
· [Versiones / Releases](https://github.com/azha2005/hp50suite/releases)

## Español

1. Descomprimir `hp50suite.zip`. Para empezar con estadística alcanza `LAB.txt`.
   `MAT1.txt` es el paquete de cálculo. No hace falta transferir ambos.
2. Conectar la HP 50g con Conn4x y elegir el directorio de destino. Hacer
   **download** del archivo desde la PC hacia la calculadora. No abrir ni
   volver a guardar los TXT con un editor: necesitan ASCII, CRLF y su cabecera.
3. En `VAR`, confirmar que llegó como **directorio**, no como string. Entrar
   en `LAB` y ejecutar `DSTATS` (no `DSTATSC`, que es el núcleo sin formulario).
4. En Datos escribir `{ 2 4 6 8 10 }`. Confirmar el formulario. Con OK se pasa
   por las tres cajas: N = 5, media = 6; varianza muestral = 10, desvío ≈
   3.16227766; CV ≈ 52.70462767 %. El formato puede cambiar con los modos.
5. Contar cómo salió en [Prueba de usuario](https://github.com/azha2005/hp50suite/issues/new?template=prueba.yml).
   Sirven tanto las pruebas que funcionan como los errores reproducibles.

`LAB.txt` ya contiene SIGFIG y los datasets: no necesitan transferirse aparte.
Para instalar programas individuales, ver el README de `programas/` en el
repositorio; sus dependencias y el orden de carga son diferentes.

**Matemática I:** para las asíntotas de `DASHO`/`DESTFUN`, transferir `DINF.txt`
como programa a HOME, introducir el infinito del teclado en la pila y ejecutar
DINF una vez. Esto crea `INF` visible desde las subcarpetas. Sigue siendo el
procedimiento soportado hasta comprobar los escapes de Conn4x en hardware.
Los ejemplos de cada programa están en los dos diccionarios incluidos.

**Estado:** los núcleos tienen baterías en Emu48 con ROM de HP 50g. Eso no
valida automáticamente los formularios, la transferencia ni el hardware real.
Probar en la propia calculadora cada programa que se vaya a usar. El detalle
histórico de hardware está en `programas/README.md` del repositorio.

Si llega como string, revisar el modo de transferencia de Conn4x y conservar
el archivo original. Si aparece `Insufficient Memory`, revisar la RAM libre:
la carga necesita espacio para el texto y el objeto compilado. Los paquetes
están compactados, pero eso no garantiza que entren en cualquier estado de RAM.

## English

Unzip `hp50suite.zip`. Transfer `LAB.txt` (statistics/economics) and/or
`MAT1.txt` (calculus) to the HP 50g using Conn4x; **download** means PC to
calculator. Preserve the original TXT bytes. In VAR, check that the result is
a directory, then enter LAB and run **DSTATS**, not its DSTATSC core.

Enter `{ 2 4 6 8 10 }` in Datos. Press OK through the three result boxes:
N = 5, mean = 6, sample variance = 10, standard deviation ≈ 3.16227766,
CV ≈ 52.70462767 %. LAB already includes its helper and course datasets.

For DASHO/DESTFUN asymptotes, transfer DINF.txt to HOME, place the infinity
symbol from the calculator keyboard on the stack and run DINF once to create
INF. See the Spanish dictionaries for individual program examples.

Emulator results do not establish real hardware or form validation. Please
[report your test](https://github.com/azha2005/hp50suite/issues/new?template=prueba.yml),
including the model, environment, input, expected and actual output. Reports
may be written in English or Spanish.

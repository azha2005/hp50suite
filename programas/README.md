# Programas — últimas versiones funcionales

Archivos listos para transferir con Conn4x. Ya están con header `%%HP:`, CRLF y
ASCII puro verificados.

**CLAUDE.md manda.** Este README dice qué cargar y en qué orden; las reglas de
UserRPL, el formato de archivo y los casos de prueba están en `../CLAUDE.md` y no
se repiten acá. Ante cualquier diferencia, vale CLAUDE.md. Lo específico de
Matemática I está en `../SUITE-MAT1.md`, que también se subordina a CLAUDE.md.

## Orden de carga (importante)

1. **`SIGFIG.txt` primero, y guardarlo en `HOME`** (no dentro de una subcarpeta).
   No tiene envoltorio `DIR` a propósito: se guarda con `'SIGFIG' STO` en HOME.
   `DOLS` y `DCOVCORR` lo llaman por nombre y no lo encuentran si está en una
   carpeta hermana (regla de scope, CLAUDE.md §5).
2. El resto de los `.txt` de esta carpeta, en cualquier orden. Cada uno trae su
   propio `DIR` y cae como subcarpeta.
3. Los archivos de `datos/` son listas sueltas (sin `DIR`). Se guardan con
   `'NOMBRE' STO` y después se usan escribiendo el nombre de la variable en
   cualquier campo "Datos:".
4. **`MAT1.txt`** (Matemática I) es una sola transferencia que cae como una
   subcarpeta con los 18 objetos adentro. Ver abajo.
5. **`DINF.txt`**, y guardarlo en `HOME`. Se corre **una vez**: se pone el
   símbolo ∞ del teclado en el nivel 1 de la pila y se ejecuta. Deja el global
   `INF`, sin el cual `DASHO` y `DESTFUN` no calculan asíntotas (`DCONT` ya no
   lo necesita). El
   porqué está en `../SUITE-MAT1.md` §2; en corto, el carácter ∞ no puede viajar
   dentro de un archivo ASCII de 7 bits y hay que capturarlo en la máquina.

6. **`TESC.txt`** es una prueba de un solo uso, y va **suelta, no dentro de
   `MAT1.txt`**, justamente porque prueba escapes que todavía no están
   confirmados en la transferencia. Transferirla y correrla: si la primera caja
   dice **TYPE 9**, Conn4x traduce `\oo` y entonces `DINF` y el global `INF`
   dejan de hacer falta, `\>=`/`\<=` reemplazan al rodeo `< NOT` y `\.S` sirve
   para `AREA`/`IMPR`. Si dice **TYPE 6**, el escape no se tradujo y todo queda
   como está. Los tres ya funcionan **dentro** de la máquina (CLAUDE.md §2.1);
   lo único que esto prueba es la traducción del archivo de texto.

## Matemática I

La fuente son los archivos sueltos de **`mat1/`**; `MAT1.txt` es **salida
generada**, no editarlo a mano.

```powershell
..\verificar.ps1 .\mat1\*.txt    # verificar la fuente
.\armar-mat1.ps1                 # regenerar MAT1.txt     (calculadora, via Conn4x)
.\armar-emu.ps1                  # regenerar MAT1-EMU.txt (emulador, via ASCIIBIN)
```

Hay **dos** paquetes generados porque los dos caminos de carga no aceptan lo
mismo:

| Archivo | Para | Forma |
|---|---|---|
| `MAT1.txt` | La calculadora real, por Conn4x | Un `DIR` con los 18 objetos |
| `MAT1-EMU.txt` | Emu48, por `ASCIIBIN` | Un programa instalador que hace los 18 `STO` |

`ASCIIBIN` falla a veces con directorios, de ahí la segunda forma. El detalle
está en `../SUITE-MAT1.md` §9. **`verificar.ps1` le marca huérfanos a
`MAT1-EMU.txt` y está bien**: son los literales de programa, deliberados.
Verificar `mat1/`, que es la fuente.

El empaquetado en un único `DIR` no es cosmético: `TD` y `TF` referencian
`TDSEP` y `TEFUN` por nombre global, y entre carpetas hermanas no hay
visibilidad. El razonamiento completo está en `../SUITE-MAT1.md` §3.

`armar-mat1.ps1` ya emite CRLF y ASCII puro, así que `MAT1.txt` no pasa por
`a-crlf.ps1`.

## Estado de prueba en hardware

| Programa | Estado |
|---|---|
| `DSTATS`, `DPCTIL`, `DMODA`, `DFRECTABLA` | Verificado contra valores de cátedra |
| `DCOVCORR`, `DOLS` | Verificados; `r` coincide entre ambos (0.9781) |
| `DHISTO` | Verificado tras corregir bug de bloque huérfano |
| `DMKT`, `DMKTFISC`, `DCOMPFIRM` | Verificados con casos conocidos (CLAUDE.md §6) |
| `DPIBPPA`, `DTCAMBIO`, `DVLRZ` | Verificados |
| `DBOXPLOT` | Versión de coordenadas reales — **probar de nuevo**, se reescribió después de la última confirmación |
| `DTROZOS` | Versión con extremos `"<"` / `"<="` — **sin confirmar** en hardware |
| `mat1/`: `TCHK`, `DINF`, `DASHO`, `DCONT`, `DESTFUN` | Corridos. Destaparon y arreglaron los dos bugs del infinito (`../SUITE-MAT1.md` §2) |
| `mat1/`: los otros 13 | **Sin probar.** Pasan `verificar.ps1`, que chequea estructura, no semántica |

Pasar la batería no es evidencia de que un programa funcione. Antes de confiar en
cualquiera de los de `mat1/`, correr `TCHK` en la calculadora (SUITE-MAT1 §2).

## Convenciones de entrada

- Expresiones algebraicas: **con comillas simples** → `'X^2+3'`
- Símbolos de desigualdad en campos: **con comillas dobles** → `"<"` , `"<="`
- Campos K / Ancho / Inicio en `0` = cálculo automático
- En `DMKTFISC`, impuesto `T` negativo = subsidio (la "Recaudación" negativa se
  lee como costo fiscal)
- Los de `mat1/` para **Parcial 1** (`DOPFUN`, `DCONT`, `DASHO`, `DASV`, `DDEF`,
  `DTANOR`, `DESTFUN`, `DVFG`, `DDOMP`) usan `INFORM` y `MSGBOX` como el resto de
  la suite, y además dejan el resultado en la pila cuando no entra en una caja de
  2 líneas.
- Los de `mat1/` para **Parcial 2 y final** (`LHOP`, `DSEP`, `DSEPI`, `LAGR`)
  todavía toman los argumentos de la pila. Falta convertirlos.
  Las interfaces de todos están en `../SUITE-MAT1.md` §7.

## Salidas especiales

- `DFRECTABLA` deja una **matriz** en la pila. Para verla como planilla: pasar a
  **modo algebraico** y hacer `EDIT` sobre ella.
- Los programas de estadística y economía usan `MSGBOX` encadenados (apretar OK
  para avanzar entre cajas).

## Inconsistencia conocida contra CLAUDE.md

CLAUDE.md §2.5 dice que el default de un campo `INFORM` numérico debe ser un
string no vacío como `"0"`, nunca `""`, porque un campo nunca visitado se envía
con su default literal. **`DPIBPPA.txt` usa `""` en sus tres campos** y sin
embargo figura como verificado.

Las dos posibilidades son que la regla esté formulada de más, o que `DPIBPPA`
tenga un bug latente que no se disparó porque en las pruebas siempre se
completaron los tres campos. No se tocó ninguno de los dos hasta resolverlo en la
máquina: cambiar un programa verificado sobre una duda sería empeorar la única
señal que hay. Prueba: correr `DPIBPPA` dejando un campo sin visitar.

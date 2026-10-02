# CLAUDE.md — Suite de programas UserRPL para HP 50g

Contexto de proyecto para continuar el desarrollo de una suite de programas en
UserRPL para una calculadora **HP 50g real** (no emulador), usada en las materias
**Laboratorio de Datos** y **Microeconomía I** (Lic. en Economía, FCE-UNLP), con
extensión planificada a **Matemática I**.

**Entorno de trabajo: Windows.** Los scripts auxiliares están en PowerShell
(`programas/verificar.ps1`, `programas/a-crlf.ps1`).

Todo lo que sigue fue verificado empíricamente en el hardware. Las reglas de la
sección "Reglas de UserRPL" NO son teoría: cada una viene de un bug real que
costó tiempo encontrar.

---

## 1. Formato de archivo y transferencia

Los programas se escriben como archivos `.txt` en la PC y se transfieren con
**Conn4x** a la calculadora.

Requisitos **obligatorios** para que Conn4x lo reconozca como objeto nativo
(programa/lista/matriz) en vez de cargarlo como string inerte:

1. Primera línea exacta: `%%HP: T(3)A(R)F(.);`
2. Terminaciones de línea **CRLF** (`\r\n`), no LF.
3. **ASCII puro de 7 bits** en todo el archivo — ni un byte fuera de 0x00–0x7F,
   ni siquiera dentro de comentarios `@`. Un carácter `Σ` en un comentario
   rompe la transferencia aunque el compilador ignore los comentarios.

Comando para convertir a CRLF al final de cada edición:

```bash
sed 's/$/\r/' archivo_lf.txt > /ruta/salida/ARCHIVO.txt
file /ruta/salida/ARCHIVO.txt   # debe decir: HP text - T(3) A(R) F(.);
```

**Terminología de Conn4x:** "download" = de la PC a la calculadora (al revés de
lo intuitivo).

**Después de cada transferencia:** confirmar el ícono del objeto en `VAR`
(programa / directorio / lista / string) antes de asumir que cargó bien.

### ⚠️ El tamaño importa: la 50g necesita el texto Y el objeto en RAM

Al recibir un `.txt`, la calculadora tiene en memoria el texto entero **y** el
objeto que compila con él. `MAT1.txt` con comentarios pesaba 171 KB y la 50g
respondió **`Syntax Error` seguido de `Insufficient Memory`** (02/10/2026): la RAM
libre de usuario ronda los 230 KB. Por eso `armar-mat1.ps1` y `armar-lab.ps1`
**sacan las líneas de comentario `@` y la sangría** al empaquetar: 171 → 52 KB
y 95 → 36 KB. Los fuentes sueltos conservan todo. Es seguro porque ningún
string ocupa dos líneas, ningún `@` va adentro de un string y ninguna línea de
comentario tiene código después de un segundo `@` (el comentario de UserRPL
termina en el fin de línea **o en el siguiente `@`**). Probado: el paquete
compacto compila como `DIR` en el emulador y 12 ejemplos del diccionario dan
igual (fork, `harness/casos-paquete.txt`).

### Estructura del archivo

```
%%HP: T(3)A(R)F(.);
DIR
  NOMBREPROG
  \<<
    ... código ...
  \>>
END
```

Un objeto suelto (sin `DIR`, ej. una lista de datos o un helper) va sin el
envoltorio y se guarda directo con `'NOMBRE' STO`.

---

## 2. Reglas de UserRPL (aprendidas a los golpes)

### 2.1 Comandos que NO existen (a pesar de sonar lógicos)

| Escribí esto ❌ | El real es ✅ | Nota |
|---|---|---|
| `ROUND` | `RND` | Necesita 2 args: `valor decimales RND`. Para entero: `0 RND` |
| `SQRT` | `\v/` | Es el símbolo √ en forma ASCII |
| `\GTE` / `\LTE` | `< NOT` / `> NOT` | No existen esos escapes. `A ≥ B` ⇔ `A B < NOT` |
| `>=` / `<=` | `< NOT` / `> NOT` | Sueltos no andan. Ver abajo: `\>=` es otra cosa |

**`\>=` y `\<=` (con barra) parecen ser los escapes correctos, y no están
probados acá.** No es lo mismo que `>=` suelto ni que `\GTE`. Hay dos fuentes
independientes de terceros, las dos de código que funciona:

- `Graf/GRAF.txt`: 7 usos de `\>=`, incluso dentro de strings que el programa
  compila en tiempo de ejecución con `OBJ\->`.
- Los fuentes de `calcnum` (ver el fork, `analisis/REVISION.md`): traen los
  símbolos como **bytes** del juego de caracteres de la HP, y ahí se lee que
  137 = ≤ y 138 = ≥. `\<=` aparece **39 veces como comando de pila**, no solo
  adentro de un algebraico: `K NMI \<=` compara dos valores y deja el flag.

**Confirmado corriendo en el emulador con ROM de 50g** (`harness/casos-escapes.txt`):
`3 3 \>=` da 1 y `4 3 \<=` da 0. Son comandos de pila de verdad. Falta lo de
abajo (que Conn4x traduzca la grafía) antes de sacarlos a producción, pero el
rodeo `< NOT` tiene los días contados. `verificar.ps1` ya distingue: marca `>=`
suelto y deja pasar `\>=`.

Escapes ASCII **confirmados por nosotros**: `\->` (flecha), `\<<` `\>>`
(programa), `\v/` (raíz), `\=/` (distinto de), `\GS` (Σ).

**`\.S` es la integral (∫)**, y toma 4 argumentos: `LOWLIM UPLIM EXPR X \.S`.
Visto en `Graf/GRAF.txt` y **confirmado en el emulador**: `0 1 'X^2' 'X' ∫ EVAL`
da `1/3`. Sirve para `AREA` e `IMPR` (§7): integral definida directa, sin pasar
por `RISCH` + `PREVAL`.

**⚠️ Los escapes son del formato de transferencia, no de la calculadora.**
`STR\->` **no los entiende**: pasarle un fuente con `\->` o `\<<` adentro da
syntax error y deja el string en la pila. Quien traduce `\->` al carácter 141 es
el programa de transferencia (Conn4x, `ASCIIBIN`), no el compilador de la
máquina. Importa cada vez que un programa compile texto en tiempo de ejecución.
La tabla de traducción está en `herramientas/compilar.py` del fork.

**⚠️ `\.oo` (infinito) transfiere y compila, pero NO sirve.** Produce un **nombre
global** (`TYPE` 6) que solo se *dibuja* como ∞. El infinito real del CAS es un
**algebraico** (`TYPE` 9). Por eso `LIMIT` con `'X=\.oo'` sustituye en vez de
calcular, y `1/\.oo` queda inerte en modo exacto. Confirmado en la máquina.

Es el caso más traicionero de esta tabla: no da error, no rompe la transferencia,
el objeto se ve bien en pantalla, y el resultado es silenciosamente equivocado.

**El infinito hay que capturarlo del teclado en la máquina**, porque el archivo
tiene que ser ASCII puro de 7 bits (§1) y ∞ está fuera de ese rango. Ver
`programas/DINF.txt` y `SUITE-MAT1.md` §2.

**⚠️ El infinito escrito en el fuente FUNCIONA — y `\.oo` no es el escape.**

Corrido en el emulador con ROM de 50g (`harness/casos-escapes.txt`, 9 de 9):

| Prueba | Resultado |
|---|---|
| `∞ TYPE` | **9** (algebraico, no nombre) |
| `'1/X' 'X' ∞ = LIMIT EVAL` | **0** |
| `'(X^2+1)/X' 'X' / 'X' ∞ = LIMIT EVAL` | **1** ← la `m` de `DASHO` |
| `'(X^2+1)/X' 'X' - 'X' ∞ = LIMIT EVAL` | **0** ← la `b` de `DASHO` |
| `∞ \->STR 3 3 SUB NUM` | **159** |

**Cuidado con lo que esto prueba y lo que no.** Lo que se probó es que el
**carácter** ∞ (código 159) metido dentro de un objeto se comporta como el
infinito del CAS. Lo hizo `herramientas/compilar.py`, que traduce los escapes a
bytes del juego de caracteres de la HP y manda el objeto ya armado. Lo que
**falta** es que Conn4x traduzca la grafía `\oo` de un archivo de texto a ese
carácter. Es un paso chico y se prueba con un archivo de una línea.

Si eso anda, `DINF` y el global `INF` sobran: `DASHO`, `DESTFUN` y las asíntotas
se escriben con el infinito en el fuente y listo.

De paso quedó claro por qué `\.oo` falla: la tercera medición dio 159 recién en
el carácter 3, porque `\->STR` de un algebraico devuelve `'+∞'` **con comillas y
con signo**. La secuencia 39 → 43 → 159 del emulador es la misma que costó tres
lecturas en la calculadora.

**Hipótesis (ahora sí solo de transferencia): el escape sería `\oo`, sin el punto.**
Toda la familia es de la forma `\.S` (∫), `\.d` (∂), `\v/` (√), `\GS` (Σ), y en
esa tabla ∞ es `\oo`. `\.oo` no aparece en ninguna fuente ajena — ni en
`Graf/GRAF.txt`, ni en los 52 fuentes de `calcnum`, ni en el ejecutable de
Debug4x, que sí contiene `\oo`. Encaja con el síntoma observado: un escape que el
compilador no reconoce se compila como **nombre con los caracteres literales**, y
en la pila se vio precisamente `1/\.oo` con la barra a la vista, no el glifo ∞.

Si se confirma, `DINF` y el global `INF` sobran. La prueba es de tres líneas y
está escrita en el fork, `analisis/REVISION.md` §2. Hasta correrla, `INF` sigue
siendo la forma soportada.

**Para detectar si un resultado del CAS es infinito, no comparar objetos.**
`+∞` y `∞` son objetos distintos (la calculadora escribe el `+` sola), así que
`SAME` contra un ∞ guardado falla. El carácter ∞ tiene **código 159** y aparece
igual en `+∞`, `-∞` o `2*∞`: `VALOR \->STR 159 CHR POS` da 0 si no hay infinito y
la posición si hay. Confirmado que el código es 159; el `SAME` frágil costó una
corrida de `DCONT` con el veredicto equivocado.

`\.d` (derivada parcial) se descartó sin probar — `DERIV` hace lo mismo y es
comando de fábrica. La decisión sigue en pie, pero ahora se sabe que pertenece a
la misma familia que `\.S`, que sí se va a necesitar.

Síntoma típico de usar un comando inexistente: el nombre queda **sin evaluar en
la pila** y el error aparece más adelante, en el comando que recibe la basura
(ej. `R\->C ERROR: BAD ARGUMENT TYPE` con `'ROUND'` visible en la pila).

### 2.2 Bloques `\<<` huérfanos ⚠️ (el bug más difícil de detectar)

Un `\<< ... \>>` que **NO** está inmediatamente precedido por una declaración
`\->` **nunca se autoejecuta** — se empuja a la pila como dato inerte (ves el
código entero sentado en el nivel 1).

Es fácil de introducir al sacar una variable `\->` que antes precedía a un `\<<`,
dejándolo huérfano.

**Este bug NO se detecta contando paréntesis** — el total puede seguir cerrando
perfecto. Hay que verificar que cada `\<<` (salvo el que abre el programa entero)
tenga un `\->` en la línea anterior. Ver script en sección 4.

### 2.3 Variables locales vs. globales y `PURGE`

- **Locales** (creadas con `\->`): se autodestruyen al cerrar su scope. Nunca
  hace falta (ni sirve) purgarlas.
- `{ NOMBRE }` con un nombre **LOCAL** evalúa al **VALOR**, no al nombre → `PURGE`
  falla con "bad argument type". Con un nombre **GLOBAL** (creado con
  `'NOMBRE' STO` sin `\->` previo) sí funciona.
- `'NOMBRE' STO` **actualiza el local existente** si ya hay uno en scope con ese
  nombre (no crea un global nuevo). Así se mutan acumuladores dentro de un loop.
- Para armar una lista de 1 elemento desde un local: `VALOR 1 \->LIST`, nunca
  `{ VALOR }` (esto último guarda el nombre sin evaluar).
- **Nunca** guardar un programa dentro de una variable local para invocarlo
  después por nombre — comportamiento inconsistente confirmado. Poner la lógica
  inline en cada punto de uso.

### 2.4 Concatenación de strings (patrón semilla)

```
"Etiqueta: " VALOR \->STR + 10 CHR +     <- semilla SIN + adelante
"Otra: " + VALOR2 \->STR +               <- cada pieza CON su +, incluida la última
MSGBOX
```

- El **primer literal es la semilla** y NO lleva `+` antes (no hay nada con qué
  concatenar todavía). Ponerlo da `+ ERROR: too few arguments`.
- Cada pieza siguiente, **incluida la última antes de `MSGBOX`**, necesita su `+`.
  Olvidar el `+` final deja dos objetos sueltos y `MSGBOX` muestra solo uno
  (bug silencioso: se ve "algo", pero falta texto).

### 2.5 `INFORM` (formularios)

- **Máximo ~4 campos** por pantalla. Con 5, el último queda inalcanzable con las
  flechas. Solución: partir en 2+ pantallas `INFORM` secuenciales.
- Campo **numérico**: `{ "label" "default" 0 }` (3 elementos, el `0` final es el
  código de tipo). Sin ese `0`, el valor vuelve como texto y rompe la aritmética.
- Campo que acepta **lista/vector/algebraico**: `{ "label" "hint" }` (2 elementos).
- El default debe ser un string no vacío como `"0"`, nunca `""` — un campo nunca
  visitado se envía con su default literal.
- `OBJ\-> DROP \-> N1 N2 N3` asigna en el **mismo orden** en que se declararon los
  campos. Invertir el orden es un bug frecuente y silencioso.

### 2.6 `MSGBOX`

- **No hace scroll.** Máximo seguro: **2 líneas de datos SIN encabezado
  decorativo** por caja. Más que eso corta contenido silenciosamente.
- Es **modal** (espera OK), así que varias llamadas seguidas encadenan solas.
  Patrón usado: partir un resumen de 6 líneas en 3 cajas de 2.

### 2.7 `FOR` y modo exacto/aproximado

- ⚠️ **Un `FOR` ejecuta el cuerpo SIEMPRE al menos una vez, incluso con
  inicio > fin.** El test está en el `NEXT`, no en el `FOR`: es un do-while.
  `2 1 FOR i 5 NEXT` deja **un** objeto en la pila, no cero. Medido en
  `harness/casos-ruf4.txt`.

  **Acá decía lo contrario** ("inicio > fin no ejecuta ni una vez"), y era
  falso. La "raya fantasma" que motivó la nota original es precisamente el
  síntoma de esta regla, mal atribuido al caso inicio = fin.

  Es peligroso porque el cuerpo corre con el índice **en el inicio**, fuera del
  rango previsto: `2 CF SIZE FOR i ... CF i GET` con `CF` de un solo elemento
  pide el elemento 2 y tira `ERROR`. Así fallaba `DRUFC` recién con la segunda
  raíz, y así fallaba `DMODAC` con un solo dato.

  **El rodeo es envolver el `FOR` en un `IF` que garantice inicio ≤ fin:**

  ```
  IF CF SIZE 1 >
  THEN
    2 CF SIZE FOR i ... NEXT
  END
  ```

  Ya aplicado en `DRUFC` y `DMODAC`; `DBOXPLOTG` ya lo tenía para los outliers,
  que es el caso donde más se nota (un boxplot sin atípicos es lo normal).
  Los `1 N FOR` sobre listas de datos rompen con lista vacía, lo que da un
  `ERROR` visible y no una respuesta equivocada: se dejaron así a propósito.
- Si el orden relativo de dos límites puede variar según el caso (ej. impuesto
  vs. subsidio), calcular explícitamente cuál es menor con IF/THEN/ELSE antes del
  `FOR`.
- Literales enteros pueden generar **fracciones exactas/simbólicas** que los
  comandos gráficos rechazan con "BAD ARGUMENT TYPE". Mitigación: escribir
  literales con punto decimal (`0.` `10.` en vez de `0` `10`) y aplicar `\->NUM`
  antes de usar un valor calculado como coordenada.

### 2.8 Gráficos: `PICT`, `R\->C`, `XRNG`/`YRNG`

- ⚠️ **Una fila con número MÁS GRANDE está FÍSICAMENTE MÁS ARRIBA** en pantalla
  (al revés de la convención top-down típica). Detectado por una pendiente
  invertida en un gráfico de dispersión.
- `XRNG`/`YRNG` **NO son cosméticos**: reescalan de verdad cómo `LINE`/`BOX`/
  `PIXON`/`R\->C` interpretan sus argumentos.
- **Enfoque recomendado** (el que usan las versiones actuales): fijar
  `XRNG`/`YRNG` al **rango real de los datos** y dibujar con **valores reales
  directos**, sin fórmula manual de escalado a píxel. Ventajas: código mucho más
  simple, y el cursor del modo interactivo lee valores reales.
- **No mezclar** coordenadas estilo píxel crudo con un `XRNG`/`YRNG` de rango
  real en el mismo programa. Elegir un enfoque y ser consistente.
- `XRNG` rechaza rangos de **ancho cero** con "bad argument value". Siempre
  poner salvaguarda: `IF XMAX XMIN == THEN XMAX 1. + 'XMAX' STO END`.
- Offsets de marcadores deben ser **proporcionales a la escala**
  (ej. `QMAX 40. /`), no constantes de píxel.
- `GOR` (pegar GROB sobre PICT) necesita **3 argumentos**, con `PICT` primero
  (nivel 3, el más profundo): `PICT grob posicion GOR`.
- `\->GROB` (string → gráfico de texto) es válido.

**Cómo probar un gráfico desde la PC** (medido en el emulador,
`harness/casos-graf.txt`):

- **`PICT` en la pila NO es un GROB** (da `TYPE` 19). Para traerlo:
  `PICT RCL`, que sí da `TYPE` 11 y se decodifica con `herramientas/hpobj.py`.
  El `PICT` de la 50g mide **131x80**, no 131x64.
- **`PIX?` entiende las coordenadas reales de `XRNG`/`YRNG`**, igual que
  `LINE`/`BOX`/`PIXON`. O sea que se puede afirmar "en el valor 17.5 y la
  frecuencia 8 hay un pixel encendido" sin traducir a píxel a mano.
- **Es exacto en bordes horizontales y verticales, en los extremos de una
  línea y en un `PIXON`.** En el **punto medio de una diagonal falla**: la
  línea rasterizada pasa por el píxel de al lado, y ni una vecindad de ±1
  píxel lo salva. Las aserciones se hacen sobre lo axis-aligned (techos de
  barras, la caja, la mediana, la cruz de equilibrio, la línea de precio) y
  sobre los extremos de las diagonales, que sí son los píxeles que se le
  pasaron.
- **`BOX` dibuja el contorno, no rellena**: el interior de una barra da 0.
  Sirve como aserción negativa.
- El par de aserciones que verifica la **orientación del eje Y** (lo de arriba
  de esta sección) es: en la barra alta hay píxel a la altura máxima, y en la
  barra baja NO lo hay a esa misma altura. Si el eje estuviera invertido, las
  dos fallarían a la vez.
- Medir no reemplaza **mirar**: `harness/ver-dibujo.py` dibuja el GROB en ASCII
  en la terminal. Las aserciones dicen que tal píxel está donde va; el dibujo
  entero dice si el gráfico tiene sentido.

### 2.9 Camino nativo de graficación (leído en código de terceros, sin probar)

```
'X^2' 'EQ' STO
-5. 5. XRNG  0. 25. YRNG
ERASE DRAX DRAW LABEL PICTURE
```

`DRAX` = ejes, `DRAW` = grafica la EQ, **`LABEL` = pone los números en los ejes
automáticamente**. Mucho más simple que dibujar con `LINE` a mano, y resuelve el
problema de rotular gráficos que habíamos abandonado.

**Ya no es especulación.** El fuente completo está en `Graf/GRAF.txt` (suite de
terceros, autor `au777fait@gmail.com`), y su programa de funciones a trozos
`PCWYZ` usa exactamente esta secuencia en producción, con `2.01 MENU` antes de
`PICTURE`. Sigue **sin probarse en nuestro hardware**: leer código ajeno que
funciona es mejor evidencia que una corazonada, pero no es una prueba.

Cuatro técnicas de ahí que valen para nuestra suite:

**a) Restricción de dominio sin dibujar tramo por tramo.** En vez de recortar a
mano, `EQ` se carga con una **lista de programas**, uno por tramo, y `DRAW` los
grafica todos de una. Cada programa devuelve la expresión del tramo si `x` cae
adentro, y `'\v/-ABS(X)'` si cae afuera:

```
\<< X \-> x
  \<<
    IF DLA x >   THEN '\v/-ABS(X)'
    ELSE IF ULA x \>= THEN EA ELSE '\v/-ABS(X)' END
    END
  \>>
\>>
```

√(−|X|) no es real, así que el plotter simplemente **saltea** ese punto. Es más
simple y más robusto que el bucle de `LINE` que usa `DTROZOS`. Ojo: no protege
contra asíntotas — un valor enorme sigue siendo real.

**b) Autoescala de ventana.** `Screen4Pw` muestrea cada tramo en 7 puntos
(`0. 6. FOR n ULp DLp - 6. / n * DLp +`) y acumula min/max de X e Y. `DTROZOS`
hoy le pide la ventana al usuario; esto la calcula solo.

**c) String → nombre global sin evaluar**, en una línea:

```
PRESERVE:  \<< "}" + "{" SWAP + OBJ\-> OBJ\-> DROP \>>
```

`"EA" PRESERVE` deja el nombre `EA` sin evaluar, listo para `STO` o `PURGE`.
Se apoya en la regla de 2.3 (los nombres adentro de una lista no se evalúan).
Combinado con `64. p + CHR` (que da "A", "B", "C"... desde el índice de un
`FOR`) permite crear variables dinámicas `EA`/`EB`/`EC`, `ULA`/`ULB`, etc.

**d) Guardar y restaurar las opciones de display del usuario.** Los programas
abren con `7. NOFORMAT` y cierran con `8. NOFORMAT`. Ataca el problema de que
ningún programa nuestro fija ni restaura flags.

**`NOFORMAT` ya está descompilado** (fork, `analisis/graf/`), y no hace falta el
binario: `7` guarda las banderas −45…−50 (formato de número) y −17/−18 (modo
angular) con `FS?` en un global `NUMfrmt`; `8` las restaura con `SF`/`CF`;
`0`…`4` es `FIX 0`…`FIX 4` y `9` es `STD`. Diez líneas de UserRPL.

**Para código propio conviene más `RCLF` / `STOF`**, que son de fábrica y guardan
el estado **completo** de la máquina de una:

```
RCLF \-> FL
\<<
  ... fijar los modos que hagan falta, hacer el trabajo ...
  FL STOF
\>>
```

Así lo hace `domain49` (fork, `analisis/domain49/LOGICA.md`). Es lo que Mat1
necesita para pasar a modo exacto y devolver la máquina como estaba.

También usa `INPUT` (no `INFORM`) con prompts multilínea, que esquiva el límite
de ~4 campos de 2.5.

### 2.10 Evaluación de expresiones algebraicas (CAS)

Confirmado que funciona:

```
'X^2+3' \-> EXPR
\<<
  2 'X' STO
  EXPR EVAL \->NUM     @ da 7
\>>
```

- El usuario debe tipear la expresión **con comillas simples**: `'X^2+3'`.
- Para símbolos sueltos (`<`, `<=`) en un campo, van **con comillas dobles**:
  `"<"`, `"<="` — si no, la calculadora intenta parsearlos como comparación
  algebraica incompleta y tira syntax error.
- Salvaguarda por si el campo devuelve string en vez de algebraico:
  `IF DUP TYPE 2 == THEN STR\-> END`

### 2.11 ⚠️ `IFERR` **no** limpia la pila

Medido en el emulador con ROM de 50g, batería `harness/casos-diag.txt`:

```
DEPTH \-> D0 \<< IFERR 1 2 0 INV THEN "E" END DEPTH D0 - \>>     @ da 3, no 1
```

El cuerpo alcanzó a empujar `1` y `2` antes de que `0 INV` fallara. **Los dos
quedaron en la pila**, y encima el `"E"` del `THEN`: 3 objetos. Si `IFERR`
restaurara la pila, el resultado sería 1.

Importa porque la suite usa `IFERR` en todos lados con la forma

```
IFERR  ARG1 ARG2 COMANDO  THEN "FALLO" END
```

y si `COMANDO` falla, `ARG1` y `ARG2` **se quedan**. Las consecuencias, de menor
a mayor:

- Si lo que sigue es `'VAR' STO`, el valor guardado es el correcto y la basura
  solo ensucia la pila. Molesto, no grave.
- Si lo que sigue es una **concatenación de strings con `+`** (patrón 2.4), el
  `+` toma los dos objetos de arriba, que ahora incluyen la basura. Sale texto
  equivocado o un `BAD ARGUMENT TYPE`.
- Si lo que sigue arma un resultado con `=` o `\->LIST` (`DSEP`, `DSEPI`), el
  programa **devuelve una respuesta equivocada sin avisar**. Es el caso peor.

El rodeo, cuando importa, es un guardián de profundidad:

```
DEPTH \-> D0
\<<
  IFERR ARG1 ARG2 COMANDO THEN "FALLO" END
  \-> R \<< DEPTH D0 - DROPN R \>>        @ tira lo que sobre y deja solo R
\>>
```

### 2.12 El CAS abre diálogos modales en medio del cálculo

`LIMIT` de `1/X` en 0 abre **"Unsigned inf. Solve?"** y se queda esperando una
respuesta. Un programa que corre solo se cuelga ahí hasta que alguien contesta.

**Los límites laterales de verdad existen** y no tienen ese problema: `'X=a-0'` y
`'X=a+0'` dan el ∞ con signo (`harness/casos-lateral.txt`). Desde la pila no se
pueden armar (`a 0 -` se reduce a `a`): hay que compilarlos desde texto con
`STR\->`, como hacen `DCONTC` y `DCONTFC`. Ojo: ignoran el dominio (`\v/X` en `0-0` da `0`).

Afectaba a `DCONT` con una rama que revienta en el punto de corte, que es
justamente el caso interesante. Y la respuesta por defecto (YES) devuelve el
infinito **sin signo**, que es por qué `DCONT` informaba `lim izq +∞` para `1/X`
cuando el límite lateral verdadero es −∞. **Resuelto:** `DCONT` pasó a
laterales y ahora da −∞.

**⚠️ Corrección (medido el 02/10/2026): los laterales TAMBIÉN abren el diálogo.**
`'1/(X^2-9)'` con `'X=3-0'` y con `'X=3+0'`: cada `LIMIT` pregunta una vez. Lo de
arriba ("no tienen ese problema") nunca se había medido: el harness contesta
ENTER cada 4 s y el diálogo pasaba sin verse. Lo que sí vale: **la respuesta
es correcta contestando YES o NO** (`-\oo` y `+\oo` con signo). En la interfaz,
`DASVT` con `1/(X^2-9)` muestra 4 diálogos (2 candidatos × 2 lados) y termina
en `X=-3, X=3` con cualquiera de las dos respuestas. Lo mismo pasa desde
siempre en `DCONT`/`DCONTF` en un polo. **En el parcial: apretar OK.**

Otros datos de la misma medición: `SUBST EVAL` en el polo da `'\oo'` **sin**
preguntar; `\->NUM` da `ERROR`; `-120 SF` **no** evita el diálogo. Y el prólogo
de las baterías (`\oo 'INF' STO`, de `armar-mat1.py`) abre **su propio**
diálogo, así que para ver si un programa pregunta hay que sacar esa línea.
Método: correr con `-EnterCadaMs` igual a `-EsperaMs` (un solo ENTER al final)
y mirar la LCD: si el resultado aparece **duplicado**, ese ENTER cayó sobre un
programa terminado y no hubo diálogo; si aparece una vez, el ENTER contestó uno.
Que el resultado llegue no prueba nada.

### 2.13 Matrices como salida tipo tabla

`{ K 6 } \->ARRY` construye una matriz de K filas × 6 columnas a partir de K*6
valores apilados. En **modo algebraico**, `EDIT` sobre esa matriz abre un editor
de celdas tipo planilla (en modo RPN solo edita la matriz plana).

### 2.14 Un resultado complejo NO es un error (y arruina los dominios)

Con el modo **Complex encendido**, `\v/(-1)` **no da error**: devuelve `(0.,1.)`, o
sea `i`. Un `IFERR` alrededor no salta, y un punto que está fuera del dominio
real pasa por bueno.

Medido en el emulador con ROM de 50g: `DDOMP` contaba **4** puntos en el dominio
de `\v/X` sobre `{ -1 0 1 4 }` en vez de 3, y `DOPFUN` evaluaba una composición
fuera de dominio en vez de decir NO EXISTE.

**La solución es mirar el TIPO, no las banderas:**

```
IFERR F \->NUM THEN "FUERA" END
IF DUP TYPE 0 ==            @ 0 = real. Un complejo es 1.
THEN  ... cuenta como dentro ...
ELSE DROP "FUERA"
END
```

Decidir por `TYPE` vale con el modo Complex prendido o apagado. Depender de que
el usuario tenga la máquina configurada como esperamos es una suposición que en
un parcial no se cumple. Ya aplicado en `DDOMPC` y `DOPFUNC`.

### 2.19 Comandos del CAS medidos para Ruffini, Weierstrass y Bolzano

Todo esto se midió **antes** de escribir los programas (`harness/casos-nuevos.txt`,
`casos-nuevos2.txt`, `casos-nuevos3.txt`), que es la regla de §3.1 y volvió a
pagar: tres de las cuatro sorpresas habrían sido bugs silenciosos.

| Comando | Qué hace de verdad |
|---|---|
| `HORNER` | **Es la división sintética de fábrica.** `'X^3-1' 1 HORNER` deja cociente / raíz / resto en los niveles 3 / 2 / 1. Solo acepta el algebraico, **no** una lista de coeficientes |
| `DEGREE` | grado del polinomio; con `'SIN(X)'` da error, que sirve de validación |
| `DIVIS` | divisores: `6 DIVIS` → `{ 1 2 3 6 }`. **`-1 DIVIS` da `{ 1 }`, pero `-6 DIVIS` da los dos signos.** No confiar en el signo del argumento: poner los ± a mano |
| `LCOEF` | **no existe.** Queda sin evaluar en la pila (síntoma de §2.1). El coeficiente principal sale de pelar con `HORNER` por 0 |
| `TABVAL` | sí existe: `'X^2' { 0 1 2 } TABVAL` → `{ { 0 1 2 } { 0 1 4 } }` |
| `TEXPAND` | **es el que abre `SIN(2*ATAN(T))`**; `SIMPLIFY` lo deja como está |

Y tres trampas, las tres del mismo tipo que el resto de este archivo — resultado
verosímil, callado y equivocado:

- **`ZEROS` con una sola raíz NO devuelve lista.** `'X^2-2*X+1' 'X' ZEROS` da
  `1` suelto (un ZINT), no `{ 1 }`. Un `SIZE` o un `GET` encima se rompe. Hay
  que normalizar: `IF DUP TYPE 5 == NOT THEN 1 \->LIST END`.
- **`ZEROS` de `X^2+1` devuelve las raíces complejas**, no lista vacía. Es §2.14
  otra vez: filtrar por `TYPE` después de `\->NUM`, no suponer que "sin
  soluciones reales" se vea como lista vacía.
- **`'1/X' 'X' 0 = SUBST EVAL \->NUM` no da error**: devuelve
  `9.99999999999E499`. O sea que **una discontinuidad no se detecta con
  `IFERR`** — hay que mirar la magnitud, como ya hacía la red numérica de
  `DCONTC`. `DWEIERC` sondea el intervalo en 21 puntos con ese criterio.

Un cuarto detalle, de presentación: **comparar un algebraico contra un número
con `\=/` no devuelve un booleano**, devuelve una ecuación simbólica, y el `IF`
revienta. Costó una corrida entera de `DRUFC`, donde los casos sin raíz pasaban
y los que encontraban raíz daban `ERROR`. Cuando hay que decidir, decidir sobre
los **coeficientes**, que son números.

### 2.20 ⚠️ Medido para los programas de Parcial 1 (desigualdades, dominio, inversa)

Tres sondeos antes de escribir `DDOM`/`DINEC`/`DINV`/`DCONTK`/`DPAR`
(fork, `harness/casos-p1sonda.txt`, `casos-p1sonda2.txt`, `casos-p1sonda3.txt`).

**`SOLVE` resuelve desigualdades, y se equivoca con racionales.**
`'X^2-X-2>0' 'X' SOLVE` da `'X<-1 OR X>2'`, bien. Pero
`'(X+1)/(X-2)\>=0' 'X' SOLVE` da `'X\<=-1 OR X\>=2'`: **mete el 2**, donde el
denominador se anula. Salida prolija y falsa, otra vez. Por eso `DINEC` resuelve
por tabla de signos (`DINTC`) y no con `SOLVE`. Sin solución da `'Impossible'`;
con todo R da `'X'`.

**El modo Complex (bandera −103) cambia lo que devuelven `ZEROS` y `SOLVE`.**
El estado `Default 50g.E49` del emulador lo tiene **prendido**. Con −103
prendido, `'ABS(6*X-3)-9' 'X' ZEROS` da `'(3*EXP(i*x1)+1)/2'` (basura compleja,
sin error) y `'Y=2^X+1' 'X' SOLVE` trae `2*i*n1*π`. Con `-103 CF`: `{ -1 2 }` y
`'X=LN(Y-1)/LN(2)'`. Los núcleos nuevos lo apagan adentro de `RCLF` … `STOF`.
Aun apagado, `\v/` y `LN` de un negativo con `\->NUM` dan complejo: sigue
valiendo §2.14.

**`OBJ\->` sobre un algebraico deja argumentos, cantidad y función**, y así se
recorre el árbol sin simplificar: `'(X-3)/(X^2-9)'` → `'X-3' 'X^2-9' 2. /`.
`'X' OBJ\->` da ERROR (es un nombre, `TYPE` 6). La función con `\->STR NUM`:
√ 131, `>` 62, `<` 60, `≥` 138, `≤` 137, `≠` 139. Con esos códigos se decide sin
poner caracteres fuera de ASCII en el fuente.

**Un límite lateral puede volver ETIQUETADO.** `'EXP(4/(X+1))'` en `'X=-1-0'`
devolvió `:+: 0` (`TYPE` 12) en `DCONTKC`. Los núcleos viejos no lo veían porque
hacen `LIMIT EVAL`, y el `EVAL` saca la etiqueta. Donde no se quiera `EVAL` (para
no evaluar un parámetro que el usuario tenga guardado): `IF DUP TYPE 12 == THEN DTAG END`.

Otros datos sueltos: `SIGNTAB` existe y marca con `'?'` donde la función no está
definida; `SREPL` existe; `DEFINE` crea un global (`DPAR` lo usa para F y G, y
las purga).

### 2.16 ⚠️ La bandera −105 decide cómo compila `STR\->`

El modo **Aproximado/Exacto** es la bandera **−105**, y no es solo cómo se
muestran los números: cambia **lo que compila un string**. Con la máquina en
aproximado, `"1" STR\-> TYPE` da **0** (real) en vez de **28** (entero exacto), y
con enteros aproximados **`RISCH` directamente falla**.

Importa porque el harness compila el fuente en la máquina (`\<< "..." STR\-> EVAL \>>`).
Una batería entera volvió con `.5*Y^2.` y `"ERR: RISCH"` en vez de `Y^2/2`, **sin
un solo error a la vista**: los resultados se veían plausibles y estaban mal.

Dos detalles que costaron tres intentos de diagnóstico:

- **La bandera actúa en tiempo de compilación, no de evaluación.** Las dos
  primeras sondas fallaron porque operaban sobre literales **ya compilados** a
  ZINT por el mismo `STR\->`, así que daban exacto igual. La sonda que sirve
  compila un string *después* de tocar la bandera.
- **No se puede arreglar desde adentro del fuente**: cuando el `-105 CF` del
  fuente corriera, el fuente ya está compilado. Tiene que ir en un `STR\->`
  **anterior**. `herramientas/compilar.py` emite `"-105 CF" STR\-> EVAL` como par
  propio antes del fuente (`PROLOGO_EXACTO`, se desactiva con `--sin-modo`).

`casos-mat1b.txt` tiene el canario: `"1" STR\-> TYPE` tiene que dar `28.`.
**Probado dejando la máquina en aproximado a propósito** (`casos-ensuciar.txt`) y
comprobando que la batería sale verde igual: 23 de 23. Un canario que nunca vio
la condición que detecta no es un canario.

### 2.17 ⚠️ `RISCH` no falla cuando no hay primitiva: devuelve `INT(...)`

`'EXP(Y^2)' 'Y' RISCH` **no da error**. Devuelve `'INT(EXP(Yttt^2),Yttt,Y)'`, un
algebraico (`TYPE` 9) con la integral **sin resolver adentro**. Medido en
`harness/casos-risch.txt`.

O sea que el `IFERR ... THEN "NO INTEGRA" END` de `DSEPC` y `DSEPIC` era **código
muerto para el caso que decía cubrir**, y la ecuación final salía armada con la
integral sin resolver: una no-respuesta con forma de respuesta. Es el mismo
patrón de `\.oo` y de la cancelación de `domain49`.

Se detecta por el texto, que es la técnica de §2.1 para el infinito:

```
IFERR MY 'Y' RISCH EXPAND THEN "NO INTEGRA M(Y)" END
IF DUP \->STR "INT(" POS 0 > THEN DROP "NO INTEGRA M(Y)" END
```

El `IFERR` **se queda igual**: cubre los fallos de verdad (argumento mal tipado).
Son dos modos de falla distintos y hacen falta los dos chequeos.

### 2.18 ⚠️ `TYPE` 29: un vector de enteros exactos no es un array real

En modo exacto, `[ 2 4 6 8 10 ]` (enteros **sin punto**, que es como los tipea
cualquiera) compila como **array simbólico, `TYPE` 29**, no como array real
(`TYPE` 3). Con punto — `[ 2. 4. 6. 8. 10. ]` — sí da 3.

Los diez núcleos de Lab que aceptan vector hacían `IF DUP TYPE 3 == THEN OBJ\-> 1 GET \->LIST END`,
así que con `TYPE` 29 **no convertían**, `SIZE` devolvía la lista `{ 5. }` en vez
del número 5, y el `FOR` de adentro reventaba con `ERROR`. Arreglado en los diez:

```
IF DUP TYPE 3 == OVER TYPE 29 == OR THEN OBJ\-> 1 GET \->LIST END
```

Es el mismo error de fondo que §2.14 (decidir por bandera lo que hay que decidir
por tipo), y apareció **solo** después de forzar modo exacto en el harness
(§2.16): en aproximado los literales enteros ya son reales y el caso no existe.
Vale la pena notar que este bug estuvo **latente y visto**: el caso
`stats-vector` había fallado una vez y "no reproducía", y se anotó como
inexplicado. Lo que pasaba era que la máquina quedaba en un modo u otro según la
corrida anterior.

### 2.15 ⚠️ Bytes de control: el bug que el chequeo de ASCII no ve

`CLAUDE.md` §1 exige ASCII de 7 bits. Un **byte de control** (0x00–0x1F) cumple
esa condición y pasa el filtro, pero es igual de venenoso.

Aparece cuando un script de Python escribe un archivo y un literal lleva barra
invertida seguida de letra: escrito `"\v/"` en Python, eso **no es la raíz
cuadrada**, es TABULADOR VERTICAL más `/`, porque `\v` sí es un escape de Python.
La familia de escapes de la HP (`\->`, `\<<`, `\.S`, `\oo`) se salva de casualidad:
ninguna de esas letras es un escape de Python. **`\v/` es la única que colisiona**, y
es la raíz cuadrada.

Pasó **tres veces** en este proyecto. La peor: `herramientas/compilar.py` tenía la
tabla de escapes con ese literal, así que la raíz **nunca se traducía** y a la
calculadora le llegaban los tres caracteres `\v/` literales. No daba error: el
algebraico compilaba igual, con un nombre basura adentro, y recién fallaba al
evaluar. **Invalidó en silencio una tanda entera de pruebas** — el veredicto de
que `domain49` fallaba con las raíces era falso, y era culpa nuestra.

Dos defensas, las dos ya puestas:

1. **`verificar.ps1` rechaza bytes de control** (chequeo 3b). Probado con un
   archivo corrompido a propósito.
2. **En Python, nunca escribir un escape de la HP como literal con barra.**
   Construirlo con `B = chr(92)`: `B + "v/"`. Así no puede volver a pasar.
   `compilar.py` y `armar-mat1.py` ya lo hacen, y los dos abortan si detectan un
   byte de control en su salida.

**Cómo comprobar que un carácter especial llegó de verdad:** no alcanza con
mirarlo en pantalla ni con `\->STR`, porque el nombre basura se dibuja igual. Hay
que medir el código: `'\v/(X-1)' \->STR 2 2 SUB NUM` tiene que dar **131**, y
`SIZE` **8**. Un control que no puede fallar no es un control.

---

## 3. Flujo de trabajo que funciona

1. **Probar aislado antes de confiar.** Ante cualquier comando o técnica nueva,
   escribir un test de 2-5 líneas y correrlo en la calculadora ANTES de meterlo
   en un programa grande. Esto ahorró horas repetidamente.
2. **Editar con `str_replace` de coincidencia exacta**, nunca reconstruir el
   archivo cortando con `head -N` y pegando pedazos — así se perdió un `\<<` en
   un empalme y costó un ciclo entero de debug.
3. **Correr la batería de verificación** (sección 4) antes de cada entrega.
4. **Convertir a CRLF** y verificar con `file`.
5. Si algo funciona en un programa pero falla en otro con patrón similar:
   **sospechar primero de una versión vieja todavía residente en la
   calculadora** antes de asumir un bug nuevo. Pasó dos veces (DBOXPLOT, DOLS).
   Purgar la vieja antes de probar la nueva.

---

## 4. Batería de verificación (correr antes de cada entrega)

**El entorno de trabajo es Windows.** Hay dos scripts de PowerShell en
`programas/`:

```powershell
# Verificar uno o varios archivos
.\verificar.ps1 DBOXPLOT.txt
.\verificar.ps1 *.txt

# Convertir a CRLF + verificar header y ASCII antes de transferir
.\a-crlf.ps1 archivo_editado.txt

# Matemática I: verificar la fuente y regenerar el paquete de transferencia
.\verificar.ps1 .\programas\mat1\*.txt
.\programas\armar-mat1.ps1
```

Si PowerShell bloquea la ejecución:
`powershell -ExecutionPolicy Bypass -File .\verificar.ps1 *.txt`

`verificar.ps1` chequea, en este orden: profundidad de anidación acumulada
(debe cerrar en 0), bloques `\<<` huérfanos, bytes no-ASCII, **bytes de control**
(§2.15 — son ASCII y el chequeo de 7 bits no los ve), comandos inválidos
(`SQRT`/`ROUND`/`>=`/`=/=`), comillas balanceadas, header `%%HP`,
terminaciones CRLF, `FOR` contra `NEXT`/`STEP`, y el balance de `END`.

El balance de `END` usa `END = THEN + CASE + DO + WHILE + DIR` (cada rama de un
`CASE` cierra con su propio `END`, y el `CASE` agrega uno más). Es el único
chequeo que detecta un **`IFERR` sin cerrar**, porque `IFERR` no abre un bloque
`\<<` y el conteo de profundidad no lo ve.

El chequeo de huérfanos exceptúa la línea previa cuando es un identificador
solo: dentro de un `DIR` esa línea es el **nombre** del objeto, y es legítima.
Así un archivo con varios objetos en un mismo `DIR` (`programas/MAT1.txt`) no
dispara falsos positivos.

**Dos agujeros de la compuerta, tapados (los dos encontrados con un archivo
roto a propósito, que es la única forma de probar un detector):**

1. La excepción del **nombre de objeto** aceptaba cualquier identificador
   suelto, y `DROP` parece un nombre: un `\<<` huérfano justo después de un
   `DROP` pasaba sin verse. Ahora la excepción vale **solo en archivos que
   tienen un `DIR`**, que son los paquetes generados. Los archivos de un solo
   programa —los que se editan a mano— quedan con el chequeo estricto.
2. Los **instaladores generados** (`MAT1-EMU.txt`, formato
   `\<< ... \>> 'NOMBRE' STO` en cadena) disparaban 26 falsos positivos en
   cada corrida. Se exceptúa el `\<<` cuya línea previa termina en `STO`:
   ahí la pila quedó limpia y lo que empieza es el objeto siguiente. Una
   compuerta que siempre se queja enseña a ignorarla.

**Advertencia:** el conteo total de paréntesis **no detecta** un `\<<` mal
ubicado si se compensó con cierres de más en otro lado. Por eso el chequeo de
profundidad acumulada y el de huérfanos son los importantes — un total
balanceado no garantiza nada.

Tras editar un bloque grande, comparar las partes **no tocadas** contra la
versión anterior (`git diff`, o `Compare-Object` en PowerShell) para detectar
truncamientos accidentales.

<details>
<summary>Equivalentes en bash (si alguna vez se trabaja en Linux/WSL)</summary>

```bash
F=archivo.txt

python3 -c "
with open('$F') as f:
    depth = 0; maxd = 0
    for line in f:
        depth += line.count('\\\\<<') - line.count('\\\\>>')
        maxd = max(maxd, depth)
    print('DEPTH FINAL:', depth, '| MAXIMA:', maxd)
"

python3 -c "
with open('$F') as f: lines = f.readlines()
h = [i+1 for i,l in enumerate(lines) if '\\\\<<' in l and i>0 and '\\\\->' not in lines[i-1]]
print('Huerfanos:', h)
"

grep -naP '[^\x00-\x7F]' $F || echo "ASCII OK"
grep -v '^\s*@' $F | grep -cE 'SQRT|ROUND|>=|=/='
sed 's/$/\r/' archivo_lf.txt > SALIDA.txt   # conversion a CRLF
```
</details>

---

## 5. Inventario de programas (16)

### Estadística descriptiva (una variable)

| Programa | Qué hace | Entrada |
|---|---|---|
| `DSTATS` | Media, varianza, desvío, CV | Datos |
| `DMODA` | Moda(s), avisa si no hay | Datos |
| `DPCTIL` | Percentil interpolado `Lp=(p/100)(n+1)`. **Mediana = p50** | Datos + p |
| `DFRECTABLA` | Tabla de frecuencias (abs, acum.abs, %, acum.%) como **matriz** | Datos + K + Ancho + Inicio |
| `DHISTO` | Histograma (barras) | Datos + K + Ancho + Inicio |
| `DBOXPLOT` | Caja, bigotes, outliers, eje, puntos individuales | Datos |

En `DFRECTABLA`/`DHISTO`, los campos K/Ancho/Inicio en `0` = automático, con la
regla de la diapositiva de la cátedra (§5, "Métodos de la cátedra"): Sturges,
ancho redondeado para arriba, inicio en un múltiplo del ancho. Con eso el de
horas trabajadas sale solo con K=5, Ancho=5, Inicio=10, que es lo que la
cátedra eligió "a mano". Lo que se fije a mano se respeta.

### Relación entre dos variables

| Programa | Qué hace |
|---|---|
| `DCOVCORR` | Covarianza, r de Pearson, dispersión + recta de regresión |
| `DOLS` | Regresión lineal (b0, b1, r, R²) por sumatorias |

Ambos piden **dos listas separadas** (X e Y), no una matriz. Ambos usan `SIGFIG`.

### Economía

| Programa | Qué hace |
|---|---|
| `DMKT` | Equilibrio de mercado simple + gráfico |
| `DMKTFISC` | Completo: impuesto/subsidio, Pb/Ps, recaudación, PIE, incidencia, elasticidades, controles de precio (techo/piso) con escasez/excedente, gráfico con áreas sombreadas |
| `DCOMPFIRM` | Empresa competitiva: Q* por P=CMg, beneficio, cierre; gráfico CMg/CVMe/P |
| `DPIBPPA` | PIB per cápita PPA |
| `DTCAMBIO` | Tasa de crecimiento anual compuesta (CAGR) |
| `DVLRZ` (`DCOMPZ`) | Valor Z, clasifica atípico si \|Z\|>3 |

### Matemática

| Programa | Qué hace |
|---|---|
| `DTROZOS` | Grafica funciones a trozos, con extremos abiertos/cerrados marcados |

`DTROZOS`: pide ventana de gráfico, luego por tramo la expresión (`'X^2'`), y
cada extremo como `"<"` / `"<="` / vacío (sin límite) + su valor.

### Matemática I (suite aparte)

59 objetos en `programas/mat1/`, empaquetados en `programas/MAT1.txt`.

Parcial 1 (cubierto entero), ya con `INFORM`/`MSGBOX` como el resto de la suite:

| Programa | Qué hace | TP |
|---|---|---|
| `DOPFUN` | Suma, resta, producto, cociente y las dos composiciones | 4 |
| `DCONT` | Continuidad de una función a trozos en el punto de corte | 7 |
| `DCONTF` | Continuidad de una función que no es a trozos en un punto; evitable/inevitable | 9 |
| `DASHO` | Asíntotas horizontales y oblicuas, a los dos infinitos | 8 |
| `DASV` | Asíntota vertical en un punto candidato | 8 |
| `DDEF` | Derivada por definición, con el cociente incremental a la vista | 9 |
| `DTANOR` | Recta tangente y recta normal en x0 | 9 |
| `DESTFUN` | Estudio de función completo, hasta donde llegue el CAS | 8+ |
| `DVFG` | Verifica una simplificación evaluando en seis puntos | 0/1 |
| `DDOMP` | Sondea qué puntos pertenecen al dominio | 1 |

Cuatro programas nuevos, pedidos para **verificar a mano** lo que la máquina
ya hace sola — que es exactamente el punto: `FACTOR` y `PROOT` dan el resultado,
la cátedra pide el procedimiento escrito.

| Programa | Qué hace | Por qué no alcanza un comando de fábrica |
|---|---|---|
| `DRUF` | Ruffini: factorea solo y muestra **la tabla de cada división** | `DIV2`/`HORNER` dividen, ninguno muestra el renglón intermedio |
| `DWEIER` | Weierstrass: extremos absolutos en `[a,b]`, con la tabla de candidatos | No existe; y además **sondea la hipótesis** de continuidad |
| `DBOLZ` | Bolzano: signos en los extremos y la raíz por **bisección** | `ZEROS` da la raíz por otro camino, no por el del teorema |
| `DWSUS` | Sustitución de Weierstrass `t = tan(x/2)` | `RISCH` sin la sustitución no puede con estas |

`DBOLZ` insiste en algo que el comando no diría: `HAY = 0` **no** significa que
no haya raíz. Bolzano es condición suficiente, no necesaria, y `X^2-1` en
`[-2,2]` tiene dos raíces con `f(a)` y `f(b)` del mismo signo. El mensaje lo
dice con todas las letras porque ése es el error típico del ejercicio.

`DWSUS` sustituye la **variable** por `2*ATAN(T)` (o sea `x = 2 arctan t`) en vez
de reemplazar `SIN(X)` y `COS(X)` por partes, que necesitaría `MATCH` con
comodines. Una sola sustitución, y el `TEXPAND` posterior hace el resto. Con
`SIMPLIFY` solo **no sustituye nada y el resultado se ve bien igual**.

**47 de 47 casos** en el emulador (`harness/casos-ruf.txt` 19,
`casos-wei.txt` 28), más 3 tandas de sondeo del CAS previas a escribirlos
(`casos-nuevos*.txt`).

Cinco más para **Parcial 1**, sacados de revisar los 42 parciales del
recopilado (fork, `MEGATXT_TODOS_LOS_PARCIALES_MATE_1.txt`). Detalle en
`SUITE-MAT1.md` §1.1:

| Programa | Qué hace | Casos |
|---|---|---|
| `DINEC` | Inecuaciones por tabla de signos, en intervalos | 25 + 5 de control |
| `DDOM` | Dominio por definición, **sin simplificar**, con las condiciones escritas; natural o con el dominio dado en el enunciado | 51 |
| `DINV` | Inversa sobre un dominio dado, con la imagen B y el aviso de no inyectiva | 26 |
| `DCONTK` | El k que hace continua una función a trozos | 21 |
| `DPAR` | Paridad; también la abstracta "F par, G impar" con representantes | 22 |
| `DASVT` | Asíntotas verticales **buscando los candidatos solo** (los puntos críticos de `DDOMC`); decide `DCONTFC` por laterales, `DASVC` queda de control | 25 |
| `DCERO` | Ceros de f, f/g, f∘g o g∘f **que están en el dominio**, sin simplificar, con los descartados a la vista | 39 |

Dos agregados del 02/10/2026, más un arreglo:

- **`DINV` daba una inversa falsa con módulo.** `'ABS(2*X-4)'` sobre R decía
  `OK`, con f⁻¹ = −(X−4)/2 e imagen (−∞, +∞): f' es `2*SIGN(2*X-4)`, `ZEROS` de
  eso da `ERROR`, y la esquina no es un cero de f'. Ahora también son
  candidatos los ceros del argumento de cada `ABS(`, y si nada aparece, un
  sondeo de 39 puntos busca un cambio de sentido (con refinamiento que descarta
  polos: `(2X+1)/(X-3)` sigue dando `OK`). 18 casos nuevos + los 26 de antes
  (`casos-dinv-abs.txt`, `casos-dinv-todo.txt`).
- `DCERO` arma f/g y las composiciones **sin `SIMPLIFY`** (al revés que
  `DOPFUN`), así `(X^2-9)/(X-3)` da el cero −3 y muestra el 3 como descartado.

`DDOM` y `DINEC` comparten un motor de cuatro objetos (`DCONDC`, `DSATC`,
`DINTC`, `DRELC`). Los dos muestran el resultado de dos maneras cuando se
puede: `R - {-3, 3}` y `(-∞, -3) U (-3, 3) U (3, +∞)`. **Este es el cálculo de dominio que §7 había descartado para
`DTROZOS`**; la decisión de §7 sigue en pie para `DTROZOS`, que solo dibuja.
Acá se hizo porque es un ejercicio de parcial, y con dos defensas contra la
salida prolija y falsa: no simplifica (el bug de `domain49`) y tiene un sondeo de
control que marca `NO CONFIABLE` cuando la tabla no coincide (probado: salta).

Parcial 2 y final, **ya con `INFORM` como el resto**: `LHOP`, `DSEP`, `DSEPI`,
`LAGR`. Estaban con entrada por pila y acá se había escrito que era "a
propósito"; era una racionalización mía, no una decisión: `SUITE-MAT1.md` decía
"falta convertir", y la entrada al final de esta sección dice que los programas
de Matemática I van con `INFORM`. Convertidos, con núcleo `XXXC` aparte.
Pruebas: `TCHK`, `TDSEP`, `TD`, `TEFUN`, `TF`.

Son **39 objetos**: 17 interfaces + 17 núcleos + 5 de prueba.

La columna TP refiere al recopilado `MEGA_TODOS_LOS_TPS (1).txt` (raíz del
repo): el temario y las resoluciones de cátedra contra las que se diseñaron.

Usan `IFERR` en todos lados para que un fallo del CAS no tire abajo el resto del
cálculo.

**Los 18 están partidos en núcleo + interfaz y probados en el emulador con ROM de
50g: 54 de 54 casos** (`casos-mat1.txt` 31 + `casos-mat1b.txt` 23). Los 13 se dividieron en `XXXC` (el cálculo, entra y sale por
pila) y `XXX` (el `INFORM` y las cajas, que llama al núcleo). El motivo es que `INFORM` es interactivo por definición y una batería no
puede tipear en un formulario: con el cálculo soldado al formulario, el harness
no podía probar **ningún** programa, y había 18 programas escritos con 0
ejecuciones. Son 31 objetos en total (13 interfaces + 13 núcleos + 5 de prueba).

Emulador **no es hardware** (§9 de `SUITE-MAT1.md`): es la ROM de la 50g, pero no
corre código ARM ni toca el teclado, la SD o la memoria real. Un verde acá es
evidencia fuerte, no es la máquina.

Documentación propia en `SUITE-MAT1.md`, que se subordina a este archivo.
Para **usar** los programas (qué pide y qué da cada uno, con ejemplos
verificados): `DICCIONARIO-MAT1.md`, el par de `DICCIONARIO-LAB.md`.

### Utilidad

| Programa | Qué hace |
|---|---|
| `SIGFIG` | Redondea a N cifras significativas. Lo usan `DOLS` y `DCOVCORR` |

**Regla de scope:** `HOME` es visible desde cualquier subcarpeta (la búsqueda de
nombres sube). Entre carpetas hermanas NO hay visibilidad.

**Con el paquete `LAB.txt` la regla deja de morder.** Todo cae en un mismo `DIR`,
y ahí los nombres se ven entre sí: cada interfaz encuentra a su núcleo y `DOLS`
encuentra a `SIGFIG`. Ya no hace falta que `SIGFIG` esté en `HOME`. Importa
porque si falta **no da error**: `DOLS` deja el nombre `'SIGFIG'` sin evaluar en
la pila y muestra un resultado equivocado. Medido en el emulador.

### Estado: partidos en núcleo + interfaz, y probados

Los 16 de esta suite siguieron el mismo camino que los de Matemática I: el
cálculo salió a un objeto `XXXC` que entra y sale por pila, y `XXX` quedó con el
`INFORM`, las cajas y los gráficos. Sin eso el harness no podía probar ninguno,
porque `INFORM` es interactivo por definición.

**120 de 120 casos** en el emulador con ROM de 50g, y contra los **datasets
reales de la cátedra**, no contra datos inventados: 78 de cálculo
(`harness/casos-lab.txt`, `casos-lab-datos.txt`, `casos-fisc.txt`) y **42 de
dibujo** (`casos-graf-histo.txt`, `casos-graf.txt`).

Los 6 casos nuevos son de **vector de enteros exactos** (§2.18), que es como un
alumno escribe los datos y daba `ERROR` en los diez núcleos que aceptan vector.

Los que dibujan quedaron en **tres capas**, no dos:

| Objeto | Qué es | Por qué aparte |
|---|---|---|
| `XXXC` | el cálculo, entra y sale por pila | `INFORM` es interactivo |
| `XXXG` | el dibujo, dibuja en `PICT` | **`PICTURE` espera una tecla** |
| `XXX` | `INFORM`, `PICTURE` y las cajas | es la parte que no se puede automatizar |

La capa del medio es lo que hace probable un gráfico: la batería llama a `XXXG`,
que dibuja y **no** abre `PICTURE`, y después mide con `PIX?` en coordenadas
reales (§2.8). Tienen `XXXG`: `DHISTO`, `DBOXPLOT`, `DCOVCORR`, `DMKT`,
`DMKTFISC` y `DCOMPFIRM`.

`DMKT` es el **único que quedó con el enfoque de coordenadas estilo píxel**
(`XRNG 0..130`, `YRNG 0..79`, escalado a mano), que es justamente lo que §2.8
recomienda no mezclar. Por eso de su dibujo solo se pueden afirmar los ejes de
referencia: todo lo demás se cruza con las diagonales de oferta y demanda y la
aserción sería ambigua. Está anotado en el código; migrarlo a rango real es
trabajo pendiente y aislado.

Dos duplicaciones eliminadas en el camino, las dos del mismo tipo que la de
`DESTFUN`/`DASHO`:

- **`DOLS` y `DCOVCORR` calculaban las mismas sumatorias por separado.** El
  comentario de `DOLS` advertía que había que mantener el **orden de las
  operaciones** idéntico para que los dos dieran el mismo número en punto
  flotante y no solo uno equivalente. Ahora `DOLSC` llama a `DCOVCORRC`: una sola
  copia, y la coincidencia es por construcción. Hay dos casos que la verifican.
- **`DHISTO` y `DFRECTABLA` tenían el mismo conteo de clases escrito dos veces.**
  `DHISTO` ahora llama a `DFRECTABLAC`. La tabla y el gráfico del mismo ejercicio
  no pueden dar clases distintas.

`DTROZOS` quedó **sin partir**: no calcula ningún resultado, solo dibuja, así que
no hay núcleo que probar. Coherente con la decisión de §7 de no invertirle más.

### Parcial 1 de Lab de Datos: 8 programas más (27/09/2026)

Pedidos para el parcial del 29/09, que es a mano y pide **los cálculos
intermedios**: varios muestran el desarrollo, no solo el resultado. Fichas en
`DICCIONARIO-LAB.md`.

| Programa | Núcleo | Qué hace | Global |
|---|---|---|---|
| `DTABLA2` | `DTABLA2C` | Tabla de desvíos, 1 o 2 variables, con fila de sumas | `TABLA2` |
| `DZLISTA` | `DZLISTAC` | z de cada dato, atípicos y z inverso | `ZTABLA` |
| `DCINCO` | `DCINCOC` | Cinco números, RIC, cercas, atípicos, asimetría | — |
| `DPCTIL2` | `DPCTIL2C` | Percentil por el método de clase y por el de Anderson | — |
| `DLOOPC` | **`DLOOPCC`** | Simula un `while` compuesto o aditivo | `LOOPT` |
| `DCHEBY` | `DCHEBYC` | Chebyshev, con k dado o sacado de [a, b] | — |
| `DPOND` | `DPONDC` | Media ponderada | — |
| `DREAL` | `DREALC` | Variación real y variaciones sucesivas | — |

**139 de 139 casos en el emulador** (fork, `harness/casos-lab2.txt`), con
todos los valores del enunciado de la tarea más bordes (0 vueltas, corte a las
500, Lp fuera de rango, largos distintos, pila limpia). **No están probados en
hardware**, y las interfaces solo se compilaron: la batería las carga (y así
un error de sintaxis se vería), pero `INFORM` no se puede correr desde ahí.

Coherencia **por construcción**, con los mismos casos que la verifican
comparando contra el programa viejo en la misma corrida:

- `DTABLA2C` saca x̄, ȳ, los desvíos, sxy y r de **`DCOVCORRC`** (o de
  `DSTATSC` con una variable) y acumula las sumas en el mismo orden, así que
  SSx/(n−1) es el mismo número que usa `DCOVCORR`. Igualdad con `==`, al bit.
- `DCINCOC` y `DPCTIL2C` piden los percentiles a **`DPCTILC`**.
- `DZLISTAC` usa `DSTATSC` para la media y s, y **`DCOMPZC`** para cada z.

**Métodos de la cátedra, leídos del material del curso** (`Desktop\labo`:
diapositivas de Cicowiez, transcripciones de clase, apunte de Excel, las dos
ediciones del Anderson). Antes se suponían; ahora hay fuente:

| Qué | Método de la cátedra | Fuente |
|---|---|---|
| Percentil | `Lp = (p/100)(n+1)`, interpolado: el de `DPCTIL` | Diapositiva Unidades 1 y 2, con `L70` de 12 precios del Big Mac = 5.4684 |
| Histograma | Sturges redondeado; ancho = R/K **redondeado para arriba**; tabla que arranca en un número redondo, clases `[a, b)` | Diapositiva "¿Calcular el tamaño del intervalo?", ejemplo Big Mac: 6.49 → 6, 0.9067 → 1, clases 1.00–1.99 … 7.00–7.99 |

Tres fuentes dicen otra cosa, y hay que saberlo para una opción múltiple:
el **apunte de Excel** de la práctica usa `CUARTIL.INC` (posición
`1 + (n−1)p`), el **Anderson 2012** en castellano usa el índice `i = np/100`, y
el **Anderson 2020** usa `(n+1)` —el del profesor—, que es `PERCENTIL.EXC`.
Con Y = `{1 4 3 5 6}` del examen intensivo, Q1 da 2 por el del profesor y 3
por los otros dos. `DPCTIL2` muestra los tres. El 22/09 el docente dijo que la
parte de estadística la toma él y que "no confundan el valor del percentil con
la posición".

Con eso se cambiaron dos programas viejos (27/09/2026):

- **`DBOXPLOTC` pasó a pedir los cuartiles a `DPCTILC`.** Antes los tomaba por
  índice, `x(⌈n/4⌉)`, y con `{1 4 3 5 6}` dibujaba Q1 = 3 y Q3 = 5 en vez de
  2 y 5.5. Ahora el gráfico, `DCINCO` y `DPCTIL` no pueden diferir. Con
  `HORAS` los dos métodos coinciden (15, 18, 22): por eso las 12 aserciones
  de píxel de `casos-graf.txt` no cambiaron.
- **`DFRECTABLAC` automático pasó a la regla de la diapositiva.** Antes el
  ancho era R/K sin redondear y arrancaba en el mínimo. Ahora `BMHIST` da las 7
  clases de la diapositiva (frecuencias 1, 11, 15, 9, 7, 1, 1) y `HORAS` da
  K=5, Ancho=5, Inicio=10. El redondeo "a la precisión adecuada" se
  implementó como **una cifra significativa para arriba**: es la lectura que
  reproduce los dos ejemplos de cátedra (0.9067 → 1 y 4.2 → 5); con dos cifras
  darían 0.91 y 4.2. Si K se fija a mano se respeta.

Las cuatro baterías viejas que tocan estos programas se volvieron a correr sin
cambiar un solo esperado: `casos-lab` 33/33, `casos-lab-datos` 25/25,
`casos-graf` 33/33, `casos-graf-histo` 9/9. `casos-graf.txt` necesitó cargar
`DPCTILC`, porque ahora `DBOXPLOTC` lo llama.

La diapositiva trae un error de tipeo: da `L50` = 4.1119, pero la cuenta que
muestra al lado, 4.091 + 0.5·(4.300 − 4.091), da **4.1955**. `DPCTIL` da 4.1955.

Cuatro detalles del camino:

- **`DLOOPC` tiene el núcleo `DLOOPCC`**, con doble C: el nombre del programa
  lo fijó la tarea y ya terminaba en C.
- **Las instrucciones de la tarea repetían la regla vieja de `FOR`** ("inicio >
  fin no ejecuta ninguna vuelta"), que §2.7 ya corrigió: ejecuta una vez. El
  único `FOR` que podía quedar vacío (`DREALC` con lista vacía) va envuelto en
  `IF`, y hay un caso que lo prueba (`re-vacia`).
- **Un campo numérico de `INFORM` sin visitar llega como `NOVAL`, no con el
  texto del segundo elemento.** Ese texto es la **ayuda** de la línea de abajo,
  no un default; el valor inicial va en el 5º argumento de `INFORM`. Es lo que
  dice el manual y explicaría la "inconsistencia conocida" de `DPIBPPA`
  (`programas/README.md`). **Medido el 02/10/2026** con `DTANOR`: OK sin tocar
  nada da `NOVAL` en la pila y `DERVX Error: Bad Argument Type`. Los programas nuevos no
  dependen de la respuesta: los formularios todo-numéricos traen valores
  iniciales (`DLOOPC` viene cargado con el ejemplo del examen), y `DZLISTAC`
  toma como 0 cualquier z objetivo que no sea un número.
- `DCHEBYC` redondea N a 9 decimales **antes** del `CEIL`: `(1 − 1/9)·9` da
  8.000000000001 y un `CEIL` directo decía 9 observaciones. Hay un caso
  (`ch-ceil`) que lo prueba.

---

## 6. Datasets de prueba (cargados como variables en la calculadora)

| Variable | Contenido | Uso |
|---|---|---|
| `BM5X` / `BM5Y` | PIB pc PPA y precio Big Mac, 5 países | Par X/Y. `r ≈ 0.9781` |
| `BMHIST` | 45 precios Big Mac | Una variable. Moda: `5.31` (frec 3) |
| `BMSCX` / `BMSCY` | PIB y precio, 46 países | Par X/Y. `r ≈ 0.7579` |
| `HORAS` | 20 valores de horas trabajadas | K=5, Ancho=5, Inicio=10 → frec `4,8,5,2,1` ⚠️ ver abajo |

Los archivos están en `programas/datos/` y entran en el paquete `LAB.txt`.

**Se pueden usar escribiendo el nombre de la variable en el campo "Datos"** en
vez de tipear la lista entera. Confirmado que funciona.

⚠️ **`HORAS` no da las frecuencias que esta tabla decía.** Acá figuraba
`2,2,6,6,4`, pero con el `datos/HORAS.txt` que tenemos, K=5 / Ancho=5 /
Inicio=10 da **`4,8,5,2,1`**. No es un problema del programa ni del criterio de
intervalo: con clases cerradas por derecha daría `6,7,4,2,1`, que tampoco es
`2,2,6,6,4`. Las dos versiones suman 20, así que son 20 datos **distintos**: o el
dataset o el número del apunte quedaron viejos. Hay que mirar el enunciado
original antes de usar este caso como verificación. Medido en el emulador;
`harness/casos-lab-datos.txt` guarda el valor real.

El resto de los valores de abajo **sí** se reprodujeron todos, exactos.

### Casos de verificación conocidos

Todos los de esta lista **están corridos** contra los datasets reales
(`harness/casos-lab-datos.txt` y `casos-fisc.txt`), salvo la nota de `HORAS` de
arriba. Dos que no estaban y ahora sí: el desvío de X que da `DCOVCORR` tiene que
ser **exactamente** el mismo que el de `DSTATS`, y su `r` el mismo que el de
`DOLS`. Antes eso era una promesa; ahora hay dos casos que lo verifican, y se
cumple por construcción porque hay una sola implementación.

- `DSTATS` con `BM5X`: Media=32172.2, sX=32930.3
- `DCOVCORR` con `BM5X`/`BM5Y`: sXY=62909.8, r=0.9781 (valores del apunte de cátedra)
- `DOLS` con `BM5X`/`BM5Y`: `Y = 1.952 + 0.0000580*X`, r=0.9781 (debe coincidir con DCOVCORR)
- `DMKT` con a=100,b=2,c=10,d=3,T=0: P*=18, Q*=64. Con T=5: P*=21, Q*=58
- `DMKTFISC` con a=100,b=2,c=10,d=3,T=5: Ps=16, Recaud=290, PIE=15, Inc 60/40, Ed=-0.7241, Es=0.8276
- `DMKTFISC` subsidio a=60,b=4,c=0,d=2,T=-3: Pb=9, Ps=12, Q*=24, Recaud=-72, PIE=6
- `DCOMPFIRM` con CF=20,b=3,c=1: P=43→Q*=20,Ben=380 | P=11→Q*=4,Ben=-4 | P=1→cierra,Ben=-20
- `DPCTIL` con `{2,4,6,8,10}`: p50→6, p70→Lp=4.2, Valor=8.4

---

## 7. Pendientes

### Programas no hechos (priorizados)

1. **Modelo macro simple** — `Y=C+I+G` con `C=a+b(Y-T)`; ingreso de equilibrio y
   multiplicador. Cierra el último hueco explícito de la Unidad 6 del programa.
2. **Monopolio** — demanda lineal + costos, resolver por `IMg=CMg`. Es el patrón
   más repetido en el TP6 de Micro.
3. **Utilidad Cobb-Douglas** — `U=X^a·Y^b` con restricción presupuestaria.
4. Elasticidad arco (entre dos puntos arbitrarios), números índice,
   interpolación lineal. Para la interpolación ya hay fuente legible de terceros
   (fork, `analisis/calcnum/fuentes/Interpolacao-Lagrange-Unidimensional.txt`).
5. **`DAJUSTE` — ajuste no lineal por linealización.** Es el único hueco de
   materia que apareció revisando los programas de terceros: `DOLS` hace la recta
   y nada más. Exponencial (`Y=A·e^(bX)`), potencial (`Y=A·X^b`), logarítmica y
   parábola, **mostrando las sumatorias** (ΣX, ΣY, ΣX², ΣX³, ΣX⁴, ΣXY, ΣX²Y,
   ΣLNX, ΣLNY), que es como lo pide la cátedra. Dos fuentes para copiar, las dos
   en el fork: `ajustedecurvas` descompilado y el `.hpe`
   `Ajuste-de-Funcoes-Regressao-com-Funcoes-Linearizaveis`.
6. **Matemática I** (cátedra Barraza): EDO separables, estudio de función,
   multiplicadores de Lagrange. — **Escritos, sin probar.** Los tres están
   cubiertos (`DSEP`/`DSEPI`, `DESTFUN`/`DASHO`, `LAGR`) junto con otros 13
   objetos. Lo que falta ahora es probarlos en la calculadora, no escribirlos.
   Ver `SUITE-MAT1.md`. Quedan sin escribir `AREA` (área entre curvas) e `IMPR`
   (integral impropia); para los dos hay ahora **dos caminos** en vez de uno:
   `\.S` como integral definida de fábrica (§2.1) y, cuando `RISCH` no puede,
   Simpson o Romberg, con fuente legible en el fork
   (`analisis/calcnum/fuentes/`).

### Mejoras pendientes

- Probar el camino nativo `DRAX/DRAW/LABEL` (sección 2.9) — simplificaría todos
  los gráficos y permitiría rotular ejes. Ya hay código de terceros que lo usa
  en producción (`Graf/GRAF.txt`); falta correrlo acá.
- **Probar la traducción de escapes de Conn4x.** Es lo único que falta para
  cerrar tres cosas de golpe (§2.1): el infinito en el fuente (y con eso se van
  `DINF` y el global `INF`), `\>=`/`\<=` en vez del rodeo `< NOT`, y `\.S` para
  `AREA`/`IMPR`. Los tres **ya funcionan en la máquina**; lo que falta es que
  las grafías `\oo`, `\>=`, `\<=`, `\.S` de un archivo de texto lleguen como los
  caracteres 159, 138, 137 y 132. Se prueba con un archivo de una línea:
  transferir `\<< \oo DUP TYPE \>>` y correrlo — tiene que dar **9**, no 6.
- **`SIMPLIFY` borra las discontinuidades evitables — revisar `DOPFUN`.** Medido
  probando `domain49` (fork, `analisis/domain49/CASOS-PROBADOS.md`): en la 50g,
  `'(X-3)/(X^2-9)' SIMPLIFY` da `'1/(X+3)'`, y con eso desaparece que `X=3` no
  pertenece al dominio. `DOPFUN` hace exactamente `F G / SIMPLIFY` para el
  cociente (línea 50), que es el caso del TP 4: muestra `f/g` ya cancelada, y el
  punto que la cátedra quiere ver excluido no se ve. Lo mismo vale para el
  `EXPAND SIMPLIFY` de `DESTFUN`. Al menos avisar en la caja de que el dominio se
  calcula **antes** de simplificar; idealmente mostrar las dos formas.
  **Hecho el aviso**: `DOPFUN` muestra una caja extra después del cociente.
  Queda pendiente lo de mostrar las dos formas.

- ~~**Arreglar los `IFERR` que dejan basura**~~ (§2.11). **Hecho en los 13
  núcleos `XXXC`**, que cierran con el guardián de profundidad y devuelven
  exactamente una lista. `DSEPC` y `DSEPIC` —el caso peor, los que podían
  devolver una respuesta equivocada sin avisar— tienen cuatro casos que lo
  verifican: `DEPTH` antes y después tiene que dar 0 incluso cuando algo falla
  por dentro.
- ~~**Correr el harness.**~~ **Hecho, y ahora prueba la suite y no solo el
  lenguaje.** `harness/armar-mat1.py` genera una batería que **se lleva puestos
  los programas**: emite `\<< ...cuerpo del .txt... \>> 'NOMBRE' STO` por cada
  objeto y después corre los casos, así la corrida es reproducible desde cero y
  no hereda una versión vieja residente (el bug de §3.5). Resultado: **54 de 54**
  (`casos-mat1.txt` 31 + `casos-mat1b.txt` 23). Lo viejo, que probaba comandos
  sueltos de la máquina, sigue en `casos.txt`. Descripción original:
  una tabla de casos, un programa `BATERIA` generado, y el resultado que vuelve
  por `DDE48 r` como objeto y se compara en la PC. Corre sobre el `Emu48` de **Debug4x**, que
  emula la 50g de verdad con la ROM `ROMG+.50G` autorizada por HP, no una 49G con
  carátula. Falta correrlo: el viaje de ida y vuelta por DDE no está probado.
  Prueba la capa de cálculo, no los formularios. Detalle en `analisis/REVISION.md`
  §3 y §6; corrige `SUITE-MAT1.md` §9.
- Meter `RCLF`/`STOF` (2.9d) para guardar y restaurar el estado de la máquina.
  Ningún programa de la suite toca flags hoy, y Mat1 necesita modo exacto. Ya no
  hace falta evaluar `NOFORMAT`: está descompilado y `RCLF`/`STOF` es mejor.
- **Leer los 52 fuentes UserRPL de `calcnum`** (fork,
  `analisis/calcnum/fuentes/`) antes de escribir `AREA` e `IMPR`: hay Trapecio,
  Simpson y Romberg en fuente legible, más Newton-Raphson y bisección como red
  numérica para cuando `ZEROS` no puede. También regresión múltiple y ajustes
  linealizables, que le faltan a `DOLS`.
- **Una sola compuerta.** Hoy hay cinco scripts sueltos (`verificar.ps1`,
  `armar-mat1.ps1`, `armar-bateria.ps1`, `armar-mat1.py`, `correr-emu.ps1`) y
  ninguno es *el* comando que dice sí o no. Debería haber un `probar-todo.ps1`
  que encadene: `verificar.ps1` sobre los 39 fuentes + compilar los 39 con
  `compilar.py` (que "¿compila?" ahora es una pregunta que se le puede hacer a
  la máquina, y es mucho más fuerte que las heurísticas de conteo) +
  `oraculo.py` + las dos baterías, y salga 0 o 1. Es la regla que el otro
  proyecto del mismo autor ya tiene con `verify.sh`.
- ~~**Partir también los programas de Lab de Datos.**~~ **Hecho: 72 de 72**
  (§5). Quedó afuera `DTROZOS`, que no calcula nada, solo dibuja.
- **Verificar el enunciado de `HORAS`** (§6): el dataset y la frecuencia
  documentada no coinciden, y uno de los dos está mal.
- ~~**Probar las salidas GRÁFICAS.**~~ **Hecho: 42 aserciones de píxel** sobre
  `DHISTO`, `DBOXPLOT`, `DCOVCORR`, `DMKT`, `DMKTFISC` y `DCOMPFIRM` (§2.8 y
  §5), más el volcado en ASCII para mirarlos. Queda afuera `DTROZOS`, que no se
  partió.
- **Migrar `DMKT` a coordenadas reales** (§5): es el único gráfico que sigue
  escalando a píxel a mano, y por eso es el único cuyo dibujo no se puede
  afirmar más allá de los ejes.
- Alinear columnas de salida con padding de espacios donde se use texto.
- `DTROZOS` no tiene protección contra asíntotas/discontinuidades dentro de un
  tramo (ej. `1/X` con un tramo que cruce 0) — va a fallar o dar resultados sin
  sentido. **La técnica de 2.9a no arregla esto**: sortea el dominio, no las
  asíntotas, porque un valor enorme sigue siendo un número real.

### Decisiones tomadas (no re-litigar)

- **No** calcular dominio/imagen automáticamente en `DTROZOS`: requiere
  matemática simbólica frágil, y el "dominio" resultante sería solo la ventana
  elegida, no el dominio matemático real. Se descartó a propósito.
- **No** parsear condiciones completas tipo `"si x < 2"`: implicaría un
  mini-parser de texto, demasiado frágil. Se optó por campos separados.
- Los gráficos usan la orientación de libro de texto donde corresponde
  (`DMKTFISC`: Precio vertical, Cantidad horizontal).
- **No** reescribir `DTROZOS`. `PCWYZ` (en `Graf/`) ya hace funciones a trozos
  mejor: autoescala la ventana, grafica todos los tramos de una con `DRAW`, y
  resuelve el dominio con el truco de `'\v/-ABS(X)'` en vez de un bucle de
  `LINE`. Invertir en `DTROZOS` sería reescribir algo que ya existe y anda.
  `DTROZOS` queda como está, sin más trabajo encima.
- **Los programas de Matemática I van con el mismo estilo que los de Lab de
  Datos**: entrada por `INFORM` desde la calculadora (nunca editando el código),
  salida por `MSGBOX`, y prefijo `D` en el nombre. Se descartó la interfaz por
  pila que tenían las primeras versiones. Cuando el resultado es una expresión
  que no entra en una caja de 2 líneas, va igual al `MSGBOX` **y** queda en la
  pila para poder leerla entera.

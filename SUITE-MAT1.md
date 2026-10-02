# Suite RPL — Matemática I (HP 50g)

Extensión de la suite a Matemática I (cátedra Barraza). Cubre el ítem 5 de
"Programas no hechos" de CLAUDE.md §7.

**CLAUDE.md manda.** Este archivo no repite sus reglas ni las contradice: solo
agrega lo propio de Mat1 (trabajo simbólico con el CAS, que el resto de la suite
no usa) y registra las decisiones que Mat1 obligó a tomar. Ante cualquier
diferencia entre este documento y CLAUDE.md, vale CLAUDE.md.

Formato de archivo, transferencia por Conn4x, reglas de UserRPL y flujo de
trabajo: CLAUDE.md §1, §2 y §3. No están duplicadas acá a propósito.

---

## 1. Estado real

**Los 18 están probados en el emulador con ROM de 50g: 44 de 44 casos.**
`TCHK`, `DINF`, `DASHO`, `DCONT` y `DESTFUN` además se corrieron en la máquina
real (§2), y entre ellos destaparon el bug de fondo con el infinito.

Para poder probarlos hubo que **partir cada programa con formulario en dos**:
`XXXC` es el cálculo (entra y sale por pila) y `XXX` es el `INFORM` con las
cajas, que llama al núcleo. Antes el cálculo estaba soldado al formulario, y
como `INFORM` es interactivo por definición, el harness no podía probar
**ninguno**: 18 programas escritos con 0 ejecuciones. Son 27 objetos ahora
(18 + 9 núcleos).

**Emulador no es hardware** (§9): es la ROM de la 50g, pero no corre código ARM
ni toca teclado, SD o memoria real. Un verde acá es evidencia fuerte y no es la
máquina. Los 27 archivos siguen pasando `verificar.ps1`, que chequea estructura,
no semántica.

**Antes de usar nada: correr `DINF` una vez** (§2). `DASHO` y `DESTFUN` no
funcionan sin el global `INF`; los dos lo avisan con una caja si falta. `DCONT`
**ya no lo necesita**: su punto de corte es finito y el infinito lo detecta por
el carácter (§2).

Los archivos viven en `programas/mat1/`. `programas/MAT1.txt` es la salida
generada para transferir (ver §3).

| Programa | Para | TP | Interfaz | Estado |
|---|---|---|---|---|
| `TCHK` | — | — | pila | **4 de 4**. El chequeo del ∞ usaba `\.oo` y daba por bueno un `'1/\.oo'` sin evaluar; ahora va por `INF` |
| `DOPFUN` | Parcial 1 | TP 4 | INFORM + `DOPFUNC` | **4 de 4**. Avisa que el cociente sale simplificado |
| `DCONT` | Parcial 1 | TP 7 | INFORM + `DCONTC` | **6 de 6** (continua, salto, evitable, esencial por los dos lados, corte negativo). Laterales con signo. No requiere `INF` |
| `DCONTF` | Parcial 1 | TP 9 | INFORM + `DCONTFC` | **22 de 22** en el emulador (`harness/casos-dcontf.txt`). Una sola f(X), no a trozos. Laterales de verdad. No requiere `INF` |
| `DASHO` | Parcial 1 | TP 8 | INFORM + `DASHOC` | **4 de 4**. Ahora distingue *m* infinita de "el CAS no pudo". Requiere `INF` |
| `DASV` | Parcial 1 | TP 8 | INFORM + `DASVC` | **4 de 4** (polo simple, polo doble, acotada) |
| `DDEF` | Parcial 1 | TP 9 | INFORM + `DDEFC` | **3 de 3** (simbólica y en un punto) |
| `DTANOR` | Parcial 1 | TP 9 | INFORM + `DTANORC` | **4 de 4**, incluida la normal vertical con f'(x0)=0 |
| `DESTFUN` | Parcial 1 y 2 | TP 8+ | INFORM + `DESTFUNC` | **4 de 4**. Las asíntotas las calcula `DASHOC`, ya no una copia. Requiere `INF` |
| `DVFG` | Parcial 1 | TP 0/1 | INFORM + `DVFGC` | **2 de 2** (simplificación buena y mala) |
| `DDOMP` | Parcial 1 | TP 1 | INFORM + `DDOMPC` | **2 de 2**. Contaba √(-1) como dentro del dominio con modo Complex; arreglado por tipo |
| `LHOP` | Parcial 2 y final | — | INFORM + `LHOPC` | **3 de 3** (0/0 y ∞/∞) |
| `DSEP` / `DSEPI` | Final | — | INFORM + `DSEPC`/`DSEPIC` | **8 de 8**. Con guardián de profundidad, y ahora avisan cuando `RISCH` deja la integral sin resolver (§2.17) |
| `LAGR` | Final | — | INFORM + `LAGRC` | **1 de 1**: arma bien el lagrangiano |
| `TDSEP` `TD` `TEFUN` `TF` | pruebas | — | pila | **5 de 5**: 7 y 8 casos, y los accesores devuelven lo que dicen |
| `DDOM` | Parcial 1 | — | INFORM + `DDOMC` | **51 de 51**. Dominio por definición, sin simplificar, natural o con el dominio dado en el enunciado (§1.1) |
| `DINEC` | Parcial 1 | — | INFORM + `DINECC` | **25 de 25** + 5 de control + 12 de dobles (`1<X<2`, 02/10/2026). Inecuaciones por tabla de signos |
| `DINV` | Parcial 1 | — | INFORM + `DINVC` | **44 de 44**. Inversa sobre un dominio dado, con la imagen B. Desde el 02/10/2026 ve la esquina del módulo (antes daba una inversa falsa de \|2X−4\| sobre R) |
| `DCONTK` | Parcial 1 | — | INFORM + `DCONTKC` | **21 de 21**. El k que hace continua una función a trozos |
| `DPAR` | Parcial 1 | — | INFORM + `DPARC` | **22 de 22**. Paridad concreta y la abstracta "F par, G impar" |
| `DASVT` | Parcial 1 | TP 8 | INFORM + `DASVTC` | **25 de 25**. Asíntotas verticales **buscando los candidatos solo** (02/10/2026) |
| `DCERO` | Parcial 1 | TP 4 | INFORM + `DCEROC` | **39 de 39**. Ceros de f, f/g, f∘g o g∘f **dentro del dominio**, sin simplificar (02/10/2026) |
| `DCONDC` `DSATC` `DINTC` `DRELC` | motor | — | pila | lo usan `DDOMC` y `DINECC`; probados por dentro de esos dos |

Parcial 1 está cubierto entero y ya en el estilo de la suite. `LHOP`, `DSEP`,
`DSEPI` y `LAGR` **también**: se convirtieron a `INFORM` + núcleo `XXXC`. Acá
había dicho antes que quedaban por pila "a propósito", y no era cierto — este
mismo archivo decía "falta convertir", y `CLAUDE.md` tiene la decisión tomada de
que todo Matemática I va con formulario. Los 13 programas abren formulario; los
únicos objetos que entran por pila son los 5 de prueba y los 13 núcleos, que no
los usa el alumno.

Dos programas desaparecieron en el camino, y no por error:

- **`EFASI` → `DASHO`.** Mismo cálculo, renombrado al prefijo `D` y pasado a
  `INFORM`. `DASV` (vertical) y `DASHO` (horizontal y oblicua) ahora hacen par.
- **`EFEST` se absorbió en `DESTFUN`.** Hacía f', ceros, f'' y ceros; `DESTFUN`
  hace eso más las asíntotas, con formulario. Tener los dos era duplicar.

La columna TP refiere al recopilado `MEGA_TODOS_LOS_TPS (1).txt`.

Pendientes de escribir: `AREA` (área entre curvas) e `IMPR` (integral impropia),
ambos del bloque de Parcial 2. Ver §6.

---


### 1.1 Los cinco de Parcial 1 que salieron de los parciales (2026-09-23)

Salieron de revisar los 42 exámenes de `MEGATXT_TODOS_LOS_PARCIALES_MATE_1.txt`
(fork): son los tipos de ejercicio de Parcial 1 que se repiten y que la suite no
cubría. Por frecuencia: inecuaciones (casi siempre el ejercicio 1), dominio
natural (f/g, g∘f "por definición"), inversa con B, el k de continuidad y
paridad.

**`DDOM` / `DINEC` comparten un motor de tres objetos:**

| Objeto | Qué hace |
|---|---|
| `DCONDC` | recorre el árbol **tal como se escribió** y junta las condiciones: denominador ≠ 0, radicando ≥ 0, argumento de `LN`/`LOG` > 0, potencia con X en el exponente → base > 0, exponente fraccionario de denominador par, `ASIN`/`ACOS`, `TAN` |
| `DSATC` | ¿un punto cumple todas las condiciones? Complejo, error o 9.99E499 cuentan como "no" (§2.14, §2.19) |
| `DINTC` | tabla de signos: puntos críticos con `ZEROS`, un punto de prueba por tramo, cada punto crítico evaluado **exacto** (de ahí el corchete o el paréntesis), y el texto en intervalos |

El recorrido es el de `domain49` (pila con `{ }` de centinela, `OBJ\->`), pero
sin su bug: `domain49` simplifica antes de buscar polos y `(X-3)/(X^2-9)` le da
`R - {-3}`. `DDOM` da `R - {-3, 3}`. Por eso **la expresión se escribe sin
simplificar**, y una composición se escribe ya compuesta (`'LN(X+2)'`).

**Dos escrituras del mismo conjunto.** `DINTC` arma el texto dos veces: con
intervalos puros y salteando los *huecos* (un punto que falta con los dos
tramos vecinos adentro), que van aparte con `- {…}`. La interfaz muestra la
principal y, en otra caja, "O bien:" la otra:

| Principal | O bien |
|---|---|
| `R - {-3, 3}` | `(-∞, -3) U (-3, 3) U (3, +∞)` |
| `(1, 3) U (3, +∞)` | `(1, +∞) - {3}` |
| `[-2, 2]` | — (no hay huecos) |

**Dominio dado en el enunciado** (`DDOM`, interruptor en el formulario). Hay
ejercicios que dan el dominio de cada función (2024 T2: f: [−3, 4], g: [−1, 7],
dominio de f/g). El núcleo recibe `'F' RES`: `RES = 0` es el dominio natural;
`{ a b }` es [a, b]; `{ { a b } { c d } }` es uno por función; `'X>0'` (o una
lista de desigualdades) sirve para los abiertos o infinitos; un extremo `INF`
no pone condición. Cada restricción entra como una condición más del mismo
sistema, así que la intersección con el dominio natural sale sola y con los
corchetes decididos igual que el resto: el 2024 T2 da `(-1, 4]`. Las
restricciones aparecen en la lista de condiciones como `Dado: X ≥ -3`. El paso
de desigualdad a condición está en `DRELC`, que comparten `DDOMC` y `DINECC`.

**Control por sondeo.** `DINTC` evalúa 31 puntos y los compara contra la tabla.
Si `ZEROS` se salteó un punto crítico, la tabla miente callada. Medido:
`'X^5-X-1>0'` daba `VACIO` y `'EXP(X)-3*X>0'` daba `R`, las dos falsas y
prolijas. Con el control, el texto sale como `NO CONFIABLE: ...` y el aviso dice
dónde no coincide (`casos-dinec-control.txt`, 4 de 4). O sea: un resultado sin
prefijo pasó la tabla **y** el sondeo.

**Límites conocidos.** Funciones periódicas en condiciones (`TAN`, trig en un
denominador) salen con aviso "Periodica: no soportado". Con dos `ABS` distintos
funciona porque `ZEROS` los resuelve con Complex apagado, pero no se probó más
allá de eso.

`DINV`: SOLVE `'Y=f'`, se queda con la rama que devuelve f(x0) a x0, la imagen
desde los extremos (o límites laterales/al infinito, abiertos) y detecta la no
inyectividad por los ceros de f' donde f da la vuelta (`X^3` no cuenta).
`DCONTK`: laterales `'X=a-0'`/`'X=a+0'` con el parámetro adentro, `SOLVE`, y cada
K verificado sustituyéndolo. `DPAR`: f(−p) contra ±f(p) en siete puntos
(incluidos enteros, donde suelen estar los huecos del dominio) y dominio
simétrico; el modo abstracto define F y G con representantes (`DEFINE`), no pisa
una F o G del usuario y las purga al final.

**Probado en el emulador (ROM 50g), no en hardware. Las interfaces `INFORM` no
se probaron**: ninguna batería puede tipear en un formulario (§9).

---

## 2. Cimientos: lo que se probó en la máquina

`TCHK` se corre sin argumentos y deja 4 resultados. **Ya se corrió.** Resultado:

| Nivel | Prueba | Esperado | Obtenido |
|---|---|---|---|
| 4 | `'X' 2 =` | `'X=2'` | ✅ correcto |
| 3 | `'X^2' 'X' RISCH` | `'X^3/3'` | ✅ `(1/3)*X^3` |
| 2 | `'1/X' 'X=\.oo' LIMIT EVAL` | `0` | ❌ **`1/\.oo`** |
| 1 | `'X^2' 'X' DERIV` | `'2*X'` | ✅ `2*X` |

De paso quedaron confirmadas tres cosas más:

- **`\.oo` transfiere y compila.** El objeto llega como programa, no como string
  inerte. (Pero produce el objeto equivocado — ver "Causa, confirmada" abajo.)
- **El paquete de un solo `DIR` transfiere bien.** El riesgo que se había
  anotado — que un escape malo tumbara la carga de los 18 objetos de una — no se
  materializó.
- **`X` mayúscula es la variable correcta del CAS.** Se había sospechado que
  `VX` fuera `x` minúscula; la pantalla muestra `X`.

### El problema abierto: `LIMIT` con infinito

`LIMIT` **sustituye en vez de calcular** cuando el punto es ∞: mete `X=\.oo`
dentro de `1/X` y devuelve `1/\.oo`. No da error, da la expresión sin reducir.

No es un problema de `LIMIT` en general ni de la firma ni de la variable: probado
a mano en la máquina, `'X^2' 'X=2' LIMIT` da `4`.

Afectaba a **`DASHO`, `DESTFUN` y `DCONT`**, los tres que dependen de límites al
infinito. Los otros seis de Parcial 1 no lo tocan. **Ya está arreglado** — ver
"El arreglo" más abajo.

`programas/TLIM.txt` (temporal) probó las tres hipótesis obvias. **Las tres
fallaron:**

| Prueba | Resultado |
|---|---|
| `'1/X' 'X=+\.oo' LIMIT` (signo explícito) | `1/\.oo` |
| `'1/X' 'X=-\.oo' LIMIT` | `-1/\.oo` |
| `LIMIT` + `EVAL` + `SIMPLIFY` | `1/\.oo` |
| `1 \.oo / EVAL` (aritmética pura) | `1/\.oo` |
| m de una oblicua real | `(\.oo^2+1)/\.oo^2` |
| b de esa oblicua | `1/\.oo` |

La línea que manda es la cuarta: **`1/∞` queda inerte sin que `LIMIT` intervenga
siquiera**. Si `\.oo` fuera la constante de infinito del CAS, en modo exacto eso
colapsaría a `0` solo.

### Causa, confirmada

`TLIM2` lo cerró comparando tipos:

| Objeto | `TYPE` |
|---|---|
| El que produce el escape `\.oo` | **6** = nombre global |
| El ∞ tipeado desde el teclado | **9** = algebraico |

**Son objetos distintos.** El escape produce un **nombre global** que solo se
*dibuja* como ∞; el infinito de verdad del CAS es un **algebraico**. `LIMIT`
sustituía porque recibía un identificador cualquiera.

Esto corrige lo anotado en CLAUDE.md §2.1: `\.oo` transfiere y compila, sí, pero
**no produce la constante de infinito**. No sirve para trabajo de CAS.

### El arreglo

La raíz es que el archivo de transferencia debe ser ASCII puro de 7 bits
(CLAUDE.md §1), así que el carácter ∞ no puede viajar dentro del fuente. Hay que
capturarlo en la máquina.

`programas/DINF.txt`: se le pone el ∞ **del teclado** en el nivel 1 y guarda
el objeto real en el global **`INF`** (va en `HOME`, por la regla de scope de
CLAUDE.md §5). Además informa el `TYPE` y el código de carácter del objeto capturado y corre
una prueba real de `LIMIT`, así se ve en el acto si el arreglo funciona.

**El infinito entra por la pila, no por `INFORM`.** Pasarlo por un campo de
texto obligaría a un `STR\->` que lo devolvería como nombre (`TYPE` 6) — justo
el objeto equivocado. Por la pila llega intacto. Es la única excepción al estilo
de formularios de §4, y tiene motivo técnico.

**Confirmado en la máquina.** `DINF` devolvió `TYPE` 9 y, sobre todo, su prueba
de `LIMIT` dio **`0`**. El mecanismo funciona.

**Aplicado** a `DASHO` y `DESTFUN`: pasaron de `'X=\.oo'` a construir la ecuación
en tiempo de ejecución con `'X' INF =` y `'X' INF NEG =`. Los dos abren con una
guarda `IF INF TYPE 9 == NOT` que avisa "Correr DINF primero" en vez de fallar en
silencio — que era el riesgo real, porque un `INF` inexistente se recallaría como
nombre y `LIMIT` volvería a sustituir sin quejarse.

`DCONT` también tenía esa guarda, y se la saqué: nunca calculó un límite en el
infinito (su punto de corte es finito), solo lo usaba para *reconocer* un límite
infinito, y eso ahora se hace de otra manera. Ver abajo.

**Confirmado en `DASHO`**, con `'(X^2+1)/X'`: devuelve la recta oblicua correcta.
`LIMIT` calcula en vez de sustituir.

`TLIM` y `TLIM2` ya cumplieron su función: **se pueden borrar**, de la carpeta y
de la calculadora.

### `+∞` no es `∞`: cómo se reconoce un límite infinito

Segundo bug del infinito, y este apareció **corriendo `DCONT` en la máquina**:
con rama izquierda `'1/X'`, rama derecha `'X'` y corte `0`, las cajas mostraron
`lím izq +∞` y `lím der 0` (los límites, bien) pero el veredicto salió
**"SALTO FINITO"** en vez de "ESENCIAL".

La causa estaba anticipada en §10: `LIMIT` devuelve `+∞` —con el signo, que es
como la calculadora lo escribe sola— y `DINF` guarda el `∞` pelado, así que las
cuatro comparaciones `SAME` daban falso:

```
IF LI INF SAME LI INF NEG SAME OR LD INF SAME OR LD INF NEG SAME OR   @ frágil
```

Comparar objetos enteros obliga a enumerar todas las formas que el CAS puede
devolver (`∞`, `+∞`, `-∞`, `2*∞`, …). **La detección va por el carácter**, que es
el mismo en todas:

```
LI \->STR 159 CHR POS LD \->STR 159 CHR POS + 'ES' STO
```

`POS` devuelve 0 si no lo encuentra, así que la suma > 0 significa "alguno de los
dos límites es infinito". El 159 es el código medido con `DINF` (abajo). Ventaja
lateral: `DCONT` dejó de depender del global `INF`.

Detrás va una red de seguridad, por si el CAS devolvió un número gigante en vez
del símbolo:

```
IFERR
  LI \->NUM ABS LD \->NUM ABS MAX 1000000000 >
  IF THEN 1 'ES' STO END
THEN
END
```

Todo adentro del `IFERR` a propósito: con un operando simbólico el `>` puede no
devolver un flag usable y el `IF` reventaría.

El mismo chequeo se agregó a las dos cajas de asíntotas de `DESTFUN`, que antes
informaban "OBLICUA m = ∞" para una cúbica. **Sin probar todavía en hardware.**

### Pendiente: sacarse la dependencia de encima

**El código de ∞ es 159.** Medido con `DINF` corregido.

Dos trampas en esa medición, las dos ya pisadas:

- La primera lectura dio **39**, el apóstrofo: `\->STR` sobre un algebraico
  devuelve `"'∞'"` **con** las comillas, así que el carácter 1 no sirve. `DINF`
  lee el carácter 2.
- La segunda dio **43**, el signo `+`: **la calculadora escribe `+∞`
  automáticamente** al tipear el símbolo. Hay que borrar el `+` a mano para
  quedarse con el ∞ pelado.

Ese segundo detalle importa más allá de la medición: significa que `+∞` y `∞`
son dos objetos distintos, y cualquier `SAME` contra `INF` falla si el CAS
devolvió la forma con signo. Es exactamente lo que pasó en `DCONT` (arriba).

Con 159 se puede reemplazar el global por algo autocontenido y ASCII puro:

```
"'" 159 CHR + "'" + STR\->
```

Las comillas van a propósito: compilar el ∞ pelado daría un **nombre** (`TYPE`
6), que es el objeto equivocado; envuelto en tildes da el **algebraico**
(`TYPE` 9), que es el que `LIMIT` entiende. **Sin probar todavía** — `INF` sigue
siendo la forma soportada hasta que esa línea se verifique en la máquina.

Lo que sí está en producción con el 159 es la mitad **fácil**: reconocer un ∞ que
ya existe, buscando el carácter dentro del `\->STR` (arriba). Eso no necesita
construir nada. Lo que falta verificar es lo otro, fabricar el objeto ∞ desde
cero para pasárselo a `LIMIT`.

### Los otros cimientos

`=` lo usan `DCONT`, `DDEF`, `DTANOR`, `DASV`, `DOPFUN`, `DESTFUN`, `DSEP`,
`DSEPI` y `LAGR`. `RISCH` lo usan `DSEP` y `DSEPI`. `DERIV` lo usa `LAGR`.
Los tres confirmados.

**El escape `\.d` (derivada parcial) no se usa.** `LAGR` arma las parciales con
`DERIV`, que es comando de fábrica y no depende de ningún escape sin confirmar.

---

## 3. Decisión de empaquetado: un solo `DIR`

`TD` y `TF` referencian `TDSEP` y `TEFUN` por nombre global. CLAUDE.md §5 es
claro: **entre carpetas hermanas no hay visibilidad**. Si cada `.txt` viajara con
su propio envoltorio `DIR`, cada uno caería como subcarpeta hermana y los helpers
quedarían invisibles.

Resolución:

- `programas/mat1/*.txt` son **objetos sueltos, sin envoltorio `DIR`**. Son la
  fuente de verdad para editar (CLAUDE.md §3.2) y lo que se pasa por
  `verificar.ps1`.
- `programas/armar-mat1.ps1` los empaqueta en **un único `programas/MAT1.txt`**
  con un solo `DIR`. Una transferencia, una subcarpeta, todos los nombres
  visibles entre sí.
- **`MAT1.txt` es salida generada. No editarlo a mano.** Editar el archivo suelto
  y volver a correr el empaquetador.

```powershell
.\verificar.ps1 .\programas\mat1\*.txt     # la fuente
.\armar-mat1.ps1                           # genera programas\MAT1.txt
```

El empaquetador ya emite CRLF y ASCII puro, así que `MAT1.txt` no necesita pasar
por `a-crlf.ps1`.

---

## 4. Decisiones de diseño (no re-litigar)

- **Interfaz `INFORM`/`MSGBOX`, igual que el resto de la suite.** Prefijo `D` en
  el nombre. La primera versión usaba la pila, con el argumento de que Mat1
  maneja expresiones y no números; se descartó. Los programas se usan en un
  parcial, y ahí no se edita código ni se arma la pila a mano: se abre el
  programa y se completan campos.
  Aplican CLAUDE.md §2.4 (patrón semilla en la concatenación), §2.5 (máximo ~4
  campos, default no vacío, orden de `OBJ\-> DROP`) y §2.6 (máximo 2 líneas por
  caja, sin encabezado decorativo).
  **Falta convertir** `LHOP`, `DSEP`, `DSEPI` y `LAGR`, todos de Parcial 2 y
  final.

- **Cuando el resultado no entra en una caja, va al `MSGBOX` igual y además
  queda en la pila.** Una recta tangente o un cociente incremental pueden ser
  largos, y `MSGBOX` no hace scroll. La caja sirve para leer el resultado de un
  vistazo; la pila para verlo entero y para seguir operando con él. Cada
  programa dice en su comentario qué deja y en qué nivel.

- **Los campos de expresión llevan el salvaguarda de CLAUDE.md §2.10**
  (`IF DUP TYPE 2 == THEN STR\-> END`), por si el campo devuelve un string en
  vez de un algebraico ya interpretado.

- **`DSEPI` no usa `STO`/`PURGE` sobre los globales `X` e `Y`.** Calcula la
  constante con `SUBST`. Guardar en los globales pisaba lo que el usuario tuviera
  ahí; y si un `IFERR` saltaba en el medio, el `PURGE` no llegaba a correr y el
  global quedaba contaminado en silencio.

- **`DVFG` y `DDOMP` sí usan el global `X`**, porque necesitan evaluar en un bucle
  y no hay alternativa limpia. Los dos purgan `X` dentro de un `IFERR` al final.
  Es el punto más frágil que queda.

- **`DASV` sondea numéricamente en vez de pedir límites laterales.** La sintaxis
  `'X=a-'` no se puede construir desde la pila. Evalúa en `a ± 0.000001` y compara
  contra 1e6. Es una heurística, no una demostración.

- **`DCONT` usa límites laterales de verdad**: la rama izquierda en `'X=a-0'`,
  la derecha en `'X=a+0'`. Antes usaba el límite ordinario, con el argumento de
  que cada rama es una función común; pero cuando la rama revienta en el corte
  —el caso interesante— el ordinario devolvía el ∞ sin signo (ver §5).

- **`LAGR` no clasifica los puntos críticos.** Los exámenes modelo nunca lo
  piden, así que no arma el hessiano orlado.

- **`DSEP` no separa la ecuación.** La separación algebraica es justo lo que el
  profesor quiere ver escrito, y automatizarla en RPL no termina nunca. Se entra
  con `M(Y)` y `N(X)` ya separadas.

- **`DDEF` devuelve el cociente incremental sin simplificar** además del límite,
  porque eso es lo que hay que copiar a la hoja.

---

## 5. Riesgos abiertos

- ~~`CONT` puede chocar con el comando de fábrica del mismo nombre~~
  **Resuelto:** se llama `DCONT`. El renombre al prefijo `D` alcanzó, y de paso
  alineó el nombre con el resto de la suite (CLAUDE.md §5).

- **Modo exacto vs. gráficos.** Mat1 necesita modo **exacto** y **Complex
  apagado** (si no, la raíz de un negativo devuelve un complejo y `DDOMP` da por
  bueno un punto que no lo es). CLAUDE.md §2.7 dice lo contrario para gráficos:
  literales con punto decimal y `\->NUM` antes de usar un valor como coordenada,
  porque las fracciones exactas dan "BAD ARGUMENT TYPE".
  **Regla de frontera:** exacto adentro, `\->NUM` al salir hacia `PICT`. Todavía
  no choca porque ningún programa de Mat1 grafica; `AREA` va a ser el primero.

- **Los modos son estado global de la máquina.** Ningún programa de la suite (ni
  de Mat1 ni de los otros 16) fija ni restaura flags. Si se pasa a modo exacto
  para Mat1 y después se corre `DMKTFISC`, el gráfico puede fallar.

- **`LAGR` asume que `X`, `Y` y `LM` no tienen valor.** Purgarlos antes.

- ⚠️ **`IFERR` no limpia la pila** (CLAUDE.md §2.11, medido en el emulador). En
  la forma que usa toda la suite —`IFERR ARG1 ARG2 COMANDO THEN "FALLO" END`— si
  el comando falla, los argumentos **se quedan apilados**. Donde sigue un
  `'VAR' STO` es solo suciedad; donde sigue una concatenación con `+` sale texto
  equivocado; y en **`DSEP` y `DSEPI`**, donde sigue `'C' +` y `=`, el programa
  puede **devolver una ecuación equivocada sin avisar**. Son los dos que hay que
  arreglar primero, con el guardián de profundidad de §2.11.

- ⚠️ **El CAS abre un diálogo modal en el medio.** `LIMIT` de `1/X` en 0 pregunta
  *"Unsigned inf. Solve?"* y espera respuesta. Afecta a `DCONT` justo en el caso
  interesante (una rama que revienta en el corte). Y la respuesta por defecto
  devuelve el infinito **sin signo**: por eso `DCONT` mostró `lim izq +∞` para
  `1/X` cuando el límite lateral verdadero es −∞. El veredicto (ESENCIAL) sale
  bien igual, porque solo mira si hay infinito; el signo que muestra la caja no
  significa nada en ese caso.
  **Resuelto:** `DCONT` y `DCONTF` usan laterales de verdad (`'X=a-0'`,
  `'X=a+0'`, medidos en `harness/casos-lateral.txt`), que dan el ∞ con signo:
  `1/X` por izquierda en 0 ahora da −∞.

---

## 6. Pendientes

- **`AREA`** — área entre curvas. Intersecciones con `ZEROS` sobre `f-g`,
  ordenarlas, e integrar por tramos sumando con el signo correcto. El caso con
  valor absoluto necesita partir también en 0. Primer programa de Mat1 que
  grafica: aplicar la regla de frontera de §5.
- **`IMPR`** — integral impropia. Reemplazar el extremo problemático por un
  parámetro, integrar con `RISCH`, evaluar con `PREVAL`, y tomar `LIMIT`.
- **Convertir a `INFORM`/`MSGBOX`** los cuatro que siguen por pila: `LHOP`,
  `DSEP`, `DSEPI`, `LAGR` (§4). Ninguno es de Parcial 1, así que no corre prisa.
- Probar los 17 en hardware, empezando por `TCHK`.
- Alternativa a evaluar para `DASHO`: `SERIES` en el infinito devuelve la parte
  lineal directamente, sin calcular `m` y `b` por separado.

---

## 7. Interfaces

### Parcial 1 — campos de `INFORM`, salida por `MSGBOX`

Las expresiones se tipean **con comillas simples** (`'X^2+3'`), como en el resto
de la suite. **El ejemplo de cada campo es solo la ayuda de la línea de abajo,
no un valor cargado**: un campo sin tocar llega como `NOVAL` y el programa corta
con `Bad Argument Type` (medido el 02/10/2026 con `DTANOR`, foto en el fork,
`harness/pantallas/vacio--*`). Acá decía que traía un default y no era cierto.
`DASVT` y `DCERO` sí traen valores iniciales (5º argumento de `INFORM`).

| Programa | Campos | Cajas | Además deja en la pila |
|---|---|---|---|
| `DOPFUN` | f(X), g(X), operación, x0 | una por operación pedida; dos de evaluación | n2 = fog, n1 = gof |
| `DCONT` | rama izq, rama der, punto a | límites; veredicto | n2 = lím izq, n1 = lím der |
| `DCONTF` | f(X), punto a | f(a) y lím izq; lím der; veredicto | n3 = f(a), n2 = lím izq, n1 = lím der |
| `DASHO` | f(X) | m y b en +∞; clasificación; ídem en −∞ | n4..n1 = m(+∞), b(+∞), m(−∞), b(−∞) |
| `DASV` | f(X), punto a | valores a los dos lados; veredicto | n2 = f(a−e), n1 = f(a+e) |
| `DDEF` | f(X), x0 (`'X'` = simbólico) | cociente; derivada | n2 = cociente, n1 = derivada |
| `DTANOR` | f(X), x0 | f'(x0) y f(x0); tangente; normal | n2 = tangente, n1 = normal |
| `DESTFUN` | f(X), candidato vert., probar sí/no | f'; críticos; f''; inflexión; +∞; −∞; vertical | n4..n1 = f', ceros f', f'', ceros f'' |
| `DVFG` | F, G, H, puntos | cuántas difieren; veredicto | n1 = lista de diferencias |
| `DDOMP` | F(X), puntos | cuántos entran; aviso | n1 = lista (valor o `"FUERA"`) |
| `DASVT` | f(X) | candidatos; asíntotas; avisos si hay | n1 = lista de asíntotas (exactas) |
| `DCERO` | f(X), g(X), operación | la expresión armada; dominio; ceros; descartados; avisos | n2 = H, n1 = lista de ceros |

`DOPFUN` cubre el TP 4 entero. El campo operación es `0` = todas, `1` a `4` las
aritméticas, `5` = fog, `6` = gof; con `0` son siete cajas seguidas, así que para
un ejercicio puntual conviene elegir una. Las dos últimas cajas evalúan las
composiciones en x0 y dicen **`NO EXISTE`** cuando el punto cae fuera del
dominio — que es exactamente lo que pide el ejercicio 3 del TP 4 ("encontrar si
es posible"). **No calcula dominios**: para eso está `DDOM` (§1.1),
que recibe la composición escrita sin simplificar.

`DESTFUN` es el estudio completo, y llega hasta donde llegue el CAS: cada bloque
va en su propio `IFERR`, así que si uno falla los demás se calculan igual. La
asíntota vertical es opcional porque el candidato lo tiene que poner el usuario
— no se deducen solos (para eso está `DASVT`, que sí los busca). Tampoco calcula dominio ni imagen (§4).

`DCONT` distingue los tres casos de la guía: esencial (algún límite infinito),
salto finito, y límites iguales. Ese último caso no se puede cerrar solo con los
límites — la caja dice explícitamente que hay que comparar con f(a) para separar
continua de evitable.

`DCONTF` es el par de `DCONT` para una función que **no** es a trozos (TP 9,
ej. 2 y 3). Chequea las tres condiciones y clasifica como la cátedra:
**evitable** si el límite existe (sin f(a), o con f(a) distinto), **inevitable
(esencial)** si no existe (salto finito, límite infinito, o un lateral que no
existe). Cuando a es borde del dominio, como `\v/X` en 0, dice **continua de
un solo lado**. En los evitables la caja dice con qué valor redefinir f(a).
Usa límites laterales de verdad (`'X=a-0'`, armado como texto porque desde la
pila `a 0 -` se reduce a `a`); lo medido está en el comentario de `DCONTFC`.

`DTANOR` corrige el signo: la pendiente de la normal es `-1/f'(x0)`. La
afirmación del punto 3c de la teoría de la guía es falsa por el signo. Si
`f'(x0) = 0`, la normal sale como `X = x0` en vez de explotar.

`DASVT` saca los candidatos del dominio (`DDOMC`: ceros de denominadores y
bordes de `LN` y raíces) y decide cada uno con **límites laterales** (`DCONTFC`).
`DASVC` queda de control: si el sondeo numérico y el CAS no coinciden, avisa.
Escribir f **sin simplificar**: `(X-3)/(X^2-9)` da candidatos −3 y 3, y solo −3
es asíntota (el 3 es evitable). **Abre el diálogo "Unsigned inf. Solve?"**
una vez por lado de cada polo (`CLAUDE.md` §2.12): apretar OK. La respuesta
es correcta contestando YES o NO; medido en el emulador.

`DCERO` es el par de `DOPFUN` para los ceros. Operación `0` = f sola, `1` = f/g,
`2` = f∘g, `3` = g∘f. **Arma la expresión sin `SIMPLIFY`** (al revés que
`DOPFUN`), así que el dominio sale de lo escrito: con f = `X^2-9` y g = `X-3`
(el ejemplo que trae cargado) muestra `R - {3}`, el cero −3, y el 3 en una
caja aparte como **descartado por estar fuera del dominio**, que es lo que la
cátedra pide ver escrito. Si un cero no hace 0 a la expresión, lo marca
`NO CONFIABLE`.

`DINV` (§1.1) avisa `NO INYECTIVA: partir en x=...` y propone los tramos
cuando el dominio dado no sirve, también con módulo: `ABS(2*X-4)` sobre
-INF, INF parte en 2. Si la vuelta solo la encuentra el sondeo de control, el
punto sale aproximado y el mensaje lo dice.

### Parcial 2 y final — todavía por pila

Argumentos de izquierda a derecha en el orden en que se apilan. **Falta
convertirlos a `INFORM`/`MSGBOX`.**

| Programa | Entra | Sale |
|---|---|---|
| `TCHK` | — | 4 resultados de diagnóstico |
| `LHOP` | `'f' 'g' 'X=a'` | n3 = límite original, n2 = f'/g', n1 = límite del cociente |
| `DSEP` | `'M(Y)' 'N(X)'` | n1 = `'F(Y) = G(X) + C'` |
| `DSEPI` | `'M(Y)' 'N(X)' X0 Y0` | n1 = igual, con la constante resuelta |
| `LAGR` | `'f(X,Y)' 'g(X,Y)' c` | n2 = lagrangiano, n1 = solución del sistema |
| `TD` | `n` | el caso n de `TDSEP`, listo para `DSEP` |
| `TF` | `n` | la función n de `TEFUN` |

`TEFUN` trae 8 funciones de los modelos. Dos son deliberadamente hostiles: la 5
mete una raíz cúbica sin derivada en 0, y la 8 es una indeterminada `oo/oo` que
obliga al CAS a aplicar L'Hopital solo. Si alguna cuelga la máquina, eso también
es información.


---

## 8. Comandos de fábrica que conviene no reprogramar

`FACTOR` / `FACTORS` / `PARTFRAC` / `PROOT` / `DIV2` (Ruffini) ·
`DERVX` / `DERIV` / `TANGENT` / `HESS` ·
`INTVX` / `RISCH` / `IBP` / `PREVAL` ·
`LIMIT` / `SERIES` / `DIVPC` ·
`TABVAR` / `SIGNTAB` ·
`DESOLVE` / `LDEC` ·
`EXLR` / `SUBST` / `SIMPLIFY` / `TSIMP` / `ZEROS` / `SOLVE`

No existe: L'Hopital como comando (de ahí `LHOP`), **tabla de Ruffini con pasos
intermedios** (de ahí `DRUF`: `DIV2` y `HORNER` dividen, pero ninguno muestra el
renglón de abajo, que es lo que hay que escribir), asíntotas verticales (de ahí
`DASV`), **extremos absolutos en un cerrado** (de ahí `DWEIER`), **Bolzano con
bisección** (de ahí `DBOLZ`), elasticidad, criterios de convergencia de series,
clasificación de puntos críticos en dos variables, y multiplicadores de Lagrange
(de ahí `LAGR`: el comando `LAGRANGE` es interpolación polinómica, otra cosa).

`HORNER` sí es la división sintética de fábrica, y `DRUFC` lo usa —pero solo
para sacar los coeficientes del polinomio. La tabla la calcula él, porque lo que
el ejercicio pide escrito es el renglón intermedio.

---

## 9. Probar en el emulador

**Ya está andando, y automatizado.** El harness vive en el fork, carpeta
`harness/`, con su propio README. El ciclo entero —compilar el objeto, mandarlo
a la pila por DDE, apretar EVAL por `PostMessage`, contestar los diálogos del
CAS, traerse el resultado y compararlo— corre con un comando y sin tocar el
teclado:

```powershell
.\correr-emu.ps1                                             # 16 de 16
.\correr-emu.ps1 -Fuente BESC.txt -Casos casos-escapes.txt   # 9 de 9
```

Lo que destapó en las primeras corridas está en §5 (el `IFERR` y el diálogo del
CAS) y en CLAUDE.md §2.1 (el infinito en el fuente funciona; `\>=`, `\<=` y `\.S`
también). **Prueba la capa de cálculo, no los formularios**: `INFORM` es
interactivo por definición. No es grave — los tres bugs que aparecieron en
hardware estaban todos en la capa de cálculo.

Lo que sigue es cómo se llegó ahí, y por qué el emulador que importa es el de
Debug4x.

Hay **dos** emuladores en la máquina, y no son equivalentes. La diferencia
importa más que cualquier otra cosa de esta sección.

### El de `Desktop\Emulador HP`: es una 49G

`50G.kml` declara `Rom "ROM/ROM.49G"`: es una **HP 49G** (Saturn) con una
carátula de 50g. No hay ninguna ROM de 50g en esa carpeta.

- Un resultado **rojo** ahí es información casi segura: si `RISCH` no existe en
  el 49G, casi con certeza tampoco va a funcionar como se asume en la 50g.
- Un resultado **verde NO prueba nada sobre la 50g**. El CAS del 49G (ROM 1.19)
  es el antecesor del de la 50g (ROM 2.15), no el mismo.

Sirve para **descartar** rápido, no para dar por bueno.

### El de Debug4x: es una 50g de verdad

`C:\Program Files (x86)\Hewlett-Packard\Debug4x\Emu` trae **`ROMG+.50G`** (4 MB,
julio de 2009, época de la ROM 2.15) y los KML `R50g1024.kml` / `R50g800.kml`,
que declaran:

```
Model  "Q"
Class  50
Rom    "ROMG+.50G"
```

Esto **corrige lo que decía antes este documento** ("la 50g es ARM y Emu48 emula
Saturn, no podría haber una ROM de 50g"). El `ReadMeFirst.txt` de Debug4x,
sección 19, explica cómo: *"It does not run any ARM code. Saturn is ok, but ARM
is not. A special EMU ROM must be obtained from HP. This ROM bypasses the ARM
code of the normal 49G+ ROM using Saturn or other techniques instead."* HP
autorizó esas ROMs y vienen en el paquete.

O sea: es la **ROM de la 50g** corriendo la capa Saturn, que es justo la capa
donde vive todo nuestro UserRPL — `INFORM`, `MSGBOX`, `LIMIT`, `RISCH`, el CAS y
los escapes. Un verde **acá** es evidencia fuerte: mismo ROM. Lo que queda
afuera es el código ARM y el hardware (SD, teclado, memoria real).

Aun así, nada pasa a "verificado" en la tabla de §1 por andar en el emulador —
eso sigue requiriendo la calculadora. Si se anota un resultado de emulador,
anotarlo como tal y decir cuál de los dos.

### Cómo entran los archivos

Emu48 carga un archivo que **no** empieza con el header binario `HPHP48-` /
`HPHP49-` metiéndolo en la pila **como string** (`Sources\Emu48\FILES.C`,
función `WriteStack`). Ese string se convierte al objeto real con **`ASCIIBIN`**,
que está en `C:\Program Files (x86)\HP-Emulators\Emu48\Emu48asc\ASCIIBIN.49` y
necesita justamente el header `%%HP: T(3)A(R)F(.);` completo — el mismo que ya
llevan todos los archivos de la suite.

`ASCIIBIN` **falla a veces con directorios**, así que `MAT1.txt` (que es un `DIR`)
no sirve para este camino. Por eso hay un empaquetado aparte:

```powershell
.\programas\armar-emu.ps1      # genera programas\MAT1-EMU.txt
```

`MAT1-EMU.txt` es un **programa instalador**: cada cuerpo va como literal
`\<< ... \>>` seguido de `'NOMBRE' STO`. Ese `\<<` huérfano es deliberado —
CLAUDE.md §2.2 dice que un `\<<` sin `\->` adelante se empuja como dato inerte,
que es exactamente lo que hace falta antes del `STO`. Por eso `verificar.ps1` le
marca 17 huérfanos: **es salida generada, verificar la fuente en `mat1/`.**

### Secuencia

1. Abrir `Emu48.exe` y elegir `50G.kml`.
2. **Edit > Load Object** → `Emu48asc\ASCIIBIN.49` (viene con header binario, así
   que entra como objeto directo). Después `'ASCIIBIN' STO`.
3. **Edit > Load Object** → `programas\MAT1-EMU.txt` → cae como string.
4. `ASCIIBIN` → lo compila. `EVAL` → crea los 17 globales.
5. Poner modo **exacto** y **Complex apagado** (§5).
6. Correr **`TCHK`** sin argumentos y leer los 4 resultados (§2).

Un `Load Object` y un `EVAL`, en vez de 17 ciclos manuales.

### Lo que el emulador no da

La 49G **no tiene SD**. El canal de archivos de ida y vuelta que tendría una 50g
real no existe acá, así que un harness que escriba resultados a un archivo no es
posible por esa vía.

**Pero el DDE sí sirve, y en las dos direcciones.** `Emu\DDE48.exe` (viene con
Debug4x) mueve objetos entre la pila del emulador y la PC:

```
DDE48 s archivo     @ POKE: pone el objeto en la pila del emulador
DDE48 r archivo     @ REQUEST: se trae el objeto de la pila a la PC
```

`herramientas\extraer-debug4x.ps1` del fork ya usa la ida; la vuelta es la que
cierra el ciclo, porque los resultados llegan como **objetos**, no leídos a ojo.

El DDE **no inyecta teclas** (`EMU48.txt`, sección DDE SERVER: solo CONNECT,
POKE y REQUEST), así que el ciclo mínimo es POKE → una tecla a mano → REQUEST.
La forma de aprovecharlo es un **único programa de batería** que corra todos los
casos de §10 y deje una lista de resultados: una tecla para toda la corrida. Es
`TCHK` llevado al extremo.

---

## 10. Casos de verificación

Modo **exacto** y **Complex apagado**. Correr `DINF` una vez antes de todo.

Donde dice "en la pila", es lo que queda además de las cajas.

### DOPFUN

**Caso 1 — todo definido.** f=`'X^2'`, g=`'X+1'`, oper=`0`, x0=`2`

| Caja | Debe dar |
|---|---|
| (f+g) | `X^2+X+1` |
| (f−g) | `X^2-X-1` |
| (f·g) | `X^3+X^2` |
| (f/g) | `X^2/(X+1)` |
| (fog) | `X^2+2*X+1` (= (X+1)²) |
| (gof) | `X^2+1` |
| (fog)(2) | `9` |
| (gof)(2) | `5` |

**Caso 2 — el ejercicio 3 del TP 4.** f=`'\v/(X-1)'`, g=`'2*X^2'`, oper=`0`, x0=`-3`

- (fog) = `\v/(2*X^2-1)`, (gof) = `2*X-2`
- (fog)(−3) = `\v/17` ≈ `4.1231`
- **(gof)(−3) va a dar `-8`, y la respuesta correcta de cátedra es "no existe".**
  No es un bug del programa: `gof` se simplificó a `2X−2`, que sí está definida
  en −3, pero la composición original no lo está porque f(−3)=√(−4). La
  simplificación pierde la restricción de dominio. Es la limitación de §4
  (no calcula dominios) mostrándose en un caso concreto. El dominio se escribe
  a mano.

### DCONT

| Ramas | a | Debe dar |
|---|---|---|
| `'X+1'` / `'X+3'` | `1` | lím izq `2`, lím der `4` → **SALTO FINITO** |
| `'X^2'` / `'2*X-1'` | `1` | lím izq `1`, lím der `1` → **LIMITES IGUALES** |
| `'1/X'` / `'X'` | `0` | lím izq `-∞`, lím der `0` → **ESENCIAL** |
| `'X'` / `'1/X'` | `0` | lím izq `0`, lím der `+∞` → **ESENCIAL** |
| `'X'` / `'X+1'` | `-1` | lím izq `-1`, lím der `0` → **SALTO FINITO** |

**El tercero falló y ya está arreglado.** Corrido en la máquina, daba los dos
límites bien pero el veredicto "SALTO FINITO", por el `SAME` contra `INF` que se
describe en §2. Ahora el infinito se detecta por el carácter 159. Rehacer este
caso para confirmar el arreglo; los dos primeros no dependen de eso.

**Con laterales, 6 de 6 en el emulador** (`harness/casos-mat1.txt`). El tercero
decía `+∞` en esta tabla y en la batería: era el ∞ sin signo del límite
ordinario, copiado como si fuera lo correcto. El lateral verdadero es −∞.

### DCONTF

**22 de 22 en el emulador con ROM de 50g** (`harness/casos-dcontf.txt`, el
núcleo `DCONTFC`). La interfaz solo se comprobó que compila.

| f(X) | a | Debe dar |
|---|---|---|
| `'X^2+1'` | `2` | f(a) `5`, laterales `5` → **CONTINUA** |
| `'(X^2-1)/(X-1)'` | `1` | f(a) NO EXISTE, laterales `2` → **EVITABLE**, redefinir f(1)=2 |
| `'X^2/(X^4-X^2)'` | `0` | f(a) NO EXISTE, laterales `-1` → **EVITABLE** (TP 9, ej. 2a) |
| `'X^2/(X^4-X^2)'` | `1` y `-1` | lateral infinito → **INEVITABLE** |
| `'ABS(X)/X^2'` | `0` | laterales `+∞` → **INEVITABLE** (TP 9, ej. 3c) |
| `'ABS(X)/X'` | `0` | laterales `-1` y `1` → **INEVITABLE**, salto finito |
| `'1/X'` | `0` | laterales `-∞` y `+∞`, con signo |
| `'\v/X'` | `0` | izq NO EXISTE, der `0`, f(0)=0 → **CONTINUA de 1 lado** |
| `'SIN(1/X)'` | `0` | laterales `?` → **INEVITABLE**, lateral no existe |

Dos trampas medidas antes de escribirlo (`harness/casos-lateral.txt`):

- **El CAS ignora el dominio en los laterales**: `'\v/X' 'X=0-0' LIMIT` da `0`.
  El lado fuera del dominio se reconoce porque el sondeo numérico en a−1e-6
  devuelve un complejo (§2.14 de CLAUDE.md: por `TYPE`).
- **f(a) fuera del dominio no da error**: `0/0` da `'?'` y `1/0` da `'∞'`. Se
  decide por el texto (159 y `?`) y la magnitud, no con `IFERR`.

### DASV

| f(X) | a | Debe dar |
|---|---|---|
| `'1/X'` | `0` | f(a−) ≈ `-1000000`, f(a+) ≈ `1000000` → **HAY ASINTOTA** |
| `'X^2'` | `0` | los dos ≈ `0` → **SIN ASINTOTA** |
| `'1/(X-2)'` | `2` | ± un millón → **HAY ASINTOTA** |

### DASVT

| f(X) | Debe dar |
|---|---|
| `'1/(X^2-9)'` | candidatos −3, 3 → asíntotas **X=−3, X=3** (4 diálogos: OK) |
| `'(X-3)/(X^2-9)'` | candidatos −3, 3 → asíntota solo **X=−3** |
| `'LN(X-2)/(X-5)'` | asíntotas **X=2, X=5** |
| `'\v/(X-1)'` | candidato 1 → **sin asíntotas** |
| `'X^2+1'` | sin candidatos |

### DCERO

| f, g, operación | Debe dar |
|---|---|
| `'X^2-9'`, `'X-3'`, 1 (f/g) | dominio `R - {3}`; ceros { −3 }; descartado { 3 } |
| `'LN(X)'`, `'X-1'`, 1 (f/g) | ceros { }; descartado { 1 } |
| `'\v/X'`, `'X^2-4'`, 3 (g∘f) | dominio `[0, +∞)`; ceros { 4 } |
| `'X^2-2*X+1'`, —, 0 | ceros { 1 } (raíz doble, no se rompe) |

### DINV con módulo

| f, A, B | Debe dar |
|---|---|
| `'ABS(2*X-4)'`, `-INF`, `INF` | `NO INYECTIVA: partir en x=2` |
| `'ABS(2*X-4)'`, `2`, `INF` | `OK`, f⁻¹(6) = 5 |
| `'(2*X+1)/(X-3)'`, `0`, `4.9` | `OK` (el polo no es una vuelta) |

### DDEF

| f(X) | x0 | Debe dar |
|---|---|---|
| `'X^2'` | `'X'` | cociente `((X+H)^2-X^2)/H`, derivada `2*X` |
| `'X^2'` | `3` | mismo cociente, derivada `6` |
| `'1/X'` | `2` | derivada `-1/4` |

El cociente sale **sin simplificar** a propósito: es lo que se copia a la hoja.

### DTANOR

| f(X) | x0 | Debe dar |
|---|---|---|
| `'X^2'` | `1` | f'=`2`, f=`1`; tangente `Y=2*X-1`; normal `Y=-X/2+3/2` |
| `'X^2'` | `0` | f'=`0`; tangente `Y=0`; normal **`X=0`** (vertical, no explota) |
| `'X^3'` | `2` | f'=`12`, f=`8`; tangente `Y=12*X-16` |

El segundo es el caso especial: con pendiente 0 la normal es vertical y `-1/m`
reventaría.

### DESTFUN

**Caso 1.** f=`'X^3-3*X'`, candidato `0`, probar `0`

- f' = `3*X^2-3`, críticos `{-1, 1}`
- f'' = `6*X`, inflexión `{0}`
- Las cajas de ±∞ deben decir **sin asint. (m infinito)**. Antes decían
  "OBLICUA m = ∞", que era basura —una cúbica no tiene asíntota—: el programa no
  distinguía "m infinito" de "m finito ≠ 0". Se le agregó el chequeo del carácter
  159 de §2, y este caso es el que lo prueba.

**Caso 2.** f=`'(X^2+1)/X'`, candidato `0`, probar `1`

- f' = `1-1/X^2` (o `(X^2-1)/X^2`), críticos `{-1, 1}`
- f'' = `2/X^3`, inflexión `{ }` (no tiene)

  **Corrido: devolvió `(X^2-1)/X^2` y `2/X^3`.** Correcto, aunque la primera
  derivada no se parezca a la de la hoja: f = X + 1/X, f' = 1 − 1/X², y
  `EXPAND SIMPLIFY` la deja sobre común denominador. Los críticos {−1, 1} salen
  de X²−1 = 0, que es la misma ecuación.
- +∞ → **OBLICUA m = 1**; −∞ → ídem
- vertical en 0 → **HAY ASINT. VERTICAL**

### DVFG

| F | G | H | Debe dar |
|---|---|---|---|
| `'X^2-1'` | `'X-1'` | `'X+1'` | 0 con diferencia → **SIMPLIFICACION OK** |
| `'X^2-1'` | `'X-1'` | `'X+2'` | 6 con diferencia → **NO COINCIDE** |

El segundo existe para confirmar que el programa sabe decir que no. Las seis
diferencias van a ser `-1`.

### DDOMP

f=`'\v/X'`, puntos `{ -2 -1 0 1 2 4 }`

- Lista: `{ "FUERA" "FUERA" 0 1 1.4142 2 }`
- Caja: probados `6`, en el dominio `4`

**Si los negativos no dan FUERA, Complex está prendido.** Ese es justamente el
modo que este programa necesita apagado.

### Los de pila (Parcial 2 y final)

| Programa | Entrada | Debe dar |
|---|---|---|
| `LHOP` | `'SIN(X)'` `'X'` `'X=0'` | n3 `1`, n2 `COS(X)`, n1 `1` |
| `DSEP` | `'Y'` `'X'` | `'Y^2/2 = X^2/2 + C'` |
| `DSEPI` | `'Y'` `'X'` `0` `1` | `'Y^2/2 = X^2/2 + 1/2'` |
| `LAGR` | `'X*Y'` `'X+Y'` `10` | punto crítico en `X=5, Y=5` (λ=5) |
| `TD` | `1` | n3 `'Y'`, n2 `'X'`, n1 `"dy/dx = x/y"` |
| `TF` | `1` | n2 `'(X^2-1)/(X-1)'`, n1 su nota |

`LAGR` es el más incierto de todos: depende de que `SOLVE` resuelva un sistema
de tres ecuaciones no lineales. Si devuelve el aviso de "no resolvió", no es un
bug del armado sino el límite del CAS.

# Diccionario de programas — Matemática I

Referencia rápida para usar la suite en la HP 50g. Todos se corren desde la
carpeta donde se cargó `MAT1.txt` (queda todo en un mismo `DIR`). Piden los
datos con un formulario (`INFORM`) y muestran el resultado en cajas
(`MSGBOX`): apretar **OK** para pasar a la caja siguiente.

**Antes de empezar, cinco cosas:**

1. **Escribir todos los campos.** El texto gris de abajo del formulario
   (ej. `'X^2'`) es solo una **ayuda**, no un valor cargado. Un campo que no se
   tocó llega vacío y el programa corta con `Bad Argument Type`. Medido en el
   emulador con `DTANOR`. Las excepciones son `DASVT` y `DCERO`, que sí traen
   el ejemplo cargado.
2. **Las funciones van con comillas simples**: `'X^2-9'`. La variable es `X`
   mayúscula.
3. **Escribir la función tal como está en el enunciado, sin simplificar.**
   `(X-3)/(X^2-9)` no es lo mismo que `1/(X+3)` para el dominio, y los
   programas lo saben solo si les llega la versión sin simplificar.
4. **Si aparece "Unsigned inf. Solve?", apretar OK.** Sale cuando hay un polo
   (una vez por lado de cada uno). El resultado es correcto contestando YES o NO.
5. **Guardar el infinito una vez**, si se van a usar `DASHO` o `DESTFUN`
   (si falta, lo avisan con una caja). Ver `INF` al final.

Todo lo de este archivo está probado en un emulador con la ROM de la 50g,
**no en la calculadora real**. Antes del parcial, correr un ejemplo de cada
programa que se vaya a usar.

---

## Funciones: dominio, ceros, operaciones

### DDOM — Dominio por definición
- **Pide:** f(X); si el enunciado da un dominio (1 sí, 0 no); el dominio dado.
- **Da:** las condiciones escritas (`X^2-9 <> 0`, lo que se copia en la hoja)
  y el dominio en intervalos, de las dos maneras cuando se puede:
  `R - {-3, 3}` y `(-∞, -3) U (-3, 3) U (3, +∞)`.
- **Dominio dado:** `{ a b }` para [a, b]; `{ { a b } { c d } }` uno por
  función (se intersecan); `'X>0'` para abiertos o infinitos.
- **Ejemplos:** `'(X-3)/(X^2-9)'` → `R - {-3, 3}` · `'\v/(4-X^2)'` → `[-2, 2]`
  · `'LN(X-1)/(X-3)'` → `(1, 3) U (3, +∞)`
- Si dice **`NO CONFIABLE`**, el control interno encontró que la tabla de
  signos no coincide con la función: hacer el ejercicio a mano.

### DCERO — Ceros que están en el dominio
- **Pide:** f(X), g(X), operación: `0` = f sola, `1` = f/g, `2` = f∘g,
  `3` = g∘f. Trae cargado el ejemplo de f/g.
- **Da:** la expresión armada (sin simplificar), el dominio, los ceros que
  valen y, aparte, los **descartados por caer fuera del dominio**, que es lo
  que la cátedra pide justificar.
- **Ejemplos:** f = `'X^2-9'`, g = `'X-3'`, oper 1 → dominio `R - {3}`, ceros
  { −3 }, descartado { 3 } · f = `'LN(X)'`, g = `'X-1'`, oper 1 → sin ceros,
  descartado { 1 } · f = `'\v/X'`, g = `'X^2-4'`, oper 3 → dominio `[0, +∞)`,
  ceros { 4 }

### DOPFUN — Operaciones y composición
- **Pide:** f(X), g(X), operación (`0` = todas, `1` a `4` = suma, resta,
  producto, cociente, `5` = f∘g, `6` = g∘f), x0 para evaluar las composiciones.
- **Da:** cada operación pedida, y las composiciones evaluadas en x0, o
  **`NO EXISTE`** si x0 cae fuera del dominio.
- **Ejemplo:** f = `'X^2'`, g = `'X+1'`, oper 0, x0 = 2 → f∘g = `X^2+2*X+1`,
  g∘f = `X^2+1`, (f∘g)(2) = 9, (g∘f)(2) = 5
- **Ojo:** el cociente sale **simplificado** y pierde los puntos excluidos
  (avisa en una caja). Para el dominio usar `DDOM`, y para los ceros `DCERO`.

### DINEC — Inecuaciones
- **Pide:** la inecuación entera, ej. `'X^2-X-2>0'`. También **dobles**:
  `'1<X<2'`, `'-3<2*X+1\<=5'`.
- **Da:** la solución en intervalos, por tabla de signos.
- **Ejemplos:** `'ABS(6*X-3)\>=9'` → `(-∞, -1] U [2, +∞)` ·
  `'X^2-2*X-3\>=0'` → `(-∞, -1] U [3, +∞)` · `'ABS(1/2-2*X)>1'` →
  `(-∞, -1/4) U (3/4, +∞)` · `'-3<2*X+1\<=5'` → `(-2, 2]` · `'5>X^2>1'` →
  `(-√5, -1) U (1, √5)`
- `≥` se escribe `\>=` en la PC; en la calculadora, con su tecla.

### DINV — Función inversa
- **Pide:** f(X), extremo a del dominio, extremo b (`INF` / `-INF` para
  infinito).
- **Da:** f⁻¹(X), la imagen B con sus corchetes, o **`NO INYECTIVA: partir en
  x=...`** con los tramos posibles cuando el dominio no sirve.
- **Ejemplos:** `'(X+2)^2-4'`, −2, `INF` → f⁻¹ = −2 + √(X+4), B = [−4, +∞) ·
  `'ABS(2*X-4)'`, `-INF`, `INF` → `NO INYECTIVA: partir en x=2` ·
  `'ABS(2*X-4)'`, 2, `INF` → OK, f⁻¹ = (X+4)/2
- **Elegir la rama es tuyo:** si dice no inyectiva, volver a correrlo con el
  tramo que pide el enunciado (o el que convenga).

### DPAR — Paridad
- **Pide:** f(X); si hay una F abstracta: `1` par, `-1` impar, `0` no hay; lo
  mismo para G.
- **Da:** par, impar o ninguna. Si no es ninguna, un **contraejemplo**: un
  punto p con f(p) y f(−p).
- **Ejemplos:** `'4*X+1/X'` → impar · `'X^2+COS(X)'` → par · `'X^3+1'` →
  ninguna (contraejemplo en p = 0.37)
- Con F y G abstractas ("F par, G impar"), el programa usa funciones
  representantes y no toca las tuyas.

### DDOMP — Sondear el dominio en puntos
- **Pide:** f(X), una lista de puntos.
- **Da:** el valor en cada punto, o `"FUERA"`.
- **Ejemplo:** `'\v/X'`, `{ -2 -1 0 1 2 4 }` → `{ "FUERA" "FUERA" 0 1 1.4142 2 }`

### DVFG — Verificar una simplificación
- **Pide:** F, G, la H propuesta (F/G simplificada), puntos de prueba.
- **Da:** en cuántos puntos F/G y H difieren, y el veredicto.
- **Ejemplo:** `'X^2-1'`, `'X-1'`, `'X+1'` → **SIMPLIFICACION OK** · con
  `'X+2'` → **NO COINCIDE**

---

## Límites, continuidad y asíntotas

### DCONTF — Continuidad de una función en un punto
- **Pide:** f(X), punto a.
- **Da:** f(a), los dos laterales y el veredicto: continua, **evitable** (con
  qué valor redefinir f(a)), **inevitable** (salto, infinito o lateral que no
  existe), o continua de un solo lado si a es borde del dominio.
- **Ejemplos:** `'(X^2-1)/(X-1)'`, 1 → evitable, redefinir f(1) = 2 ·
  `'ABS(X)/X'`, 0 → inevitable, salto (−1 y 1) · `'\v/X'`, 0 → continua de un
  lado

### DCONT — Continuidad de una función a trozos en el corte
- **Pide:** la rama izquierda, la rama derecha, el punto de corte a.
- **Da:** los dos laterales y el veredicto: salto finito, esencial (algún
  lateral infinito) o límites iguales.
- **Ejemplos:** `'X+1'` / `'X+3'`, 1 → salto finito (2 y 4) · `'1/X'` / `'X'`,
  0 → esencial (−∞ y 0)
- Con límites iguales, **comparar a mano con f(a)** para separar continua de
  evitable: el programa no conoce f(a) en una función a trozos.

### DCONTK — El k que hace continua una función a trozos
- **Pide:** la rama izquierda (x < a), la derecha (x > a), el punto a, el
  nombre del parámetro (`K`).
- **Da:** el o los valores de k, cada uno verificado.
- **Ejemplos:** `'X^2-K*X+3'` / `'(2*X-K)/(1+X)'`, a = 1 → k = 6 ·
  `'(X-4)^2+K'` / `'2*X'`, a = 3 → k = 5

### DASVT — Asíntotas verticales, buscando los candidatos
- **Pide:** f(X). Trae cargado `'1/(X^2-9)'`.
- **Da:** los candidatos (bordes del dominio y ceros de denominadores) y cuáles
  son asíntota.
- **Ejemplos:** `'1/(X^2-9)'` → X = −3, X = 3 (4 diálogos: OK) ·
  `'(X-3)/(X^2-9)'` → solo X = −3 (el 3 es evitable) · `'LN(X-2)/(X-5)'` →
  X = 2, X = 5 · `'\v/(X-1)'` → candidato 1, sin asíntota

### DASV — Asíntota vertical en un punto dado
- **Pide:** f(X), el candidato a.
- **Da:** los valores a cada lado de a, y si hay asíntota.
- **Ejemplo:** `'1/X'`, 0 → ± un millón, **HAY ASINTOTA**
- Para buscar los candidatos solo, usar `DASVT`.

### DASHO — Asíntotas horizontales y oblicuas
- **Pide:** f(X). **Necesita el `INF` guardado** (ver al final).
- **Da:** m y b en +∞ y en −∞, y la clasificación (horizontal, oblicua, o sin
  asíntota si m es infinita).
- **Ejemplo:** `'(X^2+1)/X'` → oblicua, m = 1, b = 0, a los dos lados

### LHOP — Un paso de L'Hôpital
- **Pide:** numerador f(X), denominador g(X), el punto: `'X=0'` o `'X=INF'`.
  **Con `'X=INF'` necesita el `INF` guardado** (ver al final).
- **Da:** f'/g' y el límite.
- **Ejemplos:** `'SIN(X)'`, `'X'`, `'X=0'` → `COS(X)`, límite 1 ·
  `'LN(X)'`, `'X'`, `'X=INF'` → `1/X`, límite 0

---

## Derivadas y estudio de función

### DDEF — Derivada por definición
- **Pide:** f(X), x0 (`'X'` para la derivada simbólica).
- **Da:** el cociente incremental **sin simplificar** (lo que se copia a la
  hoja) y la derivada.
- **Ejemplos:** `'X^2'`, `'X'` → `((X+H)^2-X^2)/H`, derivada `2*X` · `'1/X'`,
  2 → derivada −1/4

### DTANOR — Recta tangente y normal
- **Pide:** f(X), x0.
- **Da:** f'(x0), f(x0), la tangente y la normal.
- **Ejemplos:** `'X^2'`, 1 → tangente `Y=2*X-1`, normal `Y=-X/2+3/2` ·
  `'X^2'`, 0 → tangente `Y=0`, normal **`X=0`** (vertical)

### DESTFUN — Estudio de función
- **Pide:** f(X), un candidato a asíntota vertical, si probarlo (1 sí, 0 no).
  **Necesita el `INF` guardado** (ver al final).
- **Da:** f' y sus ceros, f'' y sus ceros, asíntotas en ±∞ y el veredicto de la
  vertical.
- **Ejemplo:** `'X^3-3*X'` → críticos {−1, 1}, inflexión {0}, sin asíntotas
- No calcula dominio ni imagen: para eso, `DDOM` y `DASVT`.

### DWEIER — Weierstrass: extremos absolutos en [a, b]
- **Pide:** f(X), a, b.
- **Da:** la tabla de candidatos (extremos del intervalo y críticos de
  adentro), el máximo y el mínimo absolutos. Sondea si f es continua en [a, b].
- **Ejemplos:** `'X^3-3*X'`, [−2, 3] → máx 18 en x = 3, mín −2 ·
  `'X^2-2*X'`, [0, 3] → mín −1 en x = 1, máx 3

### DBOLZ — Bolzano: ¿hay raíz en [a, b]?
- **Pide:** f(X), a, b.
- **Da:** f(a), f(b), si el teorema asegura una raíz, y la raíz por bisección.
- **Ejemplos:** `'X^3-2'`, [1, 2] → hay raíz, ≈ 1.2599 · `'X^2-1'`, [−2, 2]
  → **NO SE PUEDE AFIRMAR**
- **Ojo:** que f(a) y f(b) tengan el mismo signo **no** significa que no haya
  raíz (`X^2-1` en [−2, 2] tiene dos). Bolzano es suficiente, no necesario. El
  mensaje lo dice.

### DRUF — Ruffini: factoreo con la tabla de cada división
- **Pide:** P(X).
- **Da:** las raíces racionales, la tabla de cada división (el renglón que se
  copia) y el polinomio factoreado.
- **Ejemplos:** `'X^3-1'` → `(X-1)*(X^2+X+1)` · `'X^3+2*X^2-X-2'` →
  `(X-1)*(X+1)*(X+2)`

---

## Integrales y ecuaciones diferenciales

### DWSUS — Sustitución de Weierstrass, t = tan(x/2)
- **Pide:** f(X) con senos y cosenos.
- **Da:** f(t) después de la sustitución y la primitiva en t.
- **Ejemplo:** `'1/(1+SIN(X))'` → `2/(T^2+2*T+1)`, primitiva `-2/(T+1)`

### DSEP — EDO separable M(Y) dy = N(X) dx
- **Pide:** M(Y), N(X).
- **Da:** las dos integrales y la solución general.
- **Ejemplos:** `'Y'`, `'X'` → `Y^2/2=X^2/2+C` · `'Y'`, `'EXP(X)'` →
  `Y^2/2=EXP(X)+C`
- Si una integral no tiene primitiva elemental, dice **NO INTEGRA** en vez de
  inventar una.

### DSEPI — Problema de valor inicial separable
- **Pide:** M(Y), N(X), X0, Y0.
- **Da:** la constante C y la solución particular.
- **Ejemplo:** `'Y'`, `'X'`, X0 = 0, Y0 = 1 → C = 1/2,
  `Y^2/2=X^2/2+1/2`

### LAGR — Multiplicadores de Lagrange
- **Pide:** f(X,Y), g(X,Y), c (la restricción es g = c).
- **Da:** el lagrangiano y los puntos críticos.
- **Ejemplo:** `'X*Y'`, `'X+Y'`, 10 → punto crítico X = 5, Y = 5 (λ = 5)
- Es el más frágil: depende de que el CAS resuelva un sistema no lineal. Si
  avisa que no resolvió, es el límite del CAS, no un error del armado.

---

## Utilidad

### INF — El infinito que usan DASHO y DESTFUN
- Lo usan `DASHO`, `DESTFUN` y `LHOP` en infinito. Se hace **una vez**, parado **adentro de la carpeta de `MAT1`**: poner el ∞
  **del teclado** en la pila, escribir `'INF'` y apretar `STO`.
- Tiene que ser el ∞ del teclado: el archivo de texto no puede llevar ese
  carácter, por eso no viene cargado.
- `DINF` hace lo mismo y además verifica el objeto, pero viene en `LAB.txt`,
  no en `MAT1.txt`. Si se corre en la carpeta de Lab, el `INF` queda allá y
  desde la de Mat1 no se ve: las carpetas hermanas no comparten nombres.

---

## Lo que la calculadora no hace por vos

- **Elegir la rama** para que la función sea biyectiva: `DINV` dice dónde
  partir, pero cuál tramo usar lo decide el enunciado.
- **Escribir la justificación.** Los programas muestran las condiciones, los
  descartados y los laterales para que los copies, pero la redacción es tuya.
- **Desconfiar de un `NO CONFIABLE`.** Cuando un programa avisa eso, el control
  encontró que el CAS no coincide con un sondeo numérico: hacerlo a mano.

---

## Nota para quien mantiene la suite

Cada programa `XXX` es solo la interfaz; el cálculo está en el núcleo `XXXC`.
Los núcleos se prueban con las baterías del fork
(`harness/casos-*.txt`); las interfaces solo se pueden probar con
`harness/pantallas-ui.ps1`, que maneja el formulario con teclas y saca fotos.
Detalle técnico y estado de cada programa en `SUITE-MAT1.md`; reglas de
UserRPL en `AGENTS.md`. Este archivo es para **usar** la suite: si un ejemplo
de acá deja de dar lo que dice, el que está mal es el programa.

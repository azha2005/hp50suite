# Diccionario de programas — Laboratorio de Datos (y Micro I)

Referencia rápida para usar la suite en la HP 50g. Todos se corren desde la
carpeta donde se cargaron (`LAB.txt` los deja juntos en un mismo `DIR`).
Piden los datos con un formulario (`INFORM`) y muestran el resultado en cajas
(`MSGBOX`): apretar **OK** para pasar a la caja siguiente.

**Cómo cargar los datos:** en un campo "Datos" se puede escribir una lista
`{ 2 4 6 8 10 }`, un vector `[ 2 4 6 8 10 ]` o el **nombre** de una variable
guardada (`BM5X`, `HORAS`...).

---

## Estadística descriptiva (una variable)

### DSTATS — Medidas de resumen
- **Pide:** Datos
- **Da:** media, varianza, desvío estándar y coeficiente de variación.
- **Ejemplo:** `BM5X` → Media = 32172.2, s = 32930.3

### DMODA — Moda
- **Pide:** Datos
- **Da:** la moda (o las modas, si hay varias). Avisa si no hay moda.
- **Ejemplo:** `BMHIST` → moda 5.31 (frecuencia 3)

### DPCTIL — Percentil
- **Pide:** Datos, percentil p (0 a 100)
- **Da:** la posición `Lp = (p/100)(n+1)` y el valor interpolado.
- **Mediana = p50.** Cuartiles: p25 y p75.
- **Ejemplo:** `{ 2 4 6 8 10 }`, p=50 → 6 · p=70 → Lp = 4.2, valor = 8.4
- **Es el método del profesor.** La diapositiva de Cicowiez (Unidades 1 y 2)
  define `Lp = (p/100)(n+1)` y resuelve `L70` con 12 precios del Big Mac:
  9.1 → 5.4684. `DPCTIL` da exactamente eso. Ojo: el apunte de Excel de la
  práctica usa `PERCENTIL.INC`, que es **otro** método (ver `DPCTIL2`).

### DFRECTABLA — Tabla de frecuencias
- **Pide:** Datos, K (cantidad de clases), Ancho, Inicio. **`0` = automático,
  con la regla de la cátedra** (diapositiva "¿Calcular el tamaño del intervalo?"):
  1. K por Sturges: `1 + 3.322·log(n)`, redondeado.
  2. Ancho = rango / K, **redondeado para arriba** a una cifra
     (0.9067 → 1, 4.2 → 5).
  3. Inicio = el múltiplo del ancho justo debajo del mínimo (1.62 → 1).
  4. Las clases que hagan falta para llegar al máximo.
- Clases cerradas a izquierda, `[a, b)`, como el "1.00 − 1.99" de la
  diapositiva.
- **Ejemplos:** `BMHIST` en automático → las 7 clases de la diapositiva
  (1–2, 2–3 … 7–8) con frecuencias 1, 11, 15, 9, 7, 1, 1 · `HORAS` en
  automático → K=5, Ancho=5, Inicio=10, que es justo el enunciado de cátedra
- **Da:** una **matriz** con frecuencia absoluta, absoluta acumulada, relativa %
  y relativa acumulada %. Para verla como planilla: modo algebraico y `EDIT`.
- Si el ejercicio fija las clases, cargarlas a mano: lo que se carga se respeta.

### DHISTO — Histograma
- **Pide:** lo mismo que `DFRECTABLA` (usa exactamente las mismas clases).
- **Da:** el gráfico de barras.

### DBOXPLOT — Diagrama de caja
- **Pide:** Datos
- **Da:** gráfico con caja (Q1, mediana, Q3), bigotes, outliers marcados, eje y
  los puntos individuales.
- Cuartiles por el **método de la cátedra** (el de `DPCTIL`): el gráfico y
  `DCINCO` dan siempre los mismos cuartiles y los mismos atípicos. Para
  escribir los números en la hoja, `DCINCO`.
- Hasta el 27/09/2026 tomaba los cuartiles por posición, sin interpolar: con
  `{ 1 4 3 5 6 }` dibujaba Q1 = 3 y Q3 = 5 en vez de 2 y 5.5. Si tenés cargada
  una versión anterior en la calculadora, reemplazala.

### DCINCO — Resumen de cinco números
- **Pide:** Datos
- **Da:** mínimo, Q1, mediana, Q3, máximo, RIC = Q3 − Q1, cercas
  (Q1 − 1.5·RIC y Q3 + 1.5·RIC), los atípicos (o "ninguno"), media contra
  mediana y el diagnóstico de asimetría: media > mediana → positiva (cola a la
  derecha); media < mediana → negativa (cola a la izquierda); iguales → simétrica.
- Cuartiles por el **método de clase**: son siempre los mismos que da `DPCTIL`
  con p = 25 y p = 75 (usa el mismo cálculo).
- **Ejemplos:**
  - `{ 1 4 3 5 6 }` → min 1, Q1 = 2, mediana 4, Q3 = 5.5, max 6, RIC = 3.5,
    cercas −3.25 y 10.75, sin atípicos; media 3.8 < 4 → asimetría negativa
  - `{ 1 2 3 4 5 6 7 50 }` → Q1 = 2.25, mediana 4.5, Q3 = 6.75, RIC = 4.5,
    cercas −4.5 y 13.5 → atípico: 50; media 9.75 > 4.5 → asimetría positiva

### DPCTIL2 — Percentil por los tres métodos
- **Pide:** Datos, percentil p (0 a 100)
- **Da:**
  - **Clase** (el del profesor): `Lp = (p/100)(n+1)` y el valor interpolado.
    Es idéntico a `DPCTIL`. Si Lp < 1 da el mínimo, y si Lp > n el máximo, y
    lo avisa.
    Es también el de **Anderson 2020** y el `PERCENTIL.EXC` de Excel.
  - **Anderson 2012** (la edición en castellano): `i = (p/100)·n`. Si i no es
    entero, se redondea para arriba y el percentil es el dato en esa posición.
    Si i es entero, es el promedio de los datos i e i+1.
  - **Excel `.INC`** (el `PERCENTIL.INC` / `CUARTIL.INC` del apunte de Excel):
    posición `1 + (n−1)·p/100`, interpolado.
  - Si los tres coinciden o no ("usar el de clase").
- Sirve para ver de dónde sale una diferencia en una pregunta de opción múltiple.
- **Ejemplos:** `{ 2 4 6 8 10 }`: p=70 → clase Lp = 4.2, valor 8.4 · Anderson
  2012 i = 3.5 → posición 4 → 8 · Excel .INC 7.6. p=40 → clase 4.8 ·
  Anderson 2012 i = 2 (entero) → (4+6)/2 = 5
- Con los datos del examen intensivo, Y = `{ 1 4 3 5 6 }`: Q1 de clase = 2,
  pero Anderson 2012 y Excel .INC dan 3. Si aparece un 3 entre las opciones,
  sale de ahí.

### DZLISTA — Valor z de toda la lista, y z inverso
- **Pide:** Datos, z objetivo (se puede dejar en 0)
- **Da:** media y s (muestral), una **matriz** x | z con el z de cada dato
  (queda en la pila y en la variable `ZTABLA`), los atípicos (|z| > 3) o "sin
  atípicos", y el valor que tendría el z objetivo: `x = media + z·s`.
- Usa el mismo cálculo que `DSTATS` (media y s) y que `DCOMPZ` (cada z).
- **Ejemplo:** `{ 4.5 2 -1.5 .5 2.5 }` → media 1.6, s = 2.2472 (s² = 5.05);
  z(4.5) = 1.2905, z(2) = .1780, z(−1.5) = −1.3795, z(.5) = −.4895,
  z(2.5) = .4005; sin atípicos. z objetivo 0 → 1.6 · z objetivo 1 → 3.8472
- Ver la tabla: modo algebraico, `ZTABLA` y `EDIT`.

### DCHEBY — Chebyshev y regla empírica
- **Pide:** k, media, s, n (0 = no calcular cantidad). **Con k = 0** pide en
  una segunda pantalla el intervalo [a, b] y saca k de ahí (si el intervalo no
  es simétrico usa el k menor, y avisa).
- **Da:** k, "al menos X % de los datos" (`1 − 1/k²`), y con n: "al menos N
  observaciones" (redondeado para arriba, y el valor sin redondear). Una caja
  con la regla empírica, solo de referencia para distribuciones en campana
  (68 / 95 / 99.7 %).
- Con k ≤ 1 avisa: Chebyshev no dice nada.
- **Ejemplos:** media 70, s 5, [60, 80], n 100 → k = 2, al menos 75 %, al menos
  75 alumnos · [58, 82] → k = 2.4, al menos 82.64 % · k = 3 → al menos 88.89 %

### DPOND — Media ponderada
- **Pide:** Datos x, Pesos w (mismo largo)
- **Da:** suma de w, suma de w·x y la media ponderada = Σwx / Σw.
- **Ejemplos:** x = `{ 3 4 5 }`, w = `{ 1 2 1 }` → Σw = 4, Σwx = 16, media 4 ·
  x = `{ 7 8 5 }`, w = `{ .3 .3 .4 }` → 6.5

---

## Relación entre dos variables

### DCOVCORR — Covarianza y correlación
- **Pide:** Datos X, Datos Y (dos listas separadas, del mismo largo)
- **Da:** covarianza, r de Pearson, y el gráfico de dispersión con la recta de
  regresión.
- **Ejemplo:** `BM5X` / `BM5Y` → sXY = 62909.8, r = 0.9781

### DOLS — Regresión lineal (MCO)
- **Pide:** Datos X, Datos Y
- **Da:** b0, b1, r y R², por sumatorias.
- **Ejemplo:** `BM5X` / `BM5Y` → Y = 1.952 + 0.0000580·X, r = 0.9781
  (siempre coincide con `DCOVCORR`: usa el mismo cálculo)

### DTABLA2 — Tabla de desvíos (la que se copia en la hoja)
- **Pide:** Datos X, Datos Y (**0 = una sola variable**)
- **Da:**
  - Dos variables: una **matriz** de n+1 filas × 7 columnas:
    `x | y | x−x̄ | y−ȳ | (x−x̄)² | (y−ȳ)² | (x−x̄)(y−ȳ)`. La última fila son las
    **sumas** de cada columna (las de desvíos dan 0).
  - Una variable: n+1 filas × 3: `x | x−x̄ | (x−x̄)²`, con la fila de sumas.
  - La matriz queda en la pila y en la variable **`TABLA2`**.
  - Cajas: x̄ e ȳ · SSx y SSy (sumas de cuadrados) · Sxy (suma de productos) ·
    s²x y s²y · sx y sy · sxy (covarianza) y r.
- Todo muestral (n−1). x̄, s, sxy y r salen del mismo cálculo que `DSTATS` y
  `DCOVCORR`: no pueden dar distinto.
- Si X e Y no tienen el mismo largo, avisa y sale.
- **Ejemplos:**
  - X = `{ 1 2 3 4 5 }`, Y = `{ 1 4 3 5 6 }` → x̄ = 3, ȳ = 3.8; desvíos x:
    −2 −1 0 1 2; desvíos y: −2.8 .2 −.8 1.2 2.2; SSx = 10, SSy = 14.8,
    Sxy = 11; s²x = 2.5, s²y = 3.7; sx = 1.5811, sy = 1.9235; sxy = 2.75,
    r = 0.9042
  - Solo X = `{ 2 4 4 5 7 8 }` → matriz 7×3, SSx = 24, s² = 4.8, s = 2.1909
- Ver la tabla: modo algebraico, `TABLA2` y `EDIT`.

---

## Economía

### DMKT — Equilibrio de mercado
- **Modelo:** Demanda `Qd = a − b·P`, Oferta `Qs = c + d·P`
- **Pide:** a, b, c, d, impuesto T (0 = sin impuesto)
- **Da:** P\* y Q\*, y el gráfico.
- **Ejemplo:** a=100, b=2, c=10, d=3 → P\*=18, Q\*=64. Con T=5 → P\*=21, Q\*=58

### DMKTFISC — Mercado con política fiscal (el completo)
- **Pide:** a, b, c, d, T, Precio máximo (0 = sin techo), Precio mínimo
  (0 = sin piso). **T negativo = subsidio.**
- **Da:** Pb (paga el comprador), Ps (recibe el vendedor), Q\*, recaudación
  (negativa = costo fiscal del subsidio), pérdida irrecuperable de eficiencia
  (PIE), incidencia en % (comprador / vendedor), elasticidades de demanda y
  oferta, y con controles de precio la escasez o el excedente. Gráfico con las
  áreas sombreadas (precio en el eje vertical).
- **Ejemplos:**
  - Impuesto: a=100, b=2, c=10, d=3, T=5 → Ps=16, Recaud=290, PIE=15,
    incidencia 60/40, Ed=−0.7241, Es=0.8276
  - Subsidio: a=60, b=4, c=0, d=2, T=−3 → Pb=9, Ps=12, Q\*=24, Recaud=−72, PIE=6

### DCOMPFIRM — Empresa en competencia perfecta
- **Modelo:** `CT = CF + b·Q + c·Q²`, entonces `CMg = b + 2c·Q`
- **Pide:** CF, b, c, precio de mercado P
- **Da:** Q\* (donde P = CMg), beneficio, y si conviene cerrar (P < mín CVMe).
  Gráfico con CMg, CVMe y P.
- **Ejemplo:** CF=20, b=3, c=1 → P=43: Q\*=20, Ben=380 · P=11: Q\*=4, Ben=−4 ·
  P=1: cierra, Ben=−20

### DPIBPPA — PIB per cápita en PPA
- **Pide:** PIB nominal (moneda local), factor de conversión PPA, población
- **Da:** PIB per cápita a paridad de poder adquisitivo.
- ⚠️ Completar los tres campos: sin visitar un campo, puede fallar
  (ver `programas/README.md`, "Inconsistencia conocida").

### DTCAMBIO — Tasa de crecimiento anual compuesta
- **Pide:** variación total acumulada (%), año inicial, año final
- **Da:** la tasa anual equivalente (CAGR).

### DCOMPZ — Valor Z (en la documentación vieja aparece como `DVLRZ`)
- **Pide:** valor observado x, media, desvío
- **Da:** `Z = (x − media) / desvío`, y lo marca como **atípico si |Z| > 3**.
- Para el z de **todos** los datos de una lista, usar `DZLISTA`.

### DREAL — Variación real y variaciones sucesivas
- **Pide:** variación nominal %, inflación %, variaciones sucesivas % (lista,
  o 0 para omitir)
- **Da:**
  - Variación real % = `((1 + nom/100) / (1 + inf/100) − 1) · 100`, con "el
    poder de compra subió / cayó". Se omite solo si nominal **y** inflación
    son 0 (un salario congelado con inflación sí se calcula).
  - Variaciones sucesivas: acumulada % = `(Π(1 + vi/100) − 1) · 100`, y el
    nivel final partiendo de 100.
- **Ejemplos:** nominal 30, inflación 40 → real −7.1429 % (cayó) · nominal 50,
  inflación 20 → 25 % · sucesivas `{ -20 20 }` → acumulada −4 %, nivel 96
  (efecto base baja) · `{ 10 10 }` → 21 %, nivel 121

---

## Programación

### DLOOPC — Simulador de bucle while
Para las preguntas del tipo "¿qué imprime este `while`?". Ejemplo del examen
intensivo:

```
capital = 100 ; anios = 0
while capital <= 200:
    capital = capital * 1.10
    anios = anios + 1
print(anios)          -> 8
```

- **Pide (pantalla 1):** valor inicial, modo (1 = compuesto
  `v·(1 + tasa/100)`, 2 = aditivo `v + paso`), tasa % o paso.
  **(pantalla 2):** límite, condición (1 = `<=`, 2 = `<`, 3 = `>=`, 4 = `>`).
  El bucle sigue **mientras** `valor <condición> límite`. Los campos vienen
  cargados con el ejemplo de arriba.
- **Da:** cantidad de vueltas (el valor final del contador) y el valor final, y
  una **matriz** vuelta | valor al entrar | valor al salir (variable `LOOPT`).
  Si la condición es falsa desde el principio: 0 vueltas. Corta a las 500
  vueltas y avisa "posible bucle infinito".
- **Ejemplos:** 100, compuesto, 10 %, límite 200, `<=` → 8 vueltas, valor final
  214.3589 (con `<` también 8) · tasa 100 % con `<=` → 2 vueltas (100 → 200 →
  400); con `<` → 1 · `cnt = 1; while cnt < 5: cnt = cnt + 1` → 1, aditivo,
  paso 1, límite 5, `<` → 4 vueltas, valor final 5 (con `<=`: 5 vueltas, 6)

---

## Utilidad

### SIGFIG — Cifras significativas
Redondea un número a N cifras significativas. No se usa directamente: lo llaman
`DOLS` y `DCOVCORR`. **Tiene que estar cargado**: si falta, no da error, sino
que muestra un resultado equivocado.

---

## Datasets incluidos (`programas/datos/`)

| Variable | Qué es | Para qué programa |
|---|---|---|
| `BM5X` / `BM5Y` | PIB pc PPA y precio Big Mac, 5 países | `DCOVCORR`, `DOLS` (r ≈ 0.9781) |
| `BMSCX` / `BMSCY` | Lo mismo, 46 países | `DCOVCORR`, `DOLS` (r ≈ 0.7579) |
| `BMHIST` | 45 precios del Big Mac | `DSTATS`, `DMODA`, `DHISTO`, `DBOXPLOT` |
| `HORAS` | 20 valores de horas trabajadas | `DFRECTABLA`/`DHISTO`: en automático da K=5, Ancho=5, Inicio=10 → `4,8,5,2,1` |

---

## Nota para quien mantiene la suite

Cada programa `XXX` es la interfaz (formulario + cajas). El cálculo está en
`XXXC` y, en los que grafican, el dibujo en `XXXG`. Única excepción de nombre:
el núcleo de `DLOOPC` es `DLOOPCC` (el nombre del programa ya terminaba en C). Para el usuario alcanza
con correr `XXX`. Las reglas y el estado de las pruebas están en `AGENTS.md` §5–6.

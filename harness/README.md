# Harness: probar la suite contra una 50g de verdad

Sí se puede. La pieza que faltaba era poder **leer el resultado como dato** en
vez de a ojo en la pantalla, y eso ya está resuelto: `DDE48 r` trae el objeto de
la pila a la PC y `herramientas/hpobj.py` lo decodifica.

Prueba la **capa de cálculo**, no los formularios. `INFORM` es interactivo por
definición y no se puede correr desde una batería. No es una limitación grave:
todos los bugs que aparecieron en hardware hasta hoy — el `\.oo`, el umbral de
`DASV`, el `SAME` contra `INF` — estaban en la capa de cálculo.

## Qué no viene en el repo

- **La ROM de la 50g y el emulador.** Son de HP. Hace falta un Debug4x
  instalado (`DDE48.exe` en la ruta por defecto, o pasarla con `-Dde48`).
- **Las tablas de letras de la pantalla** (`fuente-4x6.json`,
  `fuente-6x8.json`), que salen de la ROM. `leer-pantalla.py` las arma desde
  una captura propia: `python leer-pantalla.py fuente.bin`.
- **Lo generado** (`B*.txt`, `UI-*.txt`, `.hp`, `.bin`, `pantallas/`). Lo
  rehacen `armar-bateria.ps1`, `armar-mat1.py`, `armar-ui.py` y
  `herramientas/compilar.py`.
- `oraculo.py` necesita `sympy` (`pip install sympy`).

## Las piezas

| Archivo | Qué es |
|---|---|
| `casos.txt` | la tabla: `nombre \| expresión UserRPL \| esperado` |
| `casos-escapes.txt` | tabla aparte para los escapes (`\oo`, `\>=`, `\<=`, `\.S`) |
| `casos-diag.txt` | tabla de diagnóstico, para aislar un comportamiento raro |
| `armar-bateria.ps1` | convierte una tabla en el programa `BATERIA` / `BESC` / `BDIAG` |
| `BATERIA.txt`, `BESC.txt`, `BDIAG.txt` | **salida generada**, no editar a mano |
| `BATERIA.hp` | el objeto binario, lo genera `herramientas/compilar.py` |
| `correr-emu.ps1` | **el ciclo entero, sin tocar el teclado** |
| `correr.ps1` | variante manual: solo `DDE48 r` + comparación |
| `leer-resultado.py` | decodifica lo que vuelve y lo compara contra la tabla |
| `oraculo.py` | verifica los ESPERADO contra sympy, antes de creerle a la tabla |
| `probar-tecla.ps1` | prueba mínima del canal de teclas (escribe `1 ENTER` y lee) |

Las tablas van separadas a propósito: si un escape no compila, se cae `BESC` y
no la batería principal.

## Puesta a punto

Una sola cosa: abrir el **Emu48 de Debug4x** con un estado de 50g. El ejecutable
está en `Debug4x\Emu\EMU48.EXE` y los estados en `Documents\Debug4x\Emu`;
`Default 50g.E49` sirve tal cual y arranca en **modo exacto** (`R=` en la línea
de anunciadores), que es lo que Mat1 necesita. Acepta el estado como argumento de
línea de comandos.

El KML de 50g declara `Class 50` y `Rom "ROMG+.50G"`: es la ROM de la 50g de
verdad, no una 49G con carátula (medido en el emulador).

**No hace falta instalar nada en la calculadora**: ni `ASCIIBIN`, ni `Load
Object`, ni guardar la batería como variable. El objeto viaja por DDE en cada
corrida.

## Cada corrida

```powershell
.\armar-bateria.ps1      # solo si cambiaron los casos
.\correr-emu.ps1
```

Sale una tabla caso por caso con ESPERADO / OBTENIDO / ok|FALLA.

## Automatización: quedó sin manos

`correr-emu.ps1` hace el ciclo entero sin tocar el teclado:

```powershell
.\correr-emu.ps1                                                  # bateria principal
.\correr-emu.ps1 -Fuente BESC.txt -Casos casos-escapes.txt        # escapes
.\correr-emu.ps1 -Fuente BDIAG.txt -Casos casos-diag.txt -EsperaMs 24000
```

Los cinco pasos:

1. **`herramientas/compilar.py`** arma el objeto binario. El truco que evita
   escribir un compilador de UserRPL: emite `\<< "<todo el fuente>" STR\-> EVAL \>>`
   y deja que compile la calculadora. Traduce los escapes a los bytes del juego
   de caracteres de la HP, porque **`STR\->` no entiende `\->` ni `\<<`**: eso lo
   traduce el programa de transferencia, no la máquina. Esa fue la primera
   corrida perdida.
2. **`DDE48 s`** pone el objeto en la pila. Con header `HPHP49-X` entra como
   objeto real; sin header, Emu48 lo mete como string inerte (documentado, y
   verificado por accidente).
3. **`PostMessage`** manda la tecla EVAL al handle de la ventana. No usa
   `SendKeys`, así que **no roba el foco**. El KML de 50g mapea las teclas de la
   calculadora en orden alfabético: EVAL es la tecla 42, o sea la `N` del PC
   (la tecla 45 ← Backspace ancla la fila y confirma el corrimiento).
4. **ENTER cada 4 s** durante la espera, porque el CAS abre diálogos modales en
   medio del cálculo (`"Unsigned inf. Solve?"` con el límite de `1/X` en 0) y sin
   contestarlos la batería se cuelga para siempre. ENTER sobre un programa ya
   terminado es un `DUP` del nivel 1, así que no molesta. La batería abre con
   `CLEAR` para que esos duplicados no se acumulen.
5. **`DDE48 r`** trae el nivel 1 y `leer-resultado.py` lo decodifica con
   `hpobj.py` y lo compara.

### Estado: las dos baterías en verde

| Batería | Resultado |
|---|---|
| `casos.txt` (16 casos) | **16 de 16** |
| `casos-escapes.txt` (9 casos) | **9 de 9** |

Lo que encontró en el camino, que es para lo que sirve:

- **`IFERR` no limpia la pila.** `DEPTH \-> D0 \<< IFERR 1 2 0 INV THEN "E" END DEPTH D0 - \>>`
  da **3**, no 1. Corregido en AGENTS.md §2.11, con el rodeo del guardián de
  profundidad. Es un bug latente en `DSEP` y `DSEPI`, que pueden devolver una
  respuesta equivocada sin avisar.
- **El infinito escrito en el fuente funciona**: `TYPE` 9, `LIMIT` calcula, y la
  `m` y la `b` de `DASHO` salen 1 y 0. Falta solo que Conn4x traduzca la grafía
  `\oo` (ver `programas/TESC.txt`).
- **`\>=` y `\<=` son comandos de pila de verdad**, y `\.S` integra: `0 1 'X^2' 'X' ∫`
  da `1/3`.
- **El CAS escribe distinto de como escribimos nosotros**: `'X^2' DERVX` da
  `'X*2'` y `'1/X' 'X' RISCH` da `'LN(ABS(X))'`. Por eso `casos.txt` guarda la
  forma **exacta** de la máquina y la corrección matemática la garantiza
  `oraculo.py` con sympy, por separado.
- **`RISCH` lleva dos argumentos.** La suite ya lo llamaba bien; el caso de
  prueba estaba mal.
- **En modo exacto los enteros son ZINT** (prólogo `02614`), no reales. El lector
  no los conocía.

### Por qué los resultados se etiquetan

Cada elemento vuelve como `"NOMBRE|valor"` y el lector empareja por nombre. En la
primera corrida real un caso devolvió de más y todo lo que seguía quedó corrido
una posición. Emparejar por posición es mentirse.

### El acumulador va en un global

`BRES`, no la pila. Si un caso falla dejando basura apilada (§2.11 otra vez), un
acumulador de pila queda sepultado y los resultados anteriores se pierden en el
nivel 2 — exactamente lo que pasó antes de este cambio.

### oraculo.py: verificar la tabla antes de creerle

```powershell
python oraculo.py casos.txt
```

Comprueba los ESPERADO contra **sympy** en la PC. Comparar la máquina contra una
tabla sin verificar es comparar la máquina contra un error propio. Los 16 casos
pasan; dos quedan "con reserva" porque dependen de cómo escribe la calculadora
un resultado, no de la matemática.

## Ahora prueba la SUITE, no solo el lenguaje

`casos.txt` prueba comandos sueltos de la máquina. Eso está bien pero no dice
nada de nuestros programas. `armar-mat1.py` cierra ese hueco:

```powershell
python armar-mat1.py casos-mat1.txt BMAT1.txt
.\correr-emu.ps1 -Fuente BMAT1.txt -Casos casos-mat1.txt -EsperaMs 180000
```

La batería **se lleva puestos los programas**: por cada nombre en una línea
`USAR:` emite `\<< ...cuerpo del .txt... \>> 'NOMBRE' STO` y después corre los
casos. Así la corrida es reproducible desde cero y no puede heredar una versión
vieja residente en la calculadora, que es el bug de `AGENTS.md` §3.5 (mordió dos
veces: `DBOXPLOT` y `DOLS`). También define `INF` sola, así que no hace falta
haber corrido `DINF` a mano.

Se prueban los núcleos `XXXC`, no los `XXX`: `INFORM` es interactivo por
definición. Por eso los programas de mat1 están partidos en núcleo + interfaz.

| Batería | Qué cubre | Resultado |
|---|---|---|
| `casos-mat1.txt` | los 9 núcleos de los programas con formulario | **33 de 33** (DCONT con laterales) |
| `casos-mat1b.txt` | `LHOP`, `DSEP`, `DSEPI`, `LAGR`, `TCHK`, `TD`, `TF` y los datos | **13 de 13** |
| `casos-lateral.txt` | sondeo: límites laterales `'X=a-0'`/`'X=a+0'` y f(a) fuera del dominio | 14 de 20; los 6 son hallazgos, no fallas (ver `DCONTFC`) |
| `casos-dcontf.txt` | núcleo `DCONTFC` (continuidad de una función que no es a trozos) | **22 de 22** |
| `casos-p1sonda*.txt` (3) | sondeo previo a los de Parcial 1: `OBJ\->`, `SOLVE` con desigualdades, `ZEROS` con Complex prendido y apagado | sin ESPERADO, se miraba el OBTENIDO |
| `casos-ddom.txt` | `DDOMC` y su motor (`DCONDC`, `DSATC`, `DINTC`, `DRELC`): natural, las dos escrituras y el dominio dado | **51 de 51** |
| `casos-dinec.txt` | `DINECC`, con las inecuaciones de los parciales | **25 de 25** |
| `casos-dinec-control.txt` | que el sondeo de control de `DINTC` salte cuando `ZEROS` no alcanza | **5 de 5** |
| `casos-dinv.txt` | `DINVC`, las inversas de los parciales | **26 de 26** |
| `casos-dcontk.txt` | `DCONTKC`, el k de continuidad | **21 de 21** |
| `casos-dpar.txt` | `DPARC`, paridad concreta y abstracta | **22 de 22** |
| `casos-lab2.txt` | Lab de Datos, Parcial 1: `DTABLA2C`, `DZLISTAC`, `DCINCOC`, `DPCTIL2C`, `DLOOPCC`, `DCHEBYC`, `DPONDC`, `DREALC`, con coherencia al bit contra `DCOVCORRC`/`DSTATSC`/`DPCTILC`/`DCOMPZC`; compila tambien las 8 interfaces. Desde el 27/09 tambien los metodos de catedra: DBOXPLOTC con (n+1), DFRECTABLAC automatico con la regla de la diapositiva, DPCTIL2C con Excel .INC | **139 de 139** |
| `casos-dinv-abs.txt` / `casos-dinv-todo.txt` | `DINVC` con modulo (la esquina no es cero de f': antes decia OK con una inversa falsa) y con polos (el sondeo no tiene que confundir un salto con una vuelta); `-todo` suma los 26 de `casos-dinv.txt` | **44 de 44** (02/10/2026) |
| `casos-dasvt.txt` | `DASVTC`: asintotas verticales buscando los candidatos solo | **25 de 25** |
| `casos-dcero.txt` | `DCEROC`: ceros de f, f/g, fog, gof dentro del dominio, sin simplificar | **39 de 39** |
| `casos-ui-nuevas.txt` | que `DASVT` y `DCERO` compilen en la maquina; ademas fotos de las dos interfaces con `pantallas-ui.ps1` (`pantallas/dcero-*`, `dasvt*-*`) | **2 de 2** |
| `casos-sil-*.txt` | sondeo del dialogo "Unsigned inf. Solve?": lo abren el LIMIT lateral en un polo y el prologo `\oo 'INF' STO`; ver AGENTS.md 2.12 | sin ESPERADO, se mira la LCD |

Lo que encontró, que es para lo que sirve:

- **`compilar.py` no traducía la raíz cuadrada.** La tabla de escapes tenía
  `"\v/"` como literal de Python, donde `\v` es **tabulador vertical**: el escape
  no matcheaba nunca y llegaban los tres caracteres literales, que compilan como
  un nombre basura y fallan recién al evaluar. **Invalidó en silencio toda prueba
  con raíces**, incluida la tanda de `domain49` — que resultó manejar bien las
  raíces. La tabla ahora se arma con `chr(92)` y las dos herramientas abortan si
  ven un byte de control.
- **Un resultado complejo no es un error.** Con modo Complex, `\v/(-1)` devuelve
  `(0.,1.)` y `DDOMP` lo contaba como perteneciente al dominio. Se decide por
  `TYPE`, no por banderas.
- **`TCHK` tenía un cimiento podrido adentro**: chequeaba el infinito con
  `\.oo` y daba por bueno un `'1/\.oo'` sin evaluar.
- **`DASHO` llamaba "el CAS no pudo" a una función sin asíntota** (m infinita).

### Cómo comprobar que un carácter especial llegó de verdad

Mirarlo en pantalla no sirve: el nombre basura se dibuja igual que la raíz. Hay
que medir el código.

```
'\v/(X-1)' \->STR 2 2 SUB NUM     @ tiene que dar 131
'\v/(X-1)' \->STR SIZE            @ tiene que dar 8
```

Un control que no puede fallar no es un control.

## Y lo que el harness no reemplaza

Un verde acá es evidencia fuerte —es la ROM de la 50g— pero no es la máquina:
no corre código ARM, y el hardware (teclado, SD, memoria real) queda afuera.
Nada pasa a "verificado" en `SUITE-MAT1.md` §1 por andar en el emulador. Si se
anota un resultado de emulador, anotarlo como tal.

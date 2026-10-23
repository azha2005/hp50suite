# Harness: probar la suite contra la ROM de 50g

## Lotes compactos y recepción segura (23/10/2026)

El generador carga fuentes actuales una sola vez y permite unir tablas,
seleccionar casos y reducir dependencias. No usa una caché residente.

```powershell
python harness/construir.py harness/casos-integ.txt harness/BMOD.txt --mas harness/casos-impl.txt --mas harness/casos-integ-sonda.txt --mas harness/casos-integ-sonda2.txt --sin-inf --min-carga
python harness/construir.py harness/casos-p2-intervalos.txt harness/BINTERVALOS.txt --sin-inf --min-carga
python harness/test_bateria.py
```

`--solo` filtra nombres por expresión regular; `--min-carga` conserva el cierre
transitivo de los objetos declarados en `USAR:` que utilizan esos casos.
También busca nombres en algebraicos y strings compilados en ejecución. Todos
los helpers deben estar declarados: no descubre dependencias fuera de `USAR:`.
`--sin-inf` sólo corresponde a tablas que no necesitan el global INF.

La reducción de una selección de 13 casos pasó de 41 a 28 objetos (50.490 a
37.860 bytes de fuente). Es una medición de tamaño, no de tiempo total. Conviene
separar familias cuando el texto y el objeto compilado juntos consumen la RAM.

Cada lote genera un manifiesto JSON con casos, hashes y una marca única. El
comparador rechaza resultados incompletos, duplicados, sobrantes o de otra
corrida. `HPTSTATE` guarda un diagnóstico y `HPTRESULT` sólo se escribe después
de terminar todos los casos y limpiar los objetos del lote. Esos dos globales
son propios del banco y permanecen para diagnóstico.

### Emu48 instalado: dos fases

DDE POKE y REQUEST pueden corromper memoria si UserRPL está ejecutándose
(advertencia de `Emu48.txt`, sección DDE SERVER). Por eso **no se sondea la pila
en vivo**. ON tampoco demuestra cancelación: un IFERR interno puede capturarlo
y continuar la batería.

```powershell
# Con la calculadora en reposo, sin programa ni diálogo pendiente:
powershell -NoProfile -File harness/correr-emu.ps1 -Fuente harness/BMOD.txt -SoloPreparar
# Ejecutar EVAL; resolver las consultas del CAS y confirmar que terminó.
powershell -NoProfile -File harness/correr-emu.ps1 -Fuente harness/BMOD.txt -SoloRecibir -Bin harness/BMOD.bin
```

El modo normal envía EVAL y espera con ENTER periódico (`-EnterCadaMs 0` lo
desactiva), pero **ya no recibe automáticamente al vencer el tiempo**. Hace
falta confirmar reposo y usar `-SoloRecibir`, que verifica la marca final antes
de comparar. Un archivo sin marca no autoriza recargar otra tanda. No ejecutar
lotes en paralelo; se rechazan varios procesos EMU48 ambiguos.

El runner de Windows conserva su envío de teclas por ventana; el controlador
de escritorio usado durante esta sesión necesita foco y puede interferir con
el teclado humano. Ninguno equivale a un motor headless. El Emu48 instalado
sólo ofrece archivos de estado en su CLI y CONNECT/POKE/REQUEST por DDE. La
[adaptación WebAssembly de Emu48](https://github.com/Claudio-ymt/emu48android-web-version/tree/master/web)
es una candidata para un adaptador aislado; aún no está integrado ni validado.

### Visor y banderas

`armar-visor.py` construye páginas con el mismo `DPANTC` que usa `DPASOS`.
Devuelve GROBs obtenidos por `LCD->` antes del redibujado de pila. Con
`--interactivo` añade dos pasos: OK, tecla, OK, tecla, CANCEL. La salida completa
termina en `VISOR-FIN`. No recibir por DDE mientras esté en INFORM o WAIT.

```powershell
python harness/armar-visor.py harness/BVISOR.txt
python harness/armar-visor.py harness/BVISORUI.txt --interactivo
```

Se revisó una LCD nativa de 131×80 con dos líneas de 20 caracteres completas.
La captura de ventana de Windows falla y la navegación completa del visor
sigue pendiente. Renderizar una página no prueba todos los formularios.

En esta ROM `-100 CF` permite que RISCH termine sin pedir una tecla por paso;
`-100 SF` abrió los pasos nativos. La tabla de banderas del apéndice del
[manual HP](https://www.ele.uri.edu/faculty/vetter/Other-stuff/HP-calculators/HP-50g/HP_50g_advanced_users_reference_manual.pdf)
contradice las entradas de comandos que describen esa bandera. Se usó el
comportamiento medido; los núcleos nuevos conservan y restauran RCLF/STOF.

### Evidencia actual

- Cinco pruebas del comparador/generador en PC: aprobadas.
- Tanda histórica final: 83/84. Se corrigió después la representación del
  infinito positivo en DLATC; repetición de ambos laterales: 2/2 aprobados.
  Falta repetir los 84 juntos sobre esa revisión.
- Tanda previa de 101 casos del módulo: 100/101. El control de fracciones
  racionales se corrigió para verificar cada componente real: 5/5 en su sonda.
  La tanda ampliada de 116 aún no tiene marca final válida; está pendiente,
  no aprobada. No atribuir los resultados anteriores a los últimos fuentes.
- La cúspide compuesta X^(2/3)+X devuelve CEROS NO RESUELTOS y no afirma
  extremos. Ese límite del CAS queda explícito en los casos de borde.
- Conn4x y hardware físico siguen sin validar esta ampliación.

Para comparar un resultado nuevo, siempre pasar el manifiesto de su corrida:

```powershell
python harness/leer-resultado.py harness/BMOD.bin --meta harness/BMOD.json
```

Los lotes antiguos sin manifiesto conservan comparación por tabla, con rechazo
de nombres y cantidades inconsistentes. `armar-mat1.py` conserva la interfaz
anterior y utiliza el mismo generador.

---

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

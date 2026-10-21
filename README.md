# hp50suite

**English** · [Español](#español)

**UserRPL programs for the HP 50g that solve university exercises the way the
exam asks for them: with the intermediate steps on screen, not just the answer.**

Written for three courses of the Economics degree at FCE-UNLP (Argentina):
*Laboratorio de Datos* (statistics), *Microeconomía I* and *Matemática I*
(calculus). The methods come from the course's own slides, worked solutions
and past exams, so the programs give the numbers the course expects.

Everything is plain UserRPL text, made for a real HP 50g and sent to it with
Conn4x. Nothing to compile and nothing to install on the PC.

## What's in it

| Area | Programs | Examples |
|---|---|---|
| Descriptive statistics | 12 | mean/variance/CV, mode, percentiles (three methods), frequency table, histogram, boxplot, z-scores, Chebyshev, weighted mean |
| Two variables | 3 | covariance and Pearson's r with scatter plot, OLS regression, deviation table with column sums |
| Economics | 6 | market equilibrium, taxes and subsidies (incidence, deadweight loss, price controls), the competitive firm, PPP GDP, CAGR, real variation |
| Calculus I | 25 | domain, inequalities, inverse functions, parity, continuity, asymptotes, derivative by definition, tangent and normal lines, Ruffini, Bolzano (bisection), Weierstrass, l'Hôpital, separable ODEs, Lagrange multipliers |
| Other | 2 | step through a `while` loop (exam question), plot a piecewise function |

Each program asks for its inputs with an `INFORM` form and answers in
`MSGBOX` boxes. You can type data as a list `{ 2 4 6 }` or a vector `[ 2 4 6 ]`,
or give the name of a stored variable.

Full reference, with a worked example for each program (in Spanish):
[`DICCIONARIO-LAB.md`](DICCIONARIO-LAB.md) (statistics and economics) and
[`DICCIONARIO-MAT1.md`](DICCIONARIO-MAT1.md) (calculus).

## Install

1. Install [Conn4x](https://www.hpcalc.org/) and connect the 50g over USB.
2. Send `programas/LAB.txt` (statistics and economics) and/or
   `programas/MAT1.txt` (calculus). Each one arrives as a single folder holding
   every program.
3. Optional: send the course datasets in `programas/datos/` (`BM5X`, `BMHIST`,
   `HORAS`…). You can then type their names into any "Datos" field.

`programas/README.md` covers the details: load order, the `DINF` one-time setup
for asymptotes, and how to load single programs.

## How it is built

- **A calculation core and an interface for each program.** `DSTATSC`
  computes and `DSTATS` shows the form and the boxes. The core goes in and out
  through the stack, so it can be tested without anyone typing into the form.
  Programs that draw also have a `…G` layer that draws without waiting for a key.
- **Tested on the 50g ROM.** The cores run in an emulator with the real HP 50g
  ROM, against the course datasets and the exercises' own results: several
  hundred cases, including pixel checks on the plots. The emulator is not the
  calculator, so try each program on the real machine before an exam.
- **Every rule was learned from a real bug.** [`CLAUDE.md`](CLAUDE.md)
  collects the UserRPL traps found along the way: `FOR` always runs at least
  once, `IFERR` doesn't clean the stack, `\.oo` isn't infinity, and several
  CAS commands give a plausible answer that is silently wrong.
- `verificar.ps1` checks each source before it is sent: nesting depth,
  orphaned `\<<` blocks, 7-bit ASCII, control bytes, `END` balance, CRLF line
  endings.

## Status

| | |
|---|---|
| Statistics and economics | 259 cases passing in the emulator |
| Calculus I | every program has an emulator test battery |
| Real hardware | the older programs, yes; the latest ones only in the emulator |
| Pending | macroeconomic model, monopoly, Cobb-Douglas, nonlinear fitting, area between curves, improper integrals |

## Credits

`Graf/` holds a third-party graphing suite (author `au777fait@gmail.com`), kept
as a reference for the native plotting path. It is not part of this suite.

## License

[MIT](LICENSE), except `Graf/`, which belongs to its author.

---

## Español

**Programas en UserRPL para la HP 50g que resuelven los ejercicios como los
pide el parcial: con los pasos intermedios en pantalla, no solo el resultado.**

Hechos para tres materias de la Lic. en Economía (FCE-UNLP): Laboratorio de
Datos, Microeconomía I y Matemática I. Los métodos salen del material de la
cátedra (diapositivas, resoluciones y parciales viejos), así que los
resultados coinciden con los de la cátedra.

- **Qué hay:** estadística descriptiva, dos variables, mercado e impuestos,
  empresa competitiva y un parcial entero de Matemática I. La lista completa,
  con un ejemplo de cada programa, está en
  [`DICCIONARIO-LAB.md`](DICCIONARIO-LAB.md) y
  [`DICCIONARIO-MAT1.md`](DICCIONARIO-MAT1.md).
- **Instalar:** pasar `programas/LAB.txt` y/o `programas/MAT1.txt` con Conn4x.
  Cada uno llega como una carpeta con todos los programas adentro. Los datos de
  la cátedra están en `programas/datos/`. El detalle está en
  [`programas/README.md`](programas/README.md).
- **Usar:** cada programa pide sus datos en un formulario y responde en cajas.
  Apretar OK para pasar de una caja a la siguiente.
- **Ojo:** está probado en un emulador con la ROM de la 50g, que no es la
  calculadora. Antes del parcial, correr en la tuya un ejemplo de cada
  programa que vayas a usar.

Las reglas de UserRPL y el porqué de cada decisión están en
[`CLAUDE.md`](CLAUDE.md).

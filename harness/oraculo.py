# -*- coding: ascii -*-
"""oraculo.py - verifica que los ESPERADO de casos.txt sean correctos.

    python oraculo.py [casos.txt]

El harness compara lo que devuelve la calculadora contra casos.txt. Eso no vale
nada si casos.txt esta mal: seria comparar la maquina contra un error propio.
Este script comprueba cada esperado contra sympy en la PC, ANTES de correr nada.

Es la division de trabajo que hace falta con un CAS: la tabla guarda la forma
EXACTA que escribe la maquina ('X*2', 'LN(ABS(X))'), porque es lo unico que
permite detectar un cambio de comportamiento; y el oraculo comprueba que esa
forma sea matematicamente la correcta, que es lo que la comparacion de texto no
puede saber.

Dos casos quedan "con reserva": los que dependen de COMO escribe la calculadora
un resultado (la posicion del caracter 159 en el string del infinito). Ahi sympy
confirma la parte matematica -que el limite sea infinito o no- y la posicion se
verifica en la maquina.
"""
import sys

import sympy as sp

X, Y = sp.symbols("X Y", real=True)
F = (X ** 2 + 1) / X

# nombre -> (verificacion(esperado_parseado) -> bool, nota)
REGLAS = {
    "DERVX":         (lambda e: sp.simplify(e - sp.diff(X ** 2, X)) == 0, ""),
    "DERIV":         (lambda e: sp.simplify(e - sp.diff(X ** 2 * Y, X)) == 0, ""),
    "RISCH":         (lambda e: derivada_es(e, 1 / X),
                      "se verifica derivando y evaluando: la primitiva de la HP "
                      "lleva valor absoluto y la de sympy no, pero las dos "
                      "derivan a 1/X. sympy no simplifica sign(X)/ABS(X) - 1/X "
                      "a cero por su cuenta"),
    "ZEROS":         (lambda e: sorted(e) == [-1, 1], ""),
    "SUBST":         (lambda e: e == 7, ""),
    "LIMIT-finito":  (lambda e: e == sp.limit((X ** 2 - 1) / (X - 1), X, 1), ""),
    "DDEF-cociente": (lambda e: sp.simplify(e - 2 * X) == 0, ""),
    "DTANOR-pend":   (lambda e: e == sp.diff(X ** 2, X).subs(X, 1), ""),
    "DESTFUN-fp":    (lambda e: sp.simplify(e - sp.diff(F, X)) == 0, ""),
    "DESTFUN-fpp":   (lambda e: sp.simplify(e - sp.diff(F, X, 2)) == 0, ""),
    "DOPFUN-comp":   (lambda e: sp.simplify(e - sp.expand((X + 1) ** 2)) == 0, ""),
    "DVFG-dif":      (lambda e: e == 0, ""),
    "DASV-umbral":   (lambda e: e == 10 ** 6, ""),
    "DASV-compara":  (lambda e: e == 1 and 10 ** 6 > 100000,
                      "el umbral que estaba mal: con 1e6 > 1e6 daba falso"),
    "DCONT-inf":     (lambda e: e == 3 and sp.limit(1 / X, X, 0, "+") is sp.oo,
                      "parcial: sympy confirma que el limite es infinito; que el "
                      "caracter caiga en la posicion 3 sale de que \->STR "
                      "devuelve '+oo', con comillas y con signo"),
    "DCONT-noinf":   (lambda e: e == 0 and sp.limit(X, X, 0) == 0,
                      "parcial: limite finito, asi que POS tiene que dar 0"),
}


def derivada_es(primitiva, integrando, puntos=(2.0, -3.0, 0.5, -0.25)):
    """Comprueba una primitiva derivandola y evaluandola en varios puntos.

    Hace falta porque LN(ABS(X)) y log(X) son las dos primitivas de 1/X y sympy
    no reduce sign(X)/ABS(X) - 1/X a cero solo.
    """
    d = sp.diff(primitiva, X)
    for v in puntos:
        try:
            if abs(complex(d.subs(X, v)) - complex(integrando.subs(X, v))) > 1e-9:
                return False
        except TypeError:
            return False
    return True


def parsear(t):
    """Pasa la notacion de la HP a algo que sympy entienda."""
    t = t.strip()
    if t.startswith("{") and t.endswith("}"):
        return [sp.Integer(x) for x in t[1:-1].split()]
    t = t.replace("^", "**").replace("LN(", "log(").replace("ABS(", "Abs(")
    # Hay que pasarle NUESTROS simbolos: sympify crea los suyos sin asunciones,
    # y X(sin asunciones) - X(real) no se simplifica a cero. Costo siete MAL.
    return sp.sympify(t, locals={"X": X, "Y": Y})


def leer_casos(ruta):
    casos = []
    with open(ruta) as f:
        for l in f:
            t = l.strip()
            if not t or t.startswith("#"):
                continue
            p = t.split("|")
            if len(p) >= 3:
                casos.append((p[0].strip(), "|".join(p[2:]).strip()))
    return casos


def main():
    ruta = sys.argv[1] if len(sys.argv) > 1 else "casos.txt"
    casos = leer_casos(ruta)
    print("Verificando los ESPERADO de %s contra sympy %s\n" % (ruta, sp.__version__))
    print("%-16s %-24s %s" % ("CASO", "ESPERA casos.txt", ""))
    print("-" * 70)
    mal = reservas = sin_regla = 0
    for nombre, esperado in casos:
        if nombre not in REGLAS:
            print("%-16s %-24s sin oraculo" % (nombre, esperado[:24]))
            sin_regla += 1
            continue
        regla, nota = REGLAS[nombre]
        try:
            ok = bool(regla(parsear(esperado)))
        except Exception as e:
            ok = False
            nota = (nota + " | no se pudo parsear: %s" % e).strip(" |")
        if not ok:
            mal += 1
        if nota.startswith("parcial"):
            reservas += 1
        print("%-16s %-24s %s" % (nombre, esperado[:24], "ok" if ok else "MAL"))
        if nota:
            print("%-16s   ^ %s" % ("", nota))
    print("\n%d bien, %d con reserva, %d MAL, %d sin oraculo."
          % (len(casos) - mal - sin_regla, reservas, mal, sin_regla))
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(main())

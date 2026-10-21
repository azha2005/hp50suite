# -*- coding: ascii -*-
"""leer-pantalla.py - lee el TEXTO de una pantalla capturada con LCD\->.

    python leer-pantalla.py fuente.bin              # arma/actualiza la tabla
    python leer-pantalla.py pantalla.bin            # lee la pantalla

Hace falta porque Domain no devuelve texto: dibuja la respuesta en la pantalla
con \->GROB y la deja ahi. La unica forma de leerla desde la PC es capturar la
pantalla (LCD\->), traerla por DDE y reconocer los glifos.

La tabla de glifos no se adivina: se le pide a la calculadora con
`32 126 FOR n n CHR 1 \->GROB 1 \->LIST + NEXT`, que devuelve un GROB por
caracter. La fuente chica resulto ser FIJA de 4x6, asi que reconocer es cortar
cada 4 columnas y buscar en la tabla.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "herramientas"))
import hpobj                                            # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
# Dos fuentes: la chica (1 \->GROB) y la de pretty-print (0 \->GROB). Domain
# usa las dos en la misma respuesta: los intervalos en la chica y el conjunto de
# puntos excluidos en la grande.
TABLAS = [(4, 6, os.path.join(AQUI, "fuente-4x6.json")),
          (6, 8, os.path.join(AQUI, "fuente-6x8.json"))]
# El orden en que se pidieron los glifos.
ORDEN = [chr(c) for c in range(32, 127)] + ["oo", "v/", "pi"]


def clave(filas, ancho, alto):
    return "".join("".join("1" if (f[j] if j < len(f) else 0) else "0"
                           for j in range(ancho)) for f in filas[:alto])


def grobs_de(ruta):
    L = hpobj.Lector(open(ruta, "rb").read())
    try:
        L.run()
    except IndexError:
        pass
    return L.grobs


def armar_tabla(ruta):
    gs = grobs_de(ruta)
    ancho, alto = gs[0][0], gs[0][1]
    destino = [t for (a, b, t) in TABLAS if (a, b) == (ancho, alto)]
    destino = destino[0] if destino else os.path.join(AQUI, "fuente-%dx%d.json" % (ancho, alto))
    if len(gs) != len(ORDEN):
        print("Ojo: %d glifos pero %d caracteres esperados" % (len(gs), len(ORDEN)))
    tabla = {}
    for (w, h, filas), ch in zip(gs, ORDEN):
        tabla[clave(filas, w, h)] = ch
    with open(destino, "w") as f:
        json.dump(tabla, f, indent=0, sort_keys=True)
    print("Tabla %dx%d guardada en %s: %d glifos distintos de %d caracteres"
          % (ancho, alto, os.path.basename(destino), len(tabla), len(gs)))
    return tabla


def leer(ruta, tablas, sin_menu=70):
    for n, (w, h, filas) in enumerate(grobs_de(ruta), 1):
        # Se agrupan las filas con contenido en lineas de texto.
        llenas = [i for i in range(min(h, sin_menu)) if any(filas[i])]
        if not llenas:
            print("GROB %d (%dx%d): pantalla vacia" % (n, w, h))
            continue
        lineas, act = [], [llenas[0]]
        for i in llenas[1:]:
            if i - act[-1] <= 1:
                act.append(i)
            else:
                lineas.append(act); act = [i]
        lineas.append(act)
        print("GROB %d (%dx%d): %d linea(s) de texto" % (n, w, h, len(lineas)))
        for ln in lineas:
            r0 = ln[0]
            # El texto no siempre arranca en una columna multiplo de 4 (Domain
            # centra algunas respuestas), asi que se prueban los cuatro desfases
            # y gana el que deja menos glifos sin reconocer.
            mejor, mejorInfo, mejorMal = "", "", 10 ** 9
            for (cw, ch_, tabla) in tablas:
                sub = [filas[r0 + k] if r0 + k < h else [0] * w for k in range(ch_)]
                for desf in range(cw):
                    texto, x, mal, vistos = "", desf, 0, 0
                    while x + cw <= w:
                        k = clave([f[x:x + cw] for f in sub], cw, ch_)
                        if k == "0" * (cw * ch_):
                            texto += " "
                        else:
                            vistos += 1
                            c = tabla.get(k)
                            if c is None:
                                texto += "?"
                                mal += 1
                            else:
                                texto += c
                        x += cw
                    if vistos and mal < mejorMal:
                        mejor, mejorMal = texto, mal
                        mejorInfo = "%dx%d desfase %d" % (cw, ch_, desf)
            aviso = "" if mejorMal == 0 else "   (%d sin reconocer)" % mejorMal
            print("   fila %2d [%s]: %s%s" % (r0, mejorInfo, mejor.strip(), aviso))


def main():
    ruta = sys.argv[1]
    if os.path.basename(ruta).startswith("fuente"):
        armar_tabla(ruta)
        return 0
    tablas = []
    for (a, b, t) in TABLAS:
        if os.path.exists(t):
            with open(t) as f:
                tablas.append((a, b, json.load(f)))
    if not tablas:
        print("Faltan las tablas. Correr: python leer-pantalla.py fuente.bin")
        return 1
    leer(ruta, tablas)
    return 0


if __name__ == "__main__":
    sys.exit(main())

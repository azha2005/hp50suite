# -*- coding: ascii -*-
"""ver-grob.py - dibuja en la terminal los GROB que haya en un objeto de HP.

    python ver-grob.py salida.bin

Domain devuelve su respuesta como GROB: arma la notacion de intervalos con
\->GROB y la pega con BLANK/REPL. No hay texto que comparar, asi que la unica
forma de leer el resultado desde la PC es decodificar el bitmap y dibujarlo.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "herramientas"))
import hpobj                                            # noqa: E402

LLENO, VACIO = "#", "."


def dibujar(ancho, alto, filas, escala=1):
    print("   +" + "-" * ancho + "+")
    for f in filas:
        print("   |" + "".join(LLENO if b else VACIO for b in f) + "|")
    print("   +" + "-" * ancho + "+   (%dx%d)" % (ancho, alto))


def main():
    data = open(sys.argv[1], "rb").read()
    L = hpobj.Lector(data)
    try:
        L.run()
    except IndexError:
        pass
    if not L.grobs:
        print("No hay GROB en %s. Tokens: %s"
              % (sys.argv[1], [(t[1], t[2]) for t in L.tokens][:12]))
        return 1
    for i, (ancho, alto, filas) in enumerate(L.grobs, 1):
        print("GROB %d:" % i)
        dibujar(ancho, alto, filas)
        print("")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: ascii -*-
"""ver-dibujo.py - dibuja en ASCII los GROBs que vuelven de la calculadora.

    python ver-dibujo.py graf.bin [nombre1 nombre2 ...]

Las aserciones con PIX? prueban que tal pixel este encendido, pero no que el
dibujo ENTERO tenga sentido. Esto es el complemento: mirarlo. Se comprime
verticalmente de a 2 filas para que una pantalla de 131x64 entre en la
terminal sin deformarse tanto.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "herramientas"))
import hpobj                                            # noqa: E402


def main():
    ruta = sys.argv[1]
    nombres = sys.argv[2:]
    L = hpobj.Lector(open(ruta, "rb").read())
    try:
        L.run()
    except IndexError:
        pass
    for n, (w, h, filas) in enumerate(L.grobs):
        etiqueta = nombres[n] if n < len(nombres) else "grob %d" % (n + 1)
        print("=== %s  (%dx%d) ===" % (etiqueta, w, h))
        for y in range(0, h, 2):
            linea = []
            for x in range(w):
                a = filas[y][x] if x < len(filas[y]) else 0
                b = filas[y + 1][x] if y + 1 < h and x < len(filas[y + 1]) else 0
                linea.append("#" if (a and b) else (":" if (a or b) else " "))
            print("".join(linea).rstrip())
        print()


if __name__ == "__main__":
    main()

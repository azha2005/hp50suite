# -*- coding: ascii -*-
"""armar-mat1.py - bateria que CARGA los programas de mat1 y los corre.

    python armar-mat1.py casos-mat1.txt BMAT1.txt

Diferencia con armar-bateria.ps1: aquella prueba comandos sueltos de la
maquina (DERVX, RISCH, la integral). Esta prueba NUESTROS programas.

Para eso el programa bajo prueba tiene que estar en la calculadora. En vez de
instalarlo a mano, la bateria se lo lleva puesto: por cada objeto emite

    \<< ...cuerpo del .txt... \>> 'NOMBRE' STO

y despues corre los casos. Asi la corrida es reproducible desde cero y no
depende de que haya quedado instalado de una corrida anterior, que es
justamente el bug que AGENTS.md 3.5 documenta (DBOXPLOT y DOLS dieron
resultados viejos por una version residente).

Se prueban los nucleos XXXC, no los XXX: el formulario INFORM es interactivo
por definicion y no se puede correr desde una bateria. Por eso los programas
estan partidos en nucleo + interfaz.

Formato del archivo de casos, igual al de armar-bateria.ps1:
    nombre | expresion UserRPL | resultado esperado
Las lineas que empiezan con  USAR:  nombran los objetos a cargar.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
PROG = os.path.normpath(os.path.join(AQUI, "..", "programas"))
# Se busca primero en mat1/ y despues en programas/: los de Matematica I y los
# de Laboratorio de Datos viven en carpetas distintas pero se prueban igual.
DIRS = [os.path.join(PROG, "mat1"), PROG,
        # Los datasets de la catedra (BM5X, HORAS...).
        os.path.join(PROG, "datos")]


def cuerpo(nombre):
    """El .txt sin el header de transferencia: queda el \<< ... \>> pelado."""
    for d in DIRS:
        ruta = os.path.join(d, nombre + ".txt")
        if os.path.exists(ruta):
            break
    else:
        raise SystemExit("No encontre %s.txt en %s" % (nombre, DIRS))
    lineas = open(ruta, "rb").read().decode("ascii").replace("\r\n", "\n").split("\n")
    return [l for l in lineas if not l.startswith("%%HP:")]


def main():
    casos_txt, salida = sys.argv[1], sys.argv[2]
    usar, casos = [], []
    for l in open(casos_txt):
        t = l.strip()
        if not t or t.startswith("#"):
            continue
        if t.startswith("USAR:"):
            usar += t[5:].replace(",", " ").split()
            continue
        p = t.split("|")
        if len(p) < 3:
            print("Linea ignorada: %s" % t)
            continue
        casos.append((p[0].strip(), p[1].strip(), "|".join(p[2:]).strip()))
    if not casos:
        raise SystemExit("Sin casos en %s" % casos_txt)

    out = ["%%HP: T(3)A(R)F(.);",
           "@ Generado por harness/armar-mat1.py desde %s" % os.path.basename(casos_txt),
           "@ Carga %d objeto(s) de programas y corre %d caso(s)."
           % (len(usar), len(casos)),
           "@ Salida generada: no editar a mano.",
           "\<<",
           "  CLEAR",
           # El infinito del CAS. Se escribe con el escape \oo, que compilar.py
           # traduce al caracter 159 del juego de la HP. Medido: TYPE 9
           # (algebraico) y LIMIT calcula de verdad con el. Asi la bateria no
           # depende de que alguien haya corrido DINF a mano en la maquina.
           "  \oo 'INF' STO"]
    for n in usar:
        out.append("  @ ---- carga %s ----" % n)
        out += ["  " + l for l in cuerpo(n) if l.strip()]
        out.append("  '%s' STO" % n)
    out.append("  { } 'BRES' STO")
    for nombre, expr, esperado in casos:
        out.append("  @ %s -> espera: %s" % (nombre, esperado))
        out.append('  IFERR %s \->STR THEN "ERROR" END "%s|" SWAP + '
                   "1 \->LIST BRES SWAP + 'BRES' STO" % (expr, nombre))
    out.append("  BRES")
    # Se limpia todo lo que la bateria creo, para que la proxima corrida
    # arranque igual de limpia y no herede nada.
    out.append("  { BRES INF %s } PURGE" % " ".join(usar))
    out.append("\>>")

    texto = "\r\n".join(out) + "\r\n"
    datos = texto.encode("ascii")
    # Guardia contra la trampa historica del proyecto: una barra invertida
    # seguida de letra dentro de un literal de Python se vuelve un byte de
    # control (el caso famoso fue  -> tabulador vertical, y aca aparecio
    #  -> BEL). Son ASCII, asi que el chequeo de 7 bits de AGENTS.md 1 NO
    # los ve, y viajan invisibles hasta la calculadora. Se corta aca.
    malos = sorted({b for b in bytearray(datos)
                    if b < 32 and b not in (9, 10, 13)})
    if malos:
        raise SystemExit("BYTES DE CONTROL en la salida: %s (revisar los "
                         "literales con barra invertida)" % malos)
    open(salida, "wb").write(datos)
    print("%s: %d objeto(s), %d caso(s), %d bytes"
          % (os.path.basename(salida), len(usar), len(casos), len(datos)))


if __name__ == "__main__":
    main()

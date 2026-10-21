# -*- coding: ascii -*-
"""armar-ui.py - arma un programa que CARGA objetos de la suite y arranca una
INTERFAZ (la que tiene INFORM), para manejarla con teclas y sacarle fotos.

    python armar-ui.py salida.txt DTABLA2 DTABLA2C DCOVCORRC DSTATSC

El primer nombre es el programa que se arranca; todos se cargan con
\\<< ...cuerpo... \\>> 'NOMBRE' STO, igual que armar-mat1.py. A diferencia de
aquel, no corre casos ni purga nada al final: la interfaz se queda esperando
en el INFORM, y quien maneja las teclas es pantallas-ui.ps1.

Es el complemento de las baterias: esas prueban los nucleos XXXC (el calculo),
esto mira las interfaces XXX (el formulario y las cajas), que una bateria no
puede correr porque INFORM espera teclas.
"""
import importlib.util
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("armar_mat1",
                                               os.path.join(AQUI, "armar-mat1.py"))
_m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m)


def main():
    salida, nombres = sys.argv[1], sys.argv[2:]
    if not nombres:
        raise SystemExit("uso: armar-ui.py salida.txt PROGRAMA [OBJETOS...]")
    out = ["%%HP: T(3)A(R)F(.);",
           "@ Generado por harness/armar-ui.py: carga %d objeto(s) y arranca %s."
           % (len(nombres), nombres[0]),
           "@ Salida generada: no editar a mano.",
           "\\<<",
           "  CLEAR"]
    for n in nombres:
        out.append("  @ ---- carga %s ----" % n)
        out += ["  " + l for l in _m.cuerpo(n) if l.strip()]
        out.append("  '%s' STO" % n)
    out.append("  %s" % nombres[0])
    out.append("\\>>")
    datos = ("\r\n".join(out) + "\r\n").encode("ascii")
    malos = sorted({b for b in bytearray(datos) if b < 32 and b not in (9, 10, 13)})
    if malos:
        raise SystemExit("BYTES DE CONTROL en la salida: %s" % malos)
    open(salida, "wb").write(datos)
    print("%s: %d objeto(s), arranca %s, %d bytes"
          % (os.path.basename(salida), len(nombres), nombres[0], len(datos)))


if __name__ == "__main__":
    main()

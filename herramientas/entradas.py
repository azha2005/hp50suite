# -*- coding: ascii -*-
"""entradas.py - tabla direccion -> nombre de entrada SysRPL.

La arma desde Suprom49.a, la lista de entry points del HP49G que instala
Debug4x en Documents\Debug4x\Include. Formato de cada linea:

    =NOMBRE         EQU     #ADDR   [comentario]

Varios nombres pueden compartir direccion; se elige el mas corto y, a igual
largo, el alfabeticamente primero, para que el listado quede estable.
"""
import os
import re

RUTA = os.path.join(os.path.expanduser("~"), "Documents", "Debug4x",
                    "Include", "Suprom49.a")

LINEA = re.compile(r"^=(\S+)\s+EQU\s+#([0-9A-Fa-f]{5})\b")


def cargar(ruta=None):
    ruta = ruta or RUTA
    tabla = {}
    with open(ruta, "r") as f:
        for l in f:
            m = LINEA.match(l)
            if not m:
                continue
            nombre, addr = m.group(1), int(m.group(2), 16)
            ant = tabla.get(addr)
            if ant is None or (len(nombre), nombre) < (len(ant), ant):
                tabla[addr] = nombre
    return tabla


if __name__ == "__main__":
    t = cargar()
    print("entradas:", len(t))
    for a in (0x35289, 0x02D9D, 0x0312B, 0x389B9):
        print("  %05X -> %s" % (a, t.get(a, "(sin nombre)")))

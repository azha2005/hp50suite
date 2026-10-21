# -*- coding: ascii -*-
"""descompilar.py - reconstruye el fuente UserRPL de un objeto binario de HP.

    python descompilar.py OBJETO [> salida.txt]

Combina hpobj.py (estructura a nivel nibble) con entradas.py (tabla
direccion -> nombre, sacada del Suprom49.a que instala Debug4x). Si el objeto
es UserRPL, el 100% de las direcciones se resuelve y sale codigo legible.

Lo que NO reconstruye, y hay que tenerlo presente al leer:
  - comentarios y sangria originales (no viajan en el objeto),
  - los nombres de los XLIB (referencias a comandos de libreria): quedan como
    `XLIB lib cmd`. Son pocos y se nombran en el emulador.
  - ojo: los nombres salen de la tabla de entradas de SysRPL, y algunos no se
    escriben igual que en el fuente. El caso claro es `SQRT`, que en UserRPL se
    tipea `\v/` (ya se traduce). Si aparece un nombre raro, cotejarlo contra
    Suprom49.a antes de copiarlo a codigo propio.
  - un objeto SysRPL sale con sus entradas internas, no como UserRPL.

El objeto puede venir envuelto: si el primer prologo no es DOCOL se busca el
primer DOCOL cuyo parseo llegue justo al final del archivo.
"""
import sys
import hpobj
import entradas

# Nombres de comando que no se escriben igual que la entrada.
RENOMBRE = {
    "x<<": "\<<", "x>>": "\>>",
    "xRPN->": "\->",
    "x#?": "\=/", "x<=?": "\<=", "x>=?": "\>=",
    "x>>ABND": "\>>",              # cierra el scope de un \-> ... \<<
    "xSQRT": "\\v/",                 # el nombre de entrada es SQRT; se escribe \v/
    "xSTARTVAR": "FOR",             # FOR con variable; xSTART es START
    "xTHENCASE": "THEN",            # el THEN de una rama de CASE
    "xIFEND": "END", "xERREND": "END", "xWHILEEND": "END",
    "xDOEND": "END", "xCASEEND": "END", "xENDSUB": "END",
}
ABREN = set(["\<<", "IF", "THEN", "ELSE", "FOR", "START", "DO", "WHILE",
             "IFERR", "CASE", "REPEAT"])
CIERRAN = set(["\>>", "END", "NEXT", "STEP", "UNTIL", "THEN", "ELSE",
               "REPEAT"])
PROPIA_LINEA = ABREN | CIERRAN | set(["IF", "IFERR", "CASE", "UNTIL", "NEXT",
                                      "STEP"])


def nombre_comando(n):
    if n in RENOMBRE:
        return RENOMBRE[n]
    if n.startswith("x"):
        n = n[1:]
    elif n.startswith("%"):          # constante real de ROM: %1, %0, %pi
        return n[1:] if n[1:] else n
    if n in (">", "<", "==", "+", "-", "*", "/", "^"):
        return n                      # comparadores y operadores, tal cual
    # Lo que queda con ">" es una flecha, no una comparacion: los
    # comparadores ya salieron arriba y >= <= >> tienen nombre propio.
    return n.replace("->", "\->").replace(">", "\->")


def buscar_inicio(nib):
    """Devuelve el nibble donde arranca el objeto RPL de verdad."""
    if hpobj.leer(nib, 0, 5)[0] == 0x02D9D:
        return 0
    for p in range(len(nib) - 5):
        if hpobj.leer(nib, p, 5)[0] != 0x02D9D:
            continue
        L = hpobj.Lector(b"")
        L.nib = nib
        try:
            if L.objeto(p, 0) == len(nib):
                return p
        except IndexError:
            pass
    return 0


def descompilar(data):
    if data[:5] == b"HPHP4":
        data = data[8:]
    nib = hpobj.nibbles(data)
    ini = buscar_inicio(nib)
    L = hpobj.Lector(b"")
    L.nib = nib
    fin = L.objeto(ini, 0)
    T = entradas.cargar()

    piezas = []          # (texto, es_estructura)
    tick = False
    sin_resolver = 0
    for prof, tipo, txt, addr in L.tokens:
        if tipo in ("PROG", "PROG2", "LIST", "SYMB", "SEMI"):
            if tipo == "LIST":
                piezas.append(("{" if txt == "{ABRE}" else "}", False))
            elif tipo == "SYMB":
                piezas.append(("'" if txt == "{ABRE}" else "'", False))
            continue
        if tipo == "ADDR":
            n = T.get(addr)
            if n is None:
                sin_resolver += 1
                piezas.append(("@%05X" % addr, False))
                continue
            if n == "xSILENT'":
                continue
            if n == "x'":
                tick = True
                continue
            if n == "xENDTIC":
                if piezas:
                    piezas[-1] = (piezas[-1][0] + "'", piezas[-1][1])
                continue
            c = nombre_comando(n)
            piezas.append((c, c in PROPIA_LINEA))
            continue
        t = txt
        if tick:
            t = "'" + t
            tick = False
        piezas.append((t, False))

    return piezas, ini, fin, len(nib), sin_resolver


def formatear(piezas, ancho=68):
    lineas = []
    ind = 0
    buf = ""

    def volcar():
        nonlocal buf
        if buf.strip():
            lineas.append("  " * ind + buf.strip())
        buf = ""

    for txt, estructura in piezas:
        if estructura:
            volcar()
            if txt in CIERRAN and ind > 0:
                ind -= 1
            lineas.append("  " * ind + txt)
            if txt in ABREN:
                ind += 1
            continue
        if len(buf) + len(txt) + 1 > ancho:
            volcar()
        buf += (" " if buf else "") + txt
    volcar()
    return lineas


def main():
    ruta = sys.argv[1]
    data = open(ruta, "rb").read()
    piezas, ini, fin, total, sr = descompilar(data)
    print("%%HP: T(3)A(R)F(.);")
    print("@ DESCOMPILADO de %s por herramientas\descompilar.py" % ruta)
    print("@ Objeto RPL entre los nibbles %d y %d de %d." % (ini, fin, total))
    print("@ Sin comentarios ni sangria original. %d direcciones sin resolver."
          % sr)
    print("@ FUENTE DE TERCEROS - solo lectura, no transferir.")
    for l in formatear(piezas):
        print(l)


if __name__ == "__main__":
    main()

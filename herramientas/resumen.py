# -*- coding: ascii -*-
"""resumen.py - que hay adentro de un objeto binario de HP, sin leerlo entero.

    python resumen.py ARCHIVO [--prog N]

Sirve para triage: imprime los strings, los nombres globales y el inventario de
comandos de un objeto, sin importar si es programa, directorio o libreria.
Escanea el stream de nibbles buscando objetos DOCOL que parseen limpio, asi que
funciona igual con librerias, cuyo encabezado no se interpreta.

--prog N descompila el N-esimo programa rescatado (el mas grande es el 1).
"""
import collections
import sys

import entradas
import hpobj


def rescatar(data):
    """Devuelve los programas DOCOL que parsean limpio, de mayor a menor,
    sin los que estan contenidos dentro de otro."""
    if data[:5] == b"HPHP4":
        data = data[8:]
    nib = hpobj.nibbles(data)
    encontrados = []
    p = 0
    while p < len(nib) - 5:
        if hpobj.leer(nib, p, 5)[0] != 0x02D9D:
            p += 1
            continue
        L = hpobj.Lector(b"")
        L.nib = nib
        try:
            fin = L.objeto(p, 0)
        except IndexError:
            p += 1
            continue
        if fin - p > 40 and not any(t[1] == "TRUNCADO" for t in L.tokens):
            encontrados.append((p, fin, L.tokens))
            p = fin            # lo de adentro ya esta cubierto
        else:
            p += 1
    encontrados.sort(key=lambda e: e[0] - e[1])
    return encontrados, nib


def emitir(t):
    """La consola de Windows no siempre banca lo que traen estos objetos."""
    try:
        print(t)
    except UnicodeEncodeError:
        print(t.encode("ascii", "replace").decode("ascii"))


def main():
    ruta = sys.argv[1]
    data = open(ruta, "rb").read()
    progs, nib = rescatar(data)
    T = entradas.cargar()

    if "--prog" in sys.argv:
        i = int(sys.argv[sys.argv.index("--prog") + 1]) - 1
        import descompilar
        ini, fin, tokens = progs[i]
        L = hpobj.Lector(b"")
        L.nib = nib
        L.objeto(ini, 0)
        piezas, _, _, _, _ = descompilar.descompilar(b"")  # solo para el formato
        # se rehace con los tokens ya obtenidos
        sys.argv = [sys.argv[0], ruta]
        print("@ programa %d de %s: nibbles %d..%d" % (i + 1, ruta, ini, fin))
        return

    print("=" * 74)
    print(ruta, "-", len(data), "bytes,", len(progs), "programas rescatados")
    print("=" * 74)

    strings, idnts, cmds = [], [], collections.Counter()
    for ini, fin, tokens in progs:
        for prof, tipo, txt, addr in tokens:
            if tipo == "STRING":
                strings.append(txt)
            elif tipo == "IDNT":
                idnts.append(txt)
            elif tipo == "ADDR":
                n = T.get(addr)
                if n and n.startswith("x"):
                    cmds[n[1:]] += 1

    print("\n-- tamanos (nibbles) --")
    print("   " + ", ".join(str(f - i) for i, f, _ in progs[:12]))

    print("\n-- strings (%d) --" % len(strings))
    vistos = set()
    for s in strings:
        if s in vistos:
            continue
        vistos.add(s)
        emitir("   " + s.replace("\n", " | ")[:100])

    print("\n-- nombres globales --")
    emitir("   " + " ".join(sorted(set(idnts))[:40]))

    print("\n-- comandos mas usados --")
    emitir("   " + ", ".join("%s(%d)" % (n, k) for n, k in cmds.most_common(45)))


if __name__ == "__main__":
    main()

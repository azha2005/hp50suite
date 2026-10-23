# -*- coding: ascii -*-
"""leer-resultado.py - compara lo que devolvio la calculadora contra casos.txt.

    python leer-resultado.py salida.bin [casos.txt]
    python leer-resultado.py --autotest

`salida.bin` es el objeto que trae `DDE48 r` desde la pila del emulador: la
lista de strings que deja BATERIA. Se decodifica con el lector de objetos de
herramientas/hpobj.py, asi que el resultado vuelve como DATO, no leido a ojo en
la pantalla.

--autotest arma una lista de strings en binario, la lee, y verifica que el
decodificador la reconstruye. Sirve para probar esta mitad sin el emulador
abierto.
"""
import os
import re
import sys
import json
from bateria import comparar

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "herramientas"))
import hpobj                                            # noqa: E402


def normalizar(t):
    """Compara como escribe la calculadora, no como escribimos nosotros.

    Diferencias que aparecieron en corridas reales:
      - \->STR sobre un algebraico devuelve las comillas: 2*X sale como '2*X'
      - los reales salen con punto: 0 sale como 0.
      - las listas salen con espacios: {-1 1} sale como { -1 1 }
      - un entero puede volver como real segun el contexto: la moda de
        { 1 2 2 3 3 3 } vuelve { { 3. } 3. } y no { { 3 } 3 }. Es ruido de
        TIPO, no de valor, y adentro de una lista el recorte de arriba no lo
        veia. Se recorta el punto final de CADA numero, no solo del string
        entero. Un test no deberia fallar por eso: para lo que importa
        (exacto vs aproximado) hay casos dedicados que miran TYPE.
    """
    # OJO con el orden: recortar los puntos ANTES de sacar los espacios. Al
    # reves, "[ 2. 2. 6. ]" queda "2.2.6." y el punto de cada numero pasa a
    # estar seguido de un digito, asi que no se recorta ninguno.
    t = t.strip().replace("'", "")
    # 3. -> 3   (punto que no va seguido de digito, precedido de digito)
    t = re.sub(r"(?<=[0-9])\.(?![0-9])", "", t)
    # 0.5 -> .5 (la calculadora no escribe el cero de la izquierda)
    t = re.sub(r"(?<![0-9])0\.", ".", t)
    return t.replace(" ", "")


def leer_casos(ruta):
    casos = []
    with open(ruta, "r") as f:
        for l in f:
            t = l.strip()
            if not t or t.startswith("#"):
                continue
            p = t.split("|")
            if len(p) < 3:
                continue
            casos.append((p[0].strip(), "|".join(p[2:]).strip()))
    return casos


def extraer_strings(data):
    """Saca la lista de strings del objeto, probando los desplazamientos con
    que puede venir el archivo: crudo, con 4 bytes de largo (CF_HPOBJ) o con
    los 8 del header HPHP4x."""
    for salto in (8 if data[:5] == b"HPHP4" else None, 0, 4):
        if salto is None:
            continue
        nib = hpobj.nibbles(data[salto:])
        L = hpobj.Lector(b"")
        L.nib = nib
        try:
            fin = L.objeto(0, 0)
        except (IndexError, ValueError):
            continue
        # El objeto se rellena a byte par, asi que puede sobrar un nibble.
        if fin < len(nib) - 1:
            continue
        out = []
        for prof, tipo, txt, addr in L.tokens:
            if tipo == "STRING":
                out.append(txt[1:-1])
            elif tipo in ("REAL", "IDNT", "SYSBINT"):
                out.append(txt)
        return out, salto
    return None, None


def codificar_lista_de_strings(textos):
    """Arma el objeto binario de una lista de strings. Solo lo usa --autotest."""
    nib = []

    def poner(valor, cuantos):
        for i in range(cuantos):
            nib.append((valor >> (4 * i)) & 0xF)

    poner(0x02A74, 5)                       # prologo de lista
    for t in textos:
        poner(0x02A2C, 5)                   # prologo de string
        poner(5 + 2 * len(t), 5)            # largo, incluye el campo
        for ch in t:
            c = ord(ch)
            nib.append(c & 0xF)
            nib.append(c >> 4)
    poner(0x0312B, 5)                       # SEMI
    if len(nib) % 2:
        nib.append(0)
    return bytes(bytearray(nib[i] | (nib[i + 1] << 4)
                           for i in range(0, len(nib), 2)))


def autotest():
    muestra = ["2*X", "LN(X)", "{-1 1}", "ERROR", "1000000"]
    data = codificar_lista_de_strings(muestra)
    leidos, salto = extraer_strings(data)
    ok = leidos == muestra
    print("autotest: codifico %d strings, leyo %r (salto %s)"
          % (len(muestra), leidos, salto))
    print("autotest:", "OK" if ok else "FALLO")
    return 0 if ok else 1


def main():
    if "--autotest" in sys.argv:
        return autotest()
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    binario = sys.argv[1]
    meta = None
    if "--meta" in sys.argv:
        meta = json.load(open(sys.argv[sys.argv.index("--meta") + 1], encoding="ascii"))
    casos = ([(c["nombre"], c["esperado"]) for c in meta["casos"]] if meta else leer_casos(sys.argv[2] if len(sys.argv) > 2
                       else os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "casos.txt")))
    data = open(binario, "rb").read()
    obtenidos, salto = extraer_strings(data)
    if obtenidos is None:
        print("No pude decodificar %s como objeto de HP." % binario)
        print("Probe los desplazamientos 0, 4 y 8. Primeros bytes: %r" % data[:16])
        return 1

    if "--comprobar-fin" in sys.argv:
        return 0 if meta and obtenidos and obtenidos[-1] == meta["marca"] else 2
    try:
        valores = comparar(obtenidos, casos, meta["marca"] if meta else None)
    except ValueError as error:
        print(str(error))
        return 1

    print("Decodificado con desplazamiento %d: %d resultados, %d casos.\n"
          % (salto, len(valores), len(casos)))
    print("%-16s %-28s %-28s %s" % ("CASO", "ESPERADO", "OBTENIDO", ""))
    print("-" * 82)
    fallos = 0
    for i, (nombre, esperado) in enumerate(casos):
        got = valores[i]
        bien = normalizar(got) == normalizar(esperado)
        if not bien:
            fallos += 1
        print("%-16s %-28s %-28s %s"
              % (nombre, esperado[:28], got[:28], "ok" if bien else "FALLA"))
    sobran = len(valores) - len(casos)
    if sobran > 0:
        print("\nOjo: volvieron %d resultados de mas." % sobran)
    print("\n%d de %d bien, %d fallan." % (len(casos) - fallos, len(casos), fallos))
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

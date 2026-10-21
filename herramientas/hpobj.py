# -*- coding: ascii -*-
"""hpobj.py - lector de objetos binarios de HP 48/49/50 a nivel nibble.

No es un descompilador completo: separa la estructura (programas, listas,
strings, nombres, reales, XLIB) y deja las referencias a comandos como
direcciones de ROM crudas. Los nombres de esas direcciones se resuelven
aparte, con la tabla que arma rosetta.py.

Uso:
    python hpobj.py ARCHIVO            -> volcado estructural
    python hpobj.py ARCHIVO --tokens   -> una linea por token
"""
import sys

# Prologs (direcciones de ROM). Los que se usan en objetos UserRPL.
PROLOGS = {
    0x02614: "ZINT",      # entero exacto (49/50); es lo que da el modo exacto
    0x02911: "SYSBINT",   # binario del sistema (# n)
    0x02933: "REAL",
    0x02955: "LREAL",     # real extendido
    0x02977: "COMPLEX",
    0x02A0A: "ARRAY",
    0x02A2C: "STRING",
    0x02A4E: "HXS",       # hex string
    0x02A74: "LIST",
    0x02A96: "DIR",
    0x02AB8: "SYMB",      # algebraico
    0x02AFC: "TAGGED",
    0x02B1E: "GROB",     # DOGROB, confirmado en Suprom49.a
    0x02D9D: "PROG",      # DOCOL
    0x02DCC: "PROG2",     # DOCOL2 (secundario cerrado)
    0x02E48: "IDNT",      # nombre global
    0x02E6D: "LAM",       # nombre local
    0x02E92: "XLIB",      # referencia a comando de libreria
    0x02EA4: "EXT",
    0x0312B: "SEMI",      # fin de programa/lista
    0x02FA7: "LIBRARY",
    0x0263A: "ACPTR",
    0x26E8E: "FLASHPTR",  # puntero a flash (49/50)
}

# Charset de la HP: 128..159 son simbolos propios. Solo para mostrar.
HP_HIGH = {
    131: "\v/", 132: "\.S", 133: "\GS", 135: "\pi", 136: "\.d",
    137: "\<=", 138: "\>=", 139: "\=/", 141: "\->", 142: "\<-",
    159: "\oo", 171: "\<<", 187: "\>>",
}


def nibbles(data):
    out = []
    for b in data:
        out.append(b & 0x0F)
        out.append(b >> 4)
    return out


def leer(nib, pos, cuantos):
    """Lee `cuantos` nibbles como entero little-endian de nibbles."""
    v = 0
    for i in range(cuantos):
        v |= nib[pos + i] << (4 * i)
    return v, pos + cuantos


def texto(nib, pos, chars):
    s = []
    for i in range(chars):
        c = nib[pos + 2 * i] | (nib[pos + 2 * i + 1] << 4)
        if 32 <= c < 127:
            s.append(chr(c))
        elif c in HP_HIGH:
            s.append(HP_HIGH[c])
        elif c == 10:
            s.append("\n")
        else:
            s.append("<%d>" % c)
    return "".join(s), pos + 2 * chars


def bcd_real(nib, pos):
    """Real de 16 nibbles.

    Disposicion verificada contra Graf/NOFORMAT, que solo guarda numeros de
    flag de dos digitos (45, 50, -18, -50): 3 nibbles de exponente primero,
    12 de mantisa con el digito MAS significativo al final, y el signo ultimo
    (9 = negativo). Leerlo al reves da basura tipo 0.00000000001e1104.
    """
    ex = nib[pos] | (nib[pos + 1] << 4) | (nib[pos + 2] << 8)
    if ex > 0x7FF:
        ex -= 0x1000
    m = "".join(str(nib[pos + 14 - i]) for i in range(12))
    sg = "-" if nib[pos + 15] else ""
    if 0 <= ex <= 10:
        ent, fra = m[:ex + 1], m[ex + 1:].rstrip("0")
        txt = ent.lstrip("0") or "0"
        txt = txt + "." + fra
    elif -6 <= ex < 0:
        txt = "." + "0" * (-ex - 1) + m.rstrip("0")
    else:
        txt = "%s.%sE%d" % (m[0], m[1:].rstrip("0") or "0", ex)
    return sg + txt, pos + 16


class Lector(object):
    def __init__(self, data):
        if data[:5] == b"HPHP4":
            data = data[8:]
        self.nib = nibbles(data)
        self.tokens = []       # (profundidad, tipo, texto, direccion)
        self.grobs = []        # (ancho, alto, filas de bits), en orden
        self.addr_usadas = {}

    def run(self):
        pos = 0
        try:
            pos = self.objeto(pos, 0)
        except IndexError:
            self.tokens.append((0, "TRUNCADO", "se acabo el nibble stream", None))
        return pos

    def objeto(self, pos, prof):
        p0 = pos
        pro, pos = leer(self.nib, pos, 5)
        nombre = PROLOGS.get(pro)

        if nombre in ("PROG", "PROG2", "LIST", "SYMB", "DIR"):
            self.tokens.append((prof, nombre, "{ABRE}", pro))
            while True:
                if pos + 5 > len(self.nib):
                    self.tokens.append((prof, "TRUNCADO", "sin SEMI", None))
                    return pos
                sig, _ = leer(self.nib, pos, 5)
                if sig == 0x0312B:
                    pos += 5
                    self.tokens.append((prof, nombre, "{CIERRA}", pro))
                    return pos
                pos = self.objeto(pos, prof + 1)

        if nombre == "STRING":
            largo, pos = leer(self.nib, pos, 5)
            chars = (largo - 5) // 2
            s, pos = texto(self.nib, pos, chars)
            self.tokens.append((prof, "STRING", '"%s"' % s, None))
            return pos

        if nombre == "HXS":
            largo, pos = leer(self.nib, pos, 5)
            n = largo - 5
            h = "".join("%X" % self.nib[pos + i] for i in range(n))
            self.tokens.append((prof, "HXS", "#" + h, None))
            return pos + n

        if nombre in ("IDNT", "LAM"):
            n, pos = leer(self.nib, pos, 2)
            s, pos = texto(self.nib, pos, n)
            self.tokens.append((prof, nombre, s, None))
            return pos

        if nombre == "ZINT":
            # prologo + largo (5 nibbles, se incluye) + digitos LSB primero +
            # nibble de signo (9 = negativo). Verificado en el emulador: un 1
            # tipeado en modo exacto da 14 26 70 00 00 01.
            largo, pos = leer(self.nib, pos, 5)
            n = largo - 6
            dig = "".join(str(self.nib[pos + n - 1 - i]) for i in range(n))
            sg = "-" if self.nib[pos + n] else ""
            self.tokens.append((prof, "ZINT", sg + (dig.lstrip("0") or "0"), None))
            return pos + n + 1

        if nombre == "REAL":
            s, pos = bcd_real(self.nib, pos)
            self.tokens.append((prof, "REAL", s, None))
            return pos

        if nombre == "LREAL":
            self.tokens.append((prof, "LREAL", "(21 nibbles)", None))
            return pos + 21

        if nombre == "COMPLEX":
            a, pos = bcd_real(self.nib, pos)
            b, pos = bcd_real(self.nib, pos)
            self.tokens.append((prof, "COMPLEX", "(%s,%s)" % (a, b), None))
            return pos

        if nombre == "SYSBINT":
            v, pos = leer(self.nib, pos, 5)
            self.tokens.append((prof, "SYSBINT", "#%d" % v, None))
            return pos

        if nombre == "XLIB":
            lib, pos = leer(self.nib, pos, 3)
            cmd, pos = leer(self.nib, pos, 3)
            self.tokens.append((prof, "XLIB", "XLIB %d %d" % (lib, cmd), None))
            return pos

        if nombre == "TAGGED":
            n, pos = leer(self.nib, pos, 2)
            s, pos = texto(self.nib, pos, n)
            self.tokens.append((prof, "TAGGED", ":" + s + ":", None))
            return self.objeto(pos, prof)

        if nombre == "GROB":
            # prologo + largo (5, se incluye) + alto (5) + ancho (5) + bitmap.
            # Cada fila ocupa ceil(ancho/4) nibbles (arranca en nibble entero).
            # El orden alto/ancho se decide por aritmetica: se prueban los dos y
            # gana el que cierra contra el largo declarado.
            largo, pos = leer(self.nib, pos, 5)
            a, pos = leer(self.nib, pos, 5)
            b, pos = leer(self.nib, pos, 5)
            datos = largo - 15
            alto, ancho = a, b
            if not (alto and datos % alto == 0):
                alto, ancho = b, a
            # Las filas se rellenan a BYTE, no a nibble: la pantalla de 131 de
            # ancho usa 34 nibbles por fila (17 bytes), no 33. Se deduce del
            # largo declarado, que es lo unico que no se puede malinterpretar;
            # el ceil(ancho/8)*2 queda de respaldo.
            porFila = datos // alto if alto and datos % alto == 0 else ((ancho + 7) // 8) * 2
            filas = []
            for f in range(alto):
                bits = []
                for n in range(porFila):
                    v = self.nib[pos + f * porFila + n]
                    for i in range(4):
                        bits.append((v >> i) & 1)
                filas.append(bits[:ancho])
            self.grobs.append((ancho, alto, filas))
            self.tokens.append((prof, "GROB", "GROB %dx%d" % (ancho, alto), None))
            return p0 + 5 + largo

        if nombre == "ARRAY":
            largo, pos = leer(self.nib, pos, 5)
            self.tokens.append((prof, "ARRAY", "(%d nibbles)" % largo, None))
            return p0 + 5 + largo

        if nombre == "FLASHPTR":
            a, pos = leer(self.nib, pos, 3)
            b, pos = leer(self.nib, pos, 3)
            self.tokens.append((prof, "FLASHPTR", "FPTR %d %d" % (a, b), None))
            return pos

        if nombre == "SEMI":
            self.tokens.append((prof, "SEMI", ";", None))
            return pos

        # Cualquier otra cosa: es una direccion de ROM, o sea la llamada a un
        # comando de fabrica. Es lo que hay que resolver con la tabla.
        self.tokens.append((prof, "ADDR", "@%05X" % pro, pro))
        self.addr_usadas[pro] = self.addr_usadas.get(pro, 0) + 1
        return pos


def main():
    ruta = sys.argv[1]
    data = open(ruta, "rb").read()
    L = Lector(data)
    fin = L.run()
    solo_tokens = "--tokens" in sys.argv
    for prof, tipo, txt, addr in L.tokens:
        if solo_tokens:
            print("%s\t%s" % (tipo, txt))
        else:
            print("%s%-9s %s" % ("  " * prof, tipo, txt))
    print("--- %d tokens, %d nibbles de %d consumidos, %d direcciones distintas"
          % (len(L.tokens), fin, len(L.nib), len(L.addr_usadas)))


if __name__ == "__main__":
    main()

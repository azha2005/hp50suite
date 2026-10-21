# -*- coding: ascii -*-
"""compilar.py - arma un objeto binario de HP desde la PC.

    python compilar.py FUENTE.txt SALIDA.hp [--sin-header] [--sin-modo]

No es un compilador de UserRPL: no sabe armar algebraicos. Hace el truco que
evita necesitarlo. Emite el objeto

    \<< "<todo el fuente>" STR\-> EVAL \>>

es decir, mete el texto del programa como STRING y deja que lo compile la
calculadora con su propio STR\->, que es el mismo compilador que usa la
transferencia. Asi se puede mandar cualquier fuente por DDE (que solo mueve
objetos, no texto) sin pasar por ASCIIBIN ni por el menu del emulador.

Al evaluarlo queda en la pila lo que deje el fuente.

Direcciones usadas, todas de Suprom49.a:
    DOCOL 02D9D   x<< 389B9   xSTR> 3BBD9   xEVAL 395AC   x>> 389D4   SEMI 0312B
"""
import sys

DOCOL, XABRE, XSTR, XEVAL, XCIERRA, SEMI = (0x02D9D, 0x389B9, 0x3BBD9,
                                            0x395AC, 0x389D4, 0x0312B)
DOCSTR = 0x02A2C

# Escapes del formato de transferencia -> byte del juego de caracteres de la HP.
# STR\-> NO los entiende: son convencion del programa de transferencia
# (Conn4x, ASCIIBIN), no sintaxis de la calculadora. Pasarle el fuente tal cual
# da syntax error y deja el string en la pila. Costo una corrida entera.
# Escapes del formato de transferencia -> byte del juego de caracteres de la HP.
# STR\-> NO los entiende: son convencion del programa de transferencia
# (Conn4x, ASCIIBIN), no sintaxis de la calculadora. Pasarle el fuente tal cual
# da syntax error y deja el string en la pila. Costo una corrida entera.
#
# La tabla se arma con B = chr(92) y NO con literales que empiecen con barra
# invertida. Motivo medido: escrito como "/", Python lo lee como TABULADOR
# VERTICAL + "/" (porque  SI es un escape de Python), asi que la raiz
# cuadrada no se traducia NUNCA y la calculadora recibia los tres caracteres
# literales. No daba error: el algebraico se compilaba igual, con un nombre
# basura adentro, y recien fallaba al evaluar. Invalido en silencio toda prueba
# que usara una raiz. Es la misma trampa que ya habia mordido en descompilar.py.
B = chr(92)
ESCAPES = [
    (B + "<<", 171), (B + ">>", 187), (B + "->", 141), (B + "<-", 142),
    (B + "<=", 137), (B + ">=", 138), (B + "=/", 139), (B + "v/", 131),
    (B + ".S", 132), (B + ".d", 136), (B + "GS", 133), (B + "pi", 135),
    (B + "oo", 159),
]



def traducir_escapes(texto):
    for esc, cod in ESCAPES:
        texto = texto.replace(esc, chr(cod))
    return texto


def a_nibbles(valor, cuantos):
    return [(valor >> (4 * i)) & 0xF for i in range(cuantos)]


# Prologo que se compila y evalua ANTES del fuente. Fija el modo EXACTO.
#
# Por que hace falta y por que no puede ir adentro del fuente: la bandera
# -105 controla el modo aproximado, y lo que decide NO es como se opera sino
# como STR\-> COMPILA los literales. En aproximado, el `1` de un fuente se
# compila como real `1.` en vez de entero exacto, y ademas RISCH directamente
# falla. Poner `-105 CF` como primera linea del fuente no sirve: cuando eso
# se ejecuta, el fuente entero ya fue compilado.
#
# Medido en el emulador (harness/casos-flag2.txt): con -105 SF, "1" STR\->
# da TYPE 0 y no 28, y 'X^2' 'X' RISCH revienta. Una corrida entera de la
# bateria salio con `.5*Y^2.` en vez de `Y^2/2` y con "ERR: RISCH" porque la
# maquina habia quedado en aproximado de una corrida anterior -- sin aviso
# ninguno, y eso probablemente explica tambien un ERROR suelto que no habia
# podido reproducir.
#
# No se restaura al salir a proposito: el emulador es un banco de pruebas y
# lo que se quiere es que cada corrida arranque igual. Restaurarlo lo
# devolveria a aproximado y la corrida siguiente volveria a salir mal.
PROLOGO_EXACTO = "-105 CF"


def _poner_str(nib, texto):
    nib += a_nibbles(DOCSTR, 5)
    nib += a_nibbles(5 + 2 * len(texto), 5)      # el largo se incluye a si mismo
    for ch in texto:
        c = ord(ch)
        if c > 255:
            raise ValueError("caracter fuera del juego de la HP: %r" % ch)
        nib += [c & 0xF, c >> 4]
    nib += a_nibbles(XSTR, 5)
    nib += a_nibbles(XEVAL, 5)


def objeto_str_eval(texto, prologo=PROLOGO_EXACTO):
    nib = []
    nib += a_nibbles(DOCOL, 5)
    nib += a_nibbles(XABRE, 5)
    if prologo:
        _poner_str(nib, prologo)
    nib += a_nibbles(DOCSTR, 5)
    nib += a_nibbles(5 + 2 * len(texto), 5)      # el largo se incluye a si mismo
    for ch in texto:
        c = ord(ch)
        if c > 255:
            raise ValueError("caracter fuera del juego de la HP: %r" % ch)
        nib += [c & 0xF, c >> 4]
    nib += a_nibbles(XSTR, 5)
    nib += a_nibbles(XEVAL, 5)
    nib += a_nibbles(XCIERRA, 5)
    nib += a_nibbles(SEMI, 5)
    if len(nib) % 2:
        nib.append(0)
    return bytes(bytearray(nib[i] | (nib[i + 1] << 4)
                           for i in range(0, len(nib), 2)))


def main():
    fuente, salida = sys.argv[1], sys.argv[2]
    texto = open(fuente, "rb").read().decode("ascii")
    # El header %%HP es para la transferencia por Conn4x; STR\-> no lo entiende.
    lineas = [l for l in texto.replace("\r\n", "\n").split("\n")
              if not l.startswith("%%HP:") and not l.lstrip().startswith("@")]
    cuerpo = traducir_escapes("\n".join(lineas))
    prologo = "" if "--sin-modo" in sys.argv else PROLOGO_EXACTO
    obj = objeto_str_eval(cuerpo, prologo)
    if "--sin-header" in sys.argv:
        open(salida, "wb").write(obj)
    else:
        open(salida, "wb").write(b"HPHP49-X" + obj)
    print("%s: %d bytes de fuente -> %d bytes de objeto%s"
          % (salida, len(cuerpo), len(obj),
             "" if "--sin-header" in sys.argv else " (+8 de header)"))


if __name__ == "__main__":
    main()

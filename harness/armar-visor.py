"""Build native LCD fixtures, or the two-step interactive viewer check.

python harness/armar-visor.py harness/BVISOR.txt [--interactivo]
Run EVAL on an idle emulator; receive only after completion. Interactive:
OK, a key, OK, a key, CANCEL. Expected final string: VISOR-FIN.
The returned list contains each page captured by the production DPANTC renderer.
"""
import argparse
from pathlib import Path
from bateria import B, cuerpo

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("salida")
p.add_argument("--interactivo", action="store_true")
p.add_argument("--largo", action="store_true", help="Use a multi-page primitive for the interactive check")
a = p.parse_args()
s = ["%%HP: T(3)A(R)F(.);", B+"<<", "CLEAR"]
for name in ("DPAGC", "DPANTC", "DPASOS"):
    s += cuerpo(name) + ["'"+name+"' STO"]
trace = '''{ { "Planteo" 'X^2' } { "Resultado" '1/3' } }''' if a.interactivo else '''{ { "Cociente" '-(2*X+Y)/(X-3*Y^2)' } { "Candidatos" { { -2 -2 } { -1 2 } { 1 -2 } { 3 18 } } } { "Primitiva" 'X^2*SIN(X)+2*X*COS(X)-2*SIN(X)' } }'''
if a.largo:
    trace = '''{ { "Primitiva" 'X^2*SIN(X)+2*X*COS(X)-2*SIN(X)' } }'''
s += [trace+" "+B+"-> TR", B+"<<"]
if a.interactivo:
    s += ["TR DPASOS"]
s += ["{ } "+B+"-> GG", B+"<<", "1 TR SIZE FOR K", "TR K GET DPAGC "+B+"-> PG", B+"<<", "1 PG SIZE FOR P", "PG P GET K P PG SIZE DPANTC", "1 "+B+"->LIST GG SWAP + 'GG' STO", "NEXT", B+">>", "NEXT", "CLEAR GG", '"VISOR-FIN" 1 '+B+"->LIST +", B+">>", B+">>", B+">>"]
Path(a.salida).write_bytes(("\r\n".join(s)+"\r\n").encode("ascii"))
print(a.salida)

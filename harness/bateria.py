"""Build compact isolated ROM batches; validate complete, unique result sets."""
from pathlib import Path
import hashlib
import re
import uuid

B = chr(92)
ROOT = Path(__file__).resolve().parents[1]
DIRS = [ROOT / "programas" / "mat1", ROOT / "programas", ROOT / "programas" / "datos"]


def cuerpo(nombre):
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", nombre):
        raise ValueError(f"Nombre de objeto invalido: {nombre}")
    for directory in DIRS:
        path = directory / (nombre + ".txt")
        if path.is_file():
            lines = path.read_bytes().decode("ascii").replace("\r\n", "\n").split("\n")
            if lines[0] != "%%HP: T(3)A(R)F(.);":
                raise ValueError(f"Cabecera invalida: {path}")
            return lines[1:]
    raise ValueError(f"No encontre {nombre}.txt")


def leer(paths, patron=None):
    objects, cases, names = [], [], set()
    for path in paths:
        # splitlines() treats historical VT bytes inside comments as line ends.
        # A comment must be discarded as a whole, not turned into test code.
        for n, line in enumerate(Path(path).read_text(encoding="utf-8-sig").split("\n"), 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("USAR:"):
                objects.extend(line[5:].replace(",", " ").split())
                continue
            parts = line.split("|", 2)
            if len(parts) != 3:
                raise ValueError(f"{path}:{n}: caso sin tres columnas")
            name, expr, expected = [p.strip() for p in parts]
            if not re.fullmatch(r"[A-Za-z0-9_.-]+", name):
                raise ValueError(f"{path}:{n}: nombre invalido")
            if name in names:
                raise ValueError(f"Caso duplicado: {name}")
            names.add(name)
            if patron is None or re.search(patron, name):
                cases.append({"nombre": name, "expresion": expr, "esperado": expected})
    if not cases:
        raise ValueError("La seleccion no contiene casos")
    return list(dict.fromkeys(objects)), cases


def reducir_carga(objects, cases):
    """Conservative closure over declared objects, including names in strings.

    Names can occur in algebraics, quoted lists or runtime-compiled strings;
    scanning all words deliberately retains false positives. No resident cache.
    """
    declared = set(objects)
    words = lambda text: set(re.findall(r"[A-Za-z][A-Za-z0-9]*", text))
    needed = set().union(*(words(c["expresion"]) for c in cases)) & declared
    pending = list(needed)
    while pending:
        name = pending.pop()
        source = "\n".join(l for l in cuerpo(name) if not l.lstrip().startswith("@"))
        additions = words(source) & declared - needed
        needed.update(additions)
        pending.extend(additions)
    return [name for name in objects if name in needed]


def generar(paths, patron=None, infinito=True, carga_minima=False):
    objects, cases = leer(paths, patron)
    declared = list(objects)
    if carga_minima:
        objects = reducir_carga(objects, cases)
    marker = "HPTEST-" + uuid.uuid4().hex
    # The emulator is a test bank: silent mode changes avoid modal exact/
    # complex switches. This does NOT suppress unsigned-infinity queries.
    out = ["%%HP: T(3)A(R)F(.);", B + "<<", "CLEAR", "-3 CF -120 SF -123 CF -119 CF -100 CF -99 CF"]
    if infinito:
        out.append(B + "oo 'INF' STO")
    hashes = {}
    for name in objects:
        lines = [l.strip() for l in cuerpo(name) if l.strip() and not l.lstrip().startswith("@")]
        hashes[name] = hashlib.sha256("\n".join(lines).encode("ascii")).hexdigest()
        out += lines + ["'" + name + "' STO"]
    out += ["{ } " + B + "-> BRES", B + "<<"]
    for case in cases:
        # Diagnostic checkpoint is read only after independently establishing
        # idle state. ON may be caught by IFERR and is not proof of stopping.
        out += ["CLEAR", '"' + marker + '" "' + case["nombre"] + '" BRES 3 ' + B + "->LIST 'HPTSTATE' STO",
                "IFERR " + case["expresion"] + " " + B + '->STR THEN "ERROR" END',
                B + "-> BR " + B + "<< CLEAR BRES " + '"' + case["nombre"] + '|" BR + 1 ' +
                B + "->LIST + 'BRES' STO " + B + ">>"]
    out += ['"' + marker + '" "FIN CASOS" BRES 3 ' + B + "->LIST 'HPTSTATE' STO"]
    purge = objects + (["INF"] if infinito else [])
    if purge:
        # Finish cleanup before constructing the public result. Keep BRES in
        # scope until then, and persist only a fully completed result.
        out += ["CLEAR", "{ " + " ".join(purge) + " } PURGE"]
    out += ["CLEAR BRES", '"' + marker + '" 1 ' + B + "->LIST +",
            "DUP 'HPTRESULT' STO", B + ">>", B + ">>"]
    data = ("\r\n".join(out) + "\r\n").encode("ascii")
    if any(b < 32 and b not in (9, 10, 13) for b in data):
        raise ValueError("Byte de control en fuente generado")
    meta = {"version": 1, "marca": marker, "fuentes": [str(Path(p).resolve()) for p in paths],
            "carga_minima": carga_minima, "objetos_declarados": declared,
            "objetos_sha256": hashes, "casos": cases, "infinito": infinito,
            "sha256": hashlib.sha256(data).hexdigest()}
    return data, meta


def comparar(obtenidos, casos, marca=None):
    if marca is not None:
        if not obtenidos or obtenidos[-1] != marca:
            raise ValueError("Bateria incompleta o resultado de otra corrida")
        obtenidos = obtenidos[:-1]
    names = [c[0] for c in casos]
    if len(set(names)) != len(names):
        raise ValueError("Nombres de casos esperados duplicados")
    if any("|" in result for result in obtenidos):
        found = {}
        for result in obtenidos:
            if "|" not in result:
                raise ValueError("Resultado sin nombre mezclado con resultados etiquetados")
            name, value = result.split("|", 1)
            if name in found:
                raise ValueError(f"Resultado duplicado: {name}")
            found[name] = value
        if set(found) != set(names):
            raise ValueError(f"Nombres distintos: faltan {set(names)-set(found)}, sobran {set(found)-set(names)}")
        return [found[name] for name in names]
    if len(obtenidos) != len(casos):
        raise ValueError(f"Cantidad distinta: {len(obtenidos)} resultados, {len(casos)} casos")
    return obtenidos

"""Audit completed ROM results against the CURRENT sources and case tables.

Usage: python harness/verificar-lotes.py harness/BFINAL-*.json
Pass only the manifests selected for the final regression, not probe batches.
No DDE or emulator interaction: this reads previously received local files.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

from bateria import comparar, cuerpo, leer

SPEC = importlib.util.spec_from_file_location("reader", Path(__file__).with_name("leer-resultado.py"))
READER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(READER)


def audit(path):
    meta = json.loads(path.read_text(encoding="ascii"))
    if hashlib.sha256(path.with_suffix(".txt").read_bytes()).hexdigest() != meta["sha256"]:
        raise ValueError("Generated source changed")
    for name, expected in meta["objetos_sha256"].items():
        lines = [s.strip() for s in cuerpo(name) if s.strip() and not s.lstrip().startswith("@")]
        if hashlib.sha256("\n".join(lines).encode("ascii")).hexdigest() != expected:
            raise ValueError(f"Stale object: {name}")
    _, current = leer(meta["fuentes"])
    by_name = {c["nombre"]: c for c in current}
    if any(by_name.get(c["nombre"]) != c for c in meta["casos"]):
        raise ValueError("Case expression or expected result changed")
    actual, _ = READER.extraer_strings(path.with_suffix(".bin").read_bytes())
    if actual is None:
        raise ValueError("Cannot decode result")
    cases = [(c["nombre"], c["esperado"]) for c in meta["casos"]]
    values = comparar(actual, cases, meta["marca"])
    failed = [name for (name, expected), value in zip(cases, values)
              if READER.normalizar(expected) != READER.normalizar(value)]
    if failed:
        raise ValueError("Failed cases: " + ", ".join(failed))
    return len(cases)


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    total, errors = 0, 0
    for arg in sys.argv[1:]:
        path = Path(arg)
        try:
            count = audit(path)
            total += count
            print(f"{path.stem}: {count}/{count}, current sources and valid final marker")
        except (OSError, ValueError, KeyError) as error:
            errors += 1
            print(f"{path.stem}: REJECTED: {error}")
    print(f"Accepted checks: {total}; rejected batches: {errors}")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())

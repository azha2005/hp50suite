"""Build independent topic directories from the current UserRPL sources.

No ROM or emulator required. Dependencies are executable identifiers outside
comments and display strings; generated packages never rely on sibling DIRs.
"""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "programas" / "mat1"
TOPICS = {
    "P2": ["DINTEG", "DINTDEF", "DAREA", "DIMPR", "DTFC"],
    "DER": ["DDER", "DDEF", "DTANOR", "DTANP", "DIMPL", "DDERLAT", "DDERTAB", "DDIF"],
    "EST": ["DESTFUN", "DWEIER", "DTVM", "DELAST", "DSIGNOS"],
    "EDO": ["DEDO", "DSEP", "DSEPI", "DEDOVER", "DORDEN", "DRECEL"],
    "MULTI": ["DPARCIAL", "DHESS", "LAGR"],
    "TEORIA": ["DTEORIA"],
}


def read_sources():
    sources = {}
    for path in sorted(SOURCES.glob("*.txt")):
        raw = path.read_bytes()
        if not raw.startswith(b"%%HP: T(3)A(R)F(.);\r\n"):
            raise ValueError(f"Header/CRLF: {path}")
        if b"\n" in raw.replace(b"\r\n", b"") or any(
            n > 127 or n < 32 and n not in (9, 10, 13) for n in raw
        ):
            raise ValueError(f"Transfer encoding: {path}")
        sources[path.stem] = [
            line.strip() for line in raw.decode("ascii").split("\r\n")[1:]
            if line.strip() and not line.lstrip().startswith("@")
        ]
    return sources


def dependencies(roots, sources):
    result = set()
    pending = list(roots)
    while pending:
        name = pending.pop()
        if name in result:
            continue
        if name not in sources:
            raise ValueError(f"Missing object: {name}")
        result.add(name)
        code = re.sub(r'"[^"\r\n]*"', '""', "\n".join(sources[name]))
        words = set(re.findall(r"[A-Za-z][A-Za-z0-9]*", code))
        pending.extend((words & sources.keys()) - result)
    return sorted(result)


def package(roots, sources):
    names = dependencies(roots, sources)
    lines = ["%%HP: T(3)A(R)F(.);", "DIR"]
    for name in names:
        lines += [name] + sources[name]
    lines += ["END", ""]
    return "\r\n".join(lines).encode("ascii"), names


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", action="store_true", help="Rebuild MAT1.txt from its existing entry list")
    parser.add_argument("--check", action="store_true", help="Compare without modifying files")
    args = parser.parse_args()
    sources = read_sources()
    groups = dict(TOPICS)
    if args.base:
        builder = (ROOT / "programas" / "armar-mat1.ps1").read_text(encoding="utf-8-sig")
        declaration = builder.split("$orden = @(", 1)[1].split(")", 1)[0]
        groups[""] = re.findall(r"'([A-Za-z0-9]+)'", declaration)
    metadata = {}
    for group, roots in groups.items():
        path = ROOT / "programas" / ("MAT1" + ("-" + group if group else "") + ".txt")
        data, names = package(roots, sources)
        if args.check:
            if not path.is_file() or path.read_bytes() != data:
                raise SystemExit(f"Stale package: {path.name}")
        else:
            path.write_bytes(data)
        metadata[path.name] = {"entradas": roots, "objetos": names, "bytes": len(data)}
        print(f"{path.name}: {len(names)} objects, {len(data)} bytes; roots: {', '.join(roots[:8])}")
    report = ROOT / "dist" / "paquetes-mat1.json"
    if not args.check:
        report.parent.mkdir(exist_ok=True)
        report.write_text(json.dumps(metadata, indent=2) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()

"""Compact test builder: casos.txt BTEST.txt [--mas tabla.txt] [--solo REGEX] [--sin-inf]."""
import argparse
import json
from pathlib import Path
from bateria import generar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("casos")
    parser.add_argument("salida")
    parser.add_argument("--mas", action="append", default=[])
    parser.add_argument("--solo")
    parser.add_argument("--sin-inf", action="store_true")
    parser.add_argument("--min-carga", action="store_true", help="Cargar cierre de dependencias de los casos seleccionados")
    args = parser.parse_args()
    data, meta = generar([args.casos] + args.mas, args.solo, not args.sin_inf, args.min_carga)
    path = Path(args.salida)
    path.write_bytes(data)
    path.with_suffix(".json").write_text(json.dumps(meta, indent=2) + "\n", encoding="ascii")
    print(f"{path.name}: {len(meta['objetos_sha256'])} objetos, {len(meta['casos'])} casos, {len(data)} bytes")


if __name__ == "__main__":
    main()

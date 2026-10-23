"""Host tests: deliberately malformed results must never pass the ROM gate."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from bateria import comparar, generar, leer

SPEC = importlib.util.spec_from_file_location("lector", Path(__file__).with_name("leer-resultado.py"))
LECTOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LECTOR)


class TestBateria(unittest.TestCase):
    def test_wrong_run_missing_extra_and_duplicates(self):
        cases = [("uno", "1"), ("dos", "2")]
        for bad in (["uno|1", "dos|2", "OTRA"], ["uno|1", "FIN"],
                    ["uno|1", "dos|2", "extra|0", "FIN"],
                    ["uno|1", "uno|1", "dos|2", "FIN"], ["uno|1", "2", "FIN"]):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                comparar(bad, cases, "FIN")
        self.assertEqual(comparar(["dos|2", "uno|1", "FIN"], cases, "FIN"), ["1", "2"])

    def test_compact_filter_and_duplicate_loads(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp)/"a.txt", Path(tmp)/"b.txt"
            a.write_text("USAR: DSEPC\n# comment with VT \x0b still a comment\na | 1 | 1\n", encoding="ascii")
            b.write_text("USAR: DSEPC\nb | 2 | 2\n", encoding="ascii")
            data, meta = generar([a, b], "^b$", False)
            self.assertEqual(list(meta["objetos_sha256"]), ["DSEPC"])
            self.assertEqual([c["nombre"] for c in meta["casos"]], ["b"])
            self.assertNotIn(b"@", data)
            self.assertNotIn(bytes([92])+b"oo", data)
            self.assertNotIn(b"\n", data.replace(b"\r\n", b""))
            with self.assertRaises(ValueError):
                leer([a, a])
            with self.assertRaises(ValueError):
                leer([a], "absent")
            self.assertNotEqual(meta["marca"], generar([b], infinito=False)[1]["marca"])

    def test_binary_completion_marker(self):
        marker = "HPTEST-unico"
        binary = LECTOR.codificar_lista_de_strings(["uno|1", marker])
        results, offset = LECTOR.extraer_strings(binary)
        self.assertEqual(offset, 0)
        self.assertEqual(comparar(results, [("uno", "1")], marker), ["1"])
        # A source program is not a completed list of results.
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"herramientas"))
        import compilar
        result, _ = LECTOR.extraer_strings(compilar.objeto_str_eval("1"))
        with self.assertRaises(ValueError):
            comparar(result or [], [("uno", "1")], marker)

    def test_transitive_loads_and_final_result_after_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/"cases.txt"
            p.write_text("USAR: DSTATSC DSTATS DOLS DOLSC SIGFIG\na | { 1 2 3 } DSTATSC | x\n", encoding="ascii")
            data, meta = generar([p], infinito=False, carga_minima=True)
            self.assertEqual(list(meta["objetos_sha256"]), ["DSTATSC"])
            self.assertEqual(meta["objetos_declarados"], ["DSTATSC", "DSTATS", "DOLS", "DOLSC", "SIGFIG"])
            source = data.decode("ascii")
            self.assertLess(source.rindex("PURGE"), source.index("DUP 'HPTRESULT' STO"))
            self.assertIn("'HPTSTATE' STO", source)
            p.write_text("USAR: TD TDSEP DSTATSC\na | 1 TD | x\n", encoding="ascii")
            _, meta = generar([p], infinito=False, carga_minima=True)
            self.assertEqual(list(meta["objetos_sha256"]), ["TD", "TDSEP"])

    def test_compiler_prologue_is_a_program_not_bare_commands(self):
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"herramientas"))
        import compilar
        strings, _ = LECTOR.extraer_strings(compilar.objeto_str_eval("1"))
        # hpobj prints HP glyphs using transfer escapes.
        self.assertEqual(strings[0], chr(92) + "<< -105 CF " + chr(92) + ">>")


if __name__ == "__main__":
    unittest.main()

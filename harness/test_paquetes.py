"""Verify topic packages resolve current dependencies, not sibling DIRs."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("packs", ROOT / "herramientas/empaquetar-mat1.py")
PACKS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKS)


class TopicPackages(unittest.TestCase):
    def test_dependency_closure_and_display_names(self):
        sources = {"UI": ['"HELP" DROP', "CORE"], "CORE": ["UTIL"], "UTIL": ["1"], "HELP": ["99"]}
        self.assertEqual(PACKS.dependencies(["UI"], sources), ["CORE", "UI", "UTIL"])
        with self.assertRaises(ValueError):
            PACKS.dependencies(["MISSING"], sources)

    def test_every_topic_is_self_contained_and_bounded(self):
        sources = PACKS.read_sources()
        for topic, roots in PACKS.TOPICS.items():
            with self.subTest(topic=topic):
                data, names = PACKS.package(roots, sources)
                self.assertTrue(set(roots) <= set(names))
                self.assertLess(len(data), 85000, "Split the topic before the transfer text grows too large")
                self.assertEqual(data, (ROOT / "programas" / f"MAT1-{topic}.txt").read_bytes())
                self.assertNotIn(b"\n", data.replace(b"\r\n", b""))
                for name in names:
                    self.assertTrue(set(PACKS.dependencies([name], sources)) <= set(names))


if __name__ == "__main__":
    unittest.main()

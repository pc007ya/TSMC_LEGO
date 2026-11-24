"""python -m unittest discover -s tools -p test_lego_bom.py"""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lego_bom import EXTRA, ROOT, audit, columns, export_bom, ldraw_counts, load_mapping

class PartEvidence(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.evidence = self.root / "evidence.json"
        self.row = {
            "ldraw_part": "3005.dat", "ldraw_color": 41, "ldraw_color_expected": 43,
            "lego_design_id": "30071", "lego_element_id": "4141275",
            "status": "verified", "source_url": "https://www.lego.com/example/test.pdf",
        }

    def load(self, rows):
        self.evidence.write_text(json.dumps({"rows": rows}))
        return load_mapping(self.evidence)

    def test_exact_key_even_when_color_expected_differs(self):
        m = self.load([self.row])
        published = dict(zip(EXTRA, columns(m, "3005", 41)))
        self.assertEqual(published["LEGO官方元素號（含顏色）"], "4141275")
        self.assertEqual(published["採購對應LDraw色號"], 43)
        self.assertIn("原模型", published["備註"])
        for wrong in [("3005", 43), ("3005", 15), ("3005b", 41)]:
            self.assertEqual(dict(zip(EXTRA, columns(m, *wrong)))["LEGO官方元素號（含顏色）"], "")

    def test_unverified_id_is_not_a_purchase_guess(self):
        with self.assertRaisesRegex(ValueError, "unverified Element ID"):
            self.load([dict(self.row, status="unverified", source_url="", note="unverified")])

    def test_refuses_fake_official_hostname_or_duplicate(self):
        with self.assertRaisesRegex(ValueError, "official LEGO"):
            self.load([dict(self.row, source_url="https://lego.com.other.test")])
        with self.assertRaisesRegex(ValueError, "Duplicate mapping"):
            self.load([self.row, dict(self.row, ldraw_part="3005")])

    def test_embedded_mpd_primitives_not_purchases(self):
        path = self.root / "model.ldr"
        path.write_text("\n".join(["0 FILE model.ldr", "1 41 80 0 0 1 0 0 0 1 0 0 0 1 3224.dat", "0 FILE 3224.dat",
                                   "1 16 0 0 0 1 0 0 0 1 0 0 0 1 stud3.dat", "0 NOFILE"]))
        self.assertEqual(list(ldraw_counts(path)), [("3224", 41)])


class ReleaseEvidence(unittest.TestCase):
    def test_all_release_boms_match_models_and_bags(self):
        stats = audit(ROOT, load_mapping(), check=True, require_reviewed=True)
        self.assertEqual((stats["per_model_boms"], stats["series_boms"]), (16, 4))
        self.assertEqual(stats["unique_part_color_combinations"], 421)
        self.assertEqual(stats["updated_files"], 0)
        self.assertEqual(stats["missing_mapping_rows"], 0)

    def test_per_model_generator_roundtrips_download(self):
        models = json.loads((ROOT / "data" / "models.json").read_text())
        catalog = json.loads((ROOT / "data" / "catalog.json").read_text())
        with TemporaryDirectory() as tmp:
            for model in models:
                path = Path(tmp) / "bom.csv"
                export_bom(model, catalog, path)
                self.assertEqual(path.read_bytes(), (ROOT / "downloads" / model["id"] / "bom.csv").read_bytes(), model["id"])


if __name__ == "__main__":
    unittest.main()

import json
import unittest
from collections import Counter
from pathlib import Path
from design import local_cells, parts, validate, colors
from green_museumbrary import DATA, ROOT, SLAB, VOLUMES, builds, ply, verified

class GreenMuseumbraryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference_model,cls.bridges=builds()
        cls.pieces=[p for bag in cls.reference_model['bags'] for step in bag['steps'] for p in step['pieces']]
    def test_matches_public_payload_and_fits(self):
        self.assertEqual(json.loads((DATA/'green-museumbrary.json').read_text())['model'],self.reference_model)
        self.assertEqual(len(VOLUMES),8)
        self.assertEqual(max(p['y']+parts[p['part']]['h'] for p in self.pieces),69)
        validate(self.reference_model)
        self.assertTrue(all(verified(p['part'],p['color']) for p in self.pieces))
    def test_each_free_span_has_independent_studs_on_both_towers(self):
        studs={xy for p in self.pieces if p['y']+parts[p['part']]['h']==SLAB+1 for xy in local_cells(p,'studs')}
        self.assertEqual({q['route'] for q in self.bridges},{'BC','CF','FE'})
        for q in self.bridges:
            zone={tuple(i) for i in q['deck']}
            self.assertEqual(len(zone-studs),q['studs'])
            for k in q['route']:
                self.assertGreaterEqual(len(zone&studs&ply(VOLUMES[k][1])),2)
    def test_packaged_bom_agrees_with_steps_and_ldr(self):
        from lego_bom import base_rows, key, ldraw_counts, load_mapping
        out=ROOT/'downloads/green-museumbrary'
        bom=base_rows(out/'bom.csv')
        counts=Counter((p['part'],colors[p['color']][2]) for p in self.pieces)
        self.assertEqual(counts,Counter(ldraw_counts(out/'model.ldr')))
        self.assertEqual(counts,Counter({key(row[0],row[4]):int(row[5]) for row in bom[1:]}))
        mapping=load_mapping()
        self.assertTrue(all(mapping[k]['status']=='verified' for k in counts))
if __name__=='__main__':unittest.main()

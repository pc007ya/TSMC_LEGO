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
    def test_fh_curved_wall_specific_clutch_seams_and_open_center(self):
        ring=[p for p in self.pieces if p['part']=='48092' and p['x']>=58]
        self.assertEqual(len(ring),16)
        self.assertEqual({p['color'] for p in ring},{'W'})
        self.assertEqual({p['y'] for p in ring},{3,13,23,33})
        for y in (3,13,23,33):
            studs={p['r']: local_cells(p,'studs') for p in ring if p['y']==y}
            self.assertEqual(set(studs),{0,1,2,3})
            seams=[local_cells(p,'body') for p in self.pieces
                   if p['part']=='3023' and p['y']==y+3 and
                   (p['x'],p['z']) in {(61,8),(61,15),(58,11),(65,11)}]
            self.assertEqual(len(seams),4)
            self.assertEqual([sum(bool(seam&a) for a in studs.values()) for seam in seams],[2]*4)
        opening={(x,z) for x in range(60,64) for z in range(10,14)}
        self.assertFalse(opening.intersection({q for p in self.pieces if p['y']>=34 for q in local_cells(p)}))
    def test_bc_asymmetric_outer_arcs_layers_and_actual_brick(self):
        ring=[p for p in self.pieces if p['part']=='48092' and p['x']<58]
        self.assertEqual(len(ring),51)
        self.assertEqual({(p['x'],p['z'],p['r']) for p in ring},
                         {(18,7,2),(22,7,3),(14,11,2)})
        for y in range(5,56,3):
            self.assertEqual(len([p for p in ring if p['y']==y]),3)
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

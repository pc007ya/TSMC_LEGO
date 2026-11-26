import unittest
import json
from collections import Counter
from design import DATA, parts, colors, validate, local_cells, world_cell
from taichung_city_hall import build, ID, ROOT, REF, LEFT, RIGHT, Z0, Z1, H0, H1, COURTS
from green_museumbrary import verified
from lego_bom import base_rows, key, ldraw_counts, load_mapping

class HallTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=build()
        cls.items=[p for bag in cls.model['bags'] for step in bag['steps'] for p in step['pieces']]
        cls.out=ROOT/'downloads'/ID
    def test_geometry_contacts_and_steps(self):
        self.assertEqual(json.loads((DATA/(ID+'.json')).read_text()),dict(model=self.model,reference=REF))
        validate(self.model)
        self.assertTrue(all(verified(p['part'],p['color']) for p in self.items))
        self.assertTrue(all(len(s['pieces'])<=12 for bag in self.model['bags'] for s in bag['steps']))
        self.assertTrue(all(0<sum(len(s['pieces']) for s in b['steps'])<=350 for b in self.model['bags']))
    def test_portal_open_and_stitch_contacts(self):
        def studs(p,layer):
            return {(int(x),int(z)) for i,j in local_cells(p,layer) for x,z,_,_ in [world_cell(self.model,p,i,j)]}
        open_portal={(x,z) for x in range(LEFT,RIGHT) for z in range(Z0,Z1)}
        floor=4; sofit=19
        self.assertFalse(any(floor<=p['y']<sofit and studs(p,'body')&open_portal for p in self.items))
        for plane,z0,z1 in [(19,H0,H1),(41,Z0,Z1)]:
            arms=[p for p in self.items if p['y']==plane and p['part']=='4282']
            merges=[p for p in self.items if p['y']==plane+1 and p['part']=='4282']
            self.assertEqual(len(merges),(z1-z0)//2)
            for m in merges:
                a,b=sorted((p for p in arms if p['z']==m['z']),key=lambda p:p['x'])
                hits=[len(studs(m,'bottom')&studs(p,'studs')) for p in (a,b)]
                self.assertEqual(hits,[8,8])
                for p in (a,b):
                    leg=set().union(*(studs(q,'studs') for q in self.items if q['y']+parts[q['part']]['h']==plane))
                    self.assertGreaterEqual(len(leg&studs(p,'bottom')),3)
        for court in COURTS:
            mid={(x,z) for x,z in court if all((x+i,z+j) in court for i,j in ((1,0),(-1,0),(0,1),(0,-1)))}
            self.assertFalse(any(p['y'] in (4,8,12) and studs(p,'body')&mid for p in self.items))
    def test_official_bom_matches_build_and_ldr(self):
        expected=Counter((p['part'],colors[p['color']][2]) for p in self.items)
        bom=base_rows(self.out/'bom.csv')
        self.assertEqual(expected,Counter({key(row[0],row[4]):int(row[5]) for row in bom[1:]}))
        self.assertEqual(expected,Counter(ldraw_counts(self.out/'model.ldr')))
        mapping=load_mapping()
        self.assertTrue(all(mapping[k]['status']=='verified' and mapping[k]['lego_element_id'] for k in expected))
if __name__=='__main__':
    unittest.main()

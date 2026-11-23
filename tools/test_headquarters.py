"""Check the two real stud connections between the blue bridge and the grey tower."""
import unittest

from campus_models import twin
from design import Building, local_cells, parts, world_cell


class HeadquartersJointTest(unittest.TestCase):
    def test_perpendicular_bridge_grips_tower(self):
        model = twin(Building)
        pieces = [p for bag in model['bags'] for step in bag['steps'] for p in step['pieces']]

        def cells(p, layer='body'):
            return {(x, z) for i, j in local_cells(p, layer)
                    for x, z, _, _ in [world_cell(model, p, i, j)]}

        def layer_at(y, color, face):
            layer = 'studs' if face == 'top' else 'bottom'
            result = set()
            for p in pieces:
                level = p['y'] + (parts[p['part']]['h'] if face == 'top' else 0)
                if p['color'] == color and level == y:
                    result.update(cells(p, layer))
            return result

        ties = [p for p in pieces if p['part'] == '3710' and p['color'] == 'B' and p['y'] == 35]
        self.assertEqual(len(ties), 2)
        grey = layer_at(35, 'L', 'top')
        roof = layer_at(35, 'W', 'top')
        wall_above = layer_at(36, 'L', 'bottom')
        bridge_above = layer_at(36, 'B', 'bottom')
        for p in ties:
            pads = cells(p, 'bottom')
            rear = pads & grey
            self.assertEqual(len(rear), 1)
            x, z = next(iter(rear))
            forward = {(x, z + offset) for offset in (1, 2, 3)}
            self.assertEqual(pads & roof, forward)
            self.assertTrue(rear <= wall_above)
            self.assertTrue(forward <= bridge_above)
            # The top of the frame also meets the grey wall without a gap.
            self.assertIn((x, z), layer_at(38, 'L', 'bottom'))
            self.assertIn((x, z + 1), layer_at(39, 'B', 'top'))


if __name__ == '__main__':
    unittest.main()

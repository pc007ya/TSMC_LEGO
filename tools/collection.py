"""Aggregate the five verified model inventories into one procurement CSV."""
from collections import Counter
import csv
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
models=json.loads((root/'data/models.json').read_text())
catalog=json.loads((root/'data/catalog.json').read_text())
counts=[Counter((p['part'],p['color']) for b in m['bags'] for s in b['steps'] for p in s['pieces']) for m in models]
with (root/'downloads/collection-bom.csv').open('w',encoding='utf-8-sig',newline='') as f:
    out=csv.writer(f)
    out.writerow(['LDraw料號','Rebrickable料號','零件','顏色','色號','全系列合計']+[m['name'] for m in models])
    for (part,color),total in sorted(sum(counts,Counter()).items()):
        out.writerow([part,'6141' if part=='4073' else part,catalog['parts'][part]['name'],catalog['colors'][color]['name'],catalog['colors'][color]['ldraw'],total]+[c[part,color] for c in counts])

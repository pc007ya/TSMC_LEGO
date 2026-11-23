"""Aggregate the five verified model inventories into one procurement CSV."""
from collections import Counter
import csv
import json
import fitz
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
with (root/'downloads/collection-decals.csv').open('w',encoding='utf-8-sig',newline='') as f:
    out=csv.writer(f)
    out.writerow(['模型','貼紙號','貼紙位置','圖樣','枚數','寬 mm','高 mm','袋號','步驟','承貼料號','承貼面'])
    sides={'front':'前面','back':'背面','right':'右面','left':'左面'}
    for m in models:
        number=step_no=0
        for b,bag in enumerate(m['bags'],1):
            for step in bag['steps']:
                step_no+=1
                for p in step['pieces']:
                    if 'decal' not in p:continue
                    number+=1
                    d=p['decal']
                    out.writerow([m['name'],f'S{number:02}',d['label'],d['art'],1,d['widthMM'],d['heightMM'],b,step_no,p['part'],sides[d['face']]])

with fitz.open() as sheets:
    for model in models:
        with fitz.open(root/'downloads'/model['id']/'stickers.pdf') as source:
            sheets.insert_pdf(source)
    sheets.set_metadata({'title':'晶圓建築積木・五款原尺寸貼紙', 'author':'FABFORM'})
    sheets.save(root/'downloads/collection-stickers.pdf',garbage=4,deflate=True)

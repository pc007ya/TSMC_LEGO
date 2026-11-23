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

refs=json.loads((root/'data/references.json').read_text())
lines=['# 五款建築的照片來源與積木數量','',
       '原盒件數取自 TShop 商品圖上的盒面印字。商品尺寸依頁面順序抄錄；底座凸點數依俯視圖估讀。每款另列本版每袋實際放入的零件，加總即為備料數。標誌貼紙另計。','',
       '| 模型 | TShop 盒號 | 原盒件數 | 商品尺寸（公分） | 本版件數 | 本版底座（凸點） |',
       '| --- | --- | ---: | --- | ---: | --- |']
for m,counts_for_model in zip(models,counts):
    ref=refs[m['id']]
    lines.append(f'| {m["name"]} | {ref["boxCode"]} | {ref["boxPieces"]:,} | {ref["dimensionsCm"]} | {counts_for_model.total():,} | {m["width"]} × {m["depth"]} |')
lines+=['',f'五款原盒合計 **{sum(r["boxPieces"] for r in refs.values()):,} 件**。本版合計 **{sum(c.total() for c in counts):,} 件**。','',
        '本版使用標準 8 mm 凸點積木。底座大小、可購買的料號、交錯補強和屋頂細節都會影響用量。公開圖能核對外形、相對位置與商品盒件數；原盒內部扣法及逐件 BOM 無法從圖中讀出。本版內構、分袋與步驟由專案設計。','']
for m in models:
    r=refs[m['id']]
    bag_counts=[sum(len(s['pieces']) for s in b['steps']) for b in m['bags']]
    stickers=sum('decal' in p for b in m['bags'] for s in b['steps'] for p in s['pieces'])
    lines+=[f'## {m["name"]}','',r['observation'],'',
            f'依商品俯視圖估讀，原盒底座約 {r["estimatedBase"]} 凸點。本版底座 {m["width"]} × {m["depth"]} 凸點，約 {m["width"]*.8:g} × {m["depth"]*.8:g} 公分。','',
            f'依袋號備料：{" ＋ ".join(str(n) for n in bag_counts)} ＝ {sum(bag_counts):,} 件。另備 {stickers} 枚貼紙。','']
    if m['id']=='arc':
        lines+=['原盒三視圖中，斜廊最後方屋角約越過底板後緣 5 至 6 個凸點。受本版底座和廊架位置影響，重建的後懸挑約 4 格，三片 2 × 16 長板跨在前兩座支架上。','']
    lines += [f'[商品規格與原盒]({r["product"]}) · [盒面及商品三視圖原圖]({r["photo"]}) · [{r["buildingCredit"]}]({r["buildingSource"]})','',
              f'[本版俯視圖](../assets/previews/{m["id"]}-plan.webp) · [逐件手冊]({m["id"]}/manual.md) · [分袋 BOM]({m["id"]}/bom.csv)','']
(root/'downloads/reference-guide.md').write_text('\n'.join(lines),encoding='utf-8')

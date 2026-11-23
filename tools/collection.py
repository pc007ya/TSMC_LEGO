"""Build the procurement files, sticker sheets and reference notes for each series."""
import argparse
from collections import Counter
import csv
import json
import fitz
from pathlib import Path

root=Path(__file__).resolve().parents[1]
all_models=json.loads((root/'data/models.json').read_text())
catalog=json.loads((root/'data/catalog.json').read_text())

def export_series(models,series,title):
    counts=[Counter((p['part'],p['color']) for b in m['bags'] for s in b['steps'] for p in s['pieces']) for m in models]
    with (root/'downloads'/f'{series}-bom.csv').open('w',encoding='utf-8-sig',newline='') as f:
        out=csv.writer(f)
        out.writerow(['LDraw料號','Rebrickable料號','零件','顏色','色號','全系列合計']+[m['name'] for m in models])
        for (part,color),total in sorted(sum(counts,Counter()).items()):
            out.writerow([part,'6141' if part=='4073' else part,catalog['parts'][part]['name'],catalog['colors'][color]['name'],catalog['colors'][color]['ldraw'],total]+[c[part,color] for c in counts])
    with (root/'downloads'/f'{series}-decals.csv').open('w',encoding='utf-8-sig',newline='') as f:
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
        sheets.set_metadata({'title':title+'・原尺寸貼紙', 'author':'FABFORM'})
        sheets.save(root/'downloads'/f'{series}-stickers.pdf',garbage=4,deflate=True)
    return counts

parser=argparse.ArgumentParser()
parser.add_argument('--series',choices=['collection','taichung'])
series=parser.parse_args().series
refs=json.loads((root/'data/references.json').read_text())
if series in (None,'collection'):
    models=[m for m in all_models if m.get('series','collection')=='collection']
    counts=export_series(models,'collection','晶圓建築積木')
    lines=['# 五款建築的照片來源與積木數量','',
           '原盒件數取自 TShop 商品圖上的盒面印字。商品尺寸依頁面順序抄錄；底座凸點數依俯視圖估讀。每款另列本版每袋實際放入的零件，加總即為備料數。標誌貼紙另計。','',
           '| 模型 | TShop 盒號 | 原盒件數 | 商品尺寸（公分） | 本版件數 | 本版底座（凸點） |',
           '| --- | --- | ---: | --- | ---: | --- |']
    for m,counts_for_model in zip(models,counts):
        ref=refs[m['id']]
        lines.append(f'| {m["name"]} | {ref["boxCode"]} | {ref["boxPieces"]:,} | {ref["dimensionsCm"]} | {counts_for_model.total():,} | {m["width"]} × {m["depth"]} |')
    lines+=['',f'五款原盒合計 **{sum(refs[m["id"]]["boxPieces"] for m in models):,} 件**。本版合計 **{sum(c.total() for c in counts):,} 件**。','',
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

plans=[m for m in all_models if m.get('series')=='taichung']
if plans and series in (None,'taichung'):
    counts=export_series(plans,'taichung','台中產業建築')
    lines=['# 台中產業建築積木規劃','',
           'Fab 15A 與 Fab 15B 各自成盒。Fab 25 記錄 P1 鋼構施工階段。巨大集團以中科全球營運總部及自行車文化探索館同框呈現。','',
           '每格凸點間距 8 mm，每層薄板高 3.2 mm。下表為本版底座尺寸與數位設計的實際件數。建築比例經壓縮，件數由分袋零件表加總，貼紙另外計算。','',
           '| 模型 | 底座（凸點） | 底座（公分） | 積木 | 袋 | 步驟 |',
           '| --- | --- | --- | ---: | ---: | ---: |']
    for m,c in zip(plans,counts):
        steps=sum(len(b['steps']) for b in m['bags'])
        lines.append(f'| {m["name"]} | {m["width"]} × {m["depth"]} | {m["width"]*.8:g} × {m["depth"]*.8:g} | {c.total():,} | {len(m["bags"])} | {steps} |')
    lines+=['',f'系列合計 **{sum(c.total() for c in counts):,} 件積木**。採購時以料號、顏色與袋號核對。[台中系列 BOM](taichung-bom.csv) · [原尺寸貼紙](taichung-stickers.pdf)','']
    for m in plans:
        ref=refs[m['id']]
        lines+=[f'## {m["name"]}','',ref['edition'],'',f'**外觀依據**　{ref["observation"]}','',
                f'**造型取捨**　{ref["interpretation"]}','','| 袋號 | 組裝內容 | 件數 |','| ---: | --- | ---: |']
        for i,b in enumerate(m['bags'],1):
            qty=sum(len(s['pieces']) for s in b['steps'])
            lines.append(f'| {i} | {b["name"]} | {qty} |')
        mid=m['id']
        lines+=['',' · '.join(f'[{v["label"]}]({v["url"]})' for v in ref['sources']),'',
                f'[3D 模型](https://pc007ya.github.io/TSMC_LEGO/?set={mid}) · [A4 手冊]({mid}/manual.pdf) · [逐件 MD]({mid}/manual.md) · [分袋 BOM]({mid}/bom.csv) · [LDraw]({mid}/model.ldr)','']
    lines+=['## 試拼重點','','先檢查各袋的承重與接縫，再從正面、側面與上方核對立面及棟距。數位檢查涵蓋扣點、碰撞、插入順序與整體連通。實際扣合力、拆裝與搬運穩定度有待實體試拼。','']
    (root/'downloads/taichung-plan.md').write_text('\n'.join(lines),encoding='utf-8')

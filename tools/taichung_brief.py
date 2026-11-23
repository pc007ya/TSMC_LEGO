"""Print the Taichung design proposal from the same model, reference and bag data as the site."""
import base64
import json
from html import escape
from pathlib import Path

import fitz
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
MODELS=[m for m in json.loads((ROOT/'data/models.json').read_text()) if m.get('series')=='taichung']
REFS=json.loads((ROOT/'data/references.json').read_text())
PARTS=json.loads((ROOT/'data/catalog.json').read_text())['parts']
SITE='https://pc007ya.github.io/TSMC_LEGO/'

STYLE="""
@page{size:A4;margin:0}*{box-sizing:border-box}body{margin:0;font-family:"PingFang TC",sans-serif;color:#192e29;font-size:10pt;line-height:1.5}
section{width:210mm;min-height:297mm;padding:14mm 15mm 13mm;break-after:page;position:relative}section:last-child{break-after:auto}
h1,h2,h3,p,figure{margin:0}h1{font-size:27pt;line-height:1.27;margin:6mm 0 2mm}h2{font-size:22pt;line-height:1.2;margin:5mm 0 2mm}h3{font-size:11pt;margin:3mm 0 1mm}a{color:#245544}
.mast{display:flex;justify-content:space-between;border-bottom:1pt solid #748a7c;padding-bottom:3mm;font:700 9pt Arial;color:#35574a;letter-spacing:.08em}
.lead{font-size:11pt;line-height:1.65}.grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:5mm 3mm;margin:5.5mm 0}
.card{grid-column:span 2;display:block;text-decoration:none;color:inherit;border-bottom:1px solid #c4cec5;padding-bottom:3mm}.card img{width:100%;height:38mm;object-fit:contain;background:#e9eae7;display:block}
.card.giant{grid-column:span 3}.card.giant img{height:58mm}.card strong{display:block;font-size:12.5pt;margin:2mm 0 .8mm}.meta,figcaption{font-size:8.5pt;color:#476455}.spec{background:#e9efe7;padding:2.6mm 4mm;margin:3mm 0 2mm;font-weight:650}
.views{display:grid;grid-template-columns:1.7fr 1fr;gap:3mm;margin:3mm 0}.views img{display:block;width:100%;height:56mm;object-fit:contain;background:#e9eae7}.views figcaption{margin-top:1mm}
table{width:100%;border-collapse:collapse;font-size:9pt}th{text-align:left;color:#355a4a;background:#e9efe7}td,th{padding:1.1mm 2.5mm;border-bottom:.25mm solid #d6dfd6}td:first-child{font-variant-numeric:tabular-nums}th:last-child,td:last-child{text-align:right}
.links{font-size:8pt;line-height:1.9;margin-top:1mm}.footer{position:absolute;bottom:9mm;left:15mm;right:15mm;display:flex;justify-content:space-between;border-top:.3mm solid #a7b9ad;padding-top:2mm;font-size:8pt;color:#4f6a5b}
"""
def picture(mid,view=None):
    suffix='-'+view if view else ''
    raw=(ROOT/'assets/previews'/f'{mid}{suffix}.webp').read_bytes()
    return 'data:image/webp;base64,'+base64.b64encode(raw).decode()

def bag_counts(model):
    return [sum(len(s['pieces']) for s in b['steps']) for b in model['bags']]

def links(pairs):
    return '　·　'.join(f'<a href="{escape(url,quote=True)}">{escape(title)}</a>' for title,url in pairs)

def content():
    sheets=[]
    cards=[]
    for m in MODELS:
        mid=m['id'];qty=sum(bag_counts(m))
        card_class='card giant' if mid in {'giant','dajia'} else 'card'
        cards.append(f'<a class="{card_class}" href="{SITE}?set={mid}"><img src="{picture(mid)}"><strong>{escape(m["name"])}</strong><span class="meta">{m["width"]} × {m["depth"]} 凸點　／　{qty:,} 件</span></a>')
    total=sum(sum(bag_counts(m)) for m in MODELS)
    sheets.append(f'<h1>台中產業建築積木規劃</h1><p class="lead">台積電十五 A、十五 B 廠與二十五廠分別成盒。巨大中科總部與文化館共用一座底板，大甲日南廠另有一盒。點選模型可旋轉查看外觀。</p><div class="grid">{"".join(cards)}</div><div class="spec">{len(MODELS)} 款共 {total:,} 件積木　／　標準 8 mm 凸點間距</div><p class="meta">件數依本版設計清點，貼紙另計。各款採獨立比例，實際扣合力及搬運強度仍待試拼。</p>')
    for m in MODELS:
        mid=m['id'];ref=REFS[mid];quantities=bag_counts(m)
        steps=[s for b in m['bags'] for s in b['steps']]
        pieces=[p for s in steps for p in s['pieces']]
        height=max(p['y']+PARTS[p['part']]['h'] for p in pieces)*.32
        plan=next(v for v in m['views'] if v['id']=='plan')
        rows=''.join(f'<tr><td>{i:02}</td><td>{escape(b["name"])}</td><td>{q:,}</td></tr>' for i,(b,q) in enumerate(zip(m['bags'],quantities),1))
        sources=links([(s['label'],s['url']) for s in ref['sources']])
        docs=links([('旋轉模型',SITE+'?set='+mid),('分袋零件表',SITE+'downloads/'+mid+'/bom.csv'),('A4 逐步手冊',SITE+'downloads/'+mid+'/manual.pdf')])
        sheets.append(f'<h2>{escape(m["name"])}</h2><p class="meta">{escape(m["en"])}　／　{escape(ref["edition"])}</p><div class="spec">{len(pieces):,} 件　／　{len(m["bags"])} 袋　／　{len(steps)} 步　／　底座 {m["width"]*.8:g} × {m["depth"]*.8:g} cm，模型高約 {height:.1f} cm</div><div class="views"><figure><img src="{picture(mid)}"><figcaption>積木完成圖</figcaption></figure><figure><img src="{picture(mid,plan["id"])}"><figcaption>俯視配置</figcaption></figure></div><h3>建築依據</h3><p>{escape(ref["observation"])}</p><h3>積木造型與簡化</h3><p>{escape(ref["interpretation"])}</p><h3>分袋組裝</h3><table><thead><tr><th>袋號</th><th>組裝內容</th><th>件數</th></tr></thead><tbody>{rows}</tbody></table><h3>參考與備料</h3><p class="links">{sources}<br>{docs}</p>')
    pages=[]
    for i,body in enumerate(sheets):
        pages.append(f'<section><div class="mast"><span>FABFORM</span><span>TAICHUNG　／　ARCHITECTURE</span></div>{body}<div class="footer"><span>台中產業建築積木規劃</span><span>{i+1} / {len(sheets)}</span></div></section>')
    return '<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><title>台中產業建築積木規劃</title><style>'+STYLE+'</style>'+''.join(pages)+'</html>'

if __name__=='__main__':
    assert MODELS
    with sync_playwright() as e, e.chromium.launch(channel='chrome',headless=True) as browser:
        page=browser.new_page()
        page.set_content(content(),wait_until='load')
        page.evaluate('Promise.all(Array.from(document.images, i=>i.decode()))')
        raw=page.pdf(print_background=True,prefer_css_page_size=True)
    with fitz.open(stream=raw,filetype='pdf') as doc:
        assert len(doc)==1+len(MODELS)
        doc.save(ROOT/'downloads/taichung-plan.pdf',garbage=4,deflate=True,deflate_images=True,use_objstms=1)
        cover=doc[0]
        cards=cover.get_links()
        giant_cards=[card for card in cards if card.get('uri') in {SITE+'?set=giant',SITE+'?set=dajia'}]
        assert len(cards)==len(MODELS) and len(giant_cards)==2
        for filename,selection in [('taichung-series.webp',cards),('giant-pair.webp',giant_cards)]:
            gallery=fitz.Rect()
            for card in selection:
                gallery.include_rect(card['from'])
            preview=cover.get_pixmap(matrix=fitz.Matrix(2,2),clip=gallery+(-5,-5,5,5))
            Image.frombytes('RGB',(preview.width,preview.height),preview.samples).save(
                ROOT/'assets/previews'/filename,quality=90)

        print('Taichung design proposal:',len(doc),'pages')

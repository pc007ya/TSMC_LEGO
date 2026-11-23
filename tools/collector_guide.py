"""Print a scale and model comparison and construction overview for the 6,000-piece editions."""
import argparse
import base64
import json
from html import escape
from io import BytesIO
from functools import lru_cache
from pathlib import Path

import fitz
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://pc007ya.github.io/TSMC_LEGO/'
PREVIEWS = ROOT / 'assets/previews'
STYLE = """
@page{size:A4 landscape;margin:0}*{box-sizing:border-box}body{margin:0;font:10pt/1.45 'PingFang TC',sans-serif;color:#20332e}
section{width:297mm;height:210mm;padding:10mm 13mm 13mm;break-after:page;position:relative}section:last-child{break-after:auto}
header,footer{display:flex;justify-content:space-between;align-items:center;color:#496256}header{border-bottom:.35mm solid #73877a;padding-bottom:2mm;font:bold 8.5pt Arial,sans-serif;letter-spacing:.09em}
footer{position:absolute;bottom:6mm;left:13mm;right:13mm;border-top:.25mm solid #bfcdc2;padding-top:1.5mm;font-size:8pt}
h1,h2,h3,p,figure{margin:0}h1{font-size:28pt;margin:3mm 0 1mm}h2{font-size:21pt;margin:3mm 0 1mm}h3{font-size:12pt;margin-bottom:2mm}
a{color:#255a49}.intro{color:#486253;font-size:10pt}.pair,.compare,.build{display:grid;gap:5mm;margin:4mm 0}
.pair{grid-template-columns:repeat(2,minmax(0,1fr))}.pair a{border-bottom:.3mm solid #c5cec6;color:inherit;text-decoration:none;padding-bottom:2mm}
.pair img,.compare img,.detail img{display:block;width:100%;object-fit:contain;background:#d3d6d6}
.pair img{height:89mm}.pair:has(a:nth-child(3)) img{height:56mm}.pair strong,.compare strong{display:block;font-size:13pt;margin-top:1.5mm}.meta,figcaption,small{color:#476252;font-size:9pt}
.compare{grid-template-columns:1fr 1.55fr}.compare img{height:77mm}.note{display:grid;grid-template-columns:1fr 1fr;gap:5mm;margin:3mm 0}.note p{font-size:9.4pt}
.build{grid-template-columns:1fr 1.33fr;align-items:start}.detail{display:grid;grid-template-columns:34mm 1fr;gap:2mm;align-items:center;margin-bottom:2mm}.detail img{height:24mm}.build.many-details .detail img{height:19mm}.detail b{font-size:10pt}.detail figcaption{font-size:8.5pt}
table{width:100%;border-collapse:collapse;font-size:8.4pt}th{text-align:left;background:#eaf0e9;color:#315944}th,td{padding:.75mm 1.5mm;border-bottom:.2mm solid #d8dfd8}td:last-child,th:last-child{text-align:right}
.refs{margin-top:2mm;font-size:8pt}.bar{background:#e9efe8;padding:2mm 3mm;margin:2mm 0;font-weight:650}.key{padding-top:2mm;color:#375141}
"""
@lru_cache(maxsize=None)
def picture(model_id, view=None):
    path=PREVIEWS / (model_id+('-'+view if view else '')+'.webp')
    with Image.open(path) as photo:
        image=photo.convert('RGB')
    image.thumbnail((1450,950),Image.Resampling.LANCZOS)
    encoded=BytesIO()
    image.save(encoded,format='JPEG',quality=89,optimize=True)
    return 'data:image/jpeg;base64,'+base64.b64encode(encoded.getvalue()).decode('ascii')

def stats(m, parts):
    steps=[s for bag in m['bags'] for s in bag['steps']]
    pieces=[p for step in steps for p in step['pieces']]
    return (len(pieces),len(m['bags']),len(steps),max(p['y']+parts[p['part']]['h'] for p in pieces)*.32)

def linked(title,url):
    return f'<a href="{escape(url,quote=True)}">{escape(title)}</a>'

def page(body,number,total,brand,title):
    return (f'<section><header><span>FABFORM</span><span>{brand}　/　6,000 PIECES</span></header>{body}'
            f'<footer><span>{title}積木・版本與分袋對照</span><span>{number} / {total}</span></footer></section>')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--series',choices=['collector','fab-collector'],default='collector')
    group=parser.parse_args().series
    if group=='fab-collector':
        title='台積電中科三廠';brand='TSMC'
        introduction='比較十五 A 廠的玻璃角塔、十五 B 廠的金綠外屏，以及二十五廠一期在 2026 年 8 月的露天鋼構。'
        cover_file='fab-6000-series.webp'
    else:
        title='巨大建築';brand='GIANT GROUP'
        introduction='透過較大的底板與更細的構件，分別重建中科的曲面展館、大甲的街面廠房。'
        cover_file='giant-6000-series.webp'
    all_models=json.loads((ROOT/'data/models.json').read_text())
    models=[m for m in all_models if m.get('series')==group]
    originals={m['id']:m for m in all_models}
    refs=json.loads((ROOT/'data/references.json').read_text())
    parts=json.loads((ROOT/'data/catalog.json').read_text())['parts']
    assert models
    cards=[]
    for m in models:
        pcs,bags,steps,_=stats(m,parts)
        cards.append(f'<a href="{SITE}?set={m["id"]}"><img src="{picture(m["id"])}"><strong>{escape(m["tabName"])}</strong>'
                     f'<span class="meta">{pcs:,} 件積木　／　{bags} 袋　／　{steps} 步</span></a>')
    pages=[f'<h1>{title}・6,000 件版</h1><p class="intro">{introduction}點選完成圖可開啟對應模型。</p>'
            +f'<div class="pair" style="grid-template-columns:repeat({len(cards)},minmax(0,1fr))">'+''.join(cards)+'</div><p class="key">每盒獨立計件，貼紙另計。原版與高精度版均提供圖解、分袋採購表與 LDraw 設計檔。</p>']
    for m in models:
        mid=m['id'];old=originals[m['standardId']];r=refs[mid]
        pcs,bags,steps,height=stats(m,parts)
        headings=f'<h2>{escape(m["tabName"])}</h2>'
        comp=[]
        for item,cap in [(old,'原版'),(m,'高精度版')]:
            n,b,s,h=stats(item,parts)
            comp.append(f'<figure><a href="{SITE}?set={item["id"]}"><img src="{picture(item["id"])}"></a><strong>{cap}　{n:,} 件</strong>'
                        f'<figcaption>{item["width"]} × {item["depth"]} 凸點　／　{b} 袋　／　{s} 步　／　高 {h:.1f} cm</figcaption></figure>')
        pages.append(headings+'<p class="intro">兩款完成圖各自適應圖框。請用底座凸點數和完成尺寸比較實際比例。</p><div class="compare">'+''.join(comp)
                     +f'</div><div class="bar">高精度版含底座約 {m["width"]*.8:g} × {m["depth"]*.8:g} × {height:.1f} 公分</div>'
                     +f'<div class="note"><div><h3>實景依據</h3><p>{escape(r["observation"])}</p></div><div><h3>積木造型</h3><p>{escape(r["interpretation"])}</p></div></div>')
        details=[v for v in m['views'] if v.get('region')] or m['views']
        shots=[]
        for v in details:
            shots.append(f'<figure class="detail"><a href="{SITE}?set={mid}&amp;view={v["id"]}"><img src="{picture(mid,v["id"])}"></a>'
                         f'<figcaption><b>{escape(v["name"])}</b><br>{escape(v["note"])}</figcaption></figure>')
        rows=[];start=1
        for i,bag in enumerate(m['bags'],1):
            end=start+len(bag['steps'])-1;qty=sum(len(s['pieces']) for s in bag['steps'])
            rows.append(f'<tr><td>{i:02}</td><td>{escape(bag["name"])}</td><td>{start}–{end}</td><td>{qty:,}</td></tr>')
            start=end+1
        sources='　·　'.join(linked(s['label'],s['url']) for s in r['sources'])
        files='　·　'.join(linked(t,SITE+'downloads/'+mid+'/'+f) for t,f in [('逐步手冊','manual.pdf'),('分袋採購表','bom.csv'),('原尺寸貼紙','stickers.pdf')])
        pages.append(headings+f'<p class="intro">細節視角與分袋組裝</p><div class="build {"many-details" if len(shots)>4 else ""}"><div>'+''.join(shots)+
                    f'<p class="refs">{files}</p></div><div><h3>分袋順序</h3><table><thead><tr><th>袋</th><th>主要構件</th><th>步驟</th><th>件數</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div></div>'
                    +f'<p class="refs">{sources}</p><p class="refs">每顆積木已檢查碰撞、上方安裝路徑、扣點與整體連通性。尚待實體驗證扣合力及搬運穩定度。</p>')
    html='<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><title>'+title+'・6,000 件版</title><style>'+STYLE+'</style>'+''.join(page(p,i+1,len(pages),brand,title) for i,p in enumerate(pages))+'</html>'
    with sync_playwright() as engine, engine.chromium.launch(channel='chrome',headless=True) as browser:
        tab=browser.new_page();tab.set_content(html,wait_until='load')
        tab.evaluate('Promise.all(Array.from(document.images,i=>i.decode()))')
        pdf=tab.pdf(prefer_css_page_size=True,print_background=True)
    with fitz.open(stream=pdf,filetype='pdf') as doc:
        assert len(doc)==len(pages)
        doc.save(ROOT/'downloads'/f'{group}-plan.pdf',garbage=4,deflate=True,deflate_images=True,use_objstms=1)
        first=doc[0];bounds=fitz.Rect()
        for link in first.get_links():bounds.include_rect(link['from'])
        pix=first.get_pixmap(clip=bounds+(-3,-3,3,3),matrix=fitz.Matrix(1.75,1.75))
        Image.frombytes('RGB',(pix.width,pix.height),pix.samples).save(PREVIEWS/cover_file,quality=93)
    print(len(pages),'guide pages')

if __name__=='__main__':
    main()

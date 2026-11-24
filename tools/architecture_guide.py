"""Print the theatre's architectural views and bag index from its actual build."""
from html import escape
import json

import fitz
from playwright.sync_api import sync_playwright

from collector_guide import ROOT, SITE, linked, picture, stats

STYLE = """
@page{size:A4 landscape;margin:0}*{box-sizing:border-box}body{margin:0;color:#263333;font:11pt/1.5 'PingFang TC',sans-serif}
section{width:297mm;height:210mm;padding:10mm 13mm 14mm;position:relative;break-after:page}section:last-child{break-after:auto}
header,footer{display:flex;justify-content:space-between;align-items:center;border-bottom:.35mm solid #3d5856;padding-bottom:2mm;font:9pt Arial,sans-serif;color:#35514e}
footer{position:absolute;bottom:6mm;left:13mm;right:13mm;border-bottom:0;border-top:.25mm solid #bccac6;padding-top:2mm}
header b{letter-spacing:.14em}h1,h2,h3,p,figure{margin:0}h1,h2{margin:3mm 0 2mm;line-height:1.25}h1{font-size:27pt}h2{font-size:22pt}
h3{font-size:14pt;margin-bottom:1.7mm}.intro{color:#435a55}.hero{display:grid;grid-template-columns:1.95fr 1fr;align-items:center;gap:7mm;margin-top:5mm}
img{display:block;width:100%;height:100%;object-fit:contain;background:#cccfd0}.hero figure{height:110mm}
a{color:#24564d}.stats{border-block:.3mm solid #a8b9b2;margin:4mm 0;padding:2.5mm 0;font-weight:650}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:6mm;margin:4mm 0}.cards img{height:89mm}.cards h3{margin-top:2mm}
.cards p,aside p{font-size:10pt}.refs{font-size:9pt;margin-top:3mm}.inventory{display:grid;grid-template-columns:1.7fr 1fr;gap:8mm;align-items:start;margin-top:4mm}
table{border-collapse:collapse;width:100%;font-size:10pt}th,td{border-bottom:.23mm solid #cdd8d3;padding:1.25mm 1.7mm;text-align:left}
th{background:#e9eeeb}td:last-child,th:last-child{text-align:right}.inventory aside{border-left:.6mm solid #71968b;padding-left:5mm}
aside h3:not(:first-child){margin-top:5mm}figcaption{font-size:9pt;color:#4b625c}
"""

def theatre_guide():
    model=next(m for m in json.loads((ROOT/'data/models.json').read_text()) if m['id']=='ntt6000')
    model_id=model['id']
    ref=json.loads((ROOT/'data/references.json').read_text())[model_id]
    catalog=json.loads((ROOT/'data/catalog.json').read_text())
    pieces,bags,steps,height=stats(model,catalog['parts'])
    views={v['id']:v for v in model['views']}
    website=SITE+'?set='+model_id
    def scene(view=None):
        label=views[view]['name'] if view else model['name']
        return (f'<a href="{website}'+(f'&amp;view={view}' if view else '')+f'"><img alt="{escape(label)}" '
                f'src="{picture(model_id,view)}"></a>')
    def card(view):
        v=views[view]
        return f'<figure>{scene(view)}<h3>{escape(v["name"])}</h3><p>{escape(v["note"])}</p></figure>'
    def pair(heading,description,left,right):
        return f'<h2>{heading}</h2><p class="intro">{description}</p><div class="cards">{card(left)}{card(right)}</div>'
    size=f'{model["width"]*.8:g} × {model["depth"]*.8:g} × {height:.1f} 公分'
    sources='　·　'.join(linked(item['label'],item['url']) for item in ref['sources'])
    pages=[f'<h1>臺中國家歌劇院</h1><p class="intro">National Taichung Theater　／　建築與組裝導覽</p>'
           f'<div class="hero"><figure>{scene()}</figure><aside><h3>從噴水廣場看曲牆</h3><p>{escape(ref["observation"])}</p>'
           f'<p class="stats">{pieces:,} 件　／　{bags} 袋　／　{steps} 步<br>含底座約 {size}</p>'
           f'<p>點選本書的模型圖，即可在網站旋轉至相同角度。</p></aside></div>',
           pair('壺形立面與前廣場','從正面觀察玻璃、實牆與凹洞的差別，再沿水道繞到建築側面。','bottles','plaza'),
           pair('屋頂與劇場剖面','同一組積木切換兩種觀看方式。剖視會隱藏切面以上的積木，方便看清座席和舞臺。','garden','auditorium')]
    rows=[];start=1
    for index,b in enumerate(model['bags'],1):
        end=start+len(b['steps'])-1
        count=sum(len(s['pieces']) for s in b['steps'])
        rows.append(f'<tr><td>{index:02}</td><td>{escape(b["name"])}</td><td>{start}–{end}</td><td>{count}</td></tr>')
        start=end+1
    resources='　·　'.join(linked(label,SITE+'downloads/'+model_id+'/'+file) for label,file in [
        ('離線逐步圖解','manual.html'),('A4 手冊','manual.pdf'),('採購 BOM','bom.csv'),('原寸貼紙','stickers.pdf'),('LDraw','model.ldr')])
    pages.append('<h2>分袋與實物尺寸</h2><div class="inventory"><table><thead><tr><th>袋</th><th>主要構件</th><th>步驟</th><th>件數</th></tr></thead>'
                 f'<tbody>{"".join(rows)}</tbody></table><aside><h3>如何跟著組裝</h3><p>備齊該袋的料號與顏色。圖面先標出本步要加的零件，再列定位順序。遇到標誌，先將原尺寸貼紙貼在指定磚面。</p>'
                 f'<h3>縮尺處理</h3><p>{escape(ref["interpretation"])}</p><p class="refs">{resources}</p></aside></div><p class="refs">{sources}</p>')
    markup=[]
    for i,page in enumerate(pages,1):
        markup.append(f'<section><header><b>FABFORM</b><span>NATIONAL TAICHUNG THEATER</span></header>{page}'
                      f'<footer><span>臺中國家歌劇院　／　6,000 件典藏版</span><span>{i} / {len(pages)}</span></footer></section>')
    with sync_playwright() as pw, pw.chromium.launch(channel='chrome',headless=True) as browser:
        tab=browser.new_page()
        tab.set_content('<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><title>臺中國家歌劇院・建築導覽</title>'
                        +'<style>'+STYLE+'</style>'+''.join(markup)+'</html>')
        tab.evaluate('Promise.all(Array.from(document.images,i=>i.decode()))')
        for page in tab.locator('section').all():
            assert page.evaluate('''s=>{
                const footer=s.querySelector('footer').getBoundingClientRect();
                return [...s.querySelectorAll('figure, table, aside, .refs')].every(
                    item=>item.getBoundingClientRect().bottom < footer.top);
            }''')
        pdf=tab.pdf(prefer_css_page_size=True,print_background=True)
    with fitz.open(stream=pdf,filetype='pdf') as doc:
        assert len(doc)==len(pages)
        doc.save(ROOT/'downloads'/model_id/'architecture.pdf',garbage=4,deflate=True,use_objstms=1)

if __name__=='__main__':
    theatre_guide()

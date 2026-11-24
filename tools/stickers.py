"""Face-centred model decals and 1:1 vector cutting sheets."""
from design import is_collector
from html import escape
from pathlib import Path
import base64
from functools import lru_cache

import fitz

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'assets'/'decals'
MM=72/25.4
FACE={'front':'正面（朝前）','back':'背面（朝後）','left':'左側面','right':'右側面'}

def collect(model):
    """Return references to pieces in installation order; IDs restart for each model."""
    sheets=[]
    for bag_id,bag in enumerate(model['bags'],1):
        for step in bag['steps']:
            for number,p in enumerate(step['pieces'],1):
                if 'decal' in p:
                    sheets.append((p,p['decal'],bag_id,step,number))
    return {id(p):dict(id=f'S{i:02d}',decal=d,bag=bag,step=step,number=n,part=p) for i,(p,d,bag,step,n) in enumerate(sheets,1)}

def details(record):
    d=record['decal']
    positions=[]
    for axis,pos,neg in [('du','右','左'),('dv','上','下')]:
        value=d.get(axis,0)
        if value:
            positions.append(f'向{pos if value>0 else neg} {abs(value):g} mm')
    alignment='面中央' if not positions else '由中央'+'、'.join(positions)
    frame='（長廊轉向前）' if record['part'].get('pivoted') else ''
    return f'{FACE[d["face"]]}{frame}，{alignment}。'

def dimensions(record):
    d=record['decal']
    return f'{d["widthMM"]:g} × {d["heightMM"]:g} mm'

def art_uri(name):
    blob=(ART/f'{name}.svg').read_bytes()
    return 'data:image/svg+xml;base64,'+base64.b64encode(blob).decode()

def callout(record):
    d=record['decal']
    return (f'<aside class="decal-note"><img alt="{escape(d["label"])}" src="{art_uri(d["art"])}">'
            f'<div><b>貼 {record["id"]}　{escape(d["label"])}</b><br>先在圖號 {record["number"]} 的{details(record)}'
            f'貼好後再扣上積木。裁切尺寸 {dimensions(record)}。</div></aside>')

def collector_sheet(model, catalog, records, destination):
    """Lay out full-size facade panels and smaller plaques on measured A4 sheets."""
    ink=(.09,.17,.19)
    green=(.11,.36,.31)
    def label(page,x,y,value,points=10,color=ink,latin=False):
        page.insert_text((x*MM,y*MM),value,fontname='helv' if latin else 'china-t',
                         fontsize=points,color=color)
    def page_start(doc):
        page=doc.new_page(width=210*MM,height=297*MM)
        label(page,16,17,'FABFORM   /   '+model['code']+'   /   DECALS',10,green,True)
        label(page,16,29,model['name'],17)
        label(page,16,38,'A4 原寸貼紙・以 100% 實際大小列印，依外框裁切。',10)
        split=any(r['decal']['art'].startswith('giant-sign-') for r in records.values())
        label(page,16,45,'長廠房標誌由左至右分四片，每張只貼在一片牆板上。' if split else '按步驟將貼紙置於指定磚面，再扣入模型。',10)
        page.draw_line((16*MM,271*MM),(66*MM,271*MM),color=ink)
        for i in range(0,51,5):
            page.draw_line(((16+i)*MM,271*MM),((16+i)*MM,(268 if i%10==0 else 269.5)*MM),color=ink)
        label(page,16,278,'0',9,latin=True)
        label(page,57,278,'50 mm',9,latin=True)
        label(page,78,273,'用尺核對兩端刻線間距應為 50 mm。',10)
        label(page,170,282,f'{model["code"]} / {len(doc)}',9,green,True)
        return page

    steps={id(s):i for i,s in enumerate([s for b in model['bags'] for s in b['steps']],1)}
    rows=[]
    for record in records.values():
        w=record['decal']['widthMM']
        if rows and len(rows[-1])==1 and max(w,rows[-1][0]['decal']['widthMM'])<=76:
            rows[-1].append(record)
        else:
            rows.append([record])
    with fitz.open() as doc:
        page=page_start(doc)
        top=53
        for row in rows:
            max_h=max(r['decal']['heightMM'] for r in row)
            band=max_h+38
            if top+band>263:
                page=page_start(doc)
                top=53
            for idx,r in enumerate(row):
                d=r['decal']
                x=16+idx*93
                page.draw_line((x*MM,top*MM),((x+(85 if len(row)==2 else 177))*MM,top*MM),color=(.74,.81,.78),width=.45)
                w,h=d['widthMM'],d['heightMM']
                label(page,x,top+6,f'{r["id"]}  /  {w:g} x {h:g} mm',10,green,True)
                y=top+9
                box=fitz.Rect(x*MM,y*MM,(x+w)*MM,(y+h)*MM)
                with fitz.open(ART/(d['art']+'.svg')) as svg, fitz.open(stream=svg.convert_to_pdf(),filetype='pdf') as art:
                    page.show_pdf_page(box,art,0)
                page.draw_rect(box+(-.14,-.14,.14,.14),color=(.55,.60,.60),width=.25)
                y+=max_h+5
                title=d['label']
                for i in range(0,len(title),25):
                    label(page,x,y,title[i:i+25],9)
                    y+=4.2
                label(page,x,y+1,f'第 {r["bag"]} 袋・步驟 {steps[id(r["step"])]}・圖號 {r["number"]}',9)
                label(page,x,y+5.5,f'{r["part"]["part"]}　{details(r)}',8)
            top+=band
        doc.set_metadata({'title':model['name']+'・1:1 原寸貼紙','author':'FABFORM'})
        doc.save(destination,garbage=4,deflate=True,use_objstms=1)


def write_sheet(model, catalog, records, destination):
    """Place vector artwork into millimetre-sized PDF boxes. No printer margins are used to derive scale."""
    if is_collector(model):
        return collector_sheet(model,catalog,records,destination)
    doc=fitz.open(); page=doc.new_page(width=210*MM,height=297*MM)
    gray=(.30,.37,.36); ink=(.08,.17,.17); red=(.63,.19,.13)
    def text(x,y,string,sz=11,color=ink,english=False):
        page.insert_text((x*MM,y*MM),string,fontname='helv' if english else 'china-t',fontsize=sz,color=color)
    def line(x,y,x2,y2,color=gray,width=.55):
        page.draw_line((x*MM,y*MM),(x2*MM,y2*MM),color=color,width=width)
    def rect(x,y,w,h):
        return fitz.Rect(x*MM,y*MM,(x+w)*MM,(y+h)*MM)
    text(16,20,model['code']+'  /  ARCHITECTURAL DECALS',11,red,True)
    text(16,32,model['name']+'｜原寸貼紙',20)
    text(16,42,'以 A4、實際大小（100%）列印。用尺確認下方刻度，再依左欄裁切。',11)
    if any(rec['decal']['art']=='giant-word' for rec in records.values()):
        paper='建議用透明貼紙。兩枚各貼在一顆磚上，組合後圓標在左、字標在右。'
    else:
        paper='紅字、黑字的透明貼可保留磚面顏色。白底圓章請用白色貼紙紙材。'
    text(16,49,paper,10,gray)
    text(17,66,'原寸裁切',11,red);text(76,66,'放大辨識及安裝位置',11,red)
    first_step=1
    steps={id(s):i for i,s in enumerate([s for b in model['bags'] for s in b['steps']],first_step)}
    for i,rec in enumerate(records.values()):
        d=rec['decal'];w,h=d['widthMM'],d['heightMM'];top=72+i*39
        line(16,top,194,top,(.83,.86,.85))
        x,y=44-w/2,top+15-h/2
        with fitz.open(stream=(ART/(d['art']+'.svg')).read_bytes(),filetype='svg') as source:
            with fitz.open(stream=source.convert_to_pdf(),filetype='pdf') as art:
                box=rect(x,y,w,h)
                page.show_pdf_page(box,art,0,keep_proportion=True)
                # The cut stroke sits outside the nominal edge and has no effect on artwork size.
                border=fitz.Rect(box.x0-.18,box.y0-.18,box.x1+.18,box.y1+.18)
                if d['art']=='tsmc':page.draw_oval(border,color=(.58,.61,.60),width=.32)
                else:page.draw_rect(border,color=(.58,.61,.60),width=.32)
                page.show_pdf_page(rect(77,top+4,33,18),art,0,keep_proportion=True)
        text(19,top+31,rec['id']+'  |  '+dimensions(rec).replace('×','x')+'  |  1x',9,gray,True)
        label=rec['id']+'  '+d['label']
        if len(label)<=21:
            text(116,top+10,label,11)
        else:
            # The built-in CJK font also uses full-width Latin glyphs in this field.
            text(116,top+7.5,rec['id'],9,gray,True)
            for line_no,start in enumerate(range(0,len(d['label']),19)):
                text(124,top+7.5+4.4*line_no,d['label'][start:start+19],10)

        p=rec['part']
        text(116,top+18,f'袋 {rec["bag"]:02d}．步驟 {steps[id(rec["step"])]:02d}．圖號 {rec["number"]}',10)
        text(116,top+25,f'{catalog["colors"][p["color"]]["name"]} {p["part"]}　'+FACE[d['face']],10)
        text(77,top+34,details(rec),9,gray)
    y=264;line(17,y,67,y,ink,1)
    for i in range(0,51,5):line(17+i,y-(3 if i%10==0 else 1.7),17+i,y+1,ink,.75)
    text(17,y+7,'0',9,ink,True);text(57,y+7,'50 mm',9,ink,True)
    text(78,y+1,'實測兩端刻線間距應為 50 mm。',11)
    text(16,284,'FABFORM  /  '+model['code'],9,gray,True)
    text(117,284,'每個編號一張，放大圖供辨識。',9,gray)
    doc.set_metadata({'title':model['name']+'｜1:1 標誌貼紙','author':'Fabform'})
    doc.save(destination,garbage=4,deflate=True,use_objstms=1)
    doc.close()

@lru_cache(maxsize=None)
def rectangles(name):
    """Merge equal-colour pixels into planar rectangles for portable LDraw artwork."""
    from PIL import Image
    with fitz.open(stream=(ART/f'{name}.svg').read_bytes(),filetype='svg') as svg:
        scale=236/svg[0].rect.width
        pix=svg[0].get_pixmap(alpha=True,matrix=fitz.Matrix(scale,scale))
        # MuPDF samples are premultiplied. These stickers use near-solid primary inks.
        artwork=Image.frombytes('RGBA',(pix.width,pix.height),pix.samples)
    pal=artwork.convert('RGB').quantize(12,dither=Image.Dither.NONE)
    colors=[tuple(pal.getpalette()[i:i+3]) for i in range(0,36,3)]
    w,h=artwork.size
    pixels=pal.load();alpha=artwork.getchannel('A').load();active={};output=[]
    for y in range(h+1):
        runs={}
        if y<h:
            x=0
            while x<w:
                if alpha[x,y]<160:
                    x+=1;continue
                left=x;value=pixels[x,y];x+=1
                while x<w and alpha[x,y]>=160 and pixels[x,y]==value:x+=1
                key=(left,x,value);runs[key]=active.get(key,y)
        for (x0,x1,c),top in active.items():
            if (x0,x1,c) not in runs:output.append((x0/w,top/h,x1/w,y/h,colors[c]))
        active=runs
    return w/h,output

def ldraw_shapes(model,p,catalog,pivot_point):
    d=p['decal'];ratio,art=rectangles(d['art'])
    width=min(d['widthMM']/8,d['heightMM']/8*ratio);height=width/ratio
    spec=catalog['parts'][p['part']]
    a,b=(spec['d'],spec['w']) if p.get('r',0)%2 else (spec['w'],spec['d'])
    nx,nz={'front':(0,1),'left':(-1,0),'right':(1,0),'back':(0,-1)}[d['face']]
    offset=(a if nx else b)/2+.008
    dx=p['x']+a/2+nx*offset+nz*d.get('du',0)/8
    dz=p['z']+b/2+nz*offset-nx*d.get('du',0)/8
    cy=(p['y']+spec['h']/2)*.4+d.get('dv',0)/8
    def point(u,v):
        local=(u-.5)*width
        x,z=pivot_point(model,p,dx+nz*local,dz-nx*local)
        return ' '.join(f'{n:.3f}'.rstrip('0').rstrip('.') or '0' for n in (x*20,-(cy+(.5-v)*height)*20,-z*20))
    for l,t,r,bottom,c in art:
        yield '4 0x2' + ''.join(f'{i:02X}' for i in c) + ' ' + ' '.join(point(u,v) for u,v in [(l,bottom),(r,bottom),(r,t),(l,t)])

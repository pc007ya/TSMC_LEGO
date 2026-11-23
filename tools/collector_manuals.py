"""Produce printable and self-contained illustrated manuals for the high-resolution editions."""
import argparse
import base64
from functools import lru_cache
import json
from pathlib import Path

import fitz
from PIL import Image

from collector_diagrams import Meshes, View, image_bytes
from manuals import count, coord, export_bom, export_ldr, footprint, inventory_md, orientation, paginate, pivot_notes
from stickers import art_uri, collect, details, dimensions, write_sheet

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ('以底座的左後角為第 1 欄、第 1 列。X 往右、Z 往前。表中的 X、Z 是每顆積木占地的左後角，底高從桌面以薄板層數起算，一塊標準磚高三層。'
         '依圖號順序安裝。同一步若有上下重疊，子圖依序揭示各層。淡灰為已裝零件，俯視圖的圈號標示本頁新件。')
DARK=(.09,.20,.21)
TEAL=(.03,.38,.37)
MUTED=(.27,.36,.36)
LINE=(.79,.84,.82)
ACCENT=(.75,.31,.15)
MM=72/25.4
WIDTH,HEIGHT=210*MM,297*MM


def data_uri(data, mime):
    return 'data:'+mime+';base64,'+base64.b64encode(data).decode('ascii')


def sticker_note(record):
    return f'{record["id"]}　圖號 {record["number"]}　{record["decal"]["label"]}　{dimensions(record)}。{details(record)}'


class Book:
    def __init__(self,model):
        self.model=model
        self.doc=fitz.open()
        self.font=fitz.Font(fontname='cjk')
        self.toc=[]
        self.asset_xrefs={}

    def new(self,right):
        self.page=self.doc.new_page(width=WIDTH,height=HEIGHT)
        self.page.insert_font(fontname='ManualCJK',fontbuffer=self.font.buffer)
        self.pen=self.page.new_shape()
        self.text(36,36,'FABFORM    /    '+self.model['code'],9,TEAL,latin=True)
        self.text(308,36,right,10,MUTED)
        self.rule(36,47,WIDTH-36,47)
        self.rule(36,HEIGHT-44,WIDTH-36,HEIGHT-44)
        self.text(36,HEIGHT-27,self.model['name'],8,MUTED)
        self.text(WIDTH-77,HEIGHT-27,f'{self.page.number+1:04d}',9,MUTED,latin=True)
        return self.page

    def finish_page(self):
        self.pen.commit()

    def text(self,x,y,value,size=11,color=DARK,latin=False):
        self.pen.insert_text((x,y),str(value),fontsize=size,fontname='helv' if latin else 'ManualCJK',color=color)

    def wrap(self,x,y,value,width,size=11,leading=16,color=DARK):
        line='';length=0
        for c in str(value):
            advance=self.font.glyph_advance(ord(c))*size
            if line and length+advance>width:
                self.text(x,y,line,size,color);y+=leading;line='';length=0
            line+=c;length+=advance
        if line:
            self.text(x,y,line,size,color);y+=leading
        return y

    def rule(self,x1,y1,x2,y2):
        self.pen.draw_line((x1,y1),(x2,y2));self.pen.finish(color=LINE,width=.55)

    def pic(self,box,blob,key=None):
        if key is not None and key in self.asset_xrefs:
            self.page.insert_image(box,xref=self.asset_xrefs[key])
        else:
            ref=self.page.insert_image(box,stream=blob)
            if key is not None:self.asset_xrefs[key]=ref

    def chapter(self,level,title):
        self.toc.append([level,title,self.page.number+1])

    def save(self,path):
        self.doc.set_metadata({'title':self.model['name']+'｜逐步組裝手冊','author':'FABFORM'})
        self.doc.set_toc(self.toc)
        self.doc.subset_fonts()
        self.doc.save(path,garbage=3,deflate=True,use_objstms=1)
        self.doc.close()


def cover_page(book, info, preview):
    book.new('組裝說明書')
    book.chapter(1,info['name'])
    y=book.wrap(36,85,info['name'],522,25,31)
    book.text(36,y+5,f'{info["pieces"]:,} 件   ／   {len(info["bags"])} 袋   ／   {info["steps"]} 步',16,TEAL)
    book.pic((36,y+25,WIDTH-36,365),preview)
    y=book.wrap(36,396,info['description'],522,11,17)
    y=book.wrap(36,y+12,'底座 '+info['base']+'。'+GUIDE,522,10,16)
    y=book.wrap(36,y+12,info['observation']+' '+info['interpretation'],522,10,15)
    for source in info['sources']:
        if y>760:break
        book.text(36,y+10,source['label'],10,TEAL)
        book.page.insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(36,y-3,550,y+14),'uri':source['url']})
        y+=16
    book.finish_page()


def bag_inventory(book, index, bag, info, inventories, thumbs):
    rows=inventories[index]
    for start in range(0,len(rows),38):
        book.new(f'分袋清點　／　第 {index+1:02d} 袋')
        if start==0:book.chapter(1,f'第 {index+1:02d} 袋　'+bag['name'])
        book.text(36,80,f'第 {index+1:02d} 袋',21,TEAL)
        y=book.wrap(36,110,bag['name'],520,19,25)
        book.text(36,y+4,f'{bag["count"]} 件　·　{bag["steps"]} 步　·　本袋 {len(rows)} 種料色組合',12,MUTED)
        group=rows[start:start+38]
        for i,(sku,qty) in enumerate(group):
            column,at=divmod(i,19)
            x=36+column*267;y=166+at*31.8
            part,color=info['parts'][sku]
            book.pic((x,y-7,x+38,y+17),thumbs(sku)[0],sku)
            book.text(x+43,y+1,part+'　'+info['colors'][color]['name'],9)
            book.text(x+43,y+13,info['names'][part],8,MUTED)
            book.text(x+221,y+6,'×'+str(qty),10,TEAL)
            book.rule(x,y+20,x+246,y+20)
        book.finish_page()


def instruction_page(book, info, group, figures, thumbs, decals):
    n,sub,subcount=group['step'],group['phase'],group['phases']
    book.new(f'第 {group["bag"]+1:02d} 袋　／　袋內步驟 {group["local"]:02d}')
    book.text(36,84,f'{n:03d}',29,TEAL,latin=True)
    y=book.wrap(113,79,group['name'],443,17,23)
    book.text(36,109,f'圖 {sub}/{subcount}',9,MUTED)
    y=book.wrap(113,y,group['hint'],442,10,14)
    y=max(144,y+9)
    book.text(36,y,'俯視定位　／　左上為後方',11,TEAL)
    book.text(305,y,'等角安裝圖　／　'+info['direction'],11,TEAL)
    book.pic((36,y+8,291,y+166),figures[0])
    book.pic((305,y+8,560,y+166),figures[1])
    book.text(36,y+185,group['region'],10,MUTED)
    y+=218
    book.text(36,y,'本圖取件與扣合位置',14,TEAL)
    y+=25
    for xpos,label in ((36,'圖號'),(73,'零件及料號'),(250,'顏色'),(340,'X，Z'),(412,'底高'),(467,'方向')):
        book.text(xpos,y,label,9,MUTED)
    book.rule(36,y+7,559,y+7)
    for number,sku,x,z,height,direction in group['rows']:
        part,color=info['parts'][sku]
        y+=26
        book.text(38,y,str(number),11,TEAL,latin=True)
        book.pic((72,y-15,104,y+4),thumbs(sku)[0],sku)
        book.text(108,y,info['names'][part]+'  '+part,9)
        book.text(250,y,info['colors'][color]['name'],10)
        book.text(340,y,f'{x}, {z}',10,latin=True)
        book.text(413,y,str(height),10,latin=True)
        book.wrap(467,y,direction,91,9,10)
        book.rule(36,y+6,559,y+6)
    for sid in group['stickers']:
        d=decals[sid]
        y+=19
        book.pic((36,y-7,74,y+10),d['pdf_image'],'sticker-'+sid)
        y=book.wrap(84,y+4,d['note'],472,10,13,ACCENT)
    for note in group['pivotNotes']:
        y=book.wrap(36,y+14,note,515,9,12,MUTED)
    if y>HEIGHT-51:
        raise ValueError(f'Instruction page text overflow at {n}/{sub}: {y}')
    book.finish_page()


def inventory_index(bags):
    unique={}
    inventories=[]
    for bag in bags:
        items=[p for step in bag['steps'] for p in step['pieces']]
        inventory=[]
        for pair,qty in sorted(count(items).items()):
            index=unique.setdefault(pair,len(unique))
            inventory.append([index,qty])
        inventories.append(inventory)
    return list(unique),inventories


def generate(model, root, destination):
    catalog=json.loads((root/'data/catalog.json').read_text())
    transforms=json.loads((root/'assets/parts/index.json').read_text())
    ref=json.loads((root/'data/references.json').read_text())[model['id']]
    bags=model['bags']
    pieces=[p for b in bags for step in b['steps'] for p in step['pieces']]
    records=collect(model)
    destination.mkdir(parents=True,exist_ok=True)
    export_bom(model,catalog,destination/'bom.csv')
    export_ldr(model,catalog,destination/'model.ldr',transforms,records)
    write_sheet(model,catalog,records,destination/'stickers.pdf')
    print('Preparing the LDraw instruction views…',flush=True)
    meshes=Meshes(root,transforms)
    plan=View(meshes,model,catalog,pieces,plan=True)
    iso=View(meshes,model,catalog,pieces)
    pairs,inventories=inventory_index(bags)
    bag_info=[dict(name=b['name'],count=sum(len(s['pieces']) for s in b['steps']),steps=len(b['steps']),first=0) for b in bags]
    flags=model['camera']
    direction='前' if flags[2]>0 else '後'
    direction+='右上方' if flags[0]>0 else '左上方'
    info=dict(id=model['id'], name=model['name'], description=model['description'], code=model['code'], colors=catalog['colors'],
              names={k:v['name'] for k,v in catalog['parts'].items()},parts=pairs,
              steps=sum(b['steps'] for b in bag_info),pieces=len(pieces),bags=bag_info,
              base=f'{model["width"]} × {model["depth"]} 凸點',direction=direction,guide=GUIDE,
              observation=ref.get('observation',''),interpretation=ref.get('interpretation',''),sources=ref['sources'],inventories=inventories)
    by_pair={pair:i for i,pair in enumerate(pairs)}
    @lru_cache(maxsize=None)
    def thumbnail(i):
        im=iso.thumbnail(*pairs[i])
        return image_bytes(im,'PNG'),data_uri(image_bytes(im,'WEBP',quality=85),'image/webp')
    decals={}
    for r in records.values():
        d=r['decal'];svg=root/'assets/decals'/(d['art']+'.svg')
        with fitz.open(svg) as f:
            pix=f[0].get_pixmap(matrix=fitz.Matrix(160/f[0].rect.width,160/f[0].rect.width),alpha=False)
            decals[r['id']]=dict(image=art_uri(d['art']),pdf_image=pix.tobytes('png'),note=sticker_note(r))
    cover=(root/'assets/previews'/(model['id']+'.webp'))
    info['cover']=data_uri(cover.read_bytes(),'image/webp')
    preview=Image.open(cover).convert('RGB')
    preview.thumbnail((1050,690))
    book=Book(model)
    cover_page(book,info,image_bytes(preview,'JPEG',quality=84))
    md=[f'# {info["name"]}｜組裝說明書','',info['description'],'',f'{len(pieces):,} 件 · {len(bags)} 袋 · {info["steps"]} 步','',GUIDE,'',ref['observation'],'',ref['interpretation'],'',
        ' · '.join(f'[{s["label"]}]({s["url"]})' for s in ref['sources']),'',
        '[離線圖解說明書](manual.html) · [列印版](manual.pdf) · [分袋 BOM](bom.csv) · [三維模型](model.ldr) · [原寸貼紙](stickers.pdf)','']
    pages=[];step_no=cursor=0
    for b,bag in enumerate(bags):
        bag_info[b]['first']=len(pages)
        bag_inventory(book,b,bag_info[b],info,inventories,thumbnail)
        md.extend([f'## 第 {b+1:02d} 袋　{bag["name"]}','',f'{bag_info[b]["count"]} 件，{len(bag["steps"])} 步。',''])
        for local,step in enumerate(bag['steps'],1):
            step_no+=1
            md.extend([f'### 步驟 {step_no:03d}　{step["name"]}','',step.get('hint',''),'',
                       '| 圖號 | 零件 | 顏色 | X | Z | 底高 | 方向 |','| ---: | --- | --- | ---: | ---: | ---: | --- |'])
            phases=list(paginate(step['pieces'],catalog))
            for phase,group in enumerate(phases,1):
                rows=[];stickers=[];cells=set()
                for number,p in group:
                    x,z,h=coord(p);part=p['part'];col=p['color'];direction=orientation(p,catalog)
                    cells.update(footprint(p,catalog))
                    rows.append([number,by_pair[(part,col)],x,z,h,direction])
                    md.append(f'| {number} | {info["names"][part]} {part} | {info["colors"][col]["name"]} | {x} | {z} | {h} | {direction} |')
                    if id(p) in records:stickers.append(records[id(p)]['id'])
                xs,zs=zip(*cells)
                region=f'本圖新件　X {min(xs)+1}–{max(xs)+1}　／　Z {min(zs)+1}–{max(zs)+1}'
                record=dict(step=step_no,phase=phase,phases=len(phases),bag=b,local=local,name=step['name'],hint=step.get('hint',''),
                            region=region,rows=rows,stickers=stickers,pivotNotes=pivot_notes([p for _,p in group]))
                figures=[image_bytes(view.figure(group),'JPEG',quality=57,optimize=True) for view in (plan,iso)]
                instruction_page(book,info,record,figures,thumbnail,decals)
                record['start']=cursor
                cursor+=len(group)
                pages.append(record)
            for p in step['pieces']:
                if id(p) in records:md.extend(['',sticker_note(records[id(p)])])
            md.extend(['',*pivot_notes(step['pieces']),''])
        print(f'Bag {b+1}/{len(bags)} · {len(pages)} placement diagrams',flush=True)
    book.save(destination/'manual.pdf')
    md.extend(['## 全套零件表','',*inventory_md(pieces,catalog),''])
    (destination/'manual.md').write_text('\n'.join(md))
    info.update(atlases=[view.offline_atlas(pieces) for view in (plan,iso)],pages=pages,stickers={sid:{k:v for k,v in d.items() if k!='pdf_image'} for sid,d in decals.items()},thumbs=[thumbnail(i)[1] for i in range(len(pairs))])
    template=(Path(__file__).with_name('collector_reader.html')).read_text()
    encoded=json.dumps(info,separators=(',',':'),ensure_ascii=False).replace('<','\\u003c')
    renderer=(Path(__file__).with_name('collector_reader_draw.js')).read_text()
    (destination/'manual.html').write_text(template.replace('/*DRAW_READER*/',renderer).replace('/*MANUAL_DATA*/',encoded))
    print(model['id'],len(pieces),'pieces,',step_no,'steps,',len(pages),'illustrated placement pages',flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model',required=True)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--output',type=Path,help='Alternate destination for proof copies')
    args=parser.parse_args()
    models=json.loads((args.root/'data/models.json').read_text())
    model=next(m for m in models if m['id']==args.model)
    generate(model,args.root,args.output or args.root/'downloads'/model['id'])


if __name__=='__main__':main()

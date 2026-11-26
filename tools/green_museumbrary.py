"""TAICHUNG GREEN MUSEUMBRARY: original stud-grid reduction of the published SANAA drawings."""
from collections import Counter
from functools import lru_cache
from math import hypot
from pathlib import Path
from design import DATA, Building, dump, validate, stock, parts, colors
import json

SIZE=(96,64)
SLAB=13
# Vertices read from the architectural team's published third-floor drawing A2-07.
# x/z preserve its orientation; outlying appendages are modelled separately.
VOLUMES={
 'A':('美術館挑高大廳',[(381,763),(711,788),(659,1049),(375,1006)],51,'atrium'),
 'B':('特別展覽量體',[(222,310),(534,456),(374,768),(79,610)],59,'gallery'),
 'C':('常設與特別展覽量體',[(573,273),(974,252),(994,698),(593,716)],63,'gallery'),
 'D':('閱讀與文化之森露臺',[(730,847),(1094,779),(1114,1088),(814,1151)],39,'terrace'),
 'E':('親子共閱與咖啡量體',[(1128,998),(1355,870),(1472,1080),(1256,1211)],37,'glazed'),
 'F':('主圖書閱覽量體',[(1191,389),(1662,552),(1495,911),(1094,764)],68,'library'),
 'G':('多元文化與兒童閱覽量體',[(1724,115),(1965,354),(1724,599),(1482,354)],54,'library'),
 'H':('學習與行政量體',[(1005,112),(1266,115),(1266,375),(979,375)],48,'glazed'),
}
ROOT=Path(__file__).resolve().parents[1]
PROOFS={(r['ldraw_part'].removesuffix('.dat'),r['ldraw_color']):r for r in json.loads((DATA/'lego-part-verification.json').read_text())['rows'] if r['status']=='verified' and r['lego_design_id'] and r['lego_element_id'] and r['source_url']}
def verified(part,c):
    return c in stock[part] and (part,colors[c][2]) in PROOFS
def rect(x,z,w,d):
    return {(a,b) for a in range(x,x+w) for b in range(z,z+d)}
def ply(points):
    pts=[(5+(x-75)*.044,5+(z-107)*.044) for x,z in points]
    def inside(x,z):
        return sum(1 for (a,b),(c,d) in zip(pts,pts[1:]+pts[:1]) if (b>z)!=(d>z) and x<(c-a)*(z-b)/(d-b)+a)%2
    return {(x,z) for x,z in rect(0,0,*SIZE) if inside(x+.5,z+.5)}
def rim(cells):
    return {(x,z) for x,z in cells if not {(x-1,z),(x+1,z),(x,z-1),(x,z+1)}<=cells}
def expanded(cells):
    return {(x+i,z+j) for x,z in cells for i,j in [(0,0),(-1,0),(1,0),(0,-1),(0,1)]}
def circle(cx,cz,r):
    return {(x,z) for x in range(cx-r-1,cx+r+1) for z in range(cz-r-1,cz+r+1) if hypot(x+.5-cx,z+.5-cz)<=r}
@lru_cache(None)
def available(shape,color,along):
    result=[]
    for id,p in parts.items():
        if p['shape']!=shape or not verified(id,color):continue
        for r in range(1+(p['w']!=p['d'])):
            w,d=(p['d'],p['w']) if r else (p['w'],p['d'])
            result.append((w*d,w if along else d,id,w,d,r))
    return sorted(result,reverse=True)
def tile(cells,shape,color,along=False):
    pending=set(cells)
    for x,z in sorted(cells,key=lambda v:(v[1],v[0]) if along else (v[0],v[1])):
        if (x,z) not in pending: continue
        for _,__,id,w,d,r in available(shape,color,along):
            body=rect(x,z,w,d)
            if body<=pending:
                yield id,x,z,r,body
                pending-=body
                break
        else:raise ValueError((shape,color,x,z))
def lay(b,cells,shape,color,y,along=False):
    for id,x,z,r,_ in tile(cells,shape,color,along):b.put(id,color,x,z,y,r)
def stack(b,xy,y,top,c='W',round=False):
    for x,z in sorted(xy):
        h=y
        while h+3<=top:
            b.put('3062b' if round else '3005',c,x,z,h)
            h+=3
        for j in range(h,top):b.put('3024',c,x,z,j)
def glass(b,cells,y):
    todo=set(cells)
    for x,z in sorted(cells):
        if (x,z) not in todo:continue
        for dx,dz,r in ((1,0,0),(0,1,1)):
            q=(x+dx,z+dz)
            if q in todo:
                b.put('3065','C',x,z,y,r)
                todo.remove(q)
                break
        else:
            b.put('3005','C',x,z,y)
        todo.remove((x,z))
def roof_plans(p,y,along=True):
    return list(tile(p,'plate','W',along))
def slab(b,plan,y):
    for id,x,z,r,_ in plan:b.put(id,'W',x,z,y,r)
def bridge_options(cells,names):
    a,b=names; total=set.union(*cells.values())
    out=[]
    for x in range(2,SIZE[0]-2):
        for z in range(2,SIZE[1]-2):
            for r in (0,1):
                for part,length in [('3795',6),('3034',8),('4282',16)]:
                    if r:
                        body=rect(x,z,2,length); edge1=rect(x,z,2,1);edge2=rect(x,z+length-1,2,1)
                    else:
                        body=rect(x,z,length,2);edge1=rect(x,z,1,2);edge2=rect(x+length-1,z,1,2)
                    if (edge1<=cells[a] and edge2<=cells[b]) or (edge1<=cells[b] and edge2<=cells[a]):
                        free=body-total
                        if 2<=len(free)<=16 and not (body&total)-(cells[a]|cells[b]):
                            anchor=body&total
                            if sum(1 for p in anchor if p in cells[a])>=2 and sum(1 for p in anchor if p in cells[b])>=2:
                                out.append((length,len(free),-len(anchor),x,z,r,part,body,free))
    return sorted(out,key=lambda o:o[:7])
def detail(name,note,direction,**args):
    return dict(id=name[0],name=name[1],note=note,direction=direction,scope='all',**args)
def builds():
    b=Building('green-museumbrary','TC 08','臺中綠美圖・精細版','Taichung Green Museumbrary',
        '依 SANAA／劉培森建築團隊平面及剖面重現 A–H 八座量體。斜置白盒下留出柱列與陰影廣場；透明窗、銀白帷幕與空橋把美術館和圖書館串起，屋頂保留文化之森。',
        *SIZE,[.38,.70,1.02],['A–H 八棟錯角排列','玻璃內牆與銀白帷幕節奏','低層連橋、環道與文化之森','中央公園邊緣與首層開放廣場'],'SANAA + Ricky Liu & Associates')
    b.info.update(series='culture',edition='collector',tabName='臺中綠美圖',revision=1)
    cells={k:ply(v[1]) for k,v in VOLUMES.items()}
    # A stud-wide relief at tight corners avoids crossed wall approximations.
    used=set()
    for k in cells:
        cells[k]-=used
        used|=cells[k]
    print({k:(len(v),min(x for x,z in v),max(x for x,z in v),min(z for x,z in v),max(z for x,z in v)) for k,v in cells.items()})
    b.info['views']=[
        detail(('plan','八棟配置'),'俯視辨認 A–H 斜向排列與中央開口；網格角度為積木近似。',[0,1,0.001]),
        detail(('park','中央公園側'),'低視角看架空柱列、兒童館與跌落式玻璃窗線。',[.48,.25,1.0]),
        detail(('terrace','文化之森'),'局部檢視屋頂露臺、花池及橋廊。',[.65,.85,1.0],region=[29,55,31,52,32,52]),
        detail(('under','首層／橋下'),'數位剖切：顯示首層開放動線、門廳和二樓搭接桁。',[-.18,.87,1],belowLayer=16,region=[6,90,6,55,1,16]),
    ]
    b.bag('底座・中央公園與廣場定位')
    for y,c,off in [(0,'D',0),(1,'L',4)]:
        b.step('下層展示底板' if y==0 else '錯縫鎖底','第二層的接縫換位，讓同一上板跨扣多塊下板。')
        for z0 in range(-off,SIZE[1],8):
            for x0 in range(-off,SIZE[0],8):
                x,z=max(0,x0),max(0,z0)
                lay(b,rect(x,z,min(SIZE[0],x0+8)-x,min(SIZE[1],z0+8)-z),'plate',c,y)
    ground=rect(0,0,*SIZE)
    walk=set()
    for x in range(4,92):
        z=55+round(2.6*__import__('math').sin(x/12))
        walk|={(x,z+i) for i in (-1,0,1)}
    for z in range(7,57):
        x=45+round(3.2*__import__('math').sin(z/8))
        walk|={(x+i,z) for i in (-1,0,1)}
    plaza=expanded(expanded(used))|walk|circle(37,30,10)
    plaza &= ground
    water=circle(31,19,3)&plaza
    b.step('架空廣場、園路與入口水池','用淺灰寫出穿越兩館的廣場；深淺植栽形成中央公園側邊。水池留作後續藍色光面。')
    lay(b,plaza-water,'plate','L',2)
    lay(b,ground-plaza,'plate','G',2)
    lay(b,water,'plate','B',2)
    b.step('薄水面與鋪面輪廓','把透明淺藍平片扣在水池。留住旁邊的全高凸點，下一袋柱腳才有抓點。')
    lay(b,water,'tile','T',3)
    body={}
    for k,(label,_,height,kind) in VOLUMES.items():
        p=cells[k]
        b.bag(f'{k} 棟・{label}基座')
        b.step(f'{k} 棟柱列與內核','先扣住下方每片承板對應的柱位，中央通道不封死。透明窗從外緣分段扣合。')
        plan=roof_plans(p,SLAB,k in 'ACEG')
        per=rim(p)
        partitions=[]
        if kind in ('atrium','library','glazed'):
            window={q for q in per if (q[0]+q[1])%5 in (0,1,2) and (kind!='library' or k=='G' or q[1]>=sum(z for x,z in p)/len(p))}
        else:window=set()
        # Slab pieces must each receive at least one independent column; avoid one-cell contact to the extent possible.
        supports=set()
        for _,x,z,r,chunk in plan:
            candidates=sorted(chunk-water,key=lambda p:(hypot(p[0]-sum(xx for xx,_ in chunk)/len(chunk),p[1]-sum(zz for _,zz in chunk)/len(chunk)),p))
            if not candidates:raise ValueError((k,'pool blocks slab',chunk))
            supports.add(candidates[0])
            if len(chunk)>=16 and len(candidates)>4:supports.add(candidates[-1])
        if window:
            supports-=window
            support_window=window-water
        else:support_window=set()
        stack(b,supports,3,SLAB,'W',True)
        if support_window:
            for y in (3,6,9):glass(b,support_window,y)
            lay(b,support_window,'plate','W',12)
        b.step(f'{k} 棟架空層承板','每片樓板至少壓住一處下方凸點。朝中庭的視線留在細柱間。')
        slab(b,plan,SLAB)
        body[k]=per
    b.bag('二樓連通橋・兩端扣接')
    general=[]
    busy=set()
    for route in ('BC','CF','FE','HG'):
        for _,__,___,x,z,r,part,deck,free in bridge_options(cells,route):
            if not deck&busy:
                b.step(route[0]+'–'+route[1]+' 跨接承板','先同時壓住兩端樓板的凸點，中段保持懸空。這一塊連續長板是主要跨件。')
                b.put(part,'W',x,z,SLAB+1,r)
                busy|=deck
                general.append((route,free,r,deck))
                break
    assert len(general)>=3,general
    for k,p in cells.items():
        b.step(k+' 棟鎖住沿空橋樓板接點','補齊同層四周白色扣板，不壓到跨件；上層牆腳才能完整坐在凸點上。')
        lay(b,p-busy,'plate','W',SLAB+1,k in 'BG')
    for route,free,r,deck in general:
        b.step(route+' 玻璃欄板與白色步道','中央以白色光面鋪路，靠外緣的透明積木表現玻璃欄板。')
        if r: edges={(x,z) for x,z in free if x==min(a for a,_ in deck)}
        else: edges={(x,z) for x,z in free if z==min(a for _,a in deck)}
        lay(b,free-edges,'tile','W',SLAB+2)
        lay(b,edges,'plate','C',SLAB+2)
        lay(b,edges,'plate','C',SLAB+3)
        lay(b,edges,'plate','W',SLAB+4)
    for k,(label,_,height,kind) in VOLUMES.items():
        p=cells[k];per=body[k];inner=p-per
        b.bag(f'{k} 棟・{label}上層與屋頂')
        # 7-plate courses digitize floor seams; use a blank interior in the upper A atrium between ring floors.
        y=SLAB+2
        i=1
        a_core=set()
        if kind=='atrium':
            for axis in (True,False):
                for _,x,z,r,chunk in roof_plans(p,0,axis):
                    if not chunk&per:
                        a_core.add(min(chunk,key=lambda q:(hypot(q[0]-x-1,q[1]-z-1),q)))
        while y+7<=height:
            b.step(f'{k} 棟・牆層 {i:02d}','先把銀白豎框與玻璃扣進窗線；轉角依照俯視圖錯一格保留斜向量體。')
            hatch={q for q in per if (q[0]-q[1])%5==0}
            if kind in ('library','atrium','glazed','terrace'):
                # Tall transparent bays, staggered vertical mullions and slightly smoked banding.
                window=per-hatch
                glass(b,window,y)
                lay(b,hatch,'brick','W',y)
                glass(b,window,y+3)
                lay(b,hatch,'brick','W',y+3)
            elif kind=='gallery':
                slits={q for q in per if (q[0]+q[1])%11 in (2,3) and (q[1]>min(z for x,z in p)+3) and i in (2,4)}
                lay(b,per-slits,'brick','W',y)
                glass(b,slits,y)
                lay(b,per,'brick','W',y+3,True)
            else:raise ValueError(kind)
            remaining=height-(y+7)
            atrium=kind=='atrium' and remaining>=7
            deck_cells=p if not atrium else per|(rim(inner)-water)|a_core
            plan=roof_plans(deck_cells,y+6,i%2==0)
            cores=set(a_core)
            for _,x,z,r,chunk in plan:
                if not chunk&per:
                    middle=min(chunk & a_core or chunk,key=lambda q:(hypot(q[0]-x-1,q[1]-z-1),q))
                    cores.add(middle)
            if atrium:
                # The inner ring would not rest on prior ring if it expanded at a notch.
                assert cores <= deck_cells
            stack(b,cores,y,y+6)
            b.step(f'{k} 棟・樓板／帷幕水平線 {i:02d}','先扣四周薄板，再向內收；挑高大廳保留內圈空洞，其餘用細柱承住中央板。')
            slab(b,plan,y+6)
            y+=7;i+=1
        b.step(k+' 棟・平屋頂與採光細節','先用白薄板收屋面的高度，再裝同一層的光面與採光帶。')
        for h in range(y,height):
            lay(b,p,'plate','W',h,h%2==0)
        # A slab at the top of each volume is supported by the previous plate grid at roof or the closed course below.
        if k=='D':
            garden=circle(42,42,5)&p
            core=circle(42,42,3)&garden
            loop=garden-core
            rimline={q for q in loop if q in expanded(core)}
            paths=({q for q in p if (q[0]+q[1])%8 in (0,1)}|loop)-per
            b.step('文化之森・環形步道與內側透明欄板','由外圈鋪上白色步道，內圈薄透明欄板圍住植栽；靠兩端的灰片連到戶外露臺。')
            lay(b,paths-rimline,'tile','W',height)
            lay(b,rimline|per,'plate','W',height)
            lay(b,rimline,'plate','C',height+1)
            lay(b,rimline,'plate','C',height+2)
            lay(b,p-per-paths,'plate','J',height)
            for x,z in sorted(p-per-paths):
                if (x*7+z*11)%29==0 or (x,z) in {(41,40),(42,42),(43,43)}:
                    b.put('3024','F',x,z,height+1)
                    b.put('32607','G',x,z,height+2)
        elif k in ('C','F','H'):
            strips={q for q in inner if (q[0]+(q[1]//6 if k=='F' else 0))%5==2}
            lay(b,p-strips,'tile','W',height)
            lay(b,strips,'tile','B',height)
        else:
            lay(b,p,'tile','W',height)
    b.bag('中央公園林帶與咖啡休憩點')
    b.step('植栽、休憩石與緩坡步道','用兩種綠色樹冠排出疏密，讓開入口和遮蔭廣場。')
    safe=ground-plaza-expanded(walk)
    trees=set()
    for z in range(5,59,4):
        for x in range(5,92,5):
            if (x*13+z*19)%17>9 or not rect(x,z-1,2,2)<=safe or rect(x,z-1,2,2)&trees:continue
            trees |= rect(x,z-1,2,2)
            b.put('3062b','O',x,z,3)
            b.put('4032a','G' if x%3==0 else 'F',x,z-1,6)
            b.put('4073','G',x,z-1,7)
            b.put('4073','G',x+1,z,7)
    for x,z in sorted(safe-trees):
        if 2<x<94 and 2<z<62 and (x*61+z*31)%113==7:
            b.put('32607','F' if (x+z)%2 else 'G',x,z,3)
    for bag in b.info['bags']:
        groups=[]
        for s in bag['steps']:
            p=s['pieces']
            for i in range(0,len(p),12):
                tail=f'（{i//12+1}/{(len(p)+11)//12}）' if len(p)>12 else ''
                groups.append(dict(name=s['name']+tail,hint=s['hint'],pieces=p[i:i+12]))
        if not groups:raise ValueError(bag['name'])
        bag['steps']=groups
    return b.info,[dict(route=k,studs=len(v),part=[p for bag in b.info['bags'] for s in bag['steps'] if s['name'].startswith(k[0]+'–'+k[1]) for p in s['pieces']][0]['part'],deck=sorted(deck)) for k,v,_,deck in general]

SOURCES=[
 dict(label='臺中綠美圖・官方建築介紹',url='https://tgm.taichung.gov.tw/zh/about'),
 dict(label='臺中綠美圖官方開箱：文化之森、27 公尺挑高空間與環形天橋',url='https://tgm.taichung.gov.tw/zh/news/20250923-2'),
 dict(label='漫遊綠美圖・樓層導覽',url='https://tgm-go.com.tw/zh-tw/map'),
 dict(label='SANAA／劉培森建築圖：3F 平面 A2-07 與 B/C/F/G 剖面 A4-01-01（設計團隊圖，媒體刊載）',url='https://www.metalocus.es/en/news/programmatic-hybrid-taichung-green-museumbrary-sanaa'),
]
REF=dict(edition='臺中綠美圖・精細數位拼裝版',guide=True,sources=SOURCES,
         observation='依 A2-07 第三層平面對照 A–H 量體，並用 B/C/F/G 剖面比對相對高度及底層的柱間開口。臺中市立美術館與圖書館共同使用中央公園邊界。',
         interpretation='戶外空間、外牆豎框、半透明玻璃和連廊以現成積木表現；網格轉角、樓高、橋的端點及屋頂植栽必須近似。僅為收藏模型，不是等尺度施工圖。')
if __name__=='__main__':
    model,bridge=builds()
    validate(model)
    allp=[p for bag in model['bags'] for s in bag['steps'] for p in s['pieces']]
    assert all(verified(p['part'],p['color']) for p in allp)
    print(len(allp),'pieces',len(model['bags']),'bags',sum(len(b['steps']) for b in model['bags']),'steps',[(q['route'],q['studs']) for q in bridge])
    dump(DATA/'green-museumbrary.json',dict(model=model,reference=REF))
    out=ROOT/'downloads/green-museumbrary'
    out.mkdir(exist_ok=True)
    (out/'assembly-qa.json').write_text(json.dumps(dict(pieces=len(allp),bags=len(model['bags']),steps=sum(len(x['steps']) for x in model['bags']),
        maxLayer=max(p['y']+parts[p['part']]['h'] for p in allp),selectedPartColors=len(set((p['part'],p['color']) for p in allp)),
        collisions=0,unsupported=0,disconnected=0,bridges=bridge,physicalBuildTested=False),indent=2)+'\n')

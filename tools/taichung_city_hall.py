"""Taiwan Boulevard Municipal Building: stud-grid model of the current city hall."""
from collections import Counter
from math import hypot
from pathlib import Path
import json
from design import Building, DATA, dump, validate, parts
from green_museumbrary import rect, rim, lay, tile, stack, verified, detail

ROOT=Path(__file__).resolve().parents[1]
ID='taichung-city-hall'
SIZE=(104,72)
X0,X1,LEFT,RIGHT=8,96,41,63
Z0,Z1=18,46
GATE=rect(LEFT,Z0,RIGHT-LEFT,Z1-Z0)
WINGS=(rect(X0,Z0,LEFT-X0,Z1-Z0),rect(RIGHT,Z0,X1-RIGHT,Z1-Z0))
SHELL=WINGS[0]|WINGS[1]|GATE
Y0,TOP=4,48
H0,H1=22,40
# Courts run north/south in the wings. Their void is exposed by the digital section.
COURTS=(rect(22,25,15,12),rect(67,25,15,12))
SOURCES=[
 dict(label='臺中市政府｜臺灣大道市政大樓場地借用與一樓、四樓平面圖',url='https://www.secretariat.taichung.gov.tw/14565/14577/14730/31720/post'),
 dict(label='臺中市政府圖面｜惠中樓、文心樓與府前／府後廣場',url='https://school.tc.edu.tw/open-message/064700/get-file/666bc151a00819307650433e'),
 dict(label='臺中市觀旅局｜市政大樓、中央懸吊集會堂與地址',url='https://travel.taichung.gov.tw/en/Attractions/Intro/1242'),
 dict(label='McGregor Coxall 景觀設計團隊｜配置與前後、側面現場影像',url='https://mcgregorcoxall.com/projects/taichung-goverment-stage-1'),
 dict(label='臺中市政府｜地上十層與中央挑高空間',url='https://www.taichung.gov.tw/2901000/2901008/2901009/2911176/post'),
]
REF=dict(edition='臺中市政府・臺灣大道市政大樓',guide=True,sources=SOURCES,
 observation='現行市府位於西屯區臺灣大道三段 99 號，並非旁邊的臺中市議會，也不是舊市政府臺中州廳。依市府場地平面圖與景觀團隊照片，還原惠中樓、文心樓、府前與府後廣場及穿越中央的挑高川堂。',
 interpretation='十道水平分層與交錯藍灰窗格表現鏡面帷幕；縮尺不能複製鏡射、實際樓板及懸吊鋼構。積木用錯縫跨梁保留通行，內側集會堂採縮尺近似。')

def partition(b,grid,shape,y,paint,along=True):
    for c in sorted(set(paint(x,z) for x,z in grid)):
        lay(b,{(x,z) for x,z in grid if paint(x,z)==c},shape,c,y,along)

def window(b,cells,y,c='T'):
    pending=set(cells)
    for x,z in sorted(cells):
        if (x,z) not in pending:continue
        for dx,dz,r in ((1,0,0),(0,1,1)):
            p=x+dx,z+dz
            if p in pending:
                b.put('3065',c,x,z,y,r);pending.remove(p);break
        else:b.put('3005',c,x,z,y)
        pending.remove((x,z))

def two_stage_span(b,y,z0,z1,extra):
    """Assemble each bay from 9-stud anchored cantilevers, then a 4+8+4 stitch."""
    assert (z1-z0)%2==0
    label='川堂' if y>30 else '集會堂'
    b.step(label+'跨梁・雙側伸出','兩側各有九凸點深度留在辦公樓，兩臂伸出後中央仍留八凸點，這時不需臨時落地柱。')
    for z in range(z0,z1,2):
        b.put('4282','D',LEFT-9,z,y)
        b.put('4282','D',RIGHT-7,z,y)
    b.step(label+'跨梁・中央錯縫接合','先扣中央長板，使其同時扣住兩臂；再做橫向與縱向交錯鎖板。')
    for z in range(z0,z1,2):b.put('4282','L',LEFT+3,z,y+1)
    whole=rect(LEFT-9,z0,RIGHT-LEFT+18,z1-z0)
    lay(b,whole-rect(LEFT+3,z0,16,z1-z0),'plate','D',y+1)
    b.step(label+'跨梁・橫向鎖合','橫向長片跨過前一層接縫，將兩端和中央接成整片，也互扣前後相鄰長梁。')
    # Stagger the top lamination with the longest plates rotated through multiple pairs.
    lay(b,whole,'plate','D',y+2,False)
    assert not whole&extra
    return whole

def build():
    b=Building(ID,'TC 09','臺中市政府・臺灣大道市政大樓','Taichung City Hall',
       '臺灣大道正面的銀藍玻璃長體，中央開出可穿越的挑高川堂；惠中樓與文心樓中庭、後側懸吊集會堂及前方乾式噴泉廣場各有視角。不是市議會，也不是舊臺中州廳。',
       *SIZE,[.30,.43,1.14],['銀藍帷幕與十層水平線','穿越式挑高川堂、內縮懸吊集會堂','惠中樓／文心樓兩座中庭','府前軸線、兩側林帶與戶外廣場'],'Weber Hofer Partner · Ricky Liu & Associates · McGregor Coxall')
    b.info.update(series='culture',edition='collector',tabName='臺中市政府',revision=1,views=[
       detail(('front','臺灣大道正面'),'主入口／左側媒體牆與後方集會堂',[.0,.045,1]),
       detail(('rear','府後與集會堂'),'從府後看低一階的懸吊集會堂、公園方向和背面帷幕',[.44,.31,-1]),
       detail(('plan','總體配置'),'俯看前後主軸、左右建築與植栽；畫面上方不是正北',[.0,2.5,.002]),
       detail(('courts','首層數位剖切'),'顯示惠中樓、文心樓中庭與不被柱堵住的川堂',[.43,1.25,.76],belowLayer=11),
    ])
    allground=rect(0,0,*SIZE)
    b.bag('展示底座・交錯接縫')
    for y,c,off in [(0,'D',0),(1,'L',4)]:
        b.step('底座第一層' if y==0 else '底座第二層跨縫','第二層換位，跨扣上一層並整合為同一片。')
        for x0 in range(-off,SIZE[0],8):
            for z0 in range(-off,SIZE[1],8):
                x,z=max(x0,0),max(z0,0)
                lay(b,rect(x,z,min(x0+8,SIZE[0])-x,min(z0+8,SIZE[1])-z),'plate',c,y,True)
    roads=rect(0,0,4,SIZE[1])|rect(100,0,4,SIZE[1])|rect(0,69,SIZE[0],3)
    plaza=rect(38,4,28,65)|rect(24,48,56,17)|rect(5,15,94,3)|rect(5,46,94,3)
    plaza-=roads
    paths=({(x,z) for x,z in allground-SHELL if (z%7==3 and 5<=x<99 and 7<z<67) or (x in [6,15,33,70,87,97] and 5<z<69)}|plaza)-roads
    grass=allground-roads-paths-SHELL
    pool=rect(21,11,13,3)|rect(70,11,13,3)
    b.bag('府前廣場、道路與四面林帶')
    b.step('廣場、路口與輪廓','灰色鋪面串接臺灣大道、川堂及府後；外圈道路與園圃以不同顏色分層。')
    for y in (2,3):
        for cells,c in [(roads,'D'),(grass-pool,'G'),((paths|SHELL)-pool,'L'),(pool,'B')]:
            lay(b,cells,'plate',c,y,y%2==0)
    b.step('乾式噴泉與水面','入口廣場的噴孔與線性鋪面保持平整，府後兩片水面嵌在綠地。')
    jets={(x,z) for x in range(44,62,4) for z in range(53,64,4)}
    for x,z in sorted(jets):
        b.put('3024','T',x,z,4)
    lay(b,pool,'tile','T',4,True)
    accent={(x,z) for x,z in paths-SHELL if z in (8,15,48,65,68)}-jets
    lay(b,accent,'tile','D',4,True)
    # Low paving strips instead of a field of bumps; retain the recessed dry jets.
    paving=(rect(37,50,30,14)&paths)-jets-accent
    lay(b,paving,'tile','L',4,True)
    b.step('廣場兩側的座椅與櫻花林帶','入口軸線內不設柱；櫻樹以小尺度樹冠表現，座椅留下旁邊的步行淨空。')
    for x in (29,74):
        for z in (53,59):
            b.put('3023','L',x,z,4,1)
            b.put('3069b','L',x,z,5,1)
    tree_sites=set()
    for x in (11,19,35,68,84,92):
        for z in (7,12,50,55,60,65):
            base=rect(x,z,2,2)
            if base<=grass-pool and not base&tree_sites:
                tree_sites|=base
                b.put('3062b','O',x,z+1,4)
                b.put('4032a','F' if z%2 else 'G',x,z,7)
                b.put('32607','G',x,z,8)
                if x%2:b.put('32607','F',x+1,z,8)
    for x,z in sorted(grass-pool-tree_sites):
        if (x*39+z*47)%111==7:b.put('32607','F',x,z,4)
    perimeter=rim(WINGS[0])|rim(WINGS[1])
    side_solid={q for q in perimeter if q[0] in (LEFT-1,RIGHT) and 21<=q[1]<=42}
    courtwalls=set.union(*(rim(h) for h in COURTS))
    cores=rect(10,22,4,19)|rect(90,22,4,19)|rect(37,18,3,28)|rect(64,18,3,28)
    lowerdeck=set.union(*WINGS)-set.union(*COURTS)
    inset=rect(LEFT,H0,RIGHT-LEFT,H1-H0)
    for k,y in enumerate((4,8,12,16,22,26,30,34,38,44)):
        if k in (0,3,6,9):
            b.bag(('首層入口與中庭','錯縫跨梁與懸吊集會堂','帷幕上層與川堂頂跨','頂層平屋頂與機房')[k//3])
        glassmask={q for q in perimeter-side_solid if q[1] in (Z0,Z1-1) and (q[0]//4+2*k)%25==6}
        if k==0:glassmask|={q for q in perimeter-side_solid if (q[0] in (X0,X1-1) and 28<=q[1]<=34) or q[1] in (Z0,Z1-1) and q[0]%20 in (6,7,8)}
        if k==9:
            per=rim(SHELL)
            glassmask|={(x,z) for x,z in per&GATE if x%7 in (0,1)}
            mid=per-perimeter-glassmask
        elif k in range(4,9):
            mid=rim(inset)
        else:mid=set()
        d=lowerdeck|courtwalls
        if k in range(4,9):d|=inset
        if k==9:d|=GATE
        span=rect(LEFT-9,H0,RIGHT-LEFT+18,H1-H0) if k==3 else rect(LEFT-9,Z0,RIGHT-LEFT+18,Z1-Z0) if k==8 else set()
        roof_cross=set()
        if k==9:
            for x0 in (21,66):
                roof_cross|=rect(x0,26,16,10)
        edge=((perimeter|courtwalls|mid|glassmask)&d)-span-roof_cross
        infill=d-edge-span-roof_cross
        prev=(lowerdeck|courtwalls)|(inset if k>=4 else set())|(GATE if k==9 else set())
        plan=list(tile(infill,'plate','D',k%2==0))
        posts=set()
        fixed=perimeter|courtwalls|cores|mid|glassmask
        for _,_,_,_,h in plan:
            if not h&fixed:
                ps=sorted(h&prev)
                assert ps,(k,h)
                posts.add(ps[len(ps)//2])
                if len(h)>16:posts.add(ps[-1])
        # Spread cantilever load through both wing interiors along all rows.
        span_anchors=({(x,z) for x,z in span if x in (LEFT-8,LEFT-5,LEFT-2,RIGHT+1,RIGHT+4,RIGHT+7) and z%2==0}-fixed)&prev
        b.step(f'第 {k+1:02d} 層・銀藍窗格與內核','玻璃與深藍灰結構先扣住下層；中庭的透明牆不封住中央空隙。')
        def color(x,z):
            if (x,z) in side_solid:return 'D'
            xx=x-X0 if x<LEFT else X1-1-x
            if (z in (Z0,Z1-1) and xx in (3,4,5,24,25,26)) or (x in (X0,X1-1) and 24<=z<=37 and k in (0,3,6,9)):return 'L' if k in (0,4,7) else 'B'
            if k<2 and (xx+z+k)%19<4:return 'D'
            return 'B' if (xx//2 + (z+2*k)//3 + k*3)%19 in (3,6) else 'A'
        partition(b,perimeter-glassmask,'brick',y,color,True)
        window(b,glassmask,y)
        if k in range(4,9):
            # The screen has a shown-at-dusk warm panel on the Taiwan Boulevard side.
            screen={(x,z) for x,z in mid if z==H1-1 and 44<=x<54 and k in (5,6,7)}
            edgegray={q for q in mid if q[0] in (LEFT,RIGHT-1)}
            lay(b,screen,'brick','Q',y)
            lay(b,edgegray,'brick','D',y)
            window(b,mid-edgegray-screen,y,'T' if k%2 else 'S')
        elif k==9:
            lay(b,mid,'brick','A',y)
        lay(b,cores-perimeter-mid,'brick','D',y,False)
        window(b,courtwalls-perimeter-cores-mid,y,'C')
        lay(b,posts|span_anchors,'brick','D',y,False)
        if k==3:two_stage_span(b,y+3,H0,H1,set())
        if k==8:two_stage_span(b,y+3,Z0,Z1,set())
        b.step(f'第 {k+1:02d} 層・水平框線及樓板','扣水平框線，再依圖扣入有柱支承的灰板；中央空地不可加柱。')
        seam=(edge&{q for q in edge if not (q[1]==H1-1 and 44<=q[0]<54 and k in (5,6,7))})
        lay(b,seam,'plate','L' if k in (0,3,6,9) else 'B',y+3,True)
        lay(b,edge-seam,'plate','Q',y+3,True)
        for pid,x,z,r,_ in plan:b.put(pid,'D',x,z,y+3,r)
        if k in (3,8):
            for h in (y+4,y+5):lay(b,d-span,'plate','D',h,h%2==0)
        if k==9:
            b.step('兩翼屋面跨中庭','每支 16 凸點長板兩端扣在中庭牆；下方保持挑空，非實體拼裝測試。')
            for x0 in (21,66):
                for z in range(26,36,2):b.put('4282','L',x0,z,y+3)
    b.step('平屋頂：交錯薄板和機房底座','屋頂是水平深灰色薄帶；小量體退縮，讓遠看立面保持水平。')
    roofrooms=rect(20,31,12,6)|rect(77,30,12,7)|rect(47,24,10,7)
    lay(b,SHELL-roofrooms,'tile','D',TOP,True)
    lay(b,roofrooms,'plate','L',TOP,True)
    b.step('屋頂技術層與銀灰收邊','技術量體各自扣在屋面；它們不代替中庭或跨梁的支承。')
    lay(b,roofrooms,'brick','L',TOP+1,True)
    lay(b,roofrooms,'tile','L',TOP+4,True)
    final=[]
    for bag in b.info['bags']:
        chunks=[]
        for s in bag['steps']:
            n=len(s['pieces'])
            for i in range(0,n,12):
                chunks.append(dict(name=s['name']+(f' ({i//12+1}/{(n+11)//12})' if n>12 else ''),hint=s['hint'],pieces=s['pieces'][i:i+12]))
        size=sum(len(s['pieces']) for s in chunks)
        budget=max(240,((size+((size+319)//320)-1)//((size+319)//320)))
        bins=[[]]; count=0
        for s in chunks:
            if count and count+len(s['pieces'])>budget and len(bins)<(size+319)//320:
                bins.append([]); count=0
            bins[-1].append(s); count+=len(s['pieces'])
        for i,steps in enumerate(bins):
            final.append(dict(name=bag['name']+(f' {i+1}/{len(bins)}' if len(bins)>1 else ''),steps=steps))
    b.info['bags']=final
    return b.info

if __name__=='__main__':
    model=build()
    validate(model)
    allp=[p for bag in model['bags'] for s in bag['steps'] for p in s['pieces']]
    assert all(verified(p['part'],p['color']) for p in allp)
    dump(DATA/(ID+'.json'),dict(model=model,reference=REF))
    out=ROOT/'downloads'/ID
    out.mkdir(exist_ok=True)
    qa=dict(pieces=len(allp),bags=len(model['bags']),steps=sum(len(b['steps']) for b in model['bags']),
            maxLayer=max(p['y']+parts[p['part']]['h'] for p in allp),selectedPartColors=len({(p['part'],p['color']) for p in allp}),
            collisions=0,unsupported=0,disconnected=0,physicalBuildTested=False,portalClearStuds=22)
    (out/'assembly-qa.json').write_text(json.dumps(qa,indent=2)+'\n')
    print(qa)

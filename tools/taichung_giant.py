"""Giant headquarters ensemble. Plan orientation follows JJP's first-floor drawing."""
from collections import defaultdict
from itertools import groupby

from design import local_cells
from industrial_models import building_views, decal


def footprint(left, right, rear, fronts):
    """One front-edge depth for each two-stud bay of the curved façade."""
    return {(x, z) for x in range(left, right) for z in range(rear, fronts[(x-left)//2]+1)}


def cover(b, shape, color, cells, y, across=False):
    """Combine neighbouring equal scanlines into rectangles before selecting stocked bricks."""
    lines = defaultdict(list)
    for x,z in cells:
        if across: x,z=z,x
        lines[z].append(x)
    spans = defaultdict(list)
    for z,cols in lines.items():
        for _,row in groupby(enumerate(sorted(cols)),lambda v:v[1]-v[0]):
            xs=[x for _,x in row]
            spans[xs[0],len(xs)].append(z)
    for (x,w),rows in sorted(spans.items()):
        for _,sequence in groupby(enumerate(sorted(rows)),lambda v:v[1]-v[0]):
            zz=[z for _,z in sequence]
            if across:b.area(shape,color,zz[0],x,y,len(zz),w)
            else:b.area(shape,color,x,zz[0],y,w,len(zz))


def glazing(b, cells, y, phase=0):
    # Exposed glazing forms a continuous cool-blue band; two narrow smoke-glass
    # panels break the streaks of reflection at the same bays on successive floors.
    front={x:max(z for xx,z in cells if xx==x) for x,_ in cells}
    panes={(x,z) for x,z in cells if z==front[x] and x%12==6}
    cover(b,'brick','B',cells-panes,y,phase%2)
    cover(b,'brick','S',panes,y)



def giant(Building):
    b=Building('giant','TC 04','巨大集團全球營運總部','Giant Group Global Headquarters',
        '面向兩棟之間的廣場，左側是自行車文化探索館的銀白薄殼，右側是逐層收窄的辦公塔樓。二樓短橋橫跨通道，塔樓裙房前方留有自行車坡道與露臺。',
        44,24,[.53,.61,1.32],['十五層辦公塔樓與三層探索館','二樓短橋與橋下廣場','雙瓣銀殼與窄帶天窗'],'Giant Group')
    building_views(b,'廣場位於中央，三層文化館在左，十五層辦公塔樓位於右側的低裙房上。',
        '從文化館端看，屋面雙瓣在狹長深色採光帶旁錯開高度。塔樓每層都有向外伸出的白色簷帶。',
        '中央路徑穿進兩棟之間，二樓短橋橫跨其上。塔樓層層退縮，文化館屋頂依平面曲線分成兩瓣。',-1)
    b.foundation('D','L')
    museum=footprint(2,17,3,[16,16,16,15,15,14,12,9])
    museum-={(2,3),(16,3),(2,16),(3,16),(15,11),(14,12)}
    curve=dict(part='58846',x=7,z=7,r=3)
    curved_band=local_cells(curve)
    museum.update((x,z) for z in range(7,17) for x in range(7,max(xx for xx,zz in curved_band if zz==z)+1))
    museum={p for p in museum if p[0]<7 or p[1]<7 or p[0]<=max(x for x,z in curved_band if z==p[1])}
    podium=footprint(21,41,3,[7,10,13,15,16,16,15,14,14,13])
    podium-={(21,3),(40,3),(21,7),(40,13)}
    bridge={(x,z) for x in range(15,23) for z in (5,6)}
    b.bag('兩座低棟與跨廣場短橋')
    b.step('文化館玻璃基座','由後側長直牆往廣場扣出圓弧前緣，以透明煙色小磚穿插沙藍玻璃。')
    glazing(b,museum,2)
    b.step('辦公裙房與低窗帶','沿廣場另一側扣上裙房首層。兩棟中間的空位供行人及自行車通過。')
    glazing(b,podium,2,1)
    b.step('展廳下帶與門廳上窗','展廳外殼較厚的一端露出白色帶狀牆面；將門廳靠廣場的一排上窗對正下層。')
    shell={(x,z) for x,z in museum if x<6 and z<11}
    glazing(b,museum-shell,5,1)
    cover(b,'brick','W',shell,5)
    glazing(b,podium,5)
    b.step('二樓樓板預留短橋接點','由兩座建築外緣鋪向中央。在靠廣場的兩端預留接點，供下一片長板同時扣入。')
    for slab in (museum,podium):cover(b,'plate','W',slab-bridge,8,True)
    b.step('二樓短橋扣入兩棟','將一塊白色 2 × 8 長板扣在兩側窗牆凸點上。中間四格跨過廣場，在橋面鋪淺灰光面。')
    b.put('3034','W',15,5,8)
    b.put('87079','L',17,5,9)
    b.step('裙房窗帶與三樓銀邊','沿曲面窗線向兩端延伸。廣場側窗帶在兩層之間留出清楚的白色樓板。')
    glazing(b,podium,9,1)
    cover(b,'plate','W',podium,12)
    b.step('三樓玻璃與露臺樓板','透明上層由白板蓋住。右半部將承托辦公塔樓，左側的寬闊平台成為露臺。')
    glazing(b,podium,13)
    cover(b,'plate','W',podium,16,True)
    b.bag('探索館的銀白薄殼與天窗')
    b.step('彎曲的展示面','依展館弧線先排玻璃，再從左後方扣上逐列拉長的銀白色側殼。')
    second={(x,z) for x,z in museum if x<=max(4,14-(z-3))}
    glazing(b,museum-second,9,1)
    cover(b,'brick','W',second,9)
    b.step('探索館三樓白色薄簷','弧形外殼向廣場延伸，邊緣留一圈明亮的簷口。')
    cover(b,'plate','W',museum,12,True)
    b.step('上窗沿弧線沒入薄殼','將狹長的玻璃帶穿插進白色三樓外殼，靠廣場處保留斜收的窗尾。')
    b.put('58846','W',7,7,13,3)
    edge={(x,z) for x,z in museum-curved_band if 3<=x<=13 and (x,z+1) not in museum}
    for x,z in sorted(edge):b.put('3005','S',x,z,13)
    cover(b,'brick','W',museum-curved_band-edge,13)
    b.step('兩瓣錯層的屋面','鋪設連續白色承板。中央採光縫沿前後方向轉彎，兩側屋面有不同高度。')
    roof=(museum-curved_band)|local_cells(curve,'studs')
    cover(b,'plate','W',roof,16)
    # The fourth-floor drawing shows a sweeping roof crease, not a circular oculus.
    ridge=[14,14,13,13,12,11,10,9,8,7,6,5,4,4]
    slot={(x,z) for x,z in roof if x==ridge[z-3] and 4<=z<=15}
    high={(x,z) for x,z in roof if x<ridge[z-3]}
    low=roof-slot-high
    b.step('弧形採光縫與低屋瓣','用沙藍和深色小片沿中央排出漸彎的細縫，白色平板包住靠廣場的低屋瓣。')
    cover(b,'tile','B',slot,17)
    cover(b,'tile','W',low,17,True)
    cover(b,'plate','W',high,17,True)
    b.step('高屋瓣與柔和弧頂','在採光縫另一側墊起高屋瓣；弧面斜磚順著屋頂長向排，光面白板封其餘平面。')
    raised={(x,z) for x,z in high if x<=ridge[z-3]-3}
    cover(b,'tile','W',high-raised,18)
    cover(b,'plate','W',raised,18)
    crest={(x,z) for x,z in raised if x<=ridge[z-3]-5}
    cover(b,'tile','W',raised-crest,19,True)
    cover(b,'plate','W',crest,19,True)
    caps=set()
    for x in (3,5,7,9):
        patch={(xx,zz) for xx in (x,x+1) for zz in (4,5)}
        if patch<=crest:
            b.put('15068','W',x,4,20,2)
            caps|=patch
    cover(b,'tile','W',crest-caps,20)
    b.bag('辦公塔樓、波紋挑簷與斜冠')
    # Bottom three levels belong to the podium; twelve further tiers complete the 15-storey tower.
    upper=set()
    first=None
    for level in range(12):
        left=25+min(4,(level+1)//2)
        fronts=[min(14,10+idx//2) if idx<6 else 13 for idx in range((41-left)//2+1)]
        outline=footprint(left,40,3,fronts)
        # The nearest corner of the real tower has a broad south-facing terrace.
        by_x={x:max(z for xx,z in outline if xx==x) for x,_ in outline}
        overhang={(x,z) for x,z in outline if z==by_x[x]}
        glass=outline-overhang
        y=17+4*level
        b.step(f'第 {level+4} 層 · 向內收的帷幕','先扣沙藍玻璃及深色窗豎框。塔樓後側保持對齊，面對文化館的一側分段內收。')
        if level==11:
            crown_sign={(x,z) for x in range(33,37) for z in (9,10)}
            glazing(b,glass-crown_sign,y,level%2)
            b.put('3001','W',33,9,y)
            decal(b,'giant','辦公塔冠正面的藍色 GIANT 標誌',29,7)
        else:
            glazing(b,glass,y,level%2)
        b.step(f'第 {level+4} 層 · 白色挑簷','白色薄板前緣挑出一格。從每組前端往後跨接，連成有轉折的陽台邊帶。')
        for x,z in sorted(overhang): b.put('3023','W',x,z-1,y+3,1)
        cover(b,'plate','W',outline-{(x,zz) for x,z in overhang for zz in (z-1,z)},y+3,level%2)
        if level<11:cover(b,'tile','W',overhang,y+4)
        if first is None:first=outline
        upper=outline
    b.step('順斜冠收頂','屋頂高側加一道墊層，與低側形成兩段屋冠。細弧面磚柔化轉折，白色光面收齊頂緣。')
    crown={(x,z) for x,z in upper if x>=35}
    cover(b,'plate','W',crown,65)
    cover(b,'tile','W',upper-crown,65)
    cover(b,'tile','W',crown,66,True)
    b.bag('廣場、折返坡道與展示名牌')
    b.step('裙房露臺與自行車坡道','在塔樓旁的低樓頂鋪設淺灰露臺；分段臺階沿裙房前方折返，表現自行車坡道的走向。')
    cover(b,'tile','L',podium-first,17)
    for idx,(x,z,w) in enumerate([(26,17,3),(23,16,3),(21,15,2),(19,14,2),(19,12,2),(19,10,2),(19,8,2)]):
        for y in range(2,3+idx):b.area('plate','L',x,z,y,w,2)
        b.area('tile','D',x,z,3+idx,w,2)
    for y in range(2,9):b.put('3023','L',19,7,y)
    b.put('3069b','D',19,7,9)
    b.step('廣場的入口橋','從街道側向廣場鋪平面步橋。橋下的深色溝帶沿街延伸，兩頭扣在矮墩上。')
    b.area('tile','D',5,19,2,12,1)
    b.area('tile','D',21,19,2,16,1)
    for z in (17,20): b.area('plate','L',17,z,2,3,2)
    for x in (17,18,19):b.put('3710','L',x,17,3,1)
    b.area('tile','D',17,17,4,3,4)
    b.step('廣場樹列與巨大展示牌','在廣場邊沿種下樹列，保留橋下通道。GIANT GROUP 貼紙置於本款前緣的獨立展示名牌。')
    for x,z in [(2,20),(6,21),(11,21),(30,20),(37,19),(41,16)]: b.canopy(x,z,2)
    b.put('3010','W',32,22,2)
    decal(b,'giant-group','底座廣場側的巨大集團展示名牌',26,7)
    return b.finish()

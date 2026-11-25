"""A larger stud reconstruction following JJP's published 1F, 2F, 4F and longitudinal section."""
from collections import defaultdict
from itertools import groupby
from math import atan2, exp, hypot, pi, sin

from design import grid_buckets, local_cells, parts, stock, world_cell
from industrial_models import building_views, decal
from taichung_giant import cover


def rect(x, z, w, d):
    return {(xx, zz) for xx in range(x, x+w) for zz in range(z, z+d)}


def polygon(vertices):
    """Rasterise the drawing on stud centres. X runs left to right and +Z toward the plaza."""
    result=set()
    for z in range(min(v[1] for v in vertices), max(v[1] for v in vertices)):
        line=z+.5
        crossings=[]
        for (x1,z1),(x2,z2) in zip(vertices,vertices[1:]+vertices[:1]):
            if min(z1,z2)<=line<max(z1,z2):
                crossings.append(x1+(line-z1)*(x2-x1)/(z2-z1))
        if crossings:
            for x in range(min(v[0] for v in vertices),max(v[0] for v in vertices)):
                if sum(cross<x+.5 for cross in crossings)%2:result.add((x,z))
    return result


def exposed(cells):
    return {(x,z) for x,z in cells if any(k not in cells for k in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)))}


def planned_deck(b, cells, y, across=False):
    saved=b.current
    layout={'pieces':[]}
    b.current=layout
    cover(b,'plate','W',cells,y,across)
    b.current=saved
    return layout['pieces']


def load_path(cells, panels):
    """Add a pier only under a deck panel that would otherwise miss the perimeter or a rib."""
    rim=exposed(cells)
    ribs={(x,z) for x,z in cells if z%9==3 or (x%14==3 and z%5==0)}
    bearing=rim|ribs
    for p in panels:
        footprint=local_cells(p,'bottom')
        if not footprint&bearing:
            options=sorted(footprint&cells)
            if options:bearing.add(options[len(options)//2])
    return rim,bearing


def glass_course(b,cells,rim,y,phase=0,solid=frozenset(), style='blue'):
    """Separate 1×2 translucent glass lites from opaque spandrels and the interior load path."""
    skin=(rim&cells)-solid
    inside=cells-skin
    cover(b,'brick','L',inside,y,phase%2)
    # Long runs use actual glazing bricks. Rear spandrels and the thin mullion between
    # pane groups are sand blue, so the façade stays legible in partly lit portraits.
    available=set(skin)
    for axis in (0,1):
        rows=defaultdict(list)
        for x,z in available:
            if axis: x,z=z,x
            rows[z].append(x)
        for z,row in sorted(rows.items()):
            for _,chunk in groupby(enumerate(sorted(row)),lambda v:v[1]-v[0]):
                run=[x for _,x in chunk]
                if len(run)<2:continue
                for j in range(0,len(run)-1,2):
                    i=run[j];x0,z0=(z,i) if axis else (i,z)
                    group=(i//2)%8
                    if style=='ribbon-dark': part,c='3065','S'
                    elif style=='ribbon-blue': part,c='3065','T'
                    elif style=='dark':
                        part,c=('3065','S') if group in (2,5,7) else ('3065','T')
                    else:
                        part,c=('3065','T') if group not in (0,) else ('3065','S')
                    b.put(part,c,x0,z0,y,axis)
                    available.discard((x0,z0));available.discard((x0+(axis==0),z0+(axis==1)))
    for x,z in sorted(available): b.put('3005','D',x,z,y)


def push(b,step,hint,pieces):
    b.step(step,hint)
    b.current['pieces'].extend(pieces)


# The outer skin of the low exhibition wing follows an arc. Each six-stud facet is trapped
# between an upright, round stud at ground level and a second round stud under the roof.
FACETS=[(36,13,-85),(34,19,-67),(32,24,-49),(27,28,-31),(21,30,-14),(15,31,-5),(9,32,0)]


def facade_reserve(model):
    reserved=set()
    for x,z,a in FACETS:
        p=dict(part='3666',x=x-2,z=z,y=3,r=0,pivotAt=dict(x=x+.5,z=z+.5,degrees=a))
        for i,j in local_cells(p):
            reserved.update(grid_buckets(world_cell(model,p,i,j)))
    return reserved


def museum_facets(b):
    for index,(x,z,angle) in enumerate(FACETS):
        label=f'文化館弧牆 {index+1}'
        b.step(label+' · 下定位點','先扣一片灰色圓板。向廣場伸出的外牆以這顆凸點轉向，屋面裝上後會從上方再次定位。')
        b.put('4073','D',x,z,2)
        axis=dict(x=x+.5,z=z+.5,degrees=angle,label=label,type='module')
        start=len(b.info['bags'][-1]['steps'])
        b.step(label+' · 玻璃與窄邊','先放底梁，按俯視圖轉入角度。三片小窗並排，再以銀白薄板連住各窗的上緣。')
        b.put('3666','D',x-2,z,3)
        for y in (4,7,11):
            for k in (0,2,4):
                b.put('3065',('T' if (index+k)%6 else 'S') if y!=11 else ('T' if (index+k)%8 else 'S'),x-2+k,z,y)
            if y==7:b.put('3666','W',x-2,z,10)
        b.step(label+' · 流動銀殼','沿著展館轉角，銀白色表皮逐面向下加深。最後在頂蓋中心放一片圓板。')
        for y in (14,18,21,24):
            if (y==14 and index<6) or (y==18 and index in (1,2,3,4,5)) or (y==21 and index in (2,3)):
                # Different aperture heights shape the window wall under the shell.
                for k in (0,2,4):b.put('3065','T' if k!=4 or index%2 else 'S',x-2+k,z,y)
            else:
                b.put('3009','W',x-2,z,y)
                if index==4 and y==21:decal(b,'giant-word','文化館銀殼上的 GIANT 字標，依穿孔字牆轉製',38,7)
            if y==14:b.put('3666','W',x-2,z,17)
        b.put('3666','W',x-2,z,27)
        b.put('4073','L',x,z,28)
        b.put('3069b','W',x-2,z,28)
        b.put('63864','W',x+1,z,28)
        for step in b.info['bags'][-1]['steps'][start:]:
            for p in step['pieces']:p['pivotAt']=axis


def museum_body(b, core, bridge, levels):
    # Three structural levels span the left exhibit volume. The rear wall is a solid
    # service wall; the glazing is concentrated at either end and beside the plaza.
    for level,(bottom,heights,deck_y) in enumerate(((2,(2,5,8),11),(12,(12,15),18),(19,(19,22,25),28))):
        if level not in levels:continue
        slab=core-bridge if level==0 else core
        panels=planned_deck(b,slab,deck_y,level%2)
        rim,structure=load_path(core,panels)
        landing=core&bridge
        for y in heights:
            b.step(f'展館第 {level+1} 層的牆柱 · {y-bottom+1}','外圈沿玻璃分格扣合，內部橫肋托住長跨樓板，橋頭的支座與毗鄰的立柱同高。')
            solid={(x,z) for x,z in rim if z<6 or (level==2 and x<11)}
            glass_course(b,structure|landing,rim,y,y%2,solid,'dark' if level==0 else 'blue')
        push(b,f'展館第 {level+1} 層承板','由後側開始壓上白色承板，靠廣場的弧形面板位於承板外緣。',panels)
    # Full spanning deck at y29 also captures all round top bearings of the tangent panels.
    return core


def podium_body(b,podium,bridge,levels):
    for level,(heights,deck_y) in enumerate((((2,5,8),11),((12,15,18),21),((22,25,28),31))):
        if level not in levels:continue
        slab=podium-bridge if level==0 else podium
        panels=planned_deck(b,slab,deck_y,level%2)
        rim,structure=load_path(podium,panels)
        for y in heights:
            b.step(f'裙房第 {level+1} 層門廳與肋柱 · {y}','先裝沿中心廣場的玻璃立面，再裝通往自行車露臺一側的柱列。')
            if y==heights[-1]:
                cover(b,'brick','W',rim,y,True)
                cover(b,'brick','L',(structure|(bridge&podium))-rim,y)
            else:
                glass_course(b,structure|(bridge&podium),rim,y,level,solid={(x,z) for x,z in rim if z<5},style='dark' if level==0 else 'blue')
        push(b,f'裙房第 {level+1} 層的銀白樓簷','由前方柔和曲線回到後側直牆，樓板連住每道肋柱，保留外側坡道空間。',panels)


def two_floor_bridge(b):
    b.step('二樓空橋內縮主梁','一片 2 × 16 長薄板跨接兩端；主梁內縮至弧面底下。')
    b.put('4282','W',34,6,11)
    # The bow is visible from above. A two-stud longitudinal spine is recessed
    # beneath transverse plates; keep the front row clear at the ramp junction.
    sections=((6,4),(5,4),(3,6),(3,6),(2,6),(2,6),(3,6),(3,6),(5,4),(6,4))
    b.step('空橋弧形外緣與橫肋','橫向長板由下層主梁承接，中央後掠、兩端收回至橋頭。')
    for x,(z,w) in enumerate(sections,37):
        b.put({4:'3710',6:'3666'}[w],'W',x,z,12,1)
    b.step('空橋白色收邊、步道與透光欄板','灰色步道居中；兩側布置透明欄板，接自行車坡道處留開口。')
    walking={(x,zz) for x,(z,w) in enumerate(sections,37) for zz in range(z+1,z+w-1)}
    # Offset seams across the 1-wide cross ribs; do not enclose the approach.
    cover(b,'tile','L',walking,13)
    for x,(z,w) in enumerate(sections,37):
        f=z+w-1
        for edge in (z,f):
            if edge==f and 39<=x<=41:
                b.put('3070b','L',x,edge,13)
                continue
            b.put('3024','W',x,edge,13)
            b.put('3024','T',x,edge,14)
            b.put('3070b','T',x,edge,15)


def roof_caps(b,cells,y,side):
    """Use smooth curved slopes only on a contour that actually turns downwards."""
    cells=set(cells);caps=set()
    for x,z in sorted(cells):
        zone=rect(x,z,2,2)
        if not zone<=cells or zone&caps:continue
        if (x+2*side,z) not in cells and (x-2*side,z) in cells:
            b.put('15068','W',x,z,y,3 if side>0 else 1)
            caps|=zone
    cover(b,'tile','W',cells-caps,y,True)


def sculpted_roof(b,museum,core):
    b.step('銀殼的連續承板','沿牆頂放第一片白板，再跨越牆背支肋。靠廣場的一圈會鎖到先前各弧牆的圓形頂扣。')
    pins={(x,z) for x,z,a in FACETS}
    top=museum|pins|core
    # Keep roof pieces above the arcuate curtain physically attached even at the outer curve.
    deck=planned_deck(b,top,29,True)
    deck=[p for p in deck if local_cells(p,'bottom')&(core|pins)]
    top=set().union(*(local_cells(p,'studs') for p in deck))
    b.current['pieces'].extend(deck)
    # The 4F drawing shows a long S-shaped clerestory. At both tips it pinches to one
    # pane, widening in the middle between two sloping leaves of aluminium cladding.
    ranks={};slot=set()
    for x,z in top:
        t=max(0,min(1,(z-4)/28));ridge=9+22*(1-t**1.55)**1.75
        span=x-ridge
        if abs(span)<.8+.6*sin(pi*t) and .04<t<.97:
            slot.add((x,z));continue
        if span<0:
            rise=round(3+3.5*(1-t)+1.7*(1-exp(span/4)))
            wing=-1
        else:
            rise=round(1+2.2*(1-t)+1.6*sin(pi*t)*(1-exp(-span/4)))
            wing=1
        ranks[x,z]=(wing,rise)
    b.step('玻璃採光縫與兩瓣起點','先把透明淺藍採光縫扣在白板上。採光縫沿曲線分隔高低兩瓣，兩端逐漸收尖。')
    cover(b,'plate','B',slot,30)
    cover(b,'plate','T',slot,31,True)
    cover(b,'tile','S',slot,32)
    clerestory={(x,z) for x,z in ranks if any((x+dx,z+dz) in slot for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)))}
    for wing,title in ((-1,'高屋瓣'),(1,'廣場側低屋瓣')):
        heights={k:h for k,(side,h) in ranks.items() if side==wing}
        for level in range(max(heights.values())+1):
            b.step(f'{title} · 第 {level+1} 道等高線','順著前一道等高線交錯鋪板，先把內側高區墊起，再收平外側薄殼。弧面斜磚的高肩朝向屋脊。')
            core_cells={k for k,h in heights.items() if h>level}
            surface={k for k,h in heights.items() if h==level}
            glazing=core_cells&clerestory if 3<=level<=4 else set()
            cover(b,'plate','S',glazing,30+level)
            cover(b,'plate','W',core_cells-glazing,30+level,level%2)
            roof_caps(b,surface,30+level,wing)


def tower_plan(level,podium):
    """The west edge retreats toward the tower spine. The south edge rolls in plan."""
    retreat=(0,2,4,5,6,7,8,9,9,10,10,11)
    left=57+retreat[level]
    limits={}
    for x in range(left,91):
        t=(x-left)/(90-left)
        peak=.56+.09*sin(level*.37)
        edge=(t/peak if t<=peak else (1-t)/(1-peak))
        lip=round(14+7.2*max(0,edge)+4.0*t)
        limits[x]=lip
    outline={(x,z) for x,lip in limits.items() for z in range(4,lip+1)}&podium
    glass={(x,z) for x,z in outline if x>=left+1 and z<=limits[x]-2 and x<=89 and z>=5}
    return outline,glass


def tower(b,podium):
    for level in range(12):
        floor=level+4;y=32+level*7
        slab,glass=tower_plan(level,podium)
        # Every individually projecting eave strip must reach at least one full row of glazing.
        strips=[];lip=set();used=set()
        fronts={x:max(z for xx,z in slab if xx==x) for x in sorted({x for x,z in slab})}
        for x,front in fronts.items():
            if x in used or (x,front-3) not in glass:continue
            width=2 if fronts.get(x+1)==front and (x+1,front-3) in glass else 1
            strip=dict(part='3020' if width==2 else '3710',color='W',x=x,z=front-3,y=y+6,r=1)
            strips.append(strip);lip|=local_cells(strip);used.update(range(x,x+width))
        # For the left and right corners, run the plates inward across the end wall.
        # The remaining back strip spans the glazing line in the opposite direction.
        remaining=slab-lip
        cross=[]
        for z in sorted({z for x,z in remaining}):
            row=[x for x,zz in remaining if zz==z]
            for start,end in ((min(row),min(row)+4),(max(row)-3,max(row)+1)):
                f=rect(start,z,end-start,1)
                if f<=remaining and f&glass and f-glass:
                    p=dict(part='3710',color='W',x=start,z=z,y=y+6,r=0)
                    cross.append(p);remaining-=f
        deck=strips+cross
        for p in planned_deck(b,remaining,y+6,True):
            if local_cells(p)&glass:deck.append(p)
        slab=set().union(*(local_cells(p) for p in deck))
        rim,bearing=load_path(glass,deck)
        for off in (0,3):
            b.step(f'辦公塔第 {floor} 樓 · '+('下排玻璃' if off==0 else '上排玻璃'),'沿外牆把透明玻璃與沙藍窗間牆對齊。後方的直線是服務核心，前方窗格沿南向露臺的弧線退後。')
            glass_course(b,bearing,rim,y+off,level,solid={(x,z) for x,z in rim if z==5 or (x==89 and z<=11)},style='ribbon-dark' if off==3 else 'ribbon-blue')
        push(b,f'第 {floor} 樓的白色波浪簷帶','先跨過內肋，再將較短薄板的末端朝廣場伸出，將兩排玻璃水平連接起來。',deck)
        following=tower_plan(level+1,podium)[1] if level<11 else None
        if following:
            b.step(f'第 {floor} 樓退台鋪面','朝向展館的一端有一小段可見露臺，把短白色光面板扣在這一層外緣。')
            exposed_top={(x,z) for x,z in slab-following if z>8}
            cover(b,'tile','W',exposed_top,y+7)
    # The published longitudinal section shows the high edge of the crown behind a
    # recessed flat roof. Three interlocking parapet levels translate the rising edge.
    crown={(x,z) for x,z in slab if x>=70 and z>=5}
    rim=exposed(crown)
    b.step('塔冠內縮屋面與採光罩','沿著女兒牆內側鋪灰色屋面，在靠後方的位置留出採光罩。')
    hatch=rect(76,9,4,2)
    cover(b,'tile','L',crown-rim-hatch-rect(82,20,6,1),116)
    cover(b,'plate','B',hatch,116)
    cover(b,'tile','T',hatch,117)
    b.step('塔冠正面的 GIANT 標誌','把藍色 GIANT 貼紙置中貼在一塊白色長磚上，貼好後扣在塔冠面向廣場的一側。')
    logo=rect(82,20,6,1)
    b.put('3009','W',82,20,116)
    decal(b,'giant','塔冠面向廣場的藍色 GIANT 標誌',40,7)
    cover(b,'tile','W',logo,119)
    rim-=logo
    for dy in range(9):
        b.step(f'塔冠第 {dy+1} 道斜升收邊','塔冠靠右後角逐步抬高。每道收邊都扣在前一道的凸點，留下清楚可見的斜向輪廓。')
        standing={(x,z) for x,z in rim if dy<=round(3.3*(x-70)/20+4.9*(20-z)/15)}
        next_standing={(x,z) for x,z in standing if dy+1<=round(3.3*(x-70)/20+4.9*(20-z)/15)}
        cover(b,'plate','W',next_standing,116+dy,dy%2)
        cover(b,'tile','W',standing-next_standing,116+dy,dy%2)


def ramp_segment(b,x,z,w,d,h,finish_color='D'):
    """Each crosswise segment bears on both ends, leaving the deck open beneath."""
    if min(w,d)>1:
        foot=rect(x,z,1,d)|rect(x+w-1,z,1,d) if w>=d else rect(x,z,w,1)|rect(x,z+d-1,w,1)
    else:foot=rect(x,z,w,d)
    y=2
    while y+3<=h:
        cover(b,'brick','L',foot,y);y+=3
    while y<h:
        cover(b,'plate','L',foot,y);y+=1
    b.area('plate','W',x,z,h,w,d)
    b.area('tile',finish_color,x,z,h+1,w,d)


def landscape(b):
    b.step('通往二樓短橋的自行車坡道','從廣場外側逐段升高，每一段先裝兩端的支座，再壓上跨過支座的白板與深灰面層。轉彎後，最後一段與二樓橋面齊平。')
    # A quarter-turn cycleway swings around the planting island. Build a continuous
    # 3-stud wheel lane, then use its outside row for the short glazing panels.
    for i,x in enumerate((68,64,60,56,52,48)):
        ramp_segment(b,x,31,4,3,2+i//2)
    turn=defaultdict(set)
    for x in range(39,48):
        for z in range(25,34):
            dx,dz=48-(x+.5),z+.5-25
            if 6<=hypot(dx,dz)<9:
                h=4+round(2*atan2(dx,dz)/(pi/2))
                turn[h].add((x,z))
    for h,slab in sorted(turn.items()):
        y=2
        while y+3<=h:
            cover(b,'brick','L',slab,y);y+=3
        while y<h:
            cover(b,'plate','L',slab,y);y+=1
        cover(b,'plate','W',slab,h);cover(b,'tile','D',slab,h+1)
    for i,z in enumerate(range(23,8,-2)):
        h=6+(i+1)*5//8
        if z==9: h+=1
        ramp_segment(b,39,z,3,2,h)
    b.step('朝向廣場的透明護欄','彎道外側沿地形升高。直線段的短玻璃護欄由淺灰扶手收頭，終點與二樓短橋齊平。')
    for i,z in enumerate(range(23,8,-2)):
        h=6+(i+1)*5//8
        if z==9: h+=1
        y=2
        while y+3<=h:
            b.put('3004','L',38,z,y,1);y+=3
        while y<=h:
            b.put('3023','W',38,z,y,1);y+=1
        b.put('3065','T',38,z,h+1,1)
        b.put('3069b','L',38,z,h+4,1)
    b.step('前庭跨渠步橋','深灰色鋪面代表細長的集水帶，淺灰色橋肩與兩排橫向防滑木板一起扣住入口。')
    for x in range(20,81,4):
        if 44<=x<52:continue
        b.area('tile','D',x,39,2,4,2)
    for x in (44,50):
        b.area('plate','L',x,36,2,2,8)
    for z in range(36,44):b.area('plate','D',44,z,3,8,1)
    for z in range(36,44):b.area('tile','N',44,z,4,8,1)
    b.step('園路的淺色拼花','沿著兩棟之間的廣場繞過植栽島。鋪面裡的淡沙色色帶，在入口處收束。')
    for x in range(6,36):
        z=34+round(2*sin((x-6)/30*pi))
        b.area('tile','N',x,z,2,1,1)
    for x in range(60,89):
        z=30+round(3*sin((x-60)/29*pi))
        if z>=31 and x<73:continue
        b.area('tile','N',x,z,2,1,1)
    b.step('樹島、入口列樹與座椅','棕色樹幹穿過中央樹穴，左右樹冠錯開。入口座椅立在兩個獨立支腳上，椅面用長片連成。')
    for x,z in [(6,37),(13,37),(21,42),(30,43),(34,37),(55,36),(64,37),(76,36),(87,34),
                (88,42),(3,9),(3,18),(3,27),(93,7),(93,17),(93,28)]:
        b.area('plate','G',x-1,z-1,2,3,2)
        b.put('3062b','O',x,z,3)
        b.put('4032a','F',x-1,z-1,6)
        b.put('4073','G',x,z,7)
        b.put('4073','G',x-1,z-1,7)
    for x,z in ((9,40),(14,42),(26,37),(70,42),(79,36)):
        for xx in (x,x+3):b.put('3024','D',xx,z,2)
        b.put('2431','O',x,z,3)
    b.step('展示名牌','將 Giant Group 標誌置中貼到白色名牌正面，再把名牌扣在前庭靠右的兩個固定點上。')
    b.put('3009','W',82,44,2)
    decal(b,'giant-group','前庭的巨大集團展示名牌',39,7)


def schedule(b,goal=6000):
    """Tune the visible paving module size, then issue evenly filled bags with local steps."""
    b.pave('L')
    # The final paving can be approached from any direction. Package each local area
    # as a named operation so that a builder can find it again on the large base.
    phase=b.info['bags'][-1]
    paving=phase['steps'].pop()
    zones=defaultdict(list)
    for p in paving['pieces']:
        zones[p['z']//12,p['x']//24].append(p)
    for (z,x),stones in sorted(zones.items()):
        side=('左外側','展館側','總部側','右外側')[x]
        line=('後緣','內庭','入口內側','前緣')[z]
        push(b,f'{side}{line}鋪面','從圖中亮起的區域邊緣開始，交錯短縫填入淺灰鋪面。靠近已裝好的外牆時，垂直按壓每一片。',stones)
    phases=b.info['bags']
    rows=[s for phase in phases for s in phase['steps']]
    total=sum(len(s['pieces']) for s in rows)
    # Match the specified stock count by subdividing visible ashlar or roof panels.
    # Only their surface joints change. Every child has the same thickness and covers
    # exactly the original footprint. Reserving tiles avoids weakening spanning plates.
    halves={'4162':('2431','2431'),'6636':('63864','63864'),'2431':('3069b','3069b'),
            '63864':('3069b','3070b'),'3069b':('3070b','3070b'),'87079':('3068b','3068b')}
    while total<goal:
        initial=total
        for step in reversed(rows):
            revised=[]
            for p in step['pieces']:
                pair=halves.get(p['part'])
                if total>=goal or pair is None or any(p['color'] not in stock[q] for q in pair):
                    revised.append(p);continue
                offset=parts[pair[0]]['w']
                x,z=p['x'],p['z'];r=p['r']
                revised.extend([dict(p,part=pair[0]),dict(p,part=pair[1],x=x+(0 if r%2 else offset),z=z+(offset if r%2 else 0))])
                total+=1
            step['pieces']=revised
        if total==initial:break
    if total!=goal:raise ValueError(('Giant assembly count',total,[(p['name'],sum(len(s['pieces']) for s in p['steps'])) for p in phases]))
    steps=[]
    for phase in phases:
        for s in phase['steps']:
            n=len(s['pieces'])
            for i in range(0,n,8):
                name=s['name']+(f'（{i//8+1}/{(n+7)//8}）' if n>8 else '')
                steps.append((phase['name'],dict(name=name,hint=s['hint'],pieces=s['pieces'][i:i+8])))
    bags=[];start=0;done=0
    for bag_no in range(12):
        begin=start;count=0
        while start<len(steps) and (bag_no==11 or done+count<500*(bag_no+1)):
            count+=len(steps[start][1]['pieces']);start+=1
        a=steps[begin][0];last=steps[start-1][0]
        name=a if a==last else a+'、'+last
        bags.append(dict(name=name,steps=[s for _,s in steps[begin:start]]));done+=count
    titles=['底板與展館柱腳','一樓玻璃、裙房與短橋','展館二三樓與轉向弧牆',
            '弧牆頂扣與高屋瓣','低屋瓣與裙房二樓','裙房二三樓與大露臺',
            '南向退台與四至六樓','六至九樓玻璃窗帶','九至十二樓白色樓簷',
            '十二至十五樓與屋頂','塔冠標誌、自行車坡道與庭園','園區步道與入口鋪面']
    for bag,title in zip(bags,titles):bag['name']=title
    b.info['bags']=bags
    return b.info


def giant6000(Building):
    b=Building('giant6000','GD 01','巨大集團全球營運總部與自行車文化探索館','Giant Global Headquarters & Cycling Culture Museum',
        '從中央廣場進入，左側文化館以七面切向玻璃牆托起雙瓣銀殼，右側十五層辦公量體面向館舍逐層退台。二樓橋橫跨步行動線，下方留出通行高度。外側的縮尺自行車坡道通往短橋。',96,48,[.52,.56,1.34],
        ['十五層玻璃塔、南向退台與斜升塔冠','三層文化館的轉向外牆、雙瓣銀殼與採光縫','二樓雙端扣接弧形空橋、可循線的坡道與廣場'], '潘冀聯合建築師事務所、巨大集團')
    building_views(b,'廣場入口正面可同時讀出三層的展館、二樓空橋與十五層的辦公塔。','從展館側面看銀殼切線與窗牆交替，後方塔樓逐層收窄。','展館屋面狹長的天窗伸向廣場；跨接兩翼的弧形空橋位於基地後方。',-1)
    b.info['views'].extend([
        dict(id='photo-low',name='文化館低樓層玻璃',note='從廣場看一二樓窗帶與銀白屋簷。',direction=[-.18,.08,1],region=[7,37,5,33,1,32]),
        dict(id='photo-tower',name='仰看塔樓折線',note='從廣場側讀塔身折線與逐層退台。',direction=[-.22,.10,1],region=[48,92,4,27,28,125]),
        dict(id='shell',name='展館銀殼',note='兩瓣屋面沿彎曲的透明採光縫錯開高度。',direction=[-.45,.94,1.1],region=[4,39,2,34,3,39]),
        dict(id='bridge',name='廣場仰看弧形空橋',note='從廣場看二樓空橋、白色弧形邊帶與透明護欄。',direction=[0,.05,1],region=[31,54,4,14,1,22]),
        dict(id='crown',name='退台與塔冠',note='十五層塔冠藍字、斜升的屋頂輪廓與玻璃窗格。',direction=[.45,.22,1],region=[65,92,4,25,81,125])])
    b.foundation('D','L')
    museum=polygon([(8,5),(10,4),(34,4),(37,5),(37,12),(36,17),(34,22),(31,26),(27,29),(22,31),(16,32),(9,32),(7,31),(7,8)])
    podium=polygon([(49,4),(90,4),(92,6),(92,21),(91,23),(83,24),(77,24),(72,26),(66,27),(60,26),(56,24),(53,21),(51,16),(49,10),(48,6)])
    bridge=rect(34,6,16,2)
    museum|=rect(34,5,3,4);podium|=rect(47,5,3,4)
    available=museum-facade_reserve(b.info)
    # The fixed backing is wholly inside the rotating glazing leaves.
    core={(9,8)};todo=list(core)
    while todo:
        x,z=todo.pop()
        for k in ((x+1,z),(x-1,z),(x,z+1),(x,z-1)):
            if k in available and k not in core:core.add(k);todo.append(k)
    b.bag('一樓結構')
    museum_body(b,core,bridge,[0]);podium_body(b,podium,bridge,[0]);two_floor_bridge(b)
    b.bag('展館與弧牆')
    museum_body(b,core,bridge,[1,2]);museum_facets(b)
    b.bag('自行車展館雙瓣銀殼')
    sculpted_roof(b,museum,core)
    b.bag('辦公裙房與露臺')
    podium_body(b,podium,bridge,[1,2])
    b.bag('辦公塔樓與逐層退台')
    b.step('裙房露臺石材與花台','在塔樓基座前留出整塊弧形露臺。淺灰平板沿女兒牆轉向，西端花台面向展館。')
    plaza=podium-tower_plan(0,podium)[1]
    bed={(x,z) for x,z in plaza if 50<x<58 and 12<z<18}
    cover(b,'tile','L',plaza-bed,32)
    cover(b,'plate','G',bed,32)
    for x,z in sorted(bed):
        if (x+3*z)%6==0:b.put('4073','G',x,z,33)
    tower(b,podium)
    b.bag('廣場、單車坡道與庭園')
    landscape(b)
    return schedule(b)

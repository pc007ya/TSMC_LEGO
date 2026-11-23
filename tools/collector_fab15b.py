"""Fab 15B, Phase 5 office and the screen-fronted fabrication halls, from exterior photographs."""
from collections import defaultdict
from itertools import groupby
from math import hypot

from design import local_cells, parts, stock
from industrial_models import building_views, decal
from taichung_giant import cover


def rect(x,z,w,d):
    return {(i,j) for j in range(z,z+d) for i in range(x,x+w)}


def count(b):
    return sum(len(s['pieces']) for bag in b.info['bags'] for s in bag['steps'])


def logo(b,where,mm,face='front'):
    decal(b,'tsmc',where,mm,mm)
    b.current['pieces'][-1]['decal']['face']=face


def side_walls(b,x,z,w,d,y,layer):
    # The dark horizontal joints form considerably longer, staggered sheet-metal
    # panels on the long sides than the finer louvres of the planted end wall.
    c=['D','L','L','L','W','L','D','L','W','L'][layer%10]
    b.area('brick',c,x,z,y,w,1)
    for xx in (x,x+w-1):
        run=z+1
        while run<z+d-2:
            length=min(z+d-2-run,7 if (run+layer)%3 else 5)
            dark_reveal=(run-z+layer*3)%19==0
            b.area('brick','D' if dark_reveal else c,xx,run,y,1,length)
            run+=length


def hall(b,x,z,w,d,screen_from,title,is_front):
    front=z+d-1
    height=12 if is_front else 13
    b.bag(title+'・外牆與格柵')
    # The two thick pylons are kept at the edge of the screen. The side walls
    # behind them recede by one stud. A narrow red flash belongs to the pylon.
    left,right=x+screen_from,x+w-3
    screen_len=right-left-3
    # Place beam lines underneath the actual joints in the roof sheets. A
    # supplementary pier is needed where a short edge panel misses those lines.
    saved=b.current
    b.current={'pieces':[]}
    for xx in range(x,x+w,8):
        for zz in range(z,front,4):
            b.area('plate','L',xx,zz,2+height*3,min(8,x+w-xx),min(4,front-zz))
    roof_panels=b.current['pieces']
    b.current=saved
    piers=[(xx,zz) for xx in range(x+3,x+w-2,7) for zz in range(z+3,front-2,6)]
    bearing=rect(x,z,w,1)|rect(x,z+1,1,d-2)|rect(x+w-1,z+1,1,d-2)|rect(x,front-1,w,1)
    for xx,zz in piers:bearing|=rect(xx,zz,2,2)
    extra_piers=[]
    for panel in roof_panels:
        footprint=local_cells(panel)
        if not footprint&bearing:
            cells=sorted(footprint)
            pos=cells[len(cells)//2];extra_piers.append(pos);bearing.add(pos)
    for k in range(height):
        y=2+3*k
        b.step(f'{title}・第 {k+1} 道側牆與屋架支點',
               '由遠側向近側逐段咬合灰白金屬板，角柱和內部支點維持同高。各色帶端頭前後錯開。')
        side_walls(b,x,z,w,d,y,k)
        # Small piers integrated with the deck. The only interior elements are
        # regular, anonymous load paths for the brick-built roof.
        for xx,zz in piers:b.put('3003','L',xx,zz,y)
        for xx,zz in extra_piers:b.put('3005','L',xx,zz,y)
        if screen_from:
            b.area('brick',['L','W','D','L','L'][k%5],x,front-1,y,screen_from,1)
        for post in (left,right):
            b.area('brick','D',post,front-1,y,3,1)
            if is_front and post==right and k in (height-3,height-2):
                # The badge belongs to the side facing the street, as in the
                # photograph. It is printed on a single two-brick-high element.
                if k==height-3:
                    b.put('3245c','D',post+2,front,y,1)
                    logo(b,'前棟臨街右端柱・轉角側面的晶圓徽章',14,'right')
            else:
                b.area('brick','D',post+2,front,y,1,2)
            b.put('3005','R' if post==right else 'L',post+1,front,y)
            b.put('3005','L',post,front,y)
        b.step(f'{title}・第 {k+1} 道植生遮陽屏',
               '金綠色薄葉伸出玻璃與灰柱前方，分跨留出窄縫。注意相鄰一排的板縫錯開，最上部轉為深色帶。')
        a=left+3
        if k<2:
            b.area('brick','D' if k==0 else 'L',a,front-1,y,screen_len,1)
            if k==0:
                for xx in range(a,right,4):
                    if xx+2<=right:
                        b.put('3004','L',xx,front,y)
            if k==1:
                for xx in range(a,right,4):
                    if xx+2<=right:
                        b.put('2412b','D',xx,front,y)
        else:
            top_band=k>=height-2
            for pos in range(0,screen_len,4):
                n=min(4,screen_len-pos);xx=a+pos
                # Backing ply, stud-connected cantilever, and the slim front lip
                # are three separate heights; daylight is visible below each lip.
                c='A' if top_band else ('N' if k in (4,8) else 'V')
                backing='D' if top_band else ('F' if k%3==0 else 'V')
                for h in (y,y+1):
                    b.area('plate',backing,xx,front-1,h,n,1)
                b.area('plate',c,xx,front-1,y+2,n,2)
    y=2+height*3
    b.bag(title+'・金屬屋頂')
    b.step(title+'・交錯封頂與覆板','在牆及支點上鋪大板。兩排屋架之間的板縫交錯，最後連上正面深色帶和兩端端柱。')
    # Plan the structural panels by anchoring each along a wall or one of the
    # pier columns. Their intermediate seams also carry the upper face layer.
    b.current['pieces'].extend(roof_panels)
    b.area('plate','L',left,front,y,w-screen_from,1)
    for pos in (left+2,right+2):b.put('3024','D',pos,front+1,y)
    if not is_front:
        b.step('後棟端牆徽章與屋頂帽簷','兩側徽章分開裝在各自端牆。向前的紅色晶圓標位於直立柱的白灰帽簷下面。')
        b.put('3245c','L',right,front,y+1)
        logo(b,'後棟金綠外屏右端灰柱頂部',14)
    b.step(title+'・女兒牆與金屬直立縫','沿灰白端牆扣入窄邊板，屋面分隔成幾道縱向長槽，留出檢修走道。')
    parapet=rect(x,z,w,1)|rect(x,z+1,1,d-2)|rect(x+w-1,z+1,1,d-2)|rect(x,front-1,w,1)
    cover(b,'plate','W',parapet,y+1)
    cover(b,'tile','L',parapet,y+2)
    # The large white roof galleries, shaded slots between them, the paired
    # end grilles and the raised small cylindrical terminals are visible in the
    # public aerial; the models' number and spacing are compressed.
    inside=rect(x+1,z+1,w-2,d-3)
    used=set()
    for lane,zz in enumerate(range(z+3,front-4,6)):
        start=x+3+(0 if lane%2==0 else 2); end=x+w-4-(1 if lane%2 else 0)
        cells=rect(start,zz,end-start,3);used|=cells
        b.step(f'{title}・屋頂第 {lane+1} 條淺色長箱',
               '分段搭出照片可見的淺色長箱，灰格柵向走道，白色帽板覆在頂上。端部留一格深色分縫。')
        for pos in range(start,end,6):
            n=min(6,end-pos)
            b.area('brick','L',pos,zz,y+1,n,3)
            b.area('plate','W',pos,zz,y+4,n,3)
            if n>=4:
                b.put('2412b','L',pos,zz,y+5)
                b.put('2412b','L',pos+2,zz,y+5)
                if n>4:b.area('tile','W',pos+4,zz,y+5,n-4,1)
            else:b.area('tile','W',pos,zz,y+5,n,1)
            b.area('tile','W',pos,zz+1,y+5,n,2)
    b.step(title+'・屋面金屬板與管帽','平頂按屋架走向鋪設分縫光面板，幾處可見的小圓管分別扣在支座上。')
    terminals=[]
    for i,xx in enumerate(range(x+4,x+w-5,8)):
        terminals.append((xx,front-4,3+(i%3==0)*3))
        if i%2==0:terminals.append((xx+2,front-4,3))
    # A second line of smaller upstands sits between the two light roof boxes.
    for xx in range(x+7,x+w-7,10):terminals.append((xx,z+7,3))
    caps={(xx,zz) for xx,zz,h in terminals}
    for xx,zz,h in terminals:
        for dy in range(0,h,3):b.put('3062b','L',xx,zz,y+1+dy)
        b.put('85861','W',xx,zz,y+1+h)
    cover(b,'tile','L',inside-used-caps,y+1)



def office_shape(floor):
    # The planted podium projects six studs ahead of the short wing at its
    # second storey. The long wing has its own four-storey garden terrace.
    short_end=47 if floor<2 else 41
    bottom=30 if floor<4 else 27
    body=rect(55,23,36,12)|rect(55,23,12,short_end-23)
    body-=rect(87,bottom+4,4,max(0,35-bottom-4))
    body-=rect(63,short_end-3,4,3)
    # The inner elbow follows a quadrant tangent to both straight wings.
    for x in range(66,77):
        for z in range(35,44):
            if hypot(x+.5-76,z+.5-44)>=9:body.add((x,z))
    body-=rect(63,short_end,4,3)
    if floor<4:
        body|=rect(72,35,19,3)
        body|=rect(91,27,4,3)
        body|=rect(87,bottom+4,4,4)
    sectors=[(91,23,3),(91,bottom,0),(55,short_end,1),(59,short_end,0)]
    return body,sectors


def office(b):
    b.bag('五期辦公棟・八層水平窗帶')
    def sector_cells(sectors):
        return set().union(*(local_cells(dict(part='30565',x=x,z=z,r=r)) for x,z,r in sectors))
    def sectors_at(sectors,y,color):
        for x,z,r in sectors:b.put('30565',color,x,z,y,r)
    plans=[]
    for floor in range(8):
        body,sectors=office_shape(floor)
        rim={p for p in body if any((p[0]+dx,p[1]+dz) not in body for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)))}
        bearing=rim|{(x,z) for x,z in body if x%8==2 and z%5==0}
        plans.append((body,sectors,rim,bearing))
    # Each terrace is a continuous slab underneath the next wing, preventing
    # unsupported glazing at the retreating wall and holding the projected lip.
    decks={}
    saved=b.current
    for f in (1,3,7):
        body,_,_,bearing=plans[f];b.current={'pieces':[]}
        cover(b,'plate','L',body,5+4*f,f%2)
        decks[f]=b.current['pieces']
        for panel in decks[f]:
            footprint=local_cells(panel)
            if not footprint&bearing:
                cells=sorted(footprint);bearing.add(cells[len(cells)//2])
    b.current=saved
    # Carry every upper pier onto the slab or wall below at repeated storeys.
    for f in range(6,-1,-1):
        upper=plans[f+1][3]&plans[f][0]
        plans[f][3].update(upper)
    for floor,(body,sectors,edge,bearing) in enumerate(plans):
        y=2+4*floor;full=body|sector_cells(sectors)
        # Avoid exposed ends of crossing walls wherever a semicircle meets
        # the cap; the corresponding silhouette is genuinely round plastic.
        visible={(x,z) for x,z in edge if any((x+dx,z+dz) not in full for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)))}
        b.step(f'辦公棟第 {floor+1} 層・深色玻璃與圓端',
               '以一層深色細窗繞過面向綠庭的兩翼。長翼與短翼各以兩片真實四分之一圓件組成鼻端。')
        # Dark recessed ribbon of real transparent smoke and sand-blue
        # modular panes. All storeys share the multi-faceted inner elbow.
        for z in sorted({z for _,z in visible}):
            line=sorted(x for x,zz in visible if zz==z)
            for _,chunk in groupby(enumerate(line),lambda v:v[1]-v[0]):
                run=[x for _,x in chunk]
                if len(run)==1:b.put('3024','S',run[0],z,y)
                else:
                    for pos in range(0,len(run),4):
                        n=min(4,len(run)-pos)
                        c='B' if (pos//4+z)%4==0 else 'S'
                        b.area('plate',c,run[pos],z,y,n,1)
        cover(b,'brick','L',bearing-visible,y,floor%2)
        sectors_at(sectors,y,'B')
        b.step(f'辦公棟第 {floor+1} 層・沙綠遮陽與連續壓邊',
               '沙綠與淺灰色細帶沿窗頂伸展至轉角。入口兩側的樓板在第二層和第四層分別退入，留下屋頂花園。')
        cover(b,'plate','J',visible,y+1,floor%2)
        cover(b,'plate','L',visible,y+2,not floor%2)
        sectors_at(sectors,y+1,'L');sectors_at(sectors,y+2,'L')
        if floor in decks:b.current['pieces'].extend(decks[floor])
        else:cover(b,'plate','L',bearing,y+3,not floor%2)
        sectors_at(sectors,y+3,'L')
        if floor in (1,3):
            b.step('短翼低層屋頂草坪' if floor==1 else '長翼四樓花園露臺',
                   '在退進前後的樓牆之間鋪設草坪。深淺兩條窄板壓住邊緣；往上疊時保持花園外沿露出。')
            above,above_ends,_,_=plans[floor+1]
            terrace=full-above-sector_cells(above_ends)
            # Keep the tiles over real upper studs at the curved extremities.
            stand=set().union(*(local_cells(dict(part='30565',x=x,z=z,r=r),'studs') for x,z,r in sectors))
            terrace&=body|stand
            cover(b,'tile','F',terrace,y+4)
    body,sectors,_,_=plans[-1];y=34
    b.step('太陽能屋面與圓角壓頂','長短兩翼各有一組深藍光電板。窄灰框從光電板邊緣延伸至端部，弧形印證窗帶的轉向。')
    panels=rect(60,25,24,3)|rect(57,31,4,7)
    locks=rect(89,25,4,2)|rect(58,39,2,4)
    cover(b,'tile','L',body-panels-locks,y)
    for xx,zz,r in ((89,25,0),(58,39,1)):
        b.put('3020','L',xx,zz,y,r)
        b.put('87079','L',xx,zz,y+1,r)
    for x,z,w,d in ((60,25,24,3),(57,31,4,7)):
        for zz in range(z,z+d):
            for xx in range(x,x+w,4):
                b.area('tile','A' if zz%4 else 'B',xx,zz,y,min(4,x+w-xx),1)
    for x,z,r in sectors:b.put('27507','L',x,z,y,r)


def landscape(b):
    b.bag('臨街彎道、入口與近自然林帶')
    # Recurring setbacks in the street-front green edge and a curve of water
    # toward the L-shaped inward-facing facade belong to the exterior vignette.
    b.step('入口短雨簷與玻璃門框','沿辦公翼凹角的內牆排玻璃門，兩側圓柱支承淺簷，前方留出通往綠庭的步道。')
    for x in (74,83):
        for h in (2,5):b.put('3062b','L',x,40,h)
    for x in range(73,85,2):
        b.put('60592','L',x,38,2)
    for x in range(73,85,2):
        b.put('3021','D',x,38,8,1)
        b.put('3021','L',x,38,9,1)
    b.area('tile','L',73,38,10,12,3)
    b.step('前棟街緣條形花台與前廊','高架屏底下留一排灰色騎樓柱。多層花台的沙色擋土緣與深綠矮植栽朝向街道。')
    for x in range(9,49,4):
        b.put('3005','L',x,50,2)
    for x in range(8,48,4):
        b.put('3020','D',x,49,5)
        b.put('87079','L',x,49,6)
    for x,z,w,d in ((5,53,42,2),(6,56,34,2),(15,59,21,2)):
        b.area('plate','N',x,z,2,w,d)
        b.area('plate','F',x,z,3,w,d)
        for xx in range(x+1,x+w-1,3):
            b.put('32607','G' if xx%2 else 'F',xx,z,4)
    b.step('臨街入口的晶圓標誌','將晶圓徽章貼在灰色立磚的正面，和兩側花台對齊。此展示字牌用來辨認模型。')
    b.put('3245c','L',46,55,2)
    logo(b,'前庭的展示銘柱',14)
    b.step('入口彎道、路肩與穿越線','由前方道路向右側沿弧線轉入。先鋪深灰路面，再將短白線放到留出的格位。彎道與辦公樓庭園之間留出草坡。')
    road=rect(1,61,102,3)
    for x in range(48,103):
        mid=42+21*((102-x)/54)**2
        for z in range(max(2,round(mid)-2),min(64,round(mid)+3)):road.add((x,z))
    white={(x,z) for x,z in road if (48<=x<56 and x%2==0 and z>=61)
           or (x>56 and z==round(42+21*((102-x)/54)**2) and x%8<3)}
    shoulders={(x+dx,z+dz) for x,z in road for dx,dz in ((0,-1),(0,1),(1,0),(-1,0)) if 0<=x+dx<104 and 0<=z+dz<64}-road
    reserved=set()
    for phase in b.info['bags']:
        for step in phase['steps']:
            for piece in step['pieces']:
                if piece['y']>=2:reserved|=local_cells(piece)
    road-=reserved;white&=road;shoulders-=reserved
    cover(b,'tile','D',road-white,2)
    cover(b,'tile','W',white,2)
    cover(b,'tile','L',shoulders,2)
    b.step('入口前庭草坡與外側斜坡林帶','鋪上由照片中道路分開的兩片綠地。近牆的一側退讓給入口雨簷，外側綠地沿臨街道路收窄。')
    meadow={(x,z) for x in range(4,102) for z in range(38,61)
            if ((x-78)/19)**2+((z-47)/7.3)**2<1 or
            (x>60 and z>46 and z>59-.25*(x-60)) or
            (x<50 and (x-26)**2/24**2+(z-58)**2/3**2<1)}
    meadow-=road|shoulders|reserved
    cover(b,'plate','F',meadow,2)
    b.step('近自然林帶、小喬木與灌叢','在兩側植栽帶安排高低交錯的樹冠，前庭草坡使用較低的灌木，讓兩道退台和入口仍可看見。')
    trees=[(3,z) for z in (6,13,20,27,35,43)]+[(99,z) for z in (5,12,20,28,35,54,59)]
    trees.extend([(9,57),(18,58),(26,56),(32,58),(41,54),(47,58),(65,48),(72,46),
                  (80,43),(88,41),(70,54),(78,58),(84,55),(92,58),(95,49)])
    planted=set()
    for i,(x,z) in enumerate(trees):
        canopy=rect(x-1,z-1,4,4)
        if canopy & (road|reserved):continue
        is_lawn=(x,z) in meadow
        if not is_lawn:
            b.put('4073','G',x,z,2)
        h=3
        b.put('3062b','O',x,z,h)
        if i%3==0:
            b.put('3062b','O',x,z,h+3);h+=3
        b.put('60474','F',x-1,z-1,h+3)
        b.put('4032a','G',x,z,h+4)
        b.put('4073','G',x+1,z+1,h+5)
        b.put('32607','G',x,z,h+5)
        planted|=canopy
    for x,z in sorted(meadow-planted):
        if (x*17+z*3)%32==0:
            b.put('32607','G',x,z,3)


def finish(b,goal=6000):
    b.pave('L')
    steps=b.info['bags'][-1]['steps'];paving=steps.pop()
    zones=defaultdict(list)
    for p in paving['pieces']:zones[p['z']//16,p['x']//26].append(p)
    for (row,col),pieces in sorted(zones.items()):
        b.step(f'鋪面・第 {row+1} 列第 {col+1} 區','依照定位圖從後向前鋪設光面步道。窄石板在牆腳收邊，入口前保留路緣和樹穴。')
        b.current['pieces'].extend(pieces)
    phases=b.info['bags'];extra=goal-count(b)
    if extra<0:
        raise ValueError(f'Fab 15B has {-extra} excess pieces')
    # Preserve the outlines and heights, varying the joints between real
    # courtyard pavers to match the piece budget. Use only identical-colour tiles.
    allsteps=[s for phase in phases for s in phase['steps']]
    for step in reversed(allsteps):
        if not extra:break
        if not ('鋪面' in step['name'] or '金屬板與管帽' in step['name']):continue
        seq=[]
        for p in step['pieces']:
            sp=parts[p['part']]
            if sp['shape']!='tile' or p['color'] not in stock['3070b'] or extra==0:
                seq.append(p);continue
            w,d=(sp['d'],sp['w']) if p['r']%2 else (sp['w'],sp['d'])
            if w*d==1:seq.append(p);continue
            if w*d-1<=extra:
                seq.extend(dict(part='3070b',color=p['color'],x=x,z=z,y=p['y'],r=0)
                           for z in range(p['z'],p['z']+d) for x in range(p['x'],p['x']+w))
                extra-=w*d-1
            else:seq.append(p)
        step['pieces']=seq
    if extra:raise ValueError(f'Fab 15B needs {extra} extra pieces')
    steps=[]
    for phase in phases:
        for s in phase['steps']:
            total=(len(s['pieces'])+7)//8
            for n in range(total):
                name=s['name']+(f'（{n+1}/{total}）' if total>1 else '')
                steps.append((phase['name'],dict(name=name,hint=s['hint'],pieces=s['pieces'][8*n:8*n+8])))
    bags=[];start=done=0
    for i in range(12):
        end=start
        while end<len(steps) and (i==11 or done<500*(i+1)):
            done+=len(steps[end][1]['pieces']);end+=1
        bags.append(dict(name=steps[start][0],steps=[v for _,v in steps[start:end]]))
        start=end
    titles=['底座與前棟柱腳','前棟低牆、金綠植生屏','前棟臨街端柱與頂帶',
            '前棟白色屋面與後棟柱腳','後棟分段金屬板與深色窗縫','後棟外屏與屋頂格柵',
            '後棟管帽與辦公裙房','短翼草坪、辦公窗帶與長翼露臺','高層辦公翼與弧形窗端',
            '辦公棟光電板與入口綠庭','街道、綠坡與近自然林帶','園區步道與臨街鋪面']
    for bag,title in zip(bags,titles):bag['name']=title
    b.info['bags']=bags
    return b.info


def fab15b6000(Building):
    b=Building('fab15b6000','TF 02','台積電晶圓十五 B 廠・五期辦公棟','TSMC Fab 15B & Phase 5 Office',
               '從街口看，兩組寬大的金綠屏錯開，前棟灰白的條帶側牆延伸到較低的八層辦公翼。兩翼圓端與入口雨簷面向綠庭，庭前以彎道和複層綠地銜接道路，下層兩處綠化露臺分別朝短翼與長翼伸出。',104,64,[.66,.58,1.40],
               ['前後兩棟的金綠懸挑遮陽片、深色頂帶與端柱徽章','八層 L 形辦公翼、半圓窗端與凹入入口','屋頂縱向長槽、成列管帽與前庭林帶'],'台積電、臺灣綠建築發展協會')
    building_views(b,'金綠外屏上下分層，左右直立端柱夾住挑出的窄葉。前廊和三層植栽帶沿街道退進。',
                   '兩座廠房的灰白層帶在側面延伸。八層辦公翼比主廠房低，圓弧端頭的窗帶朝向前庭。',
                   '前後廠房錯開，露出兩道金綠屏。辦公棟兩翼折成 L 形，圍合臨街入口的綠庭。')
    b.info['views'] += [
        dict(id='louvers',name='金綠遮陽屏',direction=[.30,.28,1.4],region=[6,53,43,50,6,43],note='金綠色窄葉在深色背板前逐層挑出，兩端灰柱與紅細線包住屏面。'),
        dict(id='ribbon',name='八層圓角窗帶',direction=[.65,.45,1.2],region=[52,97,23,47,2,37],note='沙綠色遮陽帶夾著煙色細窗；短翼與長翼的植栽露臺高低錯開，向內轉折處連到綠庭。'),
        dict(id='roofline',name='兩棟屋面',direction=[-.22,1.4,.85],region=[4,98,4,45,34,48],note='從斜上方看，前後廠房的長條白箱、格柵、管帽與屋面分縫各自排列。')]
    b.foundation('D','L')
    hall(b,6,23,46,25,0,'前棟',True)
    hall(b,20,3,76,17,46,'後棟',False)
    office(b)
    landscape(b)
    return finish(b)

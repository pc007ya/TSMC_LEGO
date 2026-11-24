"""Stud-built National Taichung Theater. Coordinates follow the audience facing the front plaza."""
from collections import defaultdict
from itertools import groupby
from math import atan2, cos, degrees, hypot, pi, sin

from industrial_models import building_views, decal
from design import grid_buckets, local_cells, parts, stock, world_cell


def rectangle(x, z, w, d):
    return {(i, j) for i in range(x, x+w) for j in range(z, z+d)}


def cover(b,shape,color,cells,y,across=False):
    """Fit the largest stocked rectangle anchored at each exposed corner."""
    remaining=set(cells)
    choices=[]
    for part,spec in parts.items():
        if spec['shape']!=shape or color not in stock[part]:
            continue
        for r in range(1+(spec['w']!=spec['d'])):
            w,d=(spec['d'],spec['w']) if r else (spec['w'],spec['d'])
            choices.append((w*d,min(w,d),d if across else w,part,r,w,d))
    choices.sort(reverse=True)
    for x,z in sorted(cells,key=lambda v:(v[0],v[1]) if across else (v[1],v[0])):
        if (x,z) not in remaining:continue
        for _,__,___,part,r,w,d in choices:
            footprint=rectangle(x,z,w,d)
            if footprint<=remaining:
                b.put(part,color,x,z,y,r)
                remaining-=footprint
                break


def foundation(b):
    b.bag('錯縫展示基座')
    for y,color,offset in ((0,'D',0),(1,'L',4)):
        b.step('下層底板' if not y else '交錯鎖底',
               '把大底板平放、邊緣對齊。上層的接縫橫向與縱向各錯開四格，跨接四片下板。')
        for zz in range(-offset,76,8):
            for xx in range(-offset,102,8):
                x,z=max(0,xx),max(0,zz)
                b.area('plate',color,x,z,y,min(102,xx+8)-x,min(76,zz+8)-z)


def bands(b, spans, y, side=False):
    for color, group in groupby(enumerate(spans), key=lambda v: v[1]):
        cells = [index for index, _ in group]
        if color is None:
            continue
        pos = cells[0]
        while pos <= cells[-1]:
            glass = color in ('S', 'T')
            n = min(2 if glass else 8, cells[-1] - pos + 1)
            x,z = (12, 10+pos) if side else (12+pos, 9)
            if glass and n == 2:
                b.put('3065', color, x,z,y, int(side))
            else:
                b.area('brick', color,x,z,y, 1 if side else n,n if side else 1)
            pos += n


def secondary_shell(b):
    b.bag('後門與戶外小劇場曲牆')
    walls=[]
    for side, length, centers in ((False,71,(17,49)),(True,42,(25,))):
        levels=[]
        for course in range(20):
            t=(course+.5)/20
            width=3.0+4.5*(.5+.5*cos((t-.82)*pi*2))**2+2.7*max(0,1-t*5)
            strip=[]
            for i in range(length):
                offset=min(abs(i-c-1.4*sin(t*2*pi)) for c in centers)
                color='W'
                if offset<width:
                    color='B' if course in (3,10,16) else ('T' if 2<i%9<5 else 'S')
                elif offset<width+1.3:color='L'
                if side and i>=39 and course>=16:color=None
                strip.append(color)
            levels.append(strip)
        walls.append(levels)
    for course in range(20):
        y=2+3*course
        b.step(f'第 {course+1} 層 · 惠民路後門與側門',
               '先拼後門的淺色殼體與兩處深玻璃，再沿戶外劇場接側牆。大牆板分跨豎立，小窗的形狀逐層變化。')
        for side,levels in enumerate(walls):
            row=levels[course]
            if course<=15 and 'W' in stock['59349']:
                for i in range(len(row)-5):
                    if all(levels[k][u]=='W' for k in range(course,course+5) for u in range(i,i+6)):
                        for k in range(course,course+5):
                            levels[k][i:i+6]=[None]*6
                        x,z=(12,10+i) if side else (12+i,9)
                        b.put('59349','W',x,z,y,side)
            if course<19:
                for i in range(0,len(row)-1,2):
                    if i%6==4:continue
                    if all(levels[k][u] in ('S','T') for k in (course,course+1) for u in (i,i+1)):
                        for k in (course,course+1):
                            levels[k][i:i+2]=[None,None]
                        x,z=(12,10+i) if side else (12+i,9)
                        b.put('60592','L',x,z,y,side)
            bands(b,row,y,bool(side))


def grand_coordinates(x,z):
    # Normal to the stage lip, and the transverse distance from its centreline.
    return ((x-66)*.80+(z-36)*.60, -(x-66)*.60+(z-36)*.80)


def theater(b,grand):
    title='大劇院' if grand else '中劇院'
    color='R' if grand else 'U'
    b.bag(title+'的舞臺與觀眾席')
    field=rectangle(44,15,38,34) if grand else rectangle(17,15,24,33)
    step_sets=defaultdict(set); stage=set()
    for x,z in field:
        u,v=grand_coordinates(x+.5,z+.5) if grand else (31-(z+.5),x+.5-29)
        # The two wings of each curved row swing slightly toward the stage.
        dist=-u+(v*v)/(74 if grand else 55)
        if 1<u<=8 and abs(v)<= (10 if grand else 7):
            stage.add((x,z))
        rows=7 if grand else 5
        if 0<=dist<rows*2 and abs(v)<= (7 if grand else 4.4)+dist*.28:
            step_sets[int(dist/2)].add((x,z))
    wings=[(73,29),(64,41)] if grand else [(21,28),(36,28)]
    base=set.union(stage,*step_sets.values(),wings)
    b.step(title+' · 底層基座與舞臺口','先把觀眾席與舞臺的輪廓安在底座，保留舞臺兩側的出入口。')
    cover(b,'brick','D',base,2)
    cover(b,'plate','D',base,5,True)
    b.step(title+' · 舞臺地板與鏡框','舞臺使用暖木色地面。面向觀眾的一側留空，兩邊裝深色框架。')
    cover(b,'tile','N',stage-set(wings),6)
    for x,z in wings:b.put('3024','K',x,z,6)
    for lo in range(2,max(step_sets)+1,2):
        y=6+3*(lo//2-1)
        b.step(f'{title} · 後排階梯支承 {lo//2}','用跨排的厚磚連接後方座席，從低到高逐層縮小平面，使每排底座一起咬合。')
        upper=set.union(*(v for i,v in step_sets.items() if i>=lo))
        cover(b,'brick','D',upper,y,lo%4==0)
    for row,cells in sorted(step_sets.items()):
        b.step(f'{title} · 弧形座席第 {row+1} 排','先墊高本排，再沿弧形邊緣裝入觀眾席；深色分段是入座通道。')
        y=6+3*(row//2)
        if row%2:
            cover(b,'plate','D',cells,y);y+=1
        cover(b,'plate','D',cells,y)
        for x,z in sorted(cells):
            u,v=grand_coordinates(x+.5,z+.5) if grand else (31-(z+.5),x+.5-29)
            if (x+z)%2==0 and abs(abs(v)-(4.6 if grand else 2.7))>1.05:
                b.put('3005',color,x,z,y+1)
    b.step(title+' · 環抱觀眾席的曲牆與包廂緣','先在觀眾席後沿圍起弧面，再往舞臺側翼延伸；淺木色扶手從後排延續到兩側包廂。')
    occupied=set.union(*step_sets.values(),stage,wings)
    surroundings={(x+dx,z+dz) for x,z in set.union(*step_sets.values()) for dx,dz in ((1,0),(-1,0),(0,1),(0,-1))}
    shell=set()
    for x,z in surroundings-occupied:
        u,v=grand_coordinates(x+.5,z+.5) if grand else (31-(z+.5),x+.5-29)
        if u<-.2 and 15<=x<=80 and 14<=z<=47:shell.add((x,z))
    for yy in (2,5,8,11,14):
        cover(b,'brick',color if yy>=8 else 'D',shell,yy)
    cover(b,'tile','N',shell,17)
    b.step(title+' · 舞臺鏡框與橫向燈橋','在兩根黑色側柱上扣緊十六格橫梁。燈橋底下保持開放，面朝木色演出區的一面保留黑色舞臺口。')
    for x,z in wings:
        for y in (7,10,13,16,19):b.put('3062b','K',x,z,y)
    x,z=wings[0]
    b.put('4282','K',x,z,22)
    if grand:
        b.current['pieces'][-1]['pivotAt']=dict(label='大劇院臺口燈橋',x=x+.5,z=z+.5,degrees=degrees(atan2(4,-3)))


SPINES=(14,22,30,38,46,54,62,70,78,81)


def roof_frame(b):
    b.bag('大跨距屋架與橫向鎖板')
    # All posts stand behind or in front of both auditoria; the public cutaway
    # can expose the seats without a forest of internal support columns.
    for level,(part,y) in enumerate((('59349',2),('59349',17),('59349',32),('3245c',47),('3004',53))):
        b.step(f'前後寬壁柱第 {level+1} 節','前後兩列柱頭隱在外牆後。用寬牆板把屋架壓力分散到底座，使兩個觀眾區維持淨空。')
        for x in SPINES[:-2]:
            for z in (12,48 if x==62 else 46):
                xx=x-2 if z==48 and part=='59349' else x
                b.put(part,'N' if part=='59349' else 'L',xx,z,y)
    for level in range(9):
        b.step(f'轉角支座第 {level+1} 節','兩端柱列較窄，柱頭在凹入的外牆之後。')
        for x in SPINES[-2:]:
            for z in (12,46):b.put('3245c','L',x,z,2+level*6)
    b.step('深梁下弦 · 前後伸臂','十道屋架各從兩端往跨中拼。把十六格長板扣在前後柱頭。')
    for x in SPINES:
        b.put('4282','L',x,10,56,1)
        if x in (14,70,81):
            b.put('4282','L',x,33 if x!=70 else 34,56,1)
        else:b.put('4282','L',x,36,56,1)
    b.step('深梁中弦 · 交錯十六格長梁','中層接頭轉到跨中，前後兩片長板分別壓住下弦八格以上。')
    for x in SPINES:
        end=49 if x in (14,81) else 50 if x==70 else 52
        for z,d in ((10,6),(16,16),(32,16),(48,end-48)):
            if d==16:b.put('4282','L',x,z,57,1)
            else:b.area('plate','L',x,z,57,2,d)
    b.step('深梁上弦 · 中央跨縫','將中央的十六格板橫過中層接頭，再鎖住其餘端段。')
    for x in SPINES:
        end=49 if x in (14,81) else 50 if x==70 else 52
        for z,d in ((10,14),(24,16),(40,end-40)):
            if d==16:b.put('4282','L',x,z,58,1)
            else:b.area('plate','L',x,z,58,2,d)
    b.step('上弦加厚與屋板支座','每一段厚梁都壓在交錯長板上；前後兩端拉回到低矮轉角的內側。')
    for x in SPINES:
        b.area('brick','L',x,10,59,2,39 if x in (14,81) else 40 if x==70 else 42)


def corner_cowls(b):
    """Bridge into each low shoulder from the existing 46-plate front wall."""
    b.step('前庭兩角的低位曲面屋緣','六格寬的側牆在此向下彎。先把內挑白板扣在低位牆頂，再從後向前收成淺色斜面。')
    lower=rectangle(12,49,8,4)|rectangle(80,49,6,4)
    tops={}
    for group in b.info['bags']:
        for step in group['steps']:
            for p in step['pieces']:
                if p['x']>85 or p['z']>54 or p['z']+parts[p['part']]['w']+parts[p['part']]['d']<49:continue
                for k in local_cells(p)&lower:
                    tops[k]=max(tops.get(k,0),p['y']+parts[p['part']]['h'])
    for x in [*range(13,19),80,81,82]:
        b.put('3710','W',x,49,47,1)
        for z in range(49,53):tops[x,z]=48
    for z in (49,50,51):
        b.put('3023','W',18,z,48)
        tops[18,z]=tops[19,z]=49
    # At the outer two courses curved slopes blend the white shell into the
    # lower front lip; the actual low glazing in the neighbouring bay is exposed.
    for x in (12,14,16,80,82,84):
        b.put('15068','W',x,53,47)
    desired={}
    for (x,z),h in tops.items():
        if h<46 or (x,z)==(19,52):continue
        rise=max(0,x-15) if x<40 else max(0,82-x)
        desired[x,z]=min(62,47+2*rise+{49:11,50:7,51:4,52:1}[z])
    for y in range(47,62):
        for depth,kind in ((3,'brick'),(1,'plate')):
            cells={p for p,target in desired.items() if tops[p]==y and target>=y+depth}
            cover(b,kind,'W',cells,y)
            for p in cells:tops[p]+=depth
    for y in sorted(set(tops[p] for p in desired)):
        exposed={p for p in desired if tops[p]==y}
        cover(b,'tile','W',exposed,y)


def roof_deck(b):
    b.step('屋頂花園底板','橫向屋板與深梁垂直扣接，靠前兩角退縮，使正面曲牆的肩線能向下彎。')
    field=set()
    for z,d in [(i,4) for i in range(9,49,4)]+[(49,6)]:
        spans=[(12,4)]+[(i,8) for i in range(16,80,8)]+[(80,6)]
        if z==49:
            spans=[(20,4)]+[(i,8) for i in range(24,80,8)]
        for x,w in spans:
            b.area('plate','G',x,z,62,w,d)
            field.update(rectangle(x,z,w,d))
    return field


def stage_tower(b,small):
    title='中劇院後方臺塔' if small else '大劇院斜置臺塔'
    x,z,w,d=(22,22,16,10) if small else (60,29,18,14)
    y=63
    pivot=None if small else dict(label="大劇院斜臺塔",x=69.5,z=36.5,degrees=degrees(atan2(3,4)))
    footprint=rectangle(x,z,w,d)
    buffer=set(footprint)
    if pivot:
        # This 3:4:5 alignment mates all integer-aligned studs in the two grids.
        # Raised round supports clear the overhanging tubes from the fixed deck.
        buffer=set();studs=set()
        for i,j in footprint:
            cell=world_cell(b.info,dict(pivotAt=pivot),i,j)
            buffer.update(grid_buckets(cell))
            if abs(cell[0]-.5-round(cell[0]-.5))<1e-7 and abs(cell[1]-.5-round(cell[1]-.5))<1e-7:
                studs.add((round(cell[0]-.5),round(cell[1]-.5)))
        b.step('大劇院斜臺塔 · 三四五對位支座','在屋頂底板上安裝一格圓板，斜向底座的每五格正好對齊屋頂的四格橫距與三格縱距。')
        for i,j in sorted(studs):b.put('4073','D',i,j,y)
        y+=1
    b.step(title+' · 舞臺塔底盤','對準全部定位點才按下底板。大臺塔的長向斜穿屋面，小臺塔沿後方場館的長邊。')
    first=len(b.info['bags'][-1]['steps'])-1
    for zz in range(z,z+d,2):
        if small:b.area('plate','D',x,zz,y,w,2)
        else:
            for xx in range(x,x+w,6):b.put('3795','D',xx,zz,y)
    y+=1
    shell=footprint-rectangle(x+1,z+1,w-2,d-2)
    for n in range(2 if small else 5):
        b.step(f'{title} · 第 {n+1} 層牆板','沿塔身四面錯縫疊砌，再在裡面加上屋面支座。')
        b.ring('brick','D',x,z,y,w,d,swap=n%2==1)
        if n%2==0:
            post='3003' if not small and n==4 else '3245c'
            for xx in sorted({x+4,x+10,x+w-3}):
                for zz in range(z+3,z+d-2,4):b.put(post,'D',xx,zz,y)
        y+=3
    b.step(title+' · 深色收邊與淺灰機房','先連成一片淺灰色屋面。黑色窄邊內側有一個低矮機房上蓋。')
    for zz in range(z,z+d,2):b.area('plate','L',x,zz,y,w,2)
    y+=1
    lid=rectangle(x+w//2-3,z+d//2-2,8,4)
    cover(b,'tile','K',shell,y)
    cover(b,'tile','L',footprint-shell-lid,y)
    cover(b,'brick','D',lid,y)
    cover(b,'tile','L',lid,y+3)
    if pivot:
        for st in b.info['bags'][-1]['steps'][first:]:
            for p in st['pieces']:p['pivotAt']=pivot
    return buffer


def ring_mound(b,cx,cz,rx,rz,h,field):
    # Horizontal, offset contours reproduce the flared asymmetrical skirt.
    layers=[]
    eye_x=cx+.6;eye_z=cz-.5
    hole={(x,z) for x,z in field if ((x+.5-eye_x)/max(1.18,rx*.29))**2+((z+.5-eye_z)/max(.96,rz*.28))**2<=1}
    for level in range(h):
        t=level/(h-1)
        scale=.56+.44*(1-t)**1.8
        mx=cx+t*.6; mz=cz-t*.5
        shape={(x,z) for x,z in field if ((x+.5-mx)/(rx*scale))**2+((z+.5-mz)/(rz*scale))**2<=1}
        if layers:shape &= layers[-1]|hole
        layers.append(shape-hole)
    cover(b,'tile','D',hole,63)
    for n,cells in enumerate(layers):
        cover(b,'tile' if n==len(layers)-1 else 'plate','W',cells,63+n,bool(n%2))
    return layers[0]|hole


def distance_to_path(x,z,centers):
    ds=[]
    for (a,c),(d,f) in zip(centers,centers[1:]):
        ux=d-a;uz=f-c;t=max(0,min(1,((x-a)*ux+(z-c)*uz)/(ux*ux+uz*uz)))
        ds.append(hypot(x-a-ux*t,z-c-uz*t))
    return min(ds)


def sky_garden(b,field):
    b.bag('空中花園的曲牆頂與蜿蜒步道')
    garden=set(field)
    garden-=stage_tower(b,True)
    garden-=stage_tower(b,False)
    mounds=[(23,14,5.7,4.7,5),(46,13,4.6,4.2,6),(63,17,5,3.4,4),
            (16.4,29,4.4,4.4,5),(18,43,4.7,4,6),(39,39,4.4,3.4,5),
            (28,50,5.4,4,5),(45,51,3.8,3.5,4),(54,46,6.2,4.4,7),
            (81,19,4.2,4,6)]
    for i,p in enumerate(mounds,1):
        b.step(f'白色火山狀曲牆頂 {i}','先鋪孔底的深色光面板，再接白色外裙。往上逐層向偏心頂緣收束，中央孔口保持敞開。')
        garden-=ring_mound(b,*p,garden)
    paths=[[(12,36),(18,36),(20,33),(20,24),(23,21),(29,20),(36,20),(40,22),(41,27),(40,32),(39,34),(33,35),(30,37),(31,42),(35,45),(40,46),(44,43),(45,35),(48,32),(52,30),(54,26),(53,21),(49,18),(44,18),(41,20),(40,23)],
           [(44,44),(48,43),(51,41),(56,41),(62,45),(68,48),(74,48),(79,45),(82,40),(82,32),(79,27),(74,23),(68,22),(62,22),(58,23),(54,25)],
           [(48,32),(50,36),(54,39),(59,41)],[(36,45),(37,50),(39,54)]]
    paths_set=set();lawn=set();light=set()
    for x,z in garden:
        dist=min(distance_to_path(x+.5,z+.5,path) for path in paths)
        boundary=min(x-12,85-x,z-9,54-z)
        if dist<1.05 or boundary<1:paths_set.add((x,z))
        elif ((x-55)/7)**2+((z-24)/5)**2<1:
            light.add((x,z))
        else:lawn.add((x,z))
    b.step('蛇行白色步道與中央光庭','從兩個臺塔之間穿過，將步道分岔到火山狀量體的兩側，中央留一塊淺灰色的圓形平台。')
    cover(b,'tile','W',paths_set,63)
    cover(b,'tile','L',light,63)
    b.step('草丘與屋緣草坪','在白色路徑之間補平草坡。植栽和曲牆位置依屋頂平面縮編，保留兩座臺塔之間的開闊視線。')
    # The studded structural roof itself forms the low lawn. Raised borders
    # and olive planting beds follow the public paths around the stage towers.
    for x,z in sorted(lawn,key=lambda p:(p[1],p[0])):
        bed=rectangle(x,z,4,2)
        if x%5==1 and z%4==1 and bed<=lawn:
            b.put('3020','V',x,z,63)



def water_and_park(b):
    b.bag('噴泉廣場、酩酊溪與戶外劇場')
    tiles=defaultdict(set); planted=set()
    # Weave the narrow stream right round the public cave, separately from the fountain.
    river=[(76,55),(78,56.3),(82.4,57.4),(86.6,56.7),(89.3,54.3),(90.6,50),
           (90.1,44),(89.8,39),(91.4,34),(94,30),(94.5,25),(93,21),(90.5,18)]
    park=rectangle(1,1,100,74)-rectangle(12,9,75,47)
    amph={(x,z) for x,z in park if x<=11 and hypot(x-11.5,(z-31)*.82)<=10.35}
    plaque=rectangle(90,64,6,2)
    for x,z in park-amph-plaque:
        cx=x+.5;cz=z+.5
        radial=hypot(cx-60.5,cz-65.0)
        if radial<9.0:
            # Pale paving under daylight water, rings of fine inset jets.
            col='T' if 7.7<radial<8.45 or 4.6<radial<5.25 or radial<1.5 else 'B'
            tiles[col].add((x,z))
        elif distance_to_path(cx,cz,river)<1.18:
            tiles['T'].add((x,z))
        elif (((cx-91)/9)**2+((cz-39)/17)**2<1 or ((cx-10)/9)**2+((cz-53)/8)**2<1 or
              ((cx-25)/8)**2+((cz-67)/3.7)**2<1 or ((cx-91)/7)**2+((cz-58)/4)**2<1 or
              (cz<7 and cx<82 and cx>7)):
            planted.add((x,z))
        else:tiles['L'].add((x,z))
    for col,title in [('B','圓形噴泉池淺底'),('T','兩圈噴水孔與彎曲水道'),('L','廣場分縫石板')]:
        b.step(title,'主噴泉是獨立的圓盤。依座標區分廣場鋪面與水色磚，右側蜿蜒細渠從曲牆前方繞到草地後。')
        cover(b,'tile',col,tiles[col],2)
    b.step('草島、廣場側樹與公園帶','沿白色步道外側接上草地。把樹株放在植栽帶內，保留入口廣場中心的視線。')
    cover(b,'plate','G',planted,2)
    for x,z in [(6,51),(10,55),(22,67),(29,67),(94,42),(95,37),(95,24),(92,60),(16,4),(34,4),(52,3),(73,4)]:
        if (x,z) not in planted:continue
        b.put('3062b','O',x,z,3)
        b.put('3062b','O',x,z,6)
        b.put('4032a','F',x,z,9)
        b.put('4032a','G',x-1,z,10)
        b.put('4032a','F',x+1,z,10)
        b.put('32607','G',x,z+1,11)
        b.put('4073','G',x+2,z+1,11)
    b.step('半圓戶外劇場 · 草坡與同心坐階','戶外舞臺在左側曲牆腳下。草坡座席的弧線面朝開口，外圈比內圈更高。')
    cover(b,'plate','G',amph,2)
    for rank in range(1,5):
        arc={(x,z) for x,z in amph if hypot(x-11.5,(z-31)*.82)>=rank*1.95}
        cover(b,'plate','G' if rank%2 else 'L',arc,2+rank)
    b.step('廣場模型展示牌','將雙語標誌置於光滑面中央，再把展示牌固定在廣場外緣。這座銘牌是本模型專用的展示構件。')
    b.area('plate','D',90,64,2,6,2)
    b.put('59349','N',90,65,3)
    decal(b,'ntt-sign','廣場模型展示牌・臺中國家歌劇院雙語標誌',39.6,10)
    b.area('tile','D',90,64,3,6,1)


def finalize(b):
    # Procure smaller flat stones on public paving if needed, retaining every
    # volume, colour and bearing of the architectural assemblies.
    target=6000
    total=sum(len(s['pieces']) for g in b.info['bags'] for s in g['steps'])
    split={'87079':('3068b','3068b',2),'4162':('2431','2431',4),
           '6636':('63864','63864',3),'2431':('3069b','3069b',2),
           '63864':('3069b','3070b',2),'3068b':('3069b','3069b',1),
           '3069b':('3070b','3070b',1)}
    plazas=[s for g in b.info['bags'] for s in g['steps'] if s['name'] in ('廣場分縫石板','蛇行白色步道與中央光庭','圓形噴泉池淺底')]
    while total<target:
        previous=total
        for step in plazas:
            stones=[]
            for p in step['pieces']:
                pid=p['part']
                if total>=target or pid not in split:
                    stones.append(p);continue
                a,c,n=split[pid]
                along_x=(p['r']%2==0)!=(pid=='3068b')
                stones.extend((dict(p,part=a),dict(p,part=c,x=p['x']+(n if along_x else 0),z=p['z']+(0 if along_x else n))))
                total+=1
            step['pieces']=stones
        if total==previous:break
    if total!=target:
        raise ValueError(('National Taichung Theater edition quantity',total))
    steps=[]
    for phase in b.info['bags']:
        for step in phase['steps']:
            n=len(step['pieces'])
            for i in range(0,n,8):
                suffix=f'（{i//8+1}/{(n+7)//8}）' if n>8 else ''
                steps.append(dict(name=step['name']+suffix,hint=step['hint'],pieces=step['pieces'][i:i+8]))
    bag_names=('底座與大劇院階梯','紅廳與藍廳座席','舞臺與惠民路曲牆','後門與正面雙入口',
               '雙玻璃腰身與涵洞','正面曲牆肩部收邊','北側窗與帶孔曲牆','北側高窗與跨距屋架',
               '轉角曲面與雙臺塔','火山狀曲牆頂','空中花園與廣場噴泉','戶外劇場與展示牌')
    bags=[];pos=0;used=0
    for i,title in enumerate(bag_names):
        start=pos
        while pos<len(steps) and (used<500*(i+1) or i==11):
            used+=len(steps[pos]['pieces']);pos+=1
        bags.append(dict(name=title,steps=steps[start:pos]))
    b.info['bags']=bags
    return b.info


def opera6000(Building):
    from opera_facade import opera_facades
    b=Building('ntt6000','NT 01','臺中國家歌劇院・曲牆典藏版','National Taichung Theater',
               '從惠來路噴泉面向兩座壺形玻璃窗，右側是一道上窄下寬的內凹白色涵洞。繞到側面可見戶外劇場；屋頂走道穿過火山狀曲牆頂，剖視則能看見朝向不同的紅、藍兩座劇場。',
               102,76,[.40,.60,1.46],['兩座壺形玻璃與內凹涵洞','雙劇場階梯座席及斜置舞臺塔','空中花園、圓形噴泉與半圓戶外劇場'],
               '臺中國家歌劇院、臺中市政府觀光旅遊局、《建築師》雜誌')
    building_views(b,'惠來路正面左、中各有一座壺形玻璃窗，右側內凹涵洞連向地面水景。',
                   '由側面看，凹入的玻璃、圓潤肩線和廣場的水道繞向曲牆另一邊。',
                   '大劇院的深色臺塔斜放在屋頂右半部。兩座臺塔之間是白色步道與多組不同高度的曲牆頂。',1)
    b.info['views'] += [
        dict(id='bottles',name='壺形玻璃與涵洞',direction=[.08,.15,1],region=[13,85,46,55,3,63],note='左、中兩座玻璃向上、向下各自張開。右側沒有第三道整面玻璃，白色曲面轉進涵洞，底部開口接向廣場。'),
        dict(id='garden',name='空中花園',direction=[.34,2.8,1],region=[12,86,8,55,62,82],note='兩座臺塔一斜一正。低矮白色火山狀量體在草地中偏心收頂，白色園路繞過高臺與光庭。'),
        dict(id='plaza',name='噴泉與酩酊溪',direction=[.28,2,1],region=[40,98,43,75,0,15],note='圓形噴泉有獨立的同心孔帶。右方的細水道沿著內凹涵洞與側面綠島繞行。'),
        dict(id='auditorium',name='雙劇場剖視',direction=[.22,2.0,.79],region=[14,82,14,49,0,26],belowLayer=27,note='屋架上方暫時隱去。紅色大劇院的觀眾席斜向木色舞臺，左側中劇院以藍色階梯朝向後端。座排數量與通道依積木尺度縮編。'),
        dict(id='amphitheater',name='戶外劇場',direction=[-1.3,1,.15],region=[1,14,17,46,1,20],note='在側面草地，四層同心坐階由外向內降低，最後接到小劇場側牆腳下的開放舞臺。')]
    foundation(b)
    theater(b,True);theater(b,False)
    secondary_shell(b)
    opera_facades(b)
    roof_frame(b)
    corner_cowls(b)
    field=roof_deck(b)
    sky_garden(b,field)
    water_and_park(b)
    return finalize(b)

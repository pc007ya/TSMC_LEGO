"""Fab 25 P1 as it appeared in the Taichung City inspection photographs, 31 August 2026.

The photographs establish the exposed silhouette, deck edges, cranes and green foreground.
The regular model grid and mobile plant are scale interpretations for a working brick kit.
"""
from math import cos, sin
from design import parts, stock
from industrial_models import building_views, decal

X0, Z0, PITCH = 7, 11, 8
PLATE = {1:'3024', 2:'3023', 3:'3623', 4:'3710', 6:'3666', 8:'3460'}
TILE = {1:'3070b', 2:'3069b', 3:'63864', 4:'2431', 6:'6636', 8:'4162'}


def run(b, forms, color, x, z, y, length, along_z=False, module=8):
    """Linear strips have predictable joints and never extend beyond the layout."""
    while length:
        size=max(s for s in forms if s<=min(module,length) and color in stock[forms[s]])
        b.put(forms[size],color,x,z,y,int(along_z))
        length-=size
        if along_z:z+=size
        else:x+=size


def footprint(level):
    if level==0: return {(i,j) for i in range(9) for j in range(4)}
    if level==1: return {(i,j) for i in range(9) for j in range(4) if (i,j)!=(8,3)}
    if level==2: return {(i,j) for i in range(9) for j in range(4)
                          if (i<7 or j<3) and (i<8 or j<2)}
    return {(i,j) for i in range(7) for j in range(3) if i!=6 or j<2}


def members(bays):
    posts={(i+dx,j+dz) for i,j in bays for dx in (0,1) for dz in (0,1)}
    longs={(i,j+dz) for i,j in bays for dz in (0,1)}
    cross={(i+dx,j) for i,j in bays for dx in (0,1)}
    return sorted(posts,key=lambda p:p[::-1]), sorted(longs,key=lambda p:p[::-1]), sorted(cross,key=lambda p:p[::-1])


def node(i,j):
    return X0+i*PITCH, Z0+j*PITCH


def footings(b):
    b.bag('承台與地坪')
    nodes,_,_=members(footprint(0))
    for row in range(5):
        b.step(f'第 {row+1} 列混凝土承台與錨栓','將四格見方的承台扣在土面上。左右兩排外緣放錨栓，中央兩格保留給柱底板。')
        for i,j in nodes:
            if j!=row:continue
            x,z=node(i,j)
            b.put('3031','L',x-1,z-1,2)
            b.put('3022','D',x,z,3)
            for xx,zz in ((x-1,z-1),(x+2,z-1),(x-1,z+2),(x+2,z+2)):
                b.put('98138','L',xx,zz,3)
    b.step('地坪的澆置帶與收縮縫','由後方沿廠房長向鋪設淺灰色板。四邊露出承台，前方尚未澆置的開間保留沙色土面。')
    for j in range(4):
        for i in range(9):
            if j>=2 and i>=5:continue
            x,z=node(i,j)
            for zz in (z+3,z+5):
                b.put('87079','L',x+2,zz,2)
                b.put('3068b','L',x+6,zz,2)
            for xx in (x+3,x+5):
                b.put('3068b','D' if j==0 and xx==x+5 else 'L',xx,z+1,2)
                b.put('3068b','L',xx,z+7,2)


def lower_columns(b,level,posts,y):
    for row in sorted({j for _,j in posts}):
        b.step(f'第 {level+1} 層・柱列 {row+1} 的翼緣與接板','底層柱用雙翼扣在柱腳前後，往上各層使用較窄的前後向柱身。以方板作為柱身中段接板與頂端承板。')
        for i,j in posts:
            if j!=row:continue
            x,z=node(i,j)
            if level==0:
                for dz in (0,1):b.put('3004','O',x,z+dz,y)
                b.put('3022','O',x,z,y+3)
                b.put('3003','O',x,z,y+4)
            else:
                # The upper shaft is narrower than its splice and cap plates.
                b.put('3004','O',x+1,z,y,1)
                b.put('3022','O',x,z,y+3)
                b.put('3004','O',x+1,z,y+4,1)
            b.put('3022','O',x,z,y+7)


def girder_rows(b,level,posts,longs,cross,y):
    for j in sorted({j for _,j in posts}):
        row=sorted(i for i,k in longs if k==j)
        if not row:continue
        b.step(f'第 {level+1} 層・第 {j+1} 排主梁下翼緣','每支八格長梁的一端扣住左柱頭，另一端扣住右柱頭，兩端外側以一格短板補齊。')
        for i in row:
            x,z=node(i,j)
            b.put('3034','O',x+1,z,y)
        for i,k in ((min(row),0),(max(row)+1,1)):
            x,z=node(i,j);b.put('3023','O',x+k,z,y,1)
        b.step(f'第 {level+1} 層・主梁腹板與上翼緣 {j+1}','將較窄的腹板扣在底板中線一側，上層的雙格翼緣跨接腹板接頭，兩側留下工字鋼的退縫。')
        for i in row:
            x,z=node(i,j)
            b.put('3460','O',x+1,z,y+1)
        left,z=node(min(row),j);right,_=node(max(row)+1,j)
        for x in (left,right+1):b.put('3024','O',x,z,y+1)
        for x in range(left,right,8):
            b.put('3034','O',x,z,y+2)
        b.put('3022','O',right,z,y+2)
    for i in sorted({i for i,_ in posts}):
        line=sorted(j for h,j in cross if h==i)
        if not line:continue
        b.step(f'第 {level+1} 層・第 {i+1} 列橫接梁','將雙格橫梁依序扣上縱向翼緣。每片梁的兩端各跨一排，外側兩端以短板封住。')
        for j in line:
            x,z=node(i,j)
            b.put('3034','O',x,z+1,y+3,1)
        for j,k in ((min(line),0),(max(line)+1,1)):
            x,z=node(i,j);b.put('3023','O',x,z+k,y+3)


def deck_mode(level,i,j):
    if level==0:
        return 2 if i<7 or j<2 else 1
    if level==1:
        return 2 if i<5 or (i<8 and j<2) else (1 if (i+j)%2==0 else 0)
    if level==2:
        return 2 if (i<6 and j<2) or (i<3 and j==2) else (1 if i<7 and j<=2 else 0)
    return 2 if i<=3 and j<=1 else (1 if i<6 and j<2 else 0)


def floor_decks(b,level,bays,posts,y):
    for j in range(4):
        active=sorted(i for i,k in bays if k==j)
        if not active:continue
        b.step(f'第 {level+1} 層・進深 {j+1} 的細梁與開間','每跨以兩條單格板作為次梁；兩頭各搭在一塊主梁上。留空的開間可以向下看到交錯的柱網。')
        for i in active:
            x,z=node(i,j)
            for xx in (x+3,x+6):b.put('3460','D' if level<2 else 'O',xx,z+1,y+3,1)
        b.step(f'第 {level+1} 層・進深 {j+1} 的分片樓承板','每組板的兩處扣點分別落在下方次梁上。完整開間鋪四列，施工邊帶僅鋪後兩列，其餘保留井字開口。')
        for i in active:
            mode=deck_mode(level,i,j)
            if not mode:continue
            x,z=node(i,j)
            rows=4 if mode==2 else 2
            for r in range(rows):
                zz=z+1+2*r
                b.put('3795','L',x+2,zz,y+4)
            for xx in (x+1,x+8):
                run(b,PLATE,'L',xx,z+2,y+4,6 if mode==2 else 3,True)
            # Surface sheets overlap the central joint and expose ribbed steel at the advancing edge.
            for r in range(rows):
                zz=z+1+2*r
                if level==0 and mode==2:
                    for dz in (0,1):b.put('6636','L',x+2,zz+dz,y+5)
                    continue
                b.put('87079','L',x+3,zz,y+5)
                for xx in (x+2,x+7):
                    if mode==1 and r==1 or level>=2 and r==3:
                        b.put('2412b','L',xx,zz,y+5,1)
                    else:
                        b.put('3069b','L',xx,zz,y+5,1)
    b.step(f'第 {level+1} 層・柱頭封板','方形承板保持凸點向上，扣緊交叉的梁頭；下一層柱身將立在這組節點。')
    for i,j in posts:
        x,z=node(i,j)
        b.put('3022','O',x,z,y+4)
    b.step(f'第 {level+1} 層・邊跨斜桿','在突出樓板的那一面安裝成對的斜撐框與短連板。框面背後的淨空仍能看到下一排鋼柱。')
    for i in sorted({i for i,_ in bays}):
        j=max(k for h,k in bays if h==i)+1
        if (i+level)%3:continue
        x,z=node(i,j)
        for dx,r in ((2,2),(4,0)):b.put('3224','O',x+dx,z+1,y+3,r)
        b.put('3710','O',x+2,z+1,y+8)


def steel(b):
    for lv in range(4):
        bays=footprint(lv);posts,longs,cross=members(bays)
        b.bag(f'第 {lv+1} 層鋼架')
        y=4+13*lv
        lower_columns(b,lv,posts,y)
        girder_rows(b,lv,posts,longs,cross,y+8)
        floor_decks(b,lv,bays,posts,y+8)
    b.step('最上層錯落的待接柱頭','在裸露接柱的平台保留不等高的鋼柱。完整翼緣在下，短柱頂端只以一片接板收住。')
    for lv in (1,2,3):
        posts,_,_=members(footprint(lv))
        next_nodes=set(members(footprint(lv+1))[0]) if lv<3 else set()
        y=4+13*(lv+1)
        for i,j in posts:
            if (i,j) in next_nodes or (i+2*j)%3==1:continue
            x,z=node(i,j)
            h=2 if (i+j)%2==0 else 1
            for k in range(h):b.put('3004','O',x,z,y+k*3)
            b.put('3023','O',x,z,y+3*h)


def crawler(b,x,z,stages,body):
    """Each slanting stanchion steps the four top studs three studs toward the load."""
    b.step('履帶板與兩側行走裝置','將底架平放在地表，兩列深色履帶向前，外緣的肋紋排成輪帶；中間留出轉台位置。')
    for zz in (z,z+5):
        for xx in (x,x+4,x+8):
            b.put('3020','K',xx,zz,2)
            b.put('2877','D',xx,zz,3)
            b.put('2877','D',xx+2,zz,3)
            b.put('3010','K',xx,zz+1,3)
            b.put('3020','K',xx,zz,6)
    for xx in (x+3,x+7):b.put('3034','D',xx,z,7,1)
    b.put('3032','D',x+3,z+2,8)
    b.put('60474','D',x+4,z+2,9)
    b.put('3036',body,x+2,z+1,10)
    b.step('機房、玻璃駕駛室與後配重','在轉台後方疊配重塊。駕駛室有透明風擋，旁側的深灰色格柵為引擎散熱板。')
    rear=x+7
    for zz in (z+2,z+4):
        b.put('3021','L',rear,zz,11)
        b.put('3002','D',rear,zz,12)
        b.put('3021','L',rear,zz,15)
    cab=x+2
    b.put('3004',body,cab,z+5,11)
    b.put('3065','S',cab,z+5,14)
    b.put('3069b','W',cab,z+5,17)
    mid=x+5
    b.put('3003',body,mid,z+3,11)
    b.put('2412b','D',mid,z+3,14)
    b.put('2412b','D',mid,z+4,14)
    boom=x+2
    b.step('起重臂下的固定臂座','把寬臂座扣在平台一端。斜桁柱下方的四格底座鎖住固定臂座，較窄的上端朝向吊裝方向。')
    b.put('3020','R' if body=='R' else 'G',boom+1,z+1,11)
    color='W' if body=='R' else 'K'
    for stage in range(stages):
        b.step(f'連續斜桁臂・第 {stage+1} 節','斜桁柱的窄頂朝左，將下一節底部右半的兩排孔扣入下方全部四個凸點，兩面斜桿的延長線連續。')
        b.put('4476',color,boom-3*stage,z+1,12+stage*15)
    xx=boom-3*(stages-1)
    head=12+stages*15
    b.step('向前伸出的臂頭滑輪組','窄端的四個凸點共同承受雙格短臂。把兩顆有軸孔的滑輪座放在臂尖，紅白兩側夾板收住上緣。')
    b.put('3795',color,xx-4,z+1,head)
    for zz in (z+1,z+2):
        b.put('3700','L',xx-4,zz,head+1)
        b.put('3069b','R',xx-4,zz,head+4)
    b.put('2431',color,xx-2,z+1,head+1)


def crane_load(b):
    # The upper eye of the 192-LDU black whip ends against the underside of the boom head.
    # Between the steel load and its receiver there is a real clutch connection: the model
    # depicts the instant the girder has seated, so the apparent suspended load is supported.
    b.step('在接柱上就位的待卸吊梁','先延長臨時接柱，吊梁下翼緣扣在它的柱頭。把有孔的黑色吊耳配上紅色止擋，保留前方的索座。')
    for y in (50,53,56):b.put('3004','O',71,27,y)
    b.put('3795','O',68,27,59)
    b.put('3666','O',68,27,60)
    b.put('3795','O',68,27,61)
    b.put('3022','D',70,27,62)
    b.put('3700','K',70,28,63)
    b.put('3069b','R',70,28,66)
    b.step('臂頭下的直吊索','將黑色長桿的底座扣在吊梁索座，上端垂直對準稍後安裝的臂頭滑輪。吊梁靠接柱承重，可由上方向下組合。')
    b.put('2569','K',71,27,63)


def scaffolding(b):
    b.step('外牆施工架的成對底腳','在主要梁柱的外側排列臨時施工架。每一排的前後管柱保持一格間距，外排面向草坡。')
    for x in range(31,63,4):b.put('3020','D',x,46,2)
    b.put('3022','D',63,46,2)
    for row in range(4):
        y=3+7*row
        b.step(f'細鋼管外架・第 {row+1} 層','兩列細管之間保持淨空，銀色外排與深灰內排交錯搭接。踏板兩端各扣住一道管柱。')
        for x in range(31,64,4):
            for zz in (46,47):
                for h in (0,3):b.put('3062b','L' if zz==47 else 'D',x,zz,y+h)
        for z in (46,47):
            b.put('3024','D',31,z,y+6)
            for x in range(32,64,4):b.put('3710','D',x,z,y+6)
    b.step('工作走板與側緣','將走板跨過兩列細管，淺深灰相間的小格面呈現施工架最上層踏面。')
    for x in range(31,63,4):
        b.put('87079','D',x,46,31)
    b.put('3069b','L',63,46,31,1)


def site_details(b):
    b.bag('履帶起重機與工地邊帶')
    crane_load(b)
    crawler(b,85,26,5,'R')
    crawler(b,37,1,4,'G')
    scaffolding(b)
    b.step('墊木上的待吊工字梁','每疊鋼料先擺兩道橫向墊木，分層扣上梁的窄腹板和寬翼緣，保留兩疊之間的裝吊空間。')
    for x,z in ((86,10),(86,16),(74,49)):
        for xx in (x+1,x+6): b.put('3710','N',xx,z,2,1)
        for zz in (z,z+2):
            b.put('3034','O',x,zz,3)
            b.put('3460','O',x,zz,4)
            b.put('3034','O',x,zz,5)
            b.put('4162','O',x,zz,6)
    b.step('工作車道與落塵溝','以兩列深色短板交錯鋪出車轍，靠外側沿直線排水。吊裝作業面留在道路內側。')
    for z in range(3,46,4):
        for x in (99,102):b.put('2431','D',x,z,2,1)
        b.put('2412b','L',97,z,2,1)
    b.step('施工圍籬與工區標記','淺灰支腳承接立柱與兩色圍板。長條圍板朝向坡地，施工架立在它的後方。')
    for i in range(10):
        x=4+i*6;z=49
        b.put('3020','L',x,z,2)
        b.put('3005','D',x,z,3)
        b.put('3005','D',x,z,6)
        b.put('3010','W',x+1,z,3)
        b.put('3010','G',x+1,z,6)
        b.put('2431','L',x+1,z,9)


def front_slope(b):
    b.bag('草坡及觀景步道')
    # A continuous low knoll follows the photographed grassy foreground. Contours move
    # in both axes, exposing cropped grass, rounded shoulders and looser shrub cover.
    levels={}
    for x in range(2,102,2):
        for z in range(50,64,2):
            if z==50 and x<64 or z<=52 and 74<=x<82:continue
            shoulder=52+2.1*sin(x/14)+.8*cos(x/6)
            slope=(z-shoulder)/3.6 + .75*sin(x/16+.5) + .42*cos((x+z)/6)
            h=max(0,min(3,int(slope+1.1)))
            if z>=60: h=max(1,h)
            if x>=86 and z>=60:h=2
            if h:levels[x,z]=h
    for h in range(1,4):
        b.step(f'草坡第 {h} 條等高線','從坡後往前依圖勾出稜線，較高區塊縮短，讓地形從赤土過渡到低矮草帶。')
        for z in range(50,64,2):
            x=2
            while x<102:
                if levels.get((x,z),0)<h:x+=2;continue
                start=x
                while x<102 and levels.get((x,z),0)>=h:x+=2
                b.area('brick','O' if h==1 else 'F',start,z,2+3*(h-1),x-start,2)
    b.step('坡肩弧面、草叢與碎石步道','朝向較高地帶安裝弧面斜磚。在開闊草地交錯平面和草叢，坡頂按圖用短板鋪出轉折的碎石小徑。')
    for (x,z),h in levels.items():
        y=2+h*3
        if 88<=x<=98 and z>=60:
            b.put('3022','L',x,z,y)
            continue
        path_z=60+2*round(sin(x/13))
        if z==path_z and x>=10:
            b.put('3068b','N' if (x//2)%6 else 'L',x,z,y)
            continue
        color='F' if sin(x/7+z/8)+cos(x/13-z/6)>.25 else 'G'
        uphill=next((rot for (dx,dz),rot in (((0,2),2),((2,0),1),((-2,0),3),((0,-2),0))
                     if levels.get((x+dx,z+dz),0)>h),None)
        if uphill is not None:
            b.put('15068',color,x,z,y,uphill)
            continue
        b.put('3022','G',x,z,y)
        if (x//2+z//2)%4==0:
            b.put('4032a',color if color=='G' else 'F',x,z,y+1)
            b.put('32607','G',x,z,y+2)
        elif (x+z)%6:
            b.put('32607',color,x,z,y+1)
        else:b.put('3068b',color,x,z,y+1)
    b.step('坡頂的工程紀念牌','將晶圓圓標貼在直立沙色牆板正面。牌背一對立柱扣住整片蓋板，底座與坡頂平台相接。')
    b.put('3034','D',90,60,9)
    for x in (91,95):
        for y in (10,16):b.put('3245c','L',x,60,y)
        b.put('3004','L',x,60,22)
    b.put('59349','N',91,61,10)
    decal(b,'tsmc','坡頂工程紀念牌的台積電晶圓標誌',37,37)
    b.put('3795','D',91,60,25)


def pack(b,goal):
    """Adjust fully supported deck surface joints while keeping all beams and their bearings."""
    phases=b.info['bags']
    total=sum(len(s['pieces']) for p in phases for s in p['steps'])
    split={'6636':('63864','63864'),'87079':('3068b','3068b'),'3068b':('3069b','3069b'),'2431':('3069b','3069b'),
           '3069b':('3070b','3070b'),'4162':('2431','2431')}
    if total>goal:raise ValueError(('surplus',total))
    # Only part the smooth metal sheets where a continuous bed of studs supports both halves.
    for _ in range(3):
        for phase in phases:
            for step in phase['steps']:
                revised=[]
                for p in step['pieces']:
                    pair=split.get(p['part'])
                    if not pair or total>=goal or '分片樓承板' not in step['name']:
                        revised.append(p);continue
                    pid_a,pid_b=pair
                    assert p['color'] in stock[pid_a] and p['color'] in stock[pid_b]
                    dx,dz=parts[pid_a]['w'],0
                    if p['part']=='3068b':dx,dz=0,1
                    if p['r']%2:dx,dz=dz,dx
                    revised.extend([dict(p,part=pid_a),dict(p,part=pid_b,x=p['x']+dx,z=p['z']+dz)])
                    total+=1
                step['pieces']=revised
    if total!=goal:raise ValueError(('insufficient build',total))
    ordered=[]
    for phase in phases:
        for step in phase['steps']:
            pieces=step['pieces']
            for offset in range(0,len(pieces),8):
                serial=offset//8+1
                title=step['name']+(f'（{serial}/{(len(pieces)+7)//8}）' if len(pieces)>8 else '')
                ordered.append((phase['name'],dict(name=title,hint=step['hint'],pieces=pieces[offset:offset+8])))
    bags=[];index=0;done=0
    for n in range(12):
        names=[];steps=[];count=0
        while index<len(ordered) and (n==11 or done+count<(n+1)*500):
            name,step=ordered[index]
            if not names or names[-1]!=name:names.append(name)
            steps.append(step);count+=len(step['pieces']);index+=1
        bags.append(dict(name='、'.join(names),steps=steps));done+=count
    titles=['錯縫底板與第一列柱腳','承台錨栓及澆置地坪','首層鋼柱、工字梁與橫接梁',
            '首層分片樓承板','柱頭斜撐及二層柱身','二層縱橫梁與後段樓板',
            '二層前緣與三層柱列','三層鋼架及局部樓板','三層收邊與最高層裸梁',
            '最上層施工面、吊梁與兩台履帶吊','雙排施工架、工地圍籬與坡腳','草坡、觀景步道與工程紀念牌']
    for bag,title in zip(bags,titles,strict=True):bag['name']=title
    b.info['bags']=bags
    return b.info


def fab256000(Building):
    b=Building('fab256000','TF 03','台積電 Fab 25 P1・鋼構施工典藏版','Fab 25 P1 · Steelwork, August 2026',
               '2026 年 8 月 31 日從綠坡望去，廠房長向裸露紅棕色鋼架，灰色樓承板在不同高度收邊，數支斜吊臂突出施工天際線。模型以四段架設高度表現交錯的主梁、次梁和局部鋪板。',104,64,[.36,.68,1.34],
               ['四段高低錯落的裸露鋼架與逐跨收邊的樓承板','雙側格構斜臂履帶吊、行走裝置與配重','分層綠坡、紅土工作面與前緣展示牌'],'臺中市政府・2026 年 8 月 31 日現勘')
    building_views(b,'沿綠坡望向紅棕色鋼架，長立面每跨可見深淺不同的樓板邊緣。','由右側觀察起重機臂、未鋪板的鋼格與前後施工高度。','由上方分辨已鋪樓承板、只架次梁和僅立柱頭的不同區域。')
    b.info['views'].extend([
        dict(id='girders',name='裸露鋼梁',direction=[.52,.20,1.31],region=[55,78,33,44,23,48],note='沿前立面望進開間，雙格上下翼緣夾住較窄的腹板；少數邊跨保留透空斜撐。'),
        dict(id='deck',name='樓承板交界',direction=[.42,1.25,.78],region=[26,64,12,35,37,61],note='銀灰色壓型板在鋼格上逐跨鋪設，裸露次梁旁可看見施工面的深淺差。'),
        dict(id='crane',name='斜臂履帶吊',direction=[.34,.24,1.18],region=[67,98,25,34,3,93],note='傾斜桁柱一路連到帶軸孔的臂頭，黑色吊索垂至剛就位的鋼梁。底部可見兩列履帶、駕駛室及配重。')])
    b.foundation('D','N')
    footings(b)
    steel(b)
    site_details(b)
    front_slope(b)
    return pack(b,6000)

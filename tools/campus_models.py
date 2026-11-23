"""Photo-specific architecture and landscaping for the Morris Chang Building and Arc campus."""


def apply_decal(building, art, width, height, label):
    building.current['pieces'][-1]['decal'] = {
        'art': art, 'face': 'front', 'widthMM': width, 'heightMM': height, 'label': label
    }


def column(b, color, x, z, start, stop, width=1, depth=1):
    """Build a course of upright supports to the specified roof plane."""
    y = start
    while y+3 <= stop:
        b.area('brick', color, x, z, y, width, depth)
        y += 3
    while y < stop:
        b.area('plate', color, x, z, y, width, depth)
        y += 1


def capped_ring(b, x, z, y, body_color='L', cap_color='L'):
    """A true round coping made of four annular sectors, clear at the centre."""
    for dx, dz, r in ((0, 0, 2), (4, 0, 3), (0, 4, 1), (4, 4, 0)):
        b.put('48092', body_color, x+dx, z+dz, y, r)
        b.put('27507', cap_color, x+dx, z+dz, y+3, r)


def twin(Building):
    b = Building('twin', 'FAB 01', '張忠謀大樓', 'Morris Chang Building',
                 '白色研發棟的三道深色腰線在轉角折返；沙藍雙框環抱玻璃翼樓，與高聳的灰塔相接。沿草帶進入圓形廣場，可見張忠謀大樓銘牌與晶圓標誌。',
                 32, 32, [-.72, .76, 1.0],
                 ['三道水平腰線與轉角藍窗', '翼樓雙框與挑出玻璃門廳', '張忠謀大樓雙語銘牌'], '925877080')
    b.foundation('K', 'D')
    b.bag('三腰線主樓與晶圓徽章')
    x, z, w, d = 1, 2, 24, 7
    y = 2
    courses = [('brick', 'B'), ('brick', 'L'), ('brick', 'W'), ('brick', 'W'),
               ('brick', 'W'), ('brick', 'W'), ('plate', 'K'),
               ('brick', 'W'), ('plate', 'W'), ('plate', 'K'),
               ('brick', 'W'), ('plate', 'W'), ('plate', 'K')]
    for i, (form, color) in enumerate(courses):
        b.step('研發棟立面 · '+str(i+1), '以左邊端牆為起點，讓細腰線從主立面連續轉過兩個牆角。')
        b.ring(form, color, x, z, y, w, d, bool(i%2))
        y += 3 if form == 'brick' else 1
    for i in range(7):
        b.step('白色設備層 · '+str(i+1), '向上砌出整片白色牆面；裝徽章的位置留在左端轉角藍窗的右側。')
        if i in (4, 5):
            b.area('brick', 'W', x, z, y, w, 1)
            b.area('brick', 'W', x, z+1, y, 1, d-2)
            b.area('brick', 'W', x+w-1, z+1, y, 1, d-2)
            b.area('brick', 'W', x, z+d-1, y, 4, 1)
            b.area('brick', 'W', 7, z+d-1, y, x+w-7, 1)
            if i == 4:
                b.put('3245c', 'W', 5, z+d-1, y)
                apply_decal(b, 'tsmc', 14, 15, '研發棟上方白色牆面的晶圓徽章')
        else:
            b.ring('brick', 'W', x, z, y, w, d, bool(i%2))
        y += 3
    b.step('白色屋頂及收邊', '由兩端向中央鋪上橫跨牆身的薄板，周邊壓上平整白框，內部保留白色凸點。')
    b.deck('W', x, z, y, w, d)
    b.ring('tile', 'W', x, z, y+1, w, d)
    b.step('西角藍色光井', '在轉角齊排一條灰色直柱與一道透明窗，頂端白邊接到主樓屋頂。')
    column(b, 'L', 1, 9, 2, 53)
    for level in range(2, 53, 3):
        col = 'D' if level < 8 else 'T'
        b.area('brick', col, 2, 9, level, 2, 1)
    b.area('plate', 'W', 1, 9, 53, 3, 1)
    b.bag('高塔、設備翼與雙框')
    x, z, w, d = 26, 2, 5, 18
    for i in range(21):
        b.step('灰色設備塔 · '+str(i+1), '將塔身沿窄而深的矩形往上堆疊；每隔一層對調兩端的咬合方向。')
        b.ring('brick', 'L', x, z, 2+3*i, w, d, bool(i%2))
    b.step('高塔凹頂', '封住塔頂，在光面邊框中間留出長方形凹槽。')
    b.deck('L', x, z, 65, w, d, 'x')
    b.ring('plate', 'L', x, z, 66, w, d)
    b.ring('tile', 'L', x, z, 67, w, d)
    x, z, w, d = 17, 9, 9, 11
    y = 2
    layers = [('brick', 'D'), ('brick', 'B'), ('brick', 'B'), ('brick', 'B'),
              ('brick', 'B'), ('brick', 'B'), ('brick', 'B'),
              ('plate', 'W'), ('brick', 'T'), ('brick', 'T'), ('brick', 'T'),
              ('plate', 'W'), ('brick', 'T'), ('brick', 'T'), ('plate', 'W')]
    for i, (form, color) in enumerate(layers):
        b.step('玻璃翼樓 · '+str(i+1), '淺藍色玻璃連續包覆面向廣場的兩面，白色出簷將上下窗帶分開。')
        # The hidden back and the equipment-tower side carry the roof. The
        # outward-facing panes on the west and south remain independently legible.
        b.area(form, 'B' if color == 'T' else color, x, z, y, w, 1)
        b.area(form, 'B' if color == 'T' else color, x+w-1, z+1, y, 1, d-2)
        b.area(form, color, x, z+1, y, 1, d-2)
        b.area(form, color, x, z+d-1, y, w, 1)
        # Spine is immediately below the joint in the two-piece roof.
        b.area(form, 'L' if color == 'T' else color, x+4, z+1, y, 1, d-2)
        y += 3 if form == 'brick' else 1
    b.step('翼樓白簷', '從左、右兩邊向中央承重牆跨接薄板，做出玻璃頂端的白色水平線。')
    for zz in range(z, z+d):
        b.area('plate', 'W', x, zz, y, 5, 1)
        b.area('plate', 'W', x+5, zz, y, 4, 1)
    b.step('沙藍立柱與平行頂框', '兩道頂框橫跨翼樓，豎柱落在面向廣場的西側；靠近主樓的一道高出一層。')
    for zz, extra in [(10, 3), (16, 0)]:
        column(b, 'B', 16, zz, 2, y+1, 1, 2)
        b.area('plate', 'B', 16, zz, y+1, 10, 2)
        b.area('brick', 'B', 16, zz, y+2, 10, 2)
        if extra:
            b.area('brick', 'B', 16, zz, y+5, 10, 2)
        b.area('tile', 'B', 16, zz, y+5+extra, 10, 2)
    b.bag('玻璃大廳、雙語銘牌與景觀')
    x, z, w, d = 13, 20, 12, 6
    y = b.frame(x,z,2,w,d,[('brick','T'),('plate','T'),('brick','T'),('plate','T'),
                             ('brick','T'),('plate','T'),('brick','T'),('plate','L')], '玻璃門廳')
    b.step('門廳石材檐口', '屋面中間保留凸點，外緣用淺灰色平板環繞；這片矮屋頂位於雙框正前方。')
    b.deck('L',x,z,y,w,d)
    b.ring('tile','L',x,z,y+1,w,d)
    b.step('門套與小紅雨棚','兩側灰柱支撐上方的門楣，紅色小雨棚從深色玻璃門上向外伸出一格。')
    for xx in [15,19]:
        column(b, 'L', xx, 26, 2, 11)
    b.area('brick','T',16,26,2,3,1)
    b.area('plate','R',16,26,5,3,2)
    b.area('tile','R',16,26,6,3,2)
    b.area('plate','L',15,26,11,5,1)
    b.area('brick','L',15,26,12,5,1)
    b.area('tile','L',15,26,15,5,1)
    b.step('西入口徽章與雙語牆牌','入口小柱承托深灰徽章，右側牆身將張忠謀大樓銘牌安放在紅色基座上方。')
    for xx in [2,4]:
        column(b,'D',xx,11,2,5)
    b.area('plate','D',2,11,5,3,1)
    b.put('3245c','D',2,11,6)
    apply_decal(b,'tsmc',14,15,'西入口深灰端牆的晶圓徽章')
    b.area('brick','D',4,11,6,1,1)
    b.area('brick','D',4,11,9,1,1)
    b.area('tile','D',2,11,12,3,1)
    b.area('plate','D',5,10,2,8,2)
    b.area('plate','R',5,11,3,8,1)
    b.area('plate','R',5,10,3,8,1)
    b.area('brick','D',5,10,4,8,1)
    b.area('brick','D',5,11,4,1,1)
    b.put('3009','L',6,11,4)
    apply_decal(b,'tsmc-sign',32,8.4,'西入口紅色底座上方的中英文樓名牌')
    b.area('brick','D',12,11,4,1,1)
    b.area('plate','D',5,10,7,8,2)
    b.area('tile','D',5,10,8,8,2)
    b.step('圓環廣場與中央矮台','灰環使用四塊圓角磚連成一圈，套上環形光面板；廣場中心另放深灰色矮台。')
    capped_ring(b,3,19,2,'D','L')
    b.put('3941','D',6,22,2)
    b.put('4150','D',6,22,5)
    b.step('綠帶與多層樹冠','沿正面鋪起一長段草地，門廳旁的樹木沿斜向排列；樹幹頂部裝上葉片，最後點綴白花。')
    b.area('plate','G',2,28,2,28,3)
    b.area('plate','G',9,26,2,4,2)
    for xx,zz in [(10,27),(13,28),(20,28),(25,29)]:
        b.put('3062b','O',xx,zz,3)
        b.put('4032a','G',xx,zz-1,6)
        b.put('32607','G',xx,zz,7)
        b.put('24866','W',xx+1,zz-1,7)
    b.step('草帶前的樓名牌','將正面的灰色矮牌安在草地左端，張忠謀大樓字樣朝向展示座前方。')
    b.put('3010','L',3,29,3)
    apply_decal(b,'campus-sign',26,7.2,'草地靠近圓環的張忠謀大樓矮牌')
    b.area('tile','L',3,29,6,4,1)
    return b.finish()


def oval(Building):
    b = Building('arc','FAB 05','台積電南京園區','TSMC Nanjing Campus',
                 '池畔的白色研發棟橫跨五座鏤空 V 形支架，上下兩側的曲面在紅色 tsmc 端牌旁收圓。右側廠房以完整白色橢圓外環圍住屋頂機房，環下的灰色支墩之間可看見通廊。',
                 48, 32, [-.87,.75,1.04],
                 ['五座白色雙 V 斜撐','上下收圓的架空研發棟','二十四乘二十格的閉合橢圓外環'], '920718279')
    left_feet = [[16.5-3*i,4.5+4*i] for i in range(5)]
    right_feet = [[x+4,z+3] for x,z in left_feet]
    mounts = left_feet+right_feet
    b.info['pivot'] = dict(x=16.5,z=4.5,degrees=36.86989764584402,label='管形研發棟',mounts=mounts, rows=[left_feet,right_feet])
    b.info['revision'] = 3
    b.info['views'] = [
        dict(id='supports',name='支撐側視',direction=[.12,.19,1.0],pivoted=True,
             note='五座支架各有兩個獨立落地支腳。成對的白色斜桿支撐上方縱梁，兩側倒圓弧磚包住樓板。'),
        dict(id='oval',name='橢圓俯視',direction=[0,1,.05],bag=2,
             note='沿白色外牆繞一圈，可見四道大半徑屋緣連成封閉外環，中間留出屋頂機房。'),
    ]
    b.foundation('L','D')
    b.bag('架空支墩、橢圓廠房與中央機房')
    corners=[(22,1,1),(36,1,2),(22,11,0),(36,11,3)]
    b.step('環廊內縮的承重墩','在四道弧下面各立兩座灰色支墩。留出墩間通道，兩側草地可從廊下看見。')
    # Each pair of feet bears against the flat inner portion of its 10-stud quadrant.
    feet=[(27,5),(24,9),(39,5),(42,9),(27,15),(24,11),(39,15),(42,11)]
    for x,z in feet:b.put('3003','L',x,z,2)
    for x,z in [(33,3),(33,17)]:b.put('3003','L',x,z,2)
    b.step('支墩頂板與四道跨縫梁','加寬各墩頂，左右端的長板連起前後支墩。前後端的橫梁從內側連到兩道弧。')
    for x,z in [(27,5),(39,5),(27,15),(39,15)]:b.put('3022','D',x,z,5)
    for x in [24,42]:b.area('plate','D',x,9,5,2,4)
    for z in [3,17]:b.area('plate','L',30,z,5,8,2)
    b.step('環廊內緣的承重骨架','沿既有灰墩再砌兩層。這圈內縮的支柱承托完整的弧形屋頂，外緣留給白色直立面板。')
    for y in [6,9]:
        for x,z in feet+[(33,3),(33,17)]:b.put('3003','L',x,z,y)
    # Five tangent panels per quadrant. The central stud of an odd panel, or
    # one of its two middle studs on an even panel, fits each swivel pin.
    quadrant=[(9.5,.5,2,.5,0),(8.5,4.5,4,-.5,23),(7.5,6.5,2,.5,51),
              (4.5,8.5,3,0,61),(1.5,9.5,2,-.5,90)]
    from math import atan2, cos, degrees, radians, sin
    for sx,sz,zone in [(1,1,'東南'),(-1,1,'西南'),(-1,-1,'西北'),(1,-1,'東北')]:
        for i,(u,v,length,offset,angle) in enumerate(quadrant,1):
            ax=(36 if sx==1 else 32)+sx*u;az=11+sz*v
            theta=radians(angle)
            turn=round(degrees(atan2(sz*cos(theta),-sx*sin(theta))))
            cx=int(ax);cz=int(az)
            left=int(ax+offset-length/2)
            b.step(f'{zone}弧面 {i} · 立柱與白牆',
                   f'將細圓柱扣在第 {cx+1} 欄、第 {cz+1} 列。在圓柱上疊兩層白牆及一片光面頂板，俯視由向右的長軸轉 {turn:+d}°，面板與兩側接出圓弧。')
            b.put('3062b','L',cx,cz,2)
            axis=dict(x=ax,z=az,degrees=turn,label=f'{zone}弧面 {i}')
            for y,pid in [(5,{2:'3004',3:'3622',4:'3010'}[length]),(8,{2:'3004',3:'3622',4:'3010'}[length]),(11,{2:'3069b',3:'63864',4:'2431'}[length])]:
                b.put(pid,'W',left,cz,y);b.current['pieces'][-1]['pivotAt']=axis
    b.step('前後弧面的直線接縫','在兩道白弧之間用六格長磚接起前後兩段立面。下方的圓柱與兩側弧牆一樣，柱間保持透空。')
    for z in [1,20]:
        for x in [32,35]:b.put('3062b','L',x,z,2)
        for y in [5,8]:b.put('3009','W',31,z,y)
        b.put('6636','W',31,z,11)
    b.step('閉合的大半徑弧形屋緣','四個十格半徑白弧坐在內側灰墩上，跨過下方白牆分縫。每個外弧朝園區外側，左右兩道半環在前後短邊連接。')
    for x,z,r in corners:b.put('58846','W',x,z,12,r)
    for z,outer,inner,high,r in [(1,1,3,2,2),(17,19,17,19,0)]:
        for x in [32,34]:b.put('3020','W',x,z,12,1)
        b.area('plate','W',32,high,13,4,1)
        for x in [32,34]:b.put('15068','W',x,outer,13,r)
        for y in [13,14]:b.area('plate','W',32,inner,y,4,2)
    b.step('前後檐口壓條','在前後中央的橫梁上鎖住弧磚，將兩個白色轉角與中央連接段綁在一起。')
    for z in [4,17]:b.area('tile','W',30,z,15,8,1)
    for x in [25,42]:b.area('tile','W',x,9,15,1,4)
    # The equipment core nests in the open centre of all four curved walls.
    outline=[(5,30,37),(6,29,38),(7,29,38)]+[(zz,27,40) for zz in range(8,14)]+[(14,29,38),(15,29,38),(16,30,37)]
    for level in range(4):
        b.step('中央機房牆與承板肋 · '+str(level+1),'在外環中央砌起沙藍機房，兩端退縮，留出環形檢修走道。內側承板肋與山牆共同支撐屋頂。')
        y=2+3*level
        for zz,left,right in outline:
            if zz in (5,16):b.area('brick','B',left,zz,y,right-left+1,1)
            else:
                for xx in [left,right]:b.put('3005','B',xx,zz,y)
                b.put('3004','L',33,zz,y)
    b.step('機房屋面與藍色矮檐','從兩側牆面向中央鋪設屋面薄板，沿外緣加一層沙藍平邊。')
    for zz,left,right in outline:
        b.area('plate','L',left,zz,14,34-left,1)
        b.area('plate','L',34,zz,14,right-33,1)
    for zz,left,right in outline:
        if zz in (5,16):b.area('tile','B',left,zz,15,right-left+1,1)
        else:
            for xx in [left,right]:b.put('3070b','B',xx,zz,15)
    b.step('冷卻箱、集管與檢修塔','兩列白色冷卻箱以管線相連。三座小風機在東側排成一列，設備井緊貼屋面後方。')
    for zz in [8,12]:
        b.area('plate','L',29,zz,15,7,2)
        b.area('tile','W',29,zz,16,7,2)
    for xx in [29,31,33,35]:b.put('2412b','L',xx,10,15)
    for zz in [8,10,12]:
        b.put('4032a','L',37,zz,15);b.put('98138','D',38,zz,16)
    b.put('3004','L',34,6,15);b.put('3069b','L',34,6,18)
    b.bag('圓盤管制中心與管形研發棟')
    b.step('廊下草帶與西側小徑','先鋪好架空研發棟下方的草地、灌木與步道小景，再將支架和樓板扣上。')
    for zz,xx,span in [(20,1,2),(21,1,4),(22,1,5),(23,1,6),(24,1,7),(25,1,7),(26,1,8),(27,1,8),(28,1,8),(29,1,8)]:
        b.area('plate','F',xx,zz,2,span,1)
    for xx,zz in [(2,23),(4,26),(6,28)]:
        b.put('32607','G',xx,zz,3)
    for xx in [2,4,6]:b.put('3070b','L',xx,25,3)
    b.area('plate','G',1,15,2,4,3)
    b.area('brick','A',2,15,3,2,1)
    b.area('tile','U',2,15,6,2,1)
    b.step('管制中心圓形平台','四片扇形板扣成八格寬的深色圓盤，圓柱置於正中。')
    for dx,dz,r in [(0,0,2),(4,0,3),(0,4,1),(4,4,0)]:
        b.put('30565','D',0+dx,6+dz,2,r)
    b.put('87081','W',2,8,3)
    b.put('87081','W',2,8,6)
    b.step('管制中心白色碟形屋頂','先以四片扇形板伸出直徑八格的白色簷口，再將六格白碟居中扣在簷面，形成高起的圓頂。')
    for dx,dz,r in [(0,0,2),(4,0,3),(0,4,1),(4,4,0)]:
        b.put('30565','W',dx,6+dz,9,r)
    b.put('44375b','W',1,7,10)
    b.step('兩列獨立支腳','沿底座放好十個獨立支腳，每座斜撐左右各落在一腳上。左、右兩列各有五個支點，同列向前四格、向左三格，左右腳相隔五格斜距。')
    for xx,zz in mounts:
        x,z=int(xx),int(zz)
        b.put('4073','D',x,z,2);b.put('4073','L',x,z,3)
    first_gallery_step = len(b.info['bags'][-1]['steps'])
    for i,zz in enumerate([4,9,14,19,24],1):
        b.step(f'第 {i} 座雙 V 斜撐','左、右兩片底板分別固定在自己的支腳上，轉到研發棟方向。每片底板上的兩個白框左右相反，斜桿在中間下端會合。壓上頂梁與墊柱，形成兩組透空支撐。')
        for xx in [15,19]:b.put('3710','L',xx,zz,4)
        for xx,r in [(15,0),(17,2),(19,0),(21,2)]:b.put('3224','W',xx,zz,5,r)
        for xx in [15,19]:b.put('3710','W',xx,zz,10)
        for y in [11,12]:
            for xx in [16,20]:b.put('3023','W',xx,zz,y)
        b.put('3666','W',16,zz,13)
    b.step('跨過五座支架的縱梁','六格寬的梁帶扣在白色框頂。每根板至少壓上其中一座支架，池畔和後端各留懸挑。')
    for xx in [16,18,20]:b.area('plate','W',xx,3,14,2,24)
    b.step('兩側倒圓弧底殼','將白色 1750 的內側兩個扣位從上方扣在縱梁外排凸點。外側圓邊垂在樓板旁，兩邊鏡像；兩格一組，沿整條長廊排到池畔端。')
    for zz in range(3,27,2):
        b.put('1750','W',15,zz,14,1);b.put('1750','W',21,zz,14,3)
    b.step('底殼內緣找平','兩側內緣各疊兩層白薄板：第一層補倒弧的落差，第二層扣入上弧高肩的凹口。這樣從池畔看端面會完整封閉。中間樓板交錯壓緊。')
    for y in [16,17]:
        for xx in [16,21]:b.area('plate','W',xx,3,y,1,24)
    for y in [15,16]:
        for zz in range(3,26,2):b.area('plate','W',17,zz,y,4,min(2,26-zz))
    b.step('池畔端板與紅色字標','在最後一排中央裝四格白色端板，紅色 tsmc 朝向水池，兩旁留給上下相接的弧形端角。')
    b.put('3010','W',17,26,15);apply_decal(b,'tsmc-word',24,6,'架空研發棟面向水池的圓角端面')
    b.step('配對上弧與下弧','把兩排 15068 的高肩朝向建築中央，靠在倒圓弧上方。沿兩側檢查外殼，池畔端可見上下收圓的長橢圓剖面。')
    for zz in range(3,27,2):
        b.put('15068','W',15,zz,17,1);b.put('15068','W',21,zz,17,3)
    b.step('縱向屋面接縫','在中間四列鋪板至與端牌齊高，再沿長軸用細長白色平板壓住板縫。')
    for zz in range(3,26,2):b.area('plate','W',17,zz,17,4,min(2,26-zz))
    for xx in range(17,21):b.area('tile','W',xx,3,18,1,24)
    for step in b.info['bags'][-1]['steps'][first_gallery_step:]:
        for piece in step['pieces']:piece['pivoted']=True
    b.bag('蓮池、短橋與周邊綠帶')
    b.step('蓮池圓弧底板','兩端各用兩片扇形板接出圓弧，中間插入六格寬的直段，池岸形成圓角長形。')
    for dx,dz,r in [(0,0,2),(10,0,3),(0,6,1),(10,6,0)]:b.put('30565','L',11+dx,21+dz,2,r)
    b.area('plate','L',15,21,2,6,10)
    for xx in [11,21]:b.area('plate','L',xx,25,2,4,2)
    b.step('池岸環形平板','將四塊灰色四分之一環扣在弧岸，首尾以直線平板閉合。')
    for dx,dz,r in [(0,0,2),(10,0,3),(0,6,1),(10,6,0)]:b.put('27507','L',11+dx,21+dz,3,r)
    for zz in [21,30]:b.area('tile','L',15,zz,3,6,1)
    for xx in [11,24]:b.area('tile','L',xx,25,3,1,2)
    b.step('透明水面與池心植物','透明淺藍薄板鋪在弧岸內緣；向兩端縮短水面圓弧，水心覆蓋小片綠葉。')
    for zz,xx,length in [(22,14,8),(23,13,10),(24,12,12),(25,12,12),(26,12,12),(27,12,12),(28,13,10),(29,14,8)]:
        b.area('plate','T',xx,zz,3,length,1)
    b.put('4032a','G',17,25,4)
    b.put('32607','G',18,25,5)
    b.step('跨水步橋','將窄橋兩端墊高一層，由後岸向池心的葉島前方延伸。')
    b.put('3024','D',17,22,4)
    b.put('3024','D',17,24,4)
    b.put('63864','L',17,22,5,1)
    b.step('側院草坡與矮灌木','東南側的深綠植栽帶向後收窄，西側小草帶與管制中心步道連接。')
    for zz,xx,length in [(22,32,6),(23,30,8),(24,28,10),(25,27,11),(26,26,12),(27,25,13),(28,25,13),(29,25,13)]:
        b.area('plate','F',xx,zz,2,length+8,1)
    for xx,zz in [(27,28),(33,27),(39,26),(44,23)]:
        b.put('32607','G',xx,zz,3)
    b.step('西側植栽與管制中心步道','以深綠板沿西側框出狹長花圃，管制中心後方用透明淺藍組成一段矮欄。')
    for zz,xx,span in [(1,1,12),(2,1,11),(3,1,10),(4,1,9),(5,1,8)]:
        b.area('plate','F',xx,zz,2,span,1)
    for xx in [1,4,7,10]:
        b.put('3023','T',xx,1,3)
    for xx,zz in [(2,4),(5,3),(8,2)]:b.put('32607','G',xx,zz,3)
    b.step('園區路樹與欄柱','在池畔保留修長的樹形，沿西南側外圍依序安裝白色短柱與淺灰扶手。')
    for xx,zz in [(9,27),(10,28),(25,22),(28,22)]:
        b.put('4073','O',xx,zz,2)
        b.put('3062b','G',xx,zz,3)
        b.put('32607','G',xx,zz,6)
    for xx in [1,3,5,7,9]:
        b.put('3005','W',xx,30,2)
    for xx in [25,28,32,35,39,42]:b.put('3005','D',xx,30,2)
    for xx in [25,32,39]:b.put('2431','L',xx,30,5)
    return b.finish()

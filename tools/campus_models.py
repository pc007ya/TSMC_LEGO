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
                 '面向廣場的白色大弧牆包圍凹入的屋頂機房。印有紅色 tsmc 字樣的管形研發棟斜架於四個圓柱支點上，西側設有圓盤管制中心，前方是弧岸水池。',
                 40, 32, [-.84,.88,1.14],
                 ['直徑二十格的白色半圓主樓','四點架高的管形研發棟','圓盤管制中心與弧岸水池'], '920718279')
    mounts = [[18.5,3.5], [15.5,7.5], [12.5,11.5], [9.5,15.5]]
    b.info['pivot'] = dict(x=18.5,z=3.5,degrees=36.86989764584402,label='管形研發棟',mounts=mounts)
    b.foundation('L','D')
    b.bag('半圓弧牆與凹頂設備核心')
    # Eleven thin, vertical façade panels trace a semi-circle with an outer
    # radius of about ten studs. Each swings on ONE exposed circular stud;
    # a course of separation leaves room for the rotated underside.
    profile = [(0,21,0),(3,20,16),(6,19,36),(8,16,56),(9,13,74),(10,10,90)]
    facets = [(29-dx,zz,angle) for dx,zz,angle in reversed(profile[1:])]
    facets += [(29,21,0)]
    facets += [(29+dx,zz,-angle) for dx,zz,angle in profile[1:]]
    b.step('弧牆的十一個圓軸座','從左端開始，沿半圓逐一壓入深灰單凸點圓板。保留兩端的空間以調整面板的方向。')
    for xx,zz,_ in facets:b.put('4073','D',xx,zz,2)
    for number,(xx,zz,degrees) in enumerate(facets,1):
        side='順時針' if degrees>=0 else '逆時針'
        b.step(f'白色弧牆面板 {number:02d}',
               f'將三格底板的中央扣在第 {xx+1} 欄、第 {zz+1} 列的圓軸座，從俯視的左右向{side}轉 {abs(degrees)}°。疊上兩層白磚並以光面板封頂。')
        pivot = dict(x=xx+.5,z=zz+.5,degrees=degrees,label=f'弧牆面板 {number:02d}')
        for part,color,y in [('3623','D',3),('3622','W',4),('3622','W',7),('63864','W',10)]:
            b.put(part,color,xx-1,zz,y)
            b.current['pieces'][-1]['pivotAt'] = pivot
    b.step('環廊內側的平台','在白色弧牆內側架設兩層台基，向前逐列收窄。平台與白色面板間留出細縫。')
    terrace=[(16,24,11),(17,25,9),(18,26,7),(19,27,5)]
    for y,color in [(2,'D'),(5,'L')]:
        for zz,xx,span in terrace:b.area('brick',color,xx,zz,y,span,1)
    for zz,xx,span in terrace:b.area('tile','L',xx,zz,8,span,1)
    # Broad, chamfered equipment volume fills the rear of the ring. The front
    # bevel pulls the wall clear of the two oblique panels at the entrance.
    outline=[(3,24,34),(4,23,35)]+[(zz,23,36) for zz in range(5,8)]+[(zz,22,36) for zz in range(8,14)]+[(14,23,35),(15,24,34)]
    for level in range(4):
        y=2+3*level
        b.step('藍灰機房 · '+str(level+1),'前後角逐格縮進，屋面下方保留兩格寬的中央承重牆。')
        for zz,left,right in outline:
            if zz in (3,15):
                b.area('brick','B',left,zz,y,right-left+1,1)
            else:
                for xx in [left,right]:b.put('3005','B',xx,zz,y)
                b.put('3004','L',29,zz,y)
    b.step('凹頂工作平台','每個橫排從兩側向中間承重牆鋪板，外緣再疊上沙藍色窄框。')
    for zz,left,right in outline:
        b.area('plate','L',left,zz,14,30-left,1)
        b.area('plate','L',30,zz,14,right-29,1)
    for zz,left,right in outline:
        if zz in (3,15):
            b.area('plate','B',left,zz,15,right-left+1,1)
            b.area('tile','B',left,zz,16,right-left+1,1)
        else:
            for xx in [left,right]:
                b.put('3024','B',xx,zz,15)
                b.put('3070b','B',xx,zz,16)
    b.step('平行冷卻設備與管組','兩長排白色設備沿著管槽安放，設備東側的三座圓筒朝向後方巡檢通道。')
    for zz in [6,11]:
        b.area('plate','B',24,zz,15,8,2)
        b.area('tile','W',24,zz,16,8,2)
        b.put('2412b','L',33,zz,15)
        b.put('2412b','L',33,zz+1,15)
    for xx in [24,26,28,30,32]:b.put('2412b','L',xx,9,15)
    for xx in [30,32,34]:
        b.put('3062b','L',xx,5,15)
        b.put('98138','L',xx,5,18)
    b.step('後端機電塔','在主棟東北側砌起分段設備井，淺灰色封頂高出藍框工作平台。')
    for yy,color in [(2,'L'),(5,'L'),(8,'W'),(11,'W'),(14,'L')]:
        b.area('brick',color,37,4,yy,2,3)
    b.area('tile','L',37,4,17,2,3)
    b.bag('圓盤管制中心與管形研發棟')
    b.step('管制中心圓形平台','四片扇形板扣成八格寬的深色圓盤，圓柱置於正中。')
    for dx,dz,r in [(0,0,2),(4,0,3),(0,4,1),(4,4,0)]:
        b.put('30565','D',0+dx,6+dz,2,r)
    b.put('87081','W',2,8,3)
    b.put('87081','W',2,8,6)
    b.step('管制中心白色碟形屋頂','先以四片扇形板伸出直徑八格的白色簷口，再將六格白碟居中扣在簷面，形成高起的圓頂。')
    for dx,dz,r in [(0,0,2),(4,0,3),(0,4,1),(4,4,0)]:
        b.put('30565','W',dx,6+dz,9,r)
    b.put('44375b','W',1,7,10)
    b.step('以三四五比例定位長廊柱','四個獨立圓柱從後往前每次向左三格、向前四格。柱頂各留一顆圓凸點承接斜廊。')
    for xx,zz in mounts:
        x,z=int(xx),int(zz)
        b.put('4032a','D',x,z,2)
        b.put('3062b','L',x,z,3)
        b.put('3062b','L',x,z,6)
        b.put('4073','L',x,z,9)
    first_gallery_step = len(b.info['bags'][-1]['steps'])
    b.step('斜廊底部縱梁','先讓第一根長板對準前兩根柱的中心；長廊自身每五格正好落在下一個單凸點柱座。')
    for z,span in [(2,8),(10,6),(16,4)]:
        b.area('plate','W',18,z,10,2,span)
    b.step('膠囊長廊橫向樓板','從後至前鋪設橫向薄板，每片壓住中線縱梁，向左右均勻挑出。')
    for zz in range(2,20,2):b.area('plate','W',15,zz,11,8,2)
    b.step('白色外殼與端面字標','前後兩端收成白色端板。紅色 tsmc 貼在面向水池的那一塊四格磚上。')
    for xx in [15,22]:b.area('brick','W',xx,2,12,1,18)
    b.area('brick','W',16,2,12,6,1)
    b.put('3005','W',16,19,12)
    b.put('3010','W',17,19,12)
    apply_decal(b,'tsmc-word',24,6,'挑高斜廊朝向水池的白色端面')
    b.put('3005','W',21,19,12)
    b.step('連廊封板','八格橫板跨在兩側白牆上，將整條斜向長廊鎖成一體。')
    for zz in range(2,20,2):b.area('plate','W',15,zz,15,8,2)
    b.step('曲肩與縱向屋面細線','兩側弧面由內側高點向外滑落，正中央的細長平板與兩肩齊平。')
    b.area('plate','W',17,2,16,4,18)
    for zz in range(2,20,2):
        b.put('15068','W',15,zz,16,1)
        b.put('15068','W',21,zz,16,3)
    for xx in range(17,21):b.area('tile','W',xx,2,17,1,18)
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
        b.area('plate','F',xx,zz,2,length,1)
    for xx,zz in [(27,28),(31,27),(35,26),(36,23)]:
        b.put('32607','G',xx,zz,3)
    for zz,xx,span in [(20,1,2),(21,1,4),(22,1,5),(23,1,6),(24,1,7),(25,1,7),(26,1,8),(27,1,8),(28,1,8),(29,1,8)]:
        b.area('plate','F',xx,zz,2,span,1)
    for xx,zz in [(2,23),(4,26),(6,28)]:
        b.put('32607','G',xx,zz,3)
    b.area('plate','O',2,25,3,5,1)
    b.put('3004','A',4,25,4)
    b.put('3069b','U',4,25,7)
    b.step('西側植栽與管制中心步道','以深綠板沿西側框出狹長花圃，管制中心後方用透明淺藍組成一段矮欄。')
    for zz,xx,span in [(1,1,12),(2,1,11),(3,1,10),(4,1,9),(5,1,8)]:
        b.area('plate','F',xx,zz,2,span,1)
    for xx in [1,4,7,10]:
        b.put('3023','T',xx,1,3)
    for xx,zz in [(2,4),(5,3),(8,2)]:b.put('32607','G',xx,zz,3)
    b.area('plate','G',1,15,2,4,3)
    b.area('brick','A',2,15,3,2,1)
    b.area('tile','U',2,15,6,2,1)
    b.step('園區路樹與欄柱','在池畔保留修長的樹形，沿西南側外圍依序安裝白色短柱與淺灰扶手。')
    for xx,zz in [(9,27),(10,28),(25,22),(28,22)]:
        b.put('4073','O',xx,zz,2)
        b.put('3062b','G',xx,zz,3)
        b.put('32607','G',xx,zz,6)
    for xx in [1,3,5,7,9]:
        b.put('3005','W',xx,30,2)
    for xx in [25,28,32,35]:b.put('3005','D',xx,30,2)
    for xx in [25,32]:b.put('2431','L',xx,30,5)
    return b.finish()

"""Brick-by-brick reconstructions of three industrial buildings in the photo series."""


def decal(b, art, label, width, height):
    b.current['pieces'][-1]['decal'] = dict(art=art, face='front', label=label,
                                            widthMM=width, heightMM=height)


def subdivide(start, stop, span):
    return [(i, min(span, stop-i)) for i in range(start, stop, span)]


def banded_roof(b, x, z, y, w, depths, color):
    """Each short plate spans one bay. The wall plan supports both sides of that bay."""
    for length in depths:
        for xx, width in subdivide(x, x+w, 2):
            b.area('plate',color,xx,z,y,width,length)
        z+=length


def pipeline(b, x, z, y, length, r=0, color='L', cap='D'):
    """Join matching bar-handles end to end. Keep the empty rail side clear.

    Local +Z is the rail side. The bar faces -X after one clockwise quarter turn.
    The thin flat strip caps the studs of the carrier plates and ties their seams.
    """
    for off in range(0,length,2):
        b.put('2540',color,x+(0 if r else off),z+(off if r else 0),y,r)
    b.area('tile',cap,x,z,y+1,1 if r else length,length if r else 1)


def equipment_box(b,x,z,y,w,d,case,top):
    b.area('plate',case,x,z,y,w,d)
    b.area('tile',top,x,z,y+1,w,d)


def chimney(b,x,z,y,base='L',neck='L',tall=False):
    b.put('3062b',base,x,z,y)
    if tall:
        b.put('3062b',base,x,z,y+3)
        y+=3
    b.put('20482',neck,x,z,y+3)


def cylinder(b,x,z,y,body='N',cap='L',double=False):
    b.put('3062b',body,x,z,y)
    if double:
        b.put('3062b',body,x,z,y+3)
        y+=3
    b.put('85861',cap,x,z,y+3)


def hedge(b,x,z,y,columns):
    b.area('plate','G',x,z,y,columns,2)
    for i in range(0,columns-1,2):
        b.put('4032a','G',x+i,z,y+1)
        if i%4==0:b.put('4073','G',x+i+1,z+(i//4)%2,y+2)


def tile_perimeter(b):
    """Frame the whole presentation base; the ground-paving pass handles its interior."""
    m=b.info; w,d=m['width'],m['depth']
    c={'fins':'W','ribbon':'L','graphite':'N'}[m['id']]
    b.step('展示底座封邊','光面板沿底座四邊首尾相接，將草帶及廠房場坪收進同一個框內。')
    b.ring('tile',c,0,0,2,w,d)


def building_views(b, front, side, plan, side_sign=1):
    """Frame the entire display base so the relationships between buildings stay visible."""
    b.info['revision'] = 3
    b.info['views'] = [
        dict(id='facade',name='正面',direction=[0,.06,1],scope='all',note=front),
        dict(id='side',name='側面',direction=[side_sign,.06,0],scope='all',note=side),
        dict(id='plan',name='俯視',direction=[0,1,.001],scope='all',note=plan),
    ]


def fins(Building):
    b=Building('fins','FAB 02','全球研發中心','Global R&D Center',
        '白色圓邊展廳跨在兩座煙灰玻璃翼樓之間。十六扇細直窗與屋頂採光帶呼應，左側沙藍端牆後方保留開放的機電庭院。',
        60,46,[-.91,.99,1.30],['十六道垂直藍窗','研發中心入口銘牌','開放式機電庭院'],'926523184')
    building_views(b,'中央直柵展廳高過兩側的三道煙色玻璃窗。','前端白框圍著整片藍玻璃，後端是獨立的沙藍機電牆。','天窗在地塊前半，後半從左到右是機電井、白色場坪與綠帶。',-1)
    b.foundation('W','W')
    b.bag('沙藍機電中庭')
    # The published roof plan places the well on the rear left and paving to its right.
    for level,(kind,c,yy) in enumerate([('brick','W',2),('plate','A',5),('brick','B',6),('brick','B',9)]):
        b.step('後棟結構層 '+str(level+1),'沙藍外牆包住左後方設備井，右方預留地面白石場坪。')
        b.ring(kind,c,3,1,yy,41,23,level%2)
        for zz in [7,15]:b.area(kind,c,4,zz,yy,39,2)
    b.step('機電井平台','三列托板橫跨機房，讓每列接縫落在外牆或內部分隔牆上。')
    banded_roof(b,3,1,12,41,[7,8,8],'L')
    b.step('沙藍端牆與白色牆頂','沿側面堆疊沙藍機房外殼，正面由白色框架收邊。')
    for yy in [13,16]:
        b.area('brick','B',3,1,yy,1,23)
    b.area('tile','B',3,1,19,1,23)
    for xx in [4,43]:
        b.area('brick','W',xx,1,13,1,23)
        b.area('tile','W',xx,1,16,1,23)
    for zz in [1,23]:
        b.area('brick','W',5,zz,13,38,1)
        b.area('tile','W',5,zz,16,38,1)
    b.step('後排銀灰集管','銀色把手沿機房後牆延伸，在前後兩排風機之間轉成縱向支管。')
    for xx,zz,ln,r in [(6,3,34,0),(6,7,34,0),(6,20,34,0),(8,10,8,1),(39,10,8,1)]:
        pipeline(b,xx,zz,13,ln,r,cap='L')
    b.step('四條縱向設備帶','兩只白色長方形箱體對稱排列。內側並排的沙金色風道夾住中央的圓形風扇。')
    for xx in [12,32]:
        b.area('brick','W',xx,10,13,4,10)
        b.area('tile','W',xx,10,16,4,10)
    for xx in [18,29]:
        b.area('plate','N',xx,10,13,2,10)
        b.area('tile','N',xx,10,14,2,10)
    b.step('立管、閥組與六座中央風機','中間三排雙風機向上，直立煙管沿著後方總管排列，兩道側排泵管一高一低。')
    for xx in [22,25]:
        for zz in [11,14,17]:b.put('4032a','L',xx,zz,13)
    for xx in [7,11,16,21,26,31,36]:
        chimney(b,xx,5,13,tall=xx in [11,26])
        cylinder(b,xx+1,5,13)
    for xx in [6,40]:
        for zz in [10,13,16,19]:cylinder(b,xx,zz,13,body='L')
    b.step('右後白石場坪及兩側短樹','白色場坪緊鄰機房右牆，兩條綠帶各沿地塊一側伸至翼樓後方。')
    b.area('tile','W',44,1,2,14,23)
    for xx in [1,58]:
        b.area('plate','G',xx,1,2,1,23)
        for zz in range(2,24,4):
            b.put('3062b','G',xx,zz,3)
            b.put('4073','G',xx,zz,6)
    b.bag('雙側煙灰幕牆')
    for xx,wing_w in [(1,13),(50,9)]:
        for i,(shape,c) in enumerate([('brick','D'),('plate','K'),('brick','S'),('plate','K'),('brick','S'),('plate','K'),('brick','S')]):
            yy=[2,5,6,9,10,13,14][i]
            b.step('側翼水平窗 '+str(i+1),'以黑色橫框夾住煙灰玻璃；窄翼樓兩端的水平線需對齊。')
            b.ring(shape,c,xx,25,yy,wing_w,10,i%2)
        b.step('側翼石墨平頂','在煙灰窗頂橫架屋頂，封成平滑的深灰盒體。')
        for wall_y,wall_h in [(2,3),(5,1),(6,3),(9,1),(10,3),(13,1),(14,3)]:
            b.area('brick' if wall_h==3 else 'plate','D',xx+1,29,wall_y,wing_w-2,2)
        banded_roof(b,xx,25,17,wing_w,[5,5],'D')
        b.area('tile','D',xx,25,18,wing_w,10)
    b.bag('直柵外框與頂部採光帶')
    # Thirty-six-stud illuminated front. The glazed and white jambs share the outer plane.
    for i,(shape,c,yy) in enumerate([('brick','D',2),('plate','K',5),('brick','D',6),('plate','W',9)]):
        b.step('展廳承台 '+str(i+1),'沿白色展廳外緣砌成深灰承台，中間橫牆承托大跨屋頂。')
        b.ring(shape,c,14,25,yy,36,15,i%2,2)
        b.area(shape,'D',16,31,yy,32,2)
    for i in range(6):
        yy=10+i*3
        b.step('主廳藍色窗列 '+str(i+1),'透明磚與窄白柱交替扣在正面凸點。向左轉可見側面的整片玻璃。')
        b.area('brick','W',14,25,yy,36,1)
        b.area('brick','T',14,26,yy,1,13)
        b.area('brick','T',49,26,yy,1,13)
        b.area('brick','W',15,31,yy,34,2)
        for xx in range(16,48,2):b.put('3005','T',xx,39,yy)
        b.step('白色窗柱 '+str(i+1),'白色窄柱與藍窗交錯排列，兩側白色門框比細柱更寬。')
        if i in (0,1,2,3):b.put('3004','W',14,39,yy)
        if i==4:
            b.put('3245c','W',14,39,yy)
            decal(b,'rd-center','展廳正面左側白色門柱',14.0,7.0)
        b.put('3004','W',48,39,yy)
        for xx in range(17,48,2):
            b.put('3005','W',xx,39,yy)
    b.step('前後窗楣與白框','先連接白色柱頂與玻璃頂端，再將屋頂分成前後兩跨。')
    b.area('plate','W',14,38,28,36,2)
    b.area('plate','W',14,25,28,36,1)
    for xx in [14,49]:b.area('plate','W',xx,26,28,1,12)
    b.area('plate','W',15,31,28,34,2)
    banded_roof(b,14,25,29,36,[7,8],'W')
    b.step('圓角白簷','將彎面磚高的一端朝屋頂、低的一端朝正面，沿窗楣形成連續的白色捲邊。')
    for xx in range(14,50):b.put('11477','W',xx,38,30,1)
    b.step('屋頂中央的長形天窗','先以淺灰光面板框出採光井，再將淺藍窗條與窄金屬板交替排列。')
    b.area('tile','W',14,25,30,36,1)
    for xx in [14,49]:b.area('tile','W',xx,26,30,1,12)
    b.area('tile','L',15,26,30,34,2);b.area('tile','L',15,36,30,34,2)
    b.area('tile','L',15,28,30,2,8);b.area('tile','L',47,28,30,2,8)
    for xx in range(17,47):b.area('tile','T' if xx%2 else 'L',xx,28,30,1,8)
    b.bag('入口、環紋圓廳及圍欄')
    b.step('直窗前的白色入口壁','入口正上方的白色短牆遮住中段窗腳，牆頂約止於藍色直窗的一半。')
    for yy in [2,5,8,11,14,17]:b.put('3010','D' if yy<8 else 'W',31,40,yy)
    b.put('2431','W',31,40,20)
    b.step('前門門柱與低雨棚','門柱托住白色雨棚，最前緣露出透明藍色薄簷。')
    for xx in [30,34]:
        b.area('brick','W',xx,41,2,1,1);b.area('brick','W',xx,41,5,1,1)
    b.area('plate','W',30,41,8,5,2)
    b.area('plate','T',30,41,9,5,2);b.area('tile','W',30,41,10,5,2)
    b.step('西側環紋圓廳及圍欄','每層圓盤和中間圓筒交錯堆疊，形成沿正面車道可見的環紋。')
    for i in range(6):
        if i%2==0:
            b.put('60474','L',6,36,2+i)
        else:b.put('4032a','D',7,37,2+i)
    b.put('60474','L',6,36,8)
    for zz in [36,38,40,42]:b.area('brick','W',1,zz,2,1,1)
    for xx in [2,11]:b.area('plate','G',xx,40,2,4,3)
    b.step('廠前白石步道','延伸至建築兩端的白色鋪面保留中央車道。')
    b.area('tile','W',16,40,2,14,3)
    b.area('tile','W',35,40,2,24,3)
    b.area('tile','W',16,43,2,43,2)
    b.area('tile','D',6,40,2,4,5)
    tile_perimeter(b)
    return b.finish()


def ribbon(Building):
    b=Building('ribbon','FAB 03','JASM 熊本廠','JASM Kumamoto Fab',
        '白色生產棟屋頂的銀色管線與沙金風道平行排列。沿前庭走到 JASM 連廊，可看見五層藍白玻璃辦公棟及後方停車場。',
        56,32,[1.12,.83,1.32],['五層環繞玻璃帶','熊本廠空橋招牌','沙金風道與停車列'],'922961411')
    building_views(b,'左側六道白色廠房面板經有招牌的連廊接到右側五層藍窗辦公棟。','辦公棟貼近前庭，停車位緊接在它的後方。','右後方車輛排成四列，車場和右前辦公樓共用一條地塊。')
    b.foundation('L','L')
    b.bag('白色廠務棟及分段立面')
    for layer in range(5):
        yy=2+3*layer
        b.step('生產棟外殼 '+str(layer+1),'外牆與兩道承重牆逐層交疊，在寬白面板間留出凹縫。')
        b.ring('brick','D' if layer==0 else 'L',10,1,yy,24,21,layer%2)
        for zz in [7,14]:b.area('brick','L',11,zz,yy,22,2)
        b.step('寬白立面板 '+str(layer+1),'六面牆板朝向前庭。首片上端的 JASM 小字標貼在靠左的位置。')
        for xx in range(10,34,4):
            if xx==10 and layer==4:
                b.put('3004','W',xx,22,yy)
                decal(b,'jasm','生產棟最左白色面板上方',12,5)
                b.put('3005','W',xx+2,22,yy)
            else:
                b.area('brick','D' if layer==0 else 'W',xx,22,yy,3,1)
    b.step('後勤附屬建築','獨立的白色設備間位於主廠左側，前端並排放置三支排氣筒。')
    for i in range(4):
        b.ring('brick','D' if i==0 else 'W',1,4,2+3*i,6,16,i%2)
    b.deck('W',1,4,14,6,16,'x')
    for zz in [7,12,15]:
        b.area('plate','L',2,zz,15,4,2)
        for xx in [2,4]:b.put('2412b','L',xx,zz,16)
    for xx in [1,3,5]:chimney(b,xx,21,2,base='W',neck='L')
    for xx in range(10,34,4):b.area('tile','W',xx,22,17,3,1)
    b.step('機電層板面','三排托板橫跨外牆和承重帶，讓每列接縫落在支撐牆上。')
    banded_roof(b,10,1,17,24,[7,7,7],'L')
    for zz in [1,21]:b.area('tile','W',10,zz,18,24,1)
    for xx in [10,33]:b.area('tile','W',xx,2,18,1,19)
    b.bag('成束管線與空調機組')
    b.step('雙材質縱向母管','銀色管束分布在前後兩側，沙金風道在白色送風箱的兩條長邊平行佈置。')
    for zz in [4,7,17]:pipeline(b,16,zz,18,16,cap='L')
    for zz in [9,16]:
        b.area('plate','N',16,zz,18,16,1)
        b.area('tile','N',16,zz,19,16,1)
    b.step('主送風箱與百葉','長條白箱位於屋面中央偏前，兩側的金屬百葉面向風道。')
    b.area('plate','N',17,11,18,14,4)
    b.area('plate','W',17,11,19,14,4)
    b.area('tile','W',17,11,20,14,4)
    for zz in [10,15]:
        for xx in range(17,31,2):b.put('2412b','L',xx,zz,18)
    b.step('儲罐與煙囪群','機房左側是一整條儲罐和立管，能從建築側面看見高低錯落的管口。')
    for zz in [3,7,11,15,19]:
        for xx in [12,14]:
            if zz in [7,15]:chimney(b,xx,zz,18,base='N',neck='D',tall=xx==12)
            else:cylinder(b,xx,zz,18,body='N',double=zz==19)
    for xx in [17,21,25,29]:b.put('85861','D',xx,19,18)
    b.bag('辦公棟的五道藍色窗帶')
    for level in range(5):
        yy=2+4*level
        b.step('連續樓板 '+str(level+1),'右前角辦公棟的面寬是進深兩倍，兩層白板在四個角位交錯。')
        b.ring('plate','W',39,15,yy,16,9,level%2,2)
        b.ring('plate','W',39,15,yy+1,16,9,level%2==0,2)
        b.step('環繞淺藍窗 '+str(level+1),'每面以兩層透明薄板形成水平窗帶，背面的窗戶面向停車場。')
        for inner in range(2):b.ring('plate','T',39,15,yy+2+inner,16,9,inner==1)
        b.step('屋頂中梁 '+str(level+1),'橫向承重牆與這層窗框等高，可承托前後兩跨的退台屋頂。')
        b.area('brick','W',41,19,yy,12,2)
        b.area('plate','W',41,19,yy+3,12,2)
    b.step('辦公棟退台屋頂','兩列跨板扣在外牆和中梁上，邊緣用白色光面板收口。')
    banded_roof(b,39,15,22,16,[5,4],'W')
    b.ring('tile','W',39,15,23,16,9)
    b.area('plate','W',40,16,23,14,7)
    b.step('屋頂散熱縱條','深色百葉偏向後側停車場，前半部屋頂保留大片白色。')
    b.ring('tile','W',40,16,24,14,7)
    for zz in range(17,22):
        b.area('tile','D' if zz in [17,19] else 'L' if zz==18 else 'W',41,zz,24,12,1)
    b.bag('空橋銘牌、車列與草坪')
    b.step('連廊橋腳','兩側灰柱托起白色連廊，橋下的開口對準前庭綠帶缺口。')
    for xx in [34,37]:
        b.area('brick','D',xx,19,2,2,5)
        b.area('brick','D',xx,19,5,2,5)
    b.area('plate','W',34,19,8,5,5)
    for yy in [9,12]:
        b.area('brick','W',34,19,yy,5,4)
        if yy==9:b.area('brick','W',34,23,yy,5,1)
    b.step('印有 JASM 的白色入口','將入口字標貼在白色長磚的正面，再加上連廊天花與白色屋頂。')
    b.put('3010','W',34,23,12)
    decal(b,'jasm','連廊正面上方白色銘板',23,8)
    b.put('3005','W',38,23,12)
    b.area('plate','W',34,19,15,5,5)
    b.area('tile','W',34,19,16,5,5)
    b.step('右後停車場及停車格','按照俯視圖在辦公棟後側排出四列車位，車輛朝向側邊車道。')
    parking=[
        ['U','W','K','R','L','W','R'],
        ['K','T','R','D','W','N','K'],
        ['L','R','W','U','R','K','D'],
        ['W','K','N','R','U','L','N'],
    ]
    for col,car_colors in enumerate(parking):
        xx=39+4*col
        for row,c in enumerate(car_colors):
            zz=1+2*row
            b.put('3623','K',xx,zz,2)
            b.put('3023',c,xx,zz,3)
            b.put('3070b','L' if c=='K' else c,xx+1,zz,4)
        b.area('tile','L',xx+3,1,2,1,14)
    b.step('草坪與步道缺口','沿前緣鋪設兩段綠籬，留下對準 JASM 連廊的入口。')
    for zz in [27,29]:
        hedge(b,1,zz,2,33)
        hedge(b,40,zz,2,15)
    tile_perimeter(b)
    return b.finish()


def graphite(Building):
    b=Building('graphite','FAB 04','亞利桑那晶圓廠','Arizona Fab',
        '黑色基座與三道厚扶壁托住內凹的機電屋頂，沙金色設備列穿插銀灰管路。右側冷卻棟有雙列風扇及藍色冷卻槽，晶圓標誌位於主樓右前角。',
        48,30,[-.48,1.08,1.32],['晶圓廠徽與厚扶壁','雙列沙金設備和管網','冷卻槽與九座風扇'],'923365290')
    building_views(b,'三道深色扶壁分割主樓立面，晶圓圓徽位在右上角。','較矮的冷卻棟在前，白頂設備間退到後方，中間留出一段沙色場坪。','兩座設備棟之間有縱向窄棟。架高的橫廊從主樓跨過窄棟，通向右前冷卻棟。')
    b.foundation('N','N')
    b.bag('主樓、立柱與晶圓銘牌')
    courses=[('brick','K',2),('plate','K',5),('brick','L',6),('brick','L',9),
             ('brick','L',12),('brick','L',15),('brick','L',18)]
    for n,(shape,c,yy) in enumerate(courses):
        b.step('外牆與屋頂承重帶 '+str(n+1),'灰牆退入深色扶壁後方，中央兩道橫牆承托頂部設備層。')
        b.area(shape,c,3,3,yy,25,1)
        # A near-black horizontal ribbon remains visible behind the projecting side piers.
        for xx in [3,27]:b.area(shape,'S' if yy in [9,15] else c,xx,4,yy,1,20)
        b.area(shape,c,3,24,yy,22,1)
        if shape=='plate':
            b.area(shape,c,25,24,yy,3,1)
        else:
            if yy==15:
                b.put('3245c','L',25,24,yy)
                decal(b,'tsmc','主廠房正面右上晶圓圓徽',14.0,14.0)
            elif yy!=18:
                b.put('3004',c,25,24,yy)
            b.put('3005',c,27,24,yy)
        for zz in [9,16]:b.area(shape,'D',4,zz,yy,23,2)
        b.step('三道前扶壁與西側黑柱 '+str(n+1),'正面三道厚扶壁各寬兩格，側邊深色立柱向外凸出一格。')
        for xx in [4,13,22]:b.area(shape,'D',xx,25,yy,2,1)
        for zz in [4,10,17,22]:b.area(shape,'K',2,zz,yy,1,2)
        for xx in [4,13,22]:b.area(shape,'D',xx,2,yy,2,1)
    b.step('設備井托板','三列托板分跨外牆和橫向承重帶；深灰壓頂比機電面高出兩層薄板。')
    banded_roof(b,3,3,21,25,[7,7,8],'D')
    b.ring('plate','D',3,3,22,25,22)
    b.ring('tile','D',3,3,23,25,22,True)
    for xx in [4,13,22]:b.area('tile','D',xx,25,21,2,1)
    for zz in [4,10,17,22]:b.area('tile','K',2,zz,21,1,2)
    for xx in [4,13,22]:b.area('tile','D',xx,2,21,2,1)
    b.bag('沙金空調箱與銀灰工藝管網')
    b.step('五道主幹管','從井的後側往前組裝，讓圓桿對準下一段管端。第二和第四列留下中段支線空間。')
    for xx,zz,ln in [(5,4,22),(5,9,12),(21,9,6),(5,13,22),(5,18,16),(23,18,4),(5,22,22)]:
        pipeline(b,xx,zz,22,ln,cap='L')
    b.step('橫向回管及集管器','窄端的回管轉九十度，管線高低差由旁邊的圓筒集管器表示。')
    for xx,zz in [(26,6),(5,15),(26,20)]:pipeline(b,xx,zz,22,2,1,cap='L')
    b.step('兩排沙金熱交換箱','每列由兩具長形設備組成，淺灰底、沙色機身和光面箱蓋都可逐件拆卸。')
    for zz in [6,15]:
        for xx in [6,16]:
            b.area('plate','D',xx,zz,22,8,2)
            b.area('plate','N',xx,zz,23,8,2)
            b.area('tile','N',xx,zz,24,8,2)
    b.step('直立煙管與排氣肩圈','設備長邊排列粗細不同的煙管，較高的立管放在後方。')
    for xx,zz,tall in [(6,8,False),(8,8,True),(15,6,True),(19,11,True),(21,11,False),
                         (23,11,True),(12,17,False),(14,17,True),(18,20,False),(20,20,True)]:
        chimney(b,xx,zz,22,tall=tall)
    b.step('圓罐群與風機格柵','在管束之間補入短罐、開口端蓋及低矮的沙色散熱機組。')
    for xx,zz in [(5,11),(7,11),(9,11),(12,11),(14,11),(17,8),(19,8),(22,17),(24,17),
                  (6,20),(8,20),(12,20),(15,20)]:cylinder(b,xx,zz,22)
    for xx,zz in [(18,9),(22,20)]:
        b.put('3022','N',xx,zz,22)
        for dz in [0,1]:b.put('2412b','N',xx,zz+dz,23)
    b.bag('冷卻翼樓、風扇與連廊')
    for i,(shape,c,yy) in enumerate([('brick','K',2),('brick','D',5),('brick','L',8),('brick','L',11)]):
        b.step('右前冷卻翼樓 '+str(i+1),'先組裝較矮的右前機房，中央黑柱略為凸出淺灰前牆。')
        b.ring(shape,c,36,11,yy,10,15,i%2)
        for zz in [15,20]:b.area(shape,'D',37,zz,yy,8,2)
        b.area('brick','K',39,26,yy,3,1)
        for zz in [12,21]:b.put('3005','K',46,zz,yy)
    b.step('冷卻井板面與外框','翼樓頂板分三跨扣上，深灰邊框圍住設備並留下內凹槽。')
    banded_roof(b,36,11,14,10,[5,5,5],'D')
    b.ring('plate','D',36,11,15,10,15)
    b.ring('tile','D',36,11,16,10,15,True)
    b.step('冷卻井內的兩列風扇','左列風扇向前多延伸兩格。右列前端銜接階梯狀的冷卻槽。')
    for xx,rows in [(37,5),(40,4)]:
        b.area('plate','N',xx,12,15,2,rows*2)
        for zz in range(12,12+2*rows,2):b.put('4032a','L',xx,zz,16)
    b.step('階梯形冷卻槽及泵管','透明藍槽從前端左側逐段向右後方延伸，右後的短泵管突出屋框。')
    for xx,zz,w,d in [(37,22,2,3),(39,21,3,4),(42,18,3,7)]:
        b.area('plate','T',xx,zz,15,w,d)
        b.area('tile','T',xx,zz,16,w,d)
    pipeline(b,43,12,15,4,1,cap='L')
    chimney(b,44,14,15)
    b.step('右後獨立白頂設備間','沿右後角砌起狹長的深灰機房，長軸朝前後，與右前冷卻棟之間留出場坪。')
    for yy in [2,5,8]:b.ring('brick','D',43,1,yy,4,8,yy%2)
    b.deck('D',43,1,11,4,8,'x')
    b.ring('tile','D',43,1,12,4,8)
    b.area('tile','W',44,2,12,2,6)
    b.step('中央縱向低棟','從後方沿縱軸連續砌至主廠房前端，左右深色牆包著淺灰屋面。')
    for yy in [2,5]:
        b.ring('brick','D',30,4,yy,4,22,yy%2)
    b.deck('D',30,4,8,4,22,'x')
    for xx,c,w in [(30,'D',1),(31,'L',2),(33,'D',1)]:
        b.area('tile',c,xx,4,9,w,22)
    b.step('架高的橫向連廊','架起位於縱棟兩旁的橋腳，再以八格長板跨過低棟，在機房之間形成十字交會。')
    for xx in [28,34]:
        for yy in [2,5,8]:b.area('brick','K',xx,14,yy,2,3)
    b.deck('L',28,14,11,8,3,'x')
    b.area('brick','D',28,14,12,8,3)
    b.area('tile','L',28,14,15,8,3)
    tile_perimeter(b)
    return b.finish()

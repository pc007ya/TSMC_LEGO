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


def fins(Building):
    b=Building('fins','FAB 02','全球研發中心','Global R&D Center',
        '白色圓邊展廳跨在兩座煙灰玻璃翼樓之間。十六扇細直窗與屋頂採光帶呼應，左側沙藍端牆後方保留開放的機電庭院。',
        60,40,[-.91,.99,1.30],['十六道垂直藍窗','研發中心入口銘牌','開放式機電庭院'],'926523184')
    b.foundation('W','W')
    b.bag('沙藍機電中庭')
    # The deck is recessed below the rear parapet so risers and manifolds project from the well.
    for level,(kind,c) in enumerate([('brick','W'),('plate','A'),('brick','B'),('brick','B')]):
        yy=[2,5,6,9][level]
        b.step('後棟結構層 '+str(level+1),'外殼左端使用沙藍色長牆；中線承重帶托住後方機電樓板。')
        b.ring(kind,c,2,2,yy,54,17,level%2)
        for zz in [7,13]:b.area(kind,c,3,zz,yy,52,2)
    b.step('機電井平台','三列短跨板的接縫落在兩道承重帶上。')
    banded_roof(b,2,2,12,54,[6,6,5],'L')
    b.step('沙藍端牆與白色牆頂','左端牆比平台高二層磚，從前方透過白框可見內部管線。')
    b.area('brick','B',2,2,13,1,17);b.area('brick','B',2,2,16,1,17)
    b.area('tile','B',2,2,19,1,17)
    b.area('brick','W',3,2,13,53,1);b.area('tile','W',3,2,16,53,1)
    b.area('brick','B',55,3,13,1,16);b.area('tile','B',55,3,16,1,16)
    b.step('後排銀灰集管','窄長把手端對端形成連續的銀色管路。把手伸向空出的通道。')
    pipeline(b,4,4,13,48,cap='L')
    pipeline(b,4,11,13,14,cap='L')
    pipeline(b,27,11,13,24,cap='L')
    b.step('設備間隔板','在後棟架起四道橫隔，頂端以白色光面板收口。')
    for xx in [14,28,40,50]:
        b.area('brick','W',xx,6,13,2,4)
        b.area('tile','W',xx,6,16,2,4)
    b.step('閥組、換氣機與立管','每組高低立管旁留一格維護空間。中間的格柵是送風機，沙色圓罐採銀色肩口。')
    for xx in [5,10,18,24,32,37,44,47]:
        chimney(b,xx,7,13,tall=xx in (10,24,37))
        cylinder(b,xx+1,7,13,body='N')
    for xx in [4,17,31]:
        for off in [0,2,4]:b.put('2412b','D',xx+off,9,13)
    b.step('中庭前緣的送風機與樓板收口','兩組白色管道跨過前側機井，光面鋪板留出中間的排氣口。')
    for xx in [5,20,36,49]:
        equipment_box(b,xx,14,13,4,3,'L','W')
    pipeline(b,9,17,13,34,cap='L')
    b.bag('雙側煙灰幕牆')
    for xx,wing_w in [(1,13),(50,9)]:
        for i,(shape,c) in enumerate([('brick','D'),('plate','K'),('brick','S'),('plate','K'),('brick','S'),('plate','K'),('brick','S')]):
            yy=[2,5,6,9,10,13,14][i]
            b.step('側翼水平窗 '+str(i+1),'以黑色橫框夾住煙灰玻璃；窄翼樓兩端的水平線需對齊。')
            b.ring(shape,c,xx,19,yy,wing_w,10,i%2)
        b.step('側翼石墨平頂','在煙灰窗頂橫架屋頂，封成平滑的深灰盒體。')
        for wall_y,wall_h in [(2,3),(5,1),(6,3),(9,1),(10,3),(13,1),(14,3)]:
            b.area('brick' if wall_h==3 else 'plate','D',xx+1,23,wall_y,wing_w-2,2)
        banded_roof(b,xx,19,17,wing_w,[5,5],'D')
        b.area('tile','D',xx,19,18,wing_w,10)
    b.bag('直柵外框與頂部採光帶')
    # Thirty-six-stud illuminated front. The glazed and white jambs share the outer plane.
    for i,(shape,c,yy) in enumerate([('brick','D',2),('plate','K',5),('brick','D',6),('plate','W',9)]):
        b.step('展廳承台 '+str(i+1),'沿白色展廳外緣砌成深灰承台，中間橫牆承托大跨屋頂。')
        b.ring(shape,c,14,19,yy,36,15,i%2,2)
        b.area(shape,'D',16,25,yy,32,2)
    for i in range(6):
        yy=10+i*3
        b.step('主廳藍色窗列 '+str(i+1),'透明磚與窄白柱交替扣在正面凸點。向左轉可見側面的整片玻璃。')
        b.area('brick','W',14,19,yy,36,1)
        b.area('brick','T',14,20,yy,1,13)
        b.area('brick','T',49,20,yy,1,13)
        b.area('brick','W',15,25,yy,34,2)
        for xx in range(16,48,2):b.put('3005','T',xx,33,yy)
        b.step('白色窗柱 '+str(i+1),'白色窄柱與藍窗交錯排列，兩側白色門框比細柱更寬。')
        if i in (0,1,4,5):b.put('3004','W',14,33,yy)
        if i==2:
            b.put('3245c','W',14,33,yy)
            decal(b,'rd-center','展廳正面左側白色門柱',14.0,7.0)
        b.put('3004','W',48,33,yy)
        for xx in range(17,48,2):
            b.put('3005','W',xx,33,yy)
    b.step('前後窗楣與白框','先連接白色柱頂與玻璃頂端，再將屋頂分成前後兩跨。')
    b.area('plate','W',14,32,28,36,2)
    b.area('plate','W',14,19,28,36,1)
    for xx in [14,49]:b.area('plate','W',xx,20,28,1,12)
    b.area('plate','W',15,25,28,34,2)
    banded_roof(b,14,19,29,36,[7,8],'W')
    b.step('圓角白簷','將彎面磚高的一端朝屋頂、低的一端朝正面，沿窗楣形成連續的白色捲邊。')
    for xx in range(14,50):b.put('11477','W',xx,32,30,1)
    b.step('屋頂中央的長形天窗','先以淺灰光面板框出採光井，再將淺藍窗條與窄金屬板交替排列。')
    b.area('tile','W',14,19,30,36,1)
    for xx in [14,49]:b.area('tile','W',xx,20,30,1,12)
    b.area('tile','L',15,20,30,34,2);b.area('tile','L',15,30,30,34,2)
    b.area('tile','L',15,22,30,2,8);b.area('tile','L',47,22,30,2,8)
    for xx in range(17,47):b.area('tile','T' if xx%2 else 'L',xx,22,30,1,8)
    b.bag('入口、圓罐及圍欄')
    b.step('直窗前的白色入口壁','入口正上方的白色短牆遮住中段窗腳，牆頂約止於藍色直窗的一半。')
    for yy in [2,5,8,11,14,17]:b.put('3010','D' if yy<8 else 'W',31,34,yy)
    b.put('2431','W',31,34,20)
    b.step('前門門柱與低雨棚','門柱托住白色雨棚，最前緣露出透明藍色薄簷。')
    for xx in [30,34]:
        b.area('brick','W',xx,35,2,1,1);b.area('brick','W',xx,35,5,1,1)
    b.area('plate','W',30,35,8,5,2)
    b.area('plate','T',30,35,9,5,2);b.area('tile','W',30,35,10,5,2)
    b.step('分層圓罐及圍欄','每層圓盤和中間圓筒交錯堆疊，形成沿正面車道可見的環紋。')
    for i in range(6):
        if i%2==0:
            b.put('60474','L',6,30,2+i)
        else:b.put('4032a','D',7,31,2+i)
    b.put('60474','L',6,30,8)
    for zz in range(3,19,4):
        b.put('3023','G',1,zz,2,1);b.put('3062b','G',1,zz,3);b.put('4073','G',1,zz,6)
    for zz in [30,32,34,36]:b.area('brick','W',1,zz,2,1,1)
    for xx in [2,11]:b.area('plate','G',xx,34,2,4,3)
    b.step('廠前白石步道','延伸至建築兩端的白色鋪面保留中央車道。')
    b.area('tile','W',16,34,2,14,3)
    b.area('tile','W',35,34,2,24,3)
    b.area('tile','W',16,37,2,43,2)
    b.area('tile','D',6,34,2,4,5)
    tile_perimeter(b)
    return b.finish()


def ribbon(Building):
    b=Building('ribbon','FAB 03','JASM 熊本廠','JASM Kumamoto Fab',
        '白色生產棟屋頂的銀色管線與沙金風道平行排列。沿前庭走到 JASM 連廊，可看見五層藍白玻璃辦公棟及旁側停車列。',
        56,26,[1.12,.83,1.32],['五層環繞玻璃帶','熊本廠空橋招牌','沙金風道與停車列'],'922961411')
    b.foundation('L','L')
    b.bag('白色廠務棟及分段立面')
    # Large ribbed cleanroom block with a lower, separate west service room.
    for layer in range(5):
        yy=2+3*layer
        b.step('生產棟外殼 '+str(layer+1),'外牆與兩道承重線逐層交疊。在窗邊保留退縮的灰色縱縫。')
        b.ring('brick','D' if layer==0 else 'L',6,2,yy,24,15,layer%2)
        for zz in [6,11]:b.area('brick','L',7,zz,yy,22,2)
        b.step('寬白立面板 '+str(layer+1),'大面白牆往前凸一格，各面板間留一道深色凹縫。')
        for xx in range(6,30,4):
            b.area('brick','D' if layer==0 else 'W',xx,17,yy,3,1)
        # Upper courses overlap the side and rear pieces of the shell.
        if layer==0:b.area('plate','L',1,5,2,5,10)
    b.step('後勤設備間','生產棟左端接一間較低的白色附屬房，正面留三座排氣筒。')
    for i in range(4):
        b.ring('brick','D' if i==0 else 'W',1,5,3+3*i,5,10,i%2)
    b.deck('W',1,5,15,5,10,'x')
    for zz in [6,10]:
        b.area('plate','L',2,zz,16,3,2)
        b.put('2412b','D',2,zz,17)
    for xx in [1,3,5]:
        chimney(b,xx,16,2,base='W',neck='L',tall=False)
    for xx in range(6,30,4):b.area('tile','W',xx,17,17,3,1)
    b.step('機電層板面','三排薄板橫跨外牆與承重帶，先完成屋頂的穩固支架。')
    banded_roof(b,6,2,17,24,[5,5,5],'L')
    b.area('tile','W',6,2,18,24,1)
    b.area('tile','W',6,16,18,24,1)
    for xx in [6,29]:b.area('tile','W',xx,3,18,1,13)
    b.bag('成束管線與空調機組')
    b.step('雙材質縱向母管','銀色管線旁堆疊沙金色扁管；兩側管束之間保留檢修步道。')
    for zz,length,xx in [(3,20,8),(13,20,8)]:
        pipeline(b,xx,zz,18,length,cap='L')
    for zz in [5,12]:
        b.area('plate','N',14,zz,18,14,1);b.area('tile','N',14,zz,19,14,1)
    b.step('主送風箱與百葉','中央白色長形機組位於沙色設備座上，兩端用金屬格柵封口。')
    b.area('plate','N',15,7,18,12,3)
    b.area('plate','W',15,7,19,12,3)
    b.area('tile','W',15,7,20,12,3)
    for zz in [6,10]:
        for xx in [15,17,19,21,23,25]:b.put('2412b','L',xx,zz,18)
    b.step('儲罐與煙囪群','每組沙色儲罐加裝銀色開口肩圈，後排排氣管使用較長的頸管。')
    for xx in [8,10,12]:
        cylinder(b,xx,6,18,body='N',double=True)
        cylinder(b,xx,10,18,body='N')
    for xx in [8,10,12]:chimney(b,xx,8,18,base='N',neck='D',tall=True)
    for xx in [15,19,23,27]:b.put('85861','D',xx,15,18)
    b.bag('辦公棟的五道藍色窗帶')
    # Broad white floor plates bridge the corners around continuous courses of glass.
    for level in range(5):
        yy=2+4*level
        b.step('連續樓板 '+str(level+1),'二格寬樓板沿四面環繞一圈。次層板轉換角位接法，鎖緊接縫。')
        b.ring('plate','W',35,5,yy,16,14,level%2,2)
        b.ring('plate','W',35,5,yy+1,16,14,level%2==0,2)
        b.step('環繞淺藍窗 '+str(level+1),'玻璃與白色樓板外緣對齊，每面以兩層透明薄板接成相連的水平窗帶。')
        for inner in range(2):
            b.ring('plate','T',35,5,yy+2+inner,16,14,inner==1)
        b.step('屋頂中梁 '+str(level+1),'在建物內部放置橫牆及其上薄板，承接辦公棟的整片白色屋頂。')
        for zz in [9,14]:
            b.area('brick','W',37,zz,yy,12,2)
            b.area('plate','W',37,zz,yy+3,12,2)
    b.step('辦公棟退台屋頂','兩列跨板分別扣在玻璃和屋內承重牆，邊緣與正面玻璃對齊。')
    banded_roof(b,35,5,22,16,[8,6],'W')
    b.ring('tile','W',35,5,23,16,14)
    b.area('plate','W',36,6,23,14,12)
    b.step('屋頂散熱縱條','三條石墨色百葉拼在白色退台上，四周光面白框與外牆對齊。')
    b.ring('tile','W',36,6,24,14,12)
    for zz in range(7,17):
        if 8<=zz<=12:
            b.area('plate','L',37,zz,24,12,1)
        else:b.area('tile','W',37,zz,24,12,1)
    for zz in range(8,13):
        b.area('tile','D' if zz%2==0 else 'L',37,zz,25,12,1)
    b.bag('空橋銘牌、車列與草坪')
    b.step('空橋橋腳','兩側灰柱托起連廊，入口保留上下兩道水平遮簷。')
    for xx in [30,33]:
        b.area('brick','D',xx,16,2,2,3)
        b.area('brick','D',xx,16,5,2,3)
    b.area('plate','W',30,15,8,5,3)
    b.area('plate','W',30,18,8,5,2)
    b.area('brick','W',30,15,9,5,3)
    b.area('brick','W',30,18,9,5,1)
    b.step('印有 JASM 的白色入口','將字標貼在白色長磚的正面，讓它面向草坪中央的進入步道。')
    b.put('3010','W',30,18,12)
    decal(b,'jasm','空橋正面上方白色銘板',23,8)
    b.put('3005','W',34,18,12)
    b.area('brick','W',30,15,12,5,3)
    b.area('plate','W',30,15,15,5,4);b.area('tile','W',30,15,16,5,4)
    b.step('五輛微型車與停車格','車輛朝向辦公棟，以黑色底盤、車身與亮面車頂分層。車格間嵌入白線。')
    for zz,c in [(4,'K'),(7,'W'),(10,'R'),(13,'U'),(16,'W')]:
        b.put('3623','K',52,zz,2)
        b.put('3023',c,52,zz,3);b.put('3070b',c,54,zz,3)
        b.put('3070b','L' if c=='K' else c,53,zz,4)
        b.put('63864','W',52,zz+1,2)
    b.step('草坪與步道缺口','沿前緣鋪設兩段綠籬，留下對準 JASM 空橋的入口。')
    hedge(b,1,23,2,27);hedge(b,36,23,2,18)
    tile_perimeter(b)
    return b.finish()


def graphite(Building):
    b=Building('graphite','FAB 04','亞利桑那晶圓廠','Arizona Fab',
        '黑色基座與三道厚扶壁托住內凹的機電屋頂，沙金色設備列穿插銀灰管路。右側冷卻棟有雙列風扇及藍色冷卻槽，晶圓標誌位於主樓右前角。',
        48,28,[-.48,1.08,1.32],['晶圓廠徽與厚扶壁','雙列沙金設備和管網','冷卻槽與八座風扇'],'923365290')
    b.foundation('N','N')
    b.bag('主樓、立柱與晶圓銘牌')
    courses=[('brick','K',2),('plate','K',5),('brick','L',6),('brick','L',9),
             ('brick','L',12),('brick','L',15),('brick','L',18)]
    for n,(shape,c,yy) in enumerate(courses):
        b.step('外牆與屋頂承重帶 '+str(n+1),'灰牆退入深色扶壁後方，中央兩道橫牆承托頂部設備層。')
        b.area(shape,c,3,3,yy,25,1)
        for xx in [3,27]:b.area(shape,c,xx,4,yy,1,20)
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
    b.step('設備井托板','三列托板分跨外牆和橫向承重帶；深灰壓頂比機電面高出兩層薄板。')
    banded_roof(b,3,3,21,25,[7,7,8],'D')
    b.ring('plate','D',3,3,22,25,22)
    b.ring('tile','D',3,3,23,25,22,True)
    for xx in [4,13,22]:b.area('tile','D',xx,25,21,2,1)
    for zz in [4,10,17,22]:b.area('tile','K',2,zz,21,1,2)
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
        b.step('冷卻翼樓外框 '+str(i+1),'黑色牆腳托起較低的灰色翼樓，前柱與側框包住屋頂冷卻井。')
        b.ring(shape,c,35,5,yy,10,18,i%2)
        for zz in [10,16]:b.area(shape,'D',36,zz,yy,8,2)
        b.area('brick','K',38,23,yy,3,1)
        for zz in [6,16]:b.put('3005','K',45,zz,yy)
    b.step('冷卻井板面與外框','翼樓頂板分三跨扣上，深灰邊框圍住設備並留下內凹槽。')
    banded_roof(b,35,5,14,10,[6,6,6],'D')
    b.ring('plate','D',35,5,15,10,18)
    b.ring('tile','D',35,5,16,10,18,True)
    b.step('四乘二風扇陣列','沙色長台位於翼樓後半部，上方八片圓形風扇成兩列。')
    b.area('plate','N',36,8,15,7,8)
    for xx in [37,40]:
        for zz in [8,10,12,14]:b.put('4032a','L',xx,zz,16)
    b.step('透明冷卻槽及泵浦','由淺藍光面板與透明薄板組成兩個錯位的水面，將兩支泵管放在灰色走道。')
    for xx,zz,w,d in [(36,17,5,2),(39,19,5,2)]:
        b.area('plate','T',xx,zz,15,w,d)
        b.area('tile','T',xx,zz,16,w,d)
    for xx,zz in [(42,17),(37,20)]:chimney(b,xx,zz,15,tall=False)
    b.step('後側獨立機房','深灰外殼向上延伸，中央白色長板標出另一棟較高的方形機房。')
    b.area('brick','D',36,6,15,8,2)
    b.area('tile','L',36,6,18,8,1);b.area('tile','W',36,7,18,8,1)
    b.step('後部高位機房','小機房自底座起砌，在冷卻棟後端抬高兩層磚，白色長頂嵌在深灰框內。')
    for yy in [2,5,8,11,14,17]:b.ring('brick','D',36,1,yy,8,4,yy%2)
    b.deck('D',36,1,20,8,4)
    b.ring('tile','D',36,1,21,8,4)
    b.area('tile','W',37,2,21,6,2)
    b.step('平接廊與前方服務間','一條架高的連廊在兩棟間橫向跨接，前方另設矮灰色設備間。')
    for xx in [28,33]:b.area('brick','K',xx,11,2,2,3)
    b.area('plate','L',28,11,5,7,3)
    b.area('brick','D',28,11,6,7,3)
    b.area('plate','D',28,11,9,7,3);b.area('tile','L',28,11,10,7,3)
    for yy in [2,5]:b.area('brick','D',29,17,yy,4,6)
    b.area('tile','L',29,17,8,4,6)
    tile_perimeter(b)
    return b.finish()

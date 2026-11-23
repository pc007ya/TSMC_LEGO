"""Collector-scale vignette of the public courtyard at Giant's Rinan manufacturing plant."""
from collections import defaultdict
from itertools import groupby
from math import ceil

from design import parts, stock
from industrial_models import building_views, decal


def strips(b, kind, color, x, z, y, length, *, along_z=False, joint=6, offset=0):
    """Stagger siding, curb and brick joints along successive courses."""
    left=length
    while left:
        n=min(left,offset or joint)
        b.area(kind,color,x,z,y,1 if along_z else n,n if along_z else 1)
        if along_z:z+=n
        else:x+=n
        left-=n
        offset=0


def facade_wall(b, start_y, stop_y, course, front):
    """Perimeter masonry and roof bearings; each tenon grid stays hollow between ribs."""
    for y in range(start_y,stop_y,3):
        row=(y-2)//3
        b.step(f'廠房{course} · 牆帶 {row+1}',
               '由後牆向兩端轉角砌。外側每塊長板的立縫與上一層錯開，中央支柱和橫肋為下一層樓面留足扣點。')
        strips(b,'brick','N',4,3,y,56,joint=6,offset=3 if row%2 else 0)
        for x in (4,59):
            strips(b,'brick','N',x,4,y,16,along_z=True,joint=6,offset=3 if row%2 else 0)
        for x in (7,15,23,31,39,47,55):
            for z in (7,14): b.put('3003','L',x,z,y)
        if front:
            strips(b,'brick','N',4,20,y,56,joint=6,offset=3 if row%2 else 0)


def dock_and_trailers(b):
    b.bag('月台地坪、拖架與貨櫃列')
    b.step('月台後退的第一級基礎','灰色裝卸平台比廠房立面後退三格，數個平台共用一條連續防撞邊。前方留貨櫃拖架的空間。')
    b.area('plate','D',5,16,2,54,3)
    b.area('plate','L',5,16,3,54,3)
    b.step('貨台門、黑膠護角與防撞墩','以深灰磚做退縮的捲門，門柱左右加黑色護條。黃色系的月台邊在各門前留出裝卸區。')
    for x in range(6,55,7):
        b.area('brick','D',x,17,4,6,1)
        for xx in (x,x+5): b.put('3005','K',xx,18,4)
        b.area('plate','L',x,17,7,6,1)
    # Each trailer rests on two pairs of axle housings. The centre is clear under the rails.
    for no,(x,color,rib) in enumerate(((6,'U','U'),(13,'O','D'),(20,'R','D'),(27,'G','G'),
                                      (34,'O','D'),(41,'R','D'),(48,'G','G')),1):
        b.step(f'第 {no} 座貨櫃拖架','兩排黑色單孔磚的輪心朝兩側。橫向底板跨在兩邊輪架和車頭支腳上，讓兩軸之間可以看到底板下方。')
        for xx in (x,x+3):
            for zz in (24,27): b.put('3700','K',xx,zz,2,1)
        for xx in (x,x+3): b.put('3005','D',xx,19,2)
        for zz,d in ((19,6),(25,4)):
            b.area('plate','D',x,zz,5,4,d)
        b.step(f'第 {no} 個貨櫃 · 側肋與門鎖','將貨櫃前後端扣在拖架上，再沿兩條長邊向中間砌。格柵與窄色肋交替，雙門中央留下深色鎖縫。')
        for row in range(2):
            y=6+3*row
            b.area('brick',color,x,19,y,4,1)
            for xx,r in ((x,1),(x+3,3)):
                for zz in range(20,28,2):
                    if color in ('U','G','O'): b.put('2877',color,xx,zz,y,r)
                    else:
                        b.put('3005',color,xx,zz,y)
                        b.put('3005','O' if color=='R' else 'R',xx,zz+1,y)
            b.area('brick',color,x,28,y,4,1)
        b.step(f'第 {no} 個貨櫃 · 頂板與防撞角','四角包邊鎖住兩側肋板，頂部用窄光面片與格柵交替排列。')
        b.area('plate',color,x,19,12,4,10)
        for zz in range(19,29):
            if zz in (19,28):b.area('tile',rib,x,zz,13,4,1)
            elif zz%2: b.area('tile',color,x,zz,13,4,1)
            else:
                for xx in (x,x+2):b.put('2412b',color,xx,zz,13)
    b.bag('廠房底層鋼柱與檐下裝卸區')
    facade_wall(b,2,14,'下部',False)
    for row in range(4):
        y=2+row*3
        b.step(f'裝卸門廊 · 柱頭第 {row+1} 層','在相鄰貨櫃的間隙對齊雙格柱。靠外的支柱托住二樓裝卸雨簷，背面的捲門留在陰影內。')
        for x in (4,11,18,25,32,39,46,53,58): b.put('3003','L',x,20,y)
        if row>=2:
            for x in range(6,55,7): b.area('brick','D',x,17,y,6,1)
    b.step('底層上緣的縱橫承梁','把八格薄板跨在相鄰柱頭，前後向承梁再壓過橫接縫。裝卸平台上方由後往前封住。')
    for z in (7,14):
        for x in (8,16,24,32,40,48): b.put('3034','D',x,z,14)
        for x in (7,56): b.put('3023','D',x,z,14,1)
    b.ring('plate','L',4,3,14,56,19)
    for x in range(4,60,4):
        for z,d in ((3,6),(9,8),(17,6)): b.area('plate','L',x,z,15,4,d)
    b.step('連續外挑簷與底部包板','沙色薄板伸出裝卸線，前緣用交錯的淺色包板形成長水平帶，兩端收齊山牆。')
    for x in range(4,60,4):
        b.put('3031','N',x,20,16)
    b.area('plate','N',4,3,16,56,17)
    strips(b,'plate','W',4,23,17,56,joint=8)
    for x in range(4,60,4): b.put('2431','N',x,22,17)


def signed_hall(b):
    b.bag('淡黃立面、四段 GIANT 大招牌與豎窗')
    # The four smooth panels belong to a single flush elevation; each cut fits one panel.
    for row in range(5):
        y=17+row*3
        b.step(f'大招牌外牆 · 面板邊帶 {row+1}','兩端牆角跨接後牆，窄窗留在招牌的右側。每塊印有藍色圖形的面板朝外對齊，接縫可分開拆裝。')
        strips(b,'brick','N',4,3,y,56,joint=6,offset=3 if row%2 else 0)
        for x in (4,59): strips(b,'brick','N',x,4,y,16,along_z=True,joint=6,offset=2 if row%2 else 0)
        for x in (7,15,23,31,39,47,55):
            for z in (7,14): b.put('3003','L',x,z,y)
        strips(b,'brick','N',4,20,y,3)
        if row==0:
            for i in range(4):
                b.put('59349','N',7+6*i,20,y)
                decal(b,f'giant-sign-{i+1}',f'淡黃廠房大招牌 · 左起第 {i+1} 幅',47.8,32.81)
        for x,w in ((31,4),(36,6),(43,6),(50,5),(56,4)): strips(b,'brick','N',x,20,y,w)
        for x in (35,42,49,55):
            for i,color in enumerate(('L','S','S')): b.put('3024',color,x,20,y+i)
    b.step('招牌上方檢修燈與收邊','先用通長米色板跨過圖板接縫，再用灰板托住屋簷。檐下的淺色小固定件對準各跨位。')
    b.ring('plate','N',4,3,32,56,18)
    for x in (7,15,23,31,39,47,55):
        for z in (7,14): b.put('3022','L',x,z,32)
    b.bag('工業屋面的橫梁、金屬板縫與灰色封簷')
    for row in range(2):
        y=33+row*3
        b.step(f'銀灰屋簷 · 結構帶 {row+1}','以淺灰牆磚繞住淡黃廠房。前方保持平直，側面接縫往後錯開，屋內柱頭搭至相同高度。')
        b.ring('brick','L',4,3,y,56,18,row%2==1)
        for x in (7,15,23,31,39,47,55):
            for z in (7,14): b.put('3003','L',x,z,y)
    b.step('屋架與端牆壓縫','前後向的大板跨在兩列橫梁上，從左山牆依序向右連成一整片。')
    for z in (7,14):
        for x in (8,16,24,32,40,48): b.put('3034','L',x,z,39)
        for x in (7,56):b.put('3023','L',x,z,39,1)
    b.ring('plate','L',4,3,39,56,18)
    for x in range(4,60,4):
        for z,d in ((3,6),(9,8),(17,4)): b.area('plate','L',x,z,40,4,d)
    b.step('金屬屋面板 · 通長立縫','相鄰屋板間以細高縫收邊，兩端的金屬帽簷覆住波板。可由立縫分辨長廠房的進深及寬度。')
    for x in range(4,60):
        if x%4==0 or x==59: strips(b,'plate','L',x,3,41,18,along_z=True,joint=6)
        strips(b,'tile','L',x,3,42 if x%4==0 or x==59 else 41,18,along_z=True,joint=6,offset=3 if x%2 else 0)


def curtain(b,floor,y,side=False):
    """Actual aluminium-coloured frames in front of a separate row of tinted glazing."""
    count=9 if side else 7
    for bay in range(count):
        closed=side and ((floor==6 and (bay<2 or bay>5)) or (floor==5 and bay==8))
        x,z=(65,15+2*bay) if side else (76+2*bay,40)
        r=1 if side else 0
        bx,bz=(x+1,z) if side else (x,z-1)
        if closed:
            for h in (y,y+3):
                b.put('3004','Q',x,z,h,r)
                b.put('3004','Q',bx,bz,h,r)
            continue
        # The flank is seen obliquely. Alternate flush glazed bays and recessed frames,
        # as the real curtain wall must read as a band of glass even from the drive.
        flush_side=side and bay not in (0,3,6,8)
        if flush_side:
            for h in (y,y+3):
                b.put('3065' if floor==0 else '3004','S' if floor==0 else 'B',x,z,h,r)
            continue
        b.put('60592','L',x,z,y,r)
        for layer in range(2):
            # Coherent areas of reflected sky and shade, rather than alternating checkerboard panes.
            shade=floor==0 or floor<3 and bay==count-1
            sky=floor>=5 and bay in (1,2) and layer==1
            color='S' if shade else 'T' if sky else 'B'
            b.put('3004' if color=='B' else '3065',color,bx,bz,y+3*layer,r)


def office_end_walls(b,floor,y):
    """Deep piers and punched openings return around the sides of the two curtain walls."""
    for layer in range(2):
        h=y+layer*3
        b.step(f'第 {floor+1} 層磚翼 · 磚皮 {layer+1}','寬磚翼向外突出，中央窄窗退回三格。先扣磚牆，再扣窗洞內的小窗及上方壓磚，轉角交錯疊砌。')
        for xx in range(64,94):
            rear_window=layer==1 and floor>0 and xx in (69,70,77,78,85,86)
            if rear_window:b.put('3005','S',xx,6,h)
        for x,w in ((64,5),(71,6),(79,6),(87,7)) if layer==1 and floor>0 else ((64,30),):
            strips(b,'brick','Q',x,6,h,w,joint=4,offset=2 if (layer+floor)%2 else 0)
        for zz,d in ((7,6),(15,6),(23,6),(31,6),(39,2)):
            strips(b,'brick','Q',93,zz,h,d,along_z=True,joint=4,offset=2 if layer==1 else 0)
        for zz in (13,21,29,37):
            b.put('3065','S',93,zz,h,1) if layer==1 and floor>0 else b.put('3004','Q',93,zz,h,1)
        # Corners flank the lawn-side bay. A square high opening belongs to each upper shoulder.
        for zz,d in ((7,8),(33,9)):
            strips(b,'brick','Q',64,zz,h,d,along_z=True,joint=4,offset=2 if (floor+layer)%2 else 0)
            for off in range(0,d,2):
                length=min(2,d-off)
                col='S' if floor in (5,6) and layer==1 and off==4 else 'Q'
                b.area('brick',col,65,zz+off,h,1,length)
        b.area('brick','Q',66,41,h,3,1)
        b.area('brick','Q',68,39,h,1,2)
        b.area('brick','Q',69,38,h,2,1)
        b.put('3065','S',71,38,h) if layer==1 or floor==0 else b.put('3004','Q',71,38,h)
        b.put('3005','Q',73,38,h)
        b.area('brick','Q',74,38,h,1,4)
        b.area('brick','Q',75,40,h,1,2)
        b.area('brick','Q',90,40,h,3,2)
        b.put('3005','Q',93,41,h)
        # Hollow grid holds both roof and curtain-wall belts without filling the office.
        for xx in (67,75,83,89):
            for zz in (11,19,27,35): b.put('3003','L',xx,zz,h)


def office_belt(b,floor,y):
    for layer in range(2):
        h=y+layer
        b.step(f'第 {floor+1} 層白腰帶 · 第 {layer+1} 道',
               '白帶鎖在窗框與後排玻璃之間，進入磚翼時改用暖磚色。兩組承梁以九十度交疊，將內外牆連成一層。')
        b.area('plate','Q',64,6,h,30,1)
        b.area('plate','Q',93,7,h,1,34)
        for zz,d in ((7,8),(33,9)):
            b.area('plate','Q',64,zz,h,2,d)
        for bay in range(9):
            z=15+bay*2
            closed=(floor==6 and (bay<2 or bay>5)) or (floor==5 and bay==8)
            b.put('3022','W' if not closed else 'N',65,z,h)
        b.area('plate','Q',66,41,h,3,1)
        b.area('plate','Q',68,39,h,1,2)
        b.area('plate','Q',69,38,h,5,1)
        b.area('plate','Q',74,38,h,1,4)
        b.area('plate','Q',75,40,h,1,2)
        strips(b,'plate','W',76,39,h,14,joint=6,offset=2 if layer else 0)
        strips(b,'plate','W',76,40,h,14,joint=6,offset=3 if layer else 0)
        b.area('plate','Q',90,40,h,3,2)
        b.put('3024','Q',93,41,h)
        if layer==0:
            for z in (11,19,27,35):
                for x,w in ((67,1),(68,8),(76,8),(84,6),(90,1)):
                    b.area('plate','L',x,z,h,w,2)
        else:
            for x in (67,75,83,89):
                for z,d in ((11,1),(12,8),(20,8),(28,8),(36,1)):
                    b.area('plate','L',x,z,h,2,d)


def office_entry(b):
    b.step('入口的石板台階與兩排短柱','向草坪逐級下降的入口面向車道。左右門柱靠內一格，讓前緣薄簷伸出。')
    b.area('plate','L',58,25,2,6,10)
    b.area('plate','L',59,25,3,5,10)
    b.area('plate','D',60,25,4,4,10)
    for x in (60,63):
        for z in (25,33):
            for y in (5,8): b.put('3004','Q',x,z,y,1)
    b.step('磚色雨簷與上緣矮牆','長板從一側門柱跨到另一側，頂面鋪細磚，外緣用暖色薄板交錯包覆。')
    for x in (60,62): b.put('3034','N',x,26,11,1)
    for z in (25,34): b.put('3710','N',60,z,11)
    for z in (25,29,33): b.put('3032','N',58,z,12)
    b.area('tile','Q',58,25,13,6,12)


def office_roof(b):
    b.step('辦公屋面與四向封邊','跨過七樓的承梁封住屋面，後緣與磚翼頂部以交錯板帶包住。')
    b.area('plate','L',64,6,58,30,36)
    b.ring('plate','Q',64,6,59,30,36)
    b.ring('tile','Q',64,6,60,30,36)
    b.step('屋頂高低兩段梯廳','高梯廳退後設置，較低的小翼沿其側邊展開。背面留出窄格柵，四周保留可走的屋面。')
    for x,z,w,d,rows in ((76,12,10,8,3),(71,17,5,10,2)):
        for level in range(rows):
            b.ring('brick','Q',x,z,59+3*level,w,d,level%2==1)
        b.area('plate','N',x,z,59+3*rows,w,d)
        b.area('tile','Q',x,z,60+3*rows,w,d)
    b.step('小風箱、透氣百葉與檢修步道','沿退台旁排三座小風箱。屋頂用淺灰板分條鋪設，遇到梯廳和風箱時依邊線收切。')
    units={(x,z) for a in (67,73,81) for x in range(a,a+3) for z in range(31,34)}
    for a in (67,73,81):
        b.area('brick','W',a,31,59,3,3)
        b.area('plate','L',a,31,62,3,3)
        for zz in (31,32,33): b.put('2412b','L',a,zz,63)
        b.area('tile','W',a+2,31,63,1,3)
    for z in range(7,41):
        cells=[x for x in range(65,93) if (x,z) not in units and not (76<=x<86 and 12<=z<20 or 71<=x<76 and 17<=z<27)]
        for _,group in groupby(enumerate(cells),lambda a:a[1]-a[0]):
            row=[x for _,x in group]
            strips(b,'tile','L',row[0],z,59,len(row),joint=6,offset=3 if z%2 else 0)


def offices(b):
    for floor in range(7):
        if floor%2==0:
            b.bag(f'暖磚色廠辦 · 第 {floor+1}、{floor+2} 層' if floor<6 else '廠辦第七層、收窄窗頂與屋頂退台')
        y=2+8*floor
        office_end_walls(b,floor,y)
        b.step(f'第 {floor+1} 層帷幕 · 朝向草坪','凹窗框外露金屬側框，與齊平的藍灰玻璃交替排成窗帶。厚磚翼向草坪前伸一格。')
        curtain(b,floor,y,True)
        b.step(f'第 {floor+1} 層帷幕 · 臨街正面','外排真實窗框連成七開間，透明件與沙藍玻璃交替反射。兩邊暖色實牆夾住白色窗帶。')
        curtain(b,floor,y)
        office_belt(b,floor,y+6)
        if floor==0:office_entry(b)
    office_roof(b)


def plan_rows(b,kind,color,cells,y,span,offset=False):
    rows=defaultdict(list)
    for x,z in cells: rows[z].append(x)
    for z,row in sorted(rows.items()):
        for _,group in groupby(enumerate(sorted(row)),lambda a:a[1]-a[0]):
            run=[x for _,x in group]
            strips(b,kind,color,run[0],z,y,len(run),joint=span,offset=span//2 if offset and z%2 else 0)


def sculpted_wheel(b,x,z,y):
    # The high inner lips grip a two-stud saddle; the lower curves hang free at either side.
    b.put('3022','L',x+1,z,y)
    for off,r in ((0,1),(2,3)):b.put('1750','L',x+off,z,y,r)
    b.put('3022','L',x+1,z,y+2)
    b.put('3010','L',x,z,y+3)
    b.put('3005','L',x,z+1,y+3)
    b.put('3700','L',x+1,z+1,y+3)
    b.put('3005','L',x+3,z+1,y+3)
    b.put('3022','L',x+1,z,y+6)
    for off,r in ((0,1),(2,3)):b.put('15068','L',x+off,z,y+6,r)


def cyclist(b):
    b.step('自行車石雕 · 花崗岩基座與兩輪','以圓弧磚包住兩個石輪的上下半圈，單孔磚的孔心朝向草坪前方；兩輪之間保留石雕原有的凹口。')
    b.area('plate','D',34,38,3,12,5)
    b.area('plate','L',35,38,4,10,4)
    for x in (35,41):sculpted_wheel(b,x,40,5)
    b.step('自行車石雕 · 踏板、屈膝與車梁','後排支脊藏在石雕背面，腿部從踏板彎向座墊。車身前端留一個中央凹口，以分清車把和前輪。')
    for x,w in ((36,5),(42,2)):
        b.area('brick','L',x,39,5,w,1)
    b.put('3062b','L',39,40,5)
    b.area('brick','L',38,38,5,5,1)
    for x,w in ((37,3),(41,3)):b.area('brick','L',x,39,8,w,1)
    b.put('3023','L',39,40,8)
    b.put('3023','L',39,40,9,1)
    b.put('3023','L',39,40,10)
    b.area('brick','D',39,38,8,4,1)
    b.step('自行車石雕 · 前傾的騎士','座墊和手臂分開疊高。弧磚拼出背線，前端收一顆圓磚作頭；由側前方可以看見頭、手把與兩輪。')
    b.area('plate','L',37,38,11,6,2)
    b.area('brick','L',37,38,12,3,2)
    b.put('3023','L',41,39,12)
    b.put('3023','L',41,39,13)
    b.put('2540','L',41,39,14)
    b.put('3020','L',38,38,15)
    b.put('15068','L',38,38,16,2)
    b.put('3023','L',40,38,16)
    b.put('3062b','L',41,38,17)
    b.put('98138','L',41,38,20)


def pruned_tree(b,x,z):
    b.put('3022','G',x,z,2)
    b.put('3941','O',x,z,3)
    b.put('3941','O',x,z,6)
    b.put('60474','F',x-1,z-1,9)
    b.put('4032a','G',x,z,10)
    b.put('4032a','G',x,z,11)
    b.put('32607','G',x,z,12)
    b.put('4073','G',x+1,z+1,12)


def forecourt(b):
    b.bag('草坪、園藝與車道圓亭')
    b.step('園區草坪四角與旗桿列','四片扇形薄板收圓草坪轉角。中央規則草坪留給騎士石雕，臨街一側的圓座定位四支旗桿。')
    b.area('plate','G',21,34,2,28,17)
    for x in (17,49):b.area('plate','G',x,38,2,4,9)
    for x,z,r in ((17,34,2),(49,34,3),(17,47,1),(49,47,0)):
        b.put('30565','G',x,z,2,r)
    for x in (21,25,29,33):
        b.put('4032a','L',x,45,3)
        b.put('3062b','L',x,45,4)
        b.put('3062b','L',x,45,7)
        b.put('3957a','L',x,45,10)
    cyclist(b)
    b.step('草坪低灌木與曬影樹列','低灌木留在石雕與旗桿之間。車道外側種修剪樹冠的行道樹，讓主廠房招牌及廠辦入口保持可見。')
    shrubs=((20,39),(23,36),(28,40),(31,35),(46,46),(47,36),(23,48),(39,47))
    for x,z in shrubs:
        b.put('4032a','F',x,z,3)
        b.put('4032a','G',x,z,4)
        b.put('4073','G',x,z,5)
        b.put('4073','G',x+1,z+1,5)
    for x,z in ((54,31),(56,38),(68,46),(76,47),(85,45),(90,47)):
        pruned_tree(b,x,z)
    b.step('草坪表層與淺色路緣','從四角向中心鋪綠色薄面，樹穴及旗座周邊保留凸點。相鄰排接縫錯開，區分草坪和路緣的材質。')
    lawns={(x,z) for x in range(21,49) for z in range(34,51)}
    lawns|={(x,z) for x in list(range(17,21))+list(range(49,53)) for z in range(38,47)}
    lawns-={(x,z) for x in range(34,46) for z in range(38,43)}
    for ox,oz in list(shrubs)+[(x,45) for x in (21,25,29,33)]:
        lawns-={(ox+i,oz+j) for i in range(2) for j in range(2)}
    plan_rows(b,'tile','G',lawns,3,4,True)
    b.step('圓形警衛亭 · 窗帶與藍色環簷','綠色圓座上砌出白色牆腳。窄深色環帶繞過亭身，挑出的深藍圓簷接白色淺圓頂，面向入口。')
    b.put('11213','G',5,38,2)
    b.put('87081','W',6,39,3)
    b.put('60474','L',6,39,6)
    b.put('87081','D',6,39,7)
    b.put('60474','L',6,39,10)
    b.put('11213','U',5,38,11)
    b.put('44375b','W',5,38,12)
    b.put('4032a','W',7,40,14)

    b.step('園區金字牆與低花台','紅棕石牆面向草坪，左端為銅色小牌。右側八個金字貼在一整塊長磚上，再扣上收頂薄板。')
    b.area('plate','D',9,31,2,12,2)
    b.area('brick','O',9,32,3,1,1)
    b.put('3004','N',10,32,3)
    b.put('3008','O',12,32,3)
    decal(b,'dajia-motto','前庭紅棕石牆的「創新挑戰　追求卓越」金字',58,7.3)
    b.put('3005','O',20,32,3)
    b.area('tile','O',9,32,6,12,1)
    for x in (9,12,15,18):
        b.put('4073','G',x,31,3)

    b.bag('裝卸場、迴轉車道與分縫廣場')
    b.step('環草坪車道與入口轉彎','沿貨櫃前緣鋪深灰柏油，東側逐列轉彎繞過花園，接往辦公門前。用淺灰石條收住彎道外緣。')
    occupied=set()
    from design import local_cells
    for bag in b.info['bags']:
        for step in bag['steps']:
            for p in step['pieces']:
                if p['y']>=2:occupied.update(local_cells(p))
    road=set()
    for z in range(26,54):
        for x in range(2,94):
            ramp=(29<=z<=33 and 4<=x<=53)
            left=(10<=x<=15 and 34<=z<=48)
            turn=(32<=z<=49 and 52+max(0,4-abs(z-40)//2)<=x<=58+max(0,4-abs(z-40)//2))
            exit=(48<=z<=52 and 50<=x<=80) or (z in (47,48) and 60<=x<=92)
            arrival=(z>=49 and 3<=x<=25 and 0<=x-z+41<=9)
            if ramp or left or turn or exit or arrival:road.add((x,z))
    road-=occupied
    curbs={(x,z+1) for x,z in road if (x,z+1) not in road|occupied and z<53}
    plan_rows(b,'tile','D',road,2,4,True)
    plan_rows(b,'tile','L',curbs,2,3,True)


def bottom_course(b):
    """A long display plinth needs three crossed plate layers under both buildings."""
    b.foundation('D','L')
    first=b.info['bags'][0]['steps']
    first[0].update(name='中層底板橫跨下層接縫',hint='沿左右方向排黑灰底板，壓過下層直向板的接縫。')
    first[1].update(name='上層錯縫鎖底',hint='用淺灰板將中層接縫再錯開四格，使整座展示台能承托兩棟建築。')
    b.step('下層承重基板','黑色基板沿前後方向併排，最外兩條以半寬收邊，讓中層及上層的接縫都避開底層。')
    for z in range(-4,56,8):
        for x in range(-2,96,4):
            xx,zz=max(0,x),max(0,z)
            b.area('plate','K',xx,zz,0,min(96,x+4)-xx,min(56,z+8)-zz)
    return first.pop()


def courtyards(b,under):
    """Allocate the visible courtyard paving in small alternating running-bond stone courses."""
    from design import local_cells
    b.pave('L')
    broad=b.info['bags'][-1]['steps'].pop()['pieces']
    filled=set()
    for p in broad:filled.update(local_cells(p))
    by_z=defaultdict(list)
    for x,z in filled:by_z[z].append(x)
    runs=[]
    for z,row in sorted(by_z.items()):
        for _,group in groupby(enumerate(sorted(row)),lambda a:a[1]-a[0]):
            xs=[x for _,x in group]
            runs.append((xs[0],z,len(xs)))
    in_model=sum(len(s['pieces']) for bag in b.info['bags'] for s in bag['steps'])+len(under['pieces'])
    required=6000-in_model
    # Use wider slabs behind the plant, narrower running bonds along the curved driveway.
    counts=[ceil(w/4) for _,_,w in runs]
    assert sum(counts)<=required<=len(filled)
    for _ in range(required-sum(counts)):
        i=max((j for j,(_,_,w) in enumerate(runs) if counts[j]<w),
              key=lambda j:runs[j][2]*(1.18 if runs[j][1]>28 else .88)/(counts[j]+.5))
        counts[i]+=1
    bag_size=sum(len(s['pieces']) for s in b.info['bags'][-1]['steps'])
    split_at=(bag_size+required)//2
    started_front=False
    last_z=-1
    tile={1:'3070b',2:'3069b',3:'63864',4:'2431'}
    for (x,z,w),n in zip(runs,counts):
        if not started_front and bag_size>=split_at:
            b.bag('前庭石材分縫與底座收邊')
            started_front=True
            last_z=-1
        if last_z!=z:
            b.step(f'外部鋪面 · 由後起第 {z+1} 排','從左向右壓入相鄰石片，沿樹穴、牆腳與深灰車道收口。前後排的板縫交錯排列。')
            last_z=z
        # Spread the shorter cuts through the run; alternating row phase offsets the joints.
        phase=n//2 if z%2 else 0
        for j in range(n):
            width=((j+1)*w+phase)//n-(j*w+phase)//n
            b.put(tile[width],'L',x,z,2)
            x+=width
        bag_size+=n


def instructions(b,under):
    """Keep functional subassemblies together and each illustrated step to eight placements."""
    bags=b.info['bags']
    bags[2]['name']='廠房承重與淡黃 GIANT 招牌立面'
    bags[2]['steps'].extend(bags.pop(3)['steps'])
    seventh=next(q for q in bags if q['name'].startswith('廠辦第七層'))
    garden=next(q for q in bags if q['name'].startswith('草坪、園藝'))
    roof=seventh['steps'].pop()
    assert roof['name'].startswith('小風箱')
    garden['steps'].insert(0,roof)
    garden['name']='屋頂細部、警衛亭與石雕前庭'
    for bag in bags:
        for s in bag['steps']:
            for p in s['pieces']:p['y']+=1
    bags[0]['steps'].insert(0,under)
    for bag in bags:
        work=[]
        for step in bag['steps']:
            pieces=step['pieces']
            groups=ceil(len(pieces)/8)
            for i in range(groups):
                title=step['name']+(f'（{i+1}/{groups}）' if groups>1 else '')
                work.append(dict(name=title,hint=step['hint'],pieces=pieces[i*8:(i+1)*8]))
        bag['steps']=work
    return b.info


def dajia6000(Building):
    b=Building('dajia6000','GD 02','巨大機械大甲日南廠・典藏版','Giant Rinan Plant · Collector Edition',
               '左方淡黃製造廠的巨幅藍色 GIANT 招牌橫跨貨台，七座拖架伸向中央車道。右方磚色廠辦以深窗洞、金屬窗框與連續白腰帶框住前庭，草坪旁有石雕騎士、金字牆和藍簷圓亭。',
               96,56,[-.82,.59,1.31],['四幅連成一面的 GIANT 巨型廠牌','七層真窗框帷幕、內凹磚翼與屋頂退台','貨櫃拖架、旗桿草坪與石雕騎士'],'')
    building_views(b,'從臨街方向看，廠房招牌在左、七層磚色廠辦在右；兩個量體的屋緣高度不同。',
                   '草坪側入口雨簷位於玻璃窗下，七層白腰帶進入磚色端翼即停止，頂層玻璃再收窄。',
                   '貨櫃垂直伸出月台，弧形車道繞過旗桿草坪；圓亭、金字牆及騎士分別位於草坪外緣和中央。',-1)
    b.info['views'] += [
        dict(id='loading',name='貨台招牌',direction=[-.33,.20,1.4],region=[4,59,18,29,5,39],scope='all',note='四張原尺寸貼紙拼成連續的大招牌；下方是有側壁波紋、門框和輪架的貨櫃。'),
        dict(id='courtyard',name='庭園石雕',direction=[-.35,.28,1.3],region=[33,46,37,44,4,22],scope='all',note='石輪上下以正倒弧面圍成；孔心、折腿、低車把和前傾頭部共同勾出騎士的輪廓。'),
        dict(id='glazing',name='廠辦窗格',direction=[-.9,.33,1.1],region=[63,94,14,42,13,59],scope='all',note='兩面金屬窗框內縮在磚翼之間，後排玻璃形成第二層。兩者之間是每層都有窄窗的深凹轉角。')]
    under=bottom_course(b)
    dock_and_trailers(b)
    signed_hall(b)
    offices(b)
    forecourt(b)
    courtyards(b,under)
    return instructions(b,under)

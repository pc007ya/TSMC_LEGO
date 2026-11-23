"""Giant's Dajia/Rinan plant, looking across its lawn toward the loading hall and office."""
from industrial_models import building_views, decal


def loading_hall(b):
    """The ground-floor dock is set back beneath the pale wall of the taller hall."""
    b.bag('淡黃廠房、貨台與藍色 GIANT 招牌')
    b.step('彩色貨櫃列','依序排入貨台前方的貨櫃，長邊伸向車道。深色薄板墊出車架，頂部格柵表現貨櫃的直肋。')
    for x,c in ((3,'U'),(7,'O'),(11,'R'),(15,'G'),(19,'O'),(23,'G')):
        b.put('3020','K',x,10,2,1)
        b.put('3001',c,x,10,3,1)
        for z in (10,12): b.put('2412b',c,x,z,6,1)
    for course in range(2):
        y=2+3*course
        b.step(f'貨台內牆與柱列 · 第 {course+1} 層','先砌後牆、兩端牆和內部承板肋。街面深灰牆往內縮兩格，前緣柱頭用於承接上層。')
        b.area('brick','N',2,2,y,28,1)
        for x in (2,29): b.area('brick','N',x,3,y,1,6)
        b.area('brick','D',3,7,y,26,1)
        for x in (2,8,15,22,29): b.put('3005','L',x,9,y)
        b.area('brick','N',3,5,y,26,1)
    b.step('貨台上方的前挑樓板','先架承板，再跨過柱列逐段接起前挑簷；貨櫃由下方向前伸出。')
    b.area('plate','N',2,2,8,28,8)
    # These long plates grip the hall and project one stud over the recessed bays.
    for x in range(2,30,4): b.put('3020','N',x,9,9)
    for level in range(3):
        y=9+3*level
        b.step(f'長廠房與直條採光縫 · 第 {level+1} 層','兩端先接上米色山牆。正面中段保留整片米色外皮，右側的深色窄縫自下而上對齊。')
        b.area('brick','N',2,2,y,28,1)
        for x in (2,29): b.area('brick','N',x,3,y,1,6)
        b.area('brick','N',3,5,y,26,1)
        if level==0:
            b.area('plate','N',2,9,10,28,1)
            b.area('plate','N',2,9,11,3,1)
            b.area('plate','N',7,9,11,23,1)
            b.put('3245c','N',5,9,11)
            decal(b,'giant-emblem','廠房大招牌左側圓標，與右方 GIANT 藍字對齊',13.7,13.2)
            b.current['pieces'][-1]['decal']['dv']=-1.6
        else:
            for x,w in ((2,3),(15,3),(19,3),(23,3),(27,3)):
                b.area('brick','N',x,9,y,w,1)
            for x in (18,22,26):
                if level==1: b.put('3005','S',x,9,y)
                else:
                    for i,c in enumerate(('N','S','S')): b.put('3024',c,x,9,y+i)
            b.put('3008','N',7,9,y)
            if level==1:
                decal(b,'giant-word','廠房大招牌右側 GIANT 藍字，與左方圓標對齊',58,9.2)
            else:
                b.put('3023','N',5,9,17)
    b.step('銀灰封簷與金屬板屋頂','灰色帽簷繞住廠房頂部。銀灰屋板跨接後牆與中間的肋條，屋面接縫順著短向排列。')
    b.ring('brick','L',2,2,18,28,8,True)
    b.area('brick','L',3,5,18,26,1)
    b.deck('L',2,2,21,28,8)
    b.ring('tile','L',2,2,22,28,8)
    for x in range(3,29):
        if x%4==0: b.area('plate','L',x,3,22,1,6)
        b.area('tile','L',x,3,23 if x%4==0 else 22,1,6)


def office(b):
    b.bag('暖磚色廠辦、兩面帷幕與入口雨棚')
    for floor in range(7):
        y=2+4*floor
        b.step(f'廠辦第 {floor+1} 層 · 暖磚與藍灰窗格','背牆、右端及中肋先砌到同高。朝草坪的一面向內一格，以磚色翼牆框住玻璃；正面窄窗與另一面寬玻璃以磚柱分隔。')
        b.area('brick','Q',30,4,y,15,1)
        b.area('brick','Q',44,5,y,1,14)
        b.area('brick','N',32,11,y,12,1)
        # Left face toward the flag lawn: a wide inset curtain wall and an entrance below.
        for z,d in ((5,3),(16,4)): b.area('brick','Q',30,z,y,1,d)
        if floor==0:
            b.area('brick','S',31,8,y,1,8)
        elif floor==6:
            b.area('brick','Q',31,8,y,1,3)
            b.area('brick','B',31,11,y,1,3)
            b.area('brick','Q',31,14,y,1,2)
        else:
            b.area('brick','B',31,8,y,1,3)
            b.put('3005','A',31,11,y)
            b.area('brick','B',31,12,y,1,4)
        # Narrow return with punched windows, then a second, perpendicular curtain wall.
        b.area('brick','Q',31,19,y,1,1)
        b.area('brick','Q',32,18,y,1,1)
        b.area('brick','S' if floor else 'Q',33,18,y,2,1)
        b.area('brick','Q',35,19,y,1,1)
        glass='B' if floor else 'S'
        b.area('brick',glass,36,19,y,2,1)
        b.put('3005','A' if floor else 'K',38,19,y)
        b.area('brick',glass,39,19,y,4,1)
        b.area('brick','Q',43,19,y,2,1)
        b.step(f'廠辦第 {floor+1} 層 · 白色橫帶','磚柱上緣維持暖磚色，寬窗改用白色薄板。沿內縮窄窗與牆角收邊，兩面的白帶分別止於磚柱。')
        b.area('plate','Q',30,4,y+3,15,1)
        b.area('plate','Q',44,5,y+3,1,14)
        b.area('plate','N',32,11,y+3,12,1)
        for z,d in ((5,3),(16,4)): b.area('plate','Q',30,z,y+3,1,d)
        b.area('plate','W' if floor<6 else 'Q',31,8,y+3,1,8)
        b.area('plate','Q',31,19,y+3,1,1)
        b.area('plate','Q',32,18,y+3,3,1)
        b.area('plate','Q',35,19,y+3,1,1)
        b.area('plate','W',36,19,y+3,7,1)
        b.area('plate','Q',43,19,y+3,2,1)
    b.step('覆頂與上層退台','以跨在牆頂的板片封住屋面，左邊玻璃內縮處以短板補齊。再疊起退後的磚色屋頂小塔，讓高低屋緣從街面可辨。')
    for z,d in ((4,8),(12,8)):
        for x in (32,36,40): b.put('3035','L',x,z,30,1)
        for x in (30,44): b.area('plate','L',x,z,30,2 if x==30 else 1,d)
    b.ring('tile','Q',30,4,31,15,16)
    for x,z,w,d in ((31,5,3,14),(42,5,2,14),(34,5,8,1),(34,11,8,8)):
        b.area('tile','L',x,z,31,w,d)
    b.area('plate','Q',34,6,31,8,5)
    b.ring('brick','Q',34,6,32,8,5)
    b.area('plate','N',34,6,35,8,5)
    b.area('tile','N',34,6,36,8,5)
    b.step('草坪側的低入口雨棚','兩列暖磚色細柱支撐門前雨棚。淺沙色長簷貼著首層深色玻璃，入口朝向前庭。')
    for z in (12,17):
        for x in (27,29): b.put('3005','Q',x,z,2)
    b.put('3795','N',27,12,5,1)
    b.put('3666','N',29,12,5,1)
    b.area('tile','Q',27,12,6,3,6)


def garden(b):
    b.bag('旗桿草坪、圓亭與自行車石雕')
    b.step('草坪、車道和行道樹','在廠房與辦公翼前方排出長草坪。花台較窄的一端指向門口，兩側的灰色車道留給貨車與行人。')
    b.area('plate','G',8,18,2,16,5)
    b.area('plate','G',10,17,2,12,1)
    b.area('plate','G',10,23,2,12,1)
    for x,z,w in ((10,17,12),(8,18,5),(14,18,2),(21,18,3),(10,19,6),
                  (8,20,16),(8,21,12),(21,21,3),(17,22,7),(10,23,12)):
        b.area('tile','G',x,z,3,w,1)
    b.step('繞過草坪的車道','由貨櫃前方鋪深灰色車道，沿草坪右緣轉入暖磚色廠辦；淺灰步道留在外圍。')
    for x,z,w,d in ((2,14,21,3),(23,16,4,2),(24,18,3,5),(27,21,12,2)):
        b.area('tile','D',x,z,2,w,d)
    for x,z in ((9,19),(13,18),(20,21),(22,19)):
        b.plant(x,z,3)
    for x,z in ((25,13),(24,15),(40,23),(44,22)):
        b.canopy(x,z,2,'G')
    b.step('旗桿列與街角警衛亭','沿草坪邊緣豎立銀灰旗桿。街角小亭用白色圓磚和藍色簷板組起，頂部留窄藍邊。')
    for x in (10,12,14,16):
        b.put('3957a','L',x,22,3)
    b.put('60474','G',2,18,2)
    b.put('3941','W',3,19,3)
    b.put('4032a','B',3,19,6)
    b.put('60474','U',2,18,7)
    b.put('4032a','W',3,19,8)
    b.step('草坪上的石雕騎士','兩塊橫孔磚上的圓孔在車輪中央朝街道露出。灰色弧面與後排窄脊疊出車架、背線和前傾的騎士頭部。')
    b.area('plate','D',16,18,3,5,2)
    for x in (16,19): b.put('3700','L',x,19,4)
    b.put('3005','D',18,19,4)
    b.put('3010','L',16,18,4)
    for x in (16,19): b.put('11477','L',x,19,7,0 if x==16 else 2)
    b.put('3023','L',17,18,7)
    b.put('3623','L',17,18,8)
    b.put('11477','L',17,18,9)
    b.put('4073','L',19,18,9)
    b.put('4073','L',19,18,10)


def dajia(Building):
    b=Building('dajia','TC 05','巨大機械大甲日南廠','Giant Manufacturing · Dajia Rinan Plant',
               '從順帆路一側的前庭看，左後方淡黃廠房以大幅藍色 GIANT 標誌面向彩色貨櫃，右側暖磚色廠辦有兩面白帶玻璃窗。草坪上保留旗桿、圓亭與石雕騎士的輪廓。',
               48,28,[-.82,.59,1.31],['貨台上方的藍色 GIANT 大招牌','兩面窗帶與暖磚色廠辦','旗桿草坪和自行車石雕'],'')
    building_views(b,'廠房淡黃長牆上的 GIANT 藍色招牌位於貨櫃上方，右側廠辦以方正磚柱框住玻璃。',
                   '從草坪望向入口雨棚，可見另一面內縮玻璃和分段白帶，七層廠辦高出銀邊廠房。',
                   '遠側是長形廠房；貨櫃從貨台伸向車道。辦公棟在右，中央的旗桿綠地和圓亭沿路口配置。',-1)
    b.foundation('D','L')
    loading_hall(b)
    office(b)
    garden(b)
    return b.finish()

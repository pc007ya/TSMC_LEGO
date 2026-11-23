"""Exterior vignettes of the two Taichung Fab 15 campuses, on independent bases."""

from industrial_models import building_views, decal


def screened_hall(b, x, z, width, depth, title, gold=False, badge=False):
    """Layer the metallic side wall and the recessed planting/sunshade screen."""
    end = x + width - 1
    front = z + depth - 1
    y = 2
    for row, (kind, side, screen) in enumerate([
        ('brick', 'D', 'D'), ('plate', 'L', 'F'), ('brick', 'L', 'G'),
        ('plate', 'D', 'N' if gold else 'L'), ('brick', 'L', 'F'),
        ('plate', 'D', 'N' if gold else 'L'), ('brick', 'L', 'N' if gold else 'G'),
        ('plate', 'L', 'B'), ('brick', 'D', 'A')]):
        b.step(f'{title} · 第 {row+1} 道外牆',
               '先沿背面和兩側砌灰色條紋牆，正面植生屏退入一格，兩端立柱突出。每層將中間承板肋疊至同高。')
        b.area(kind, side, x, z, y, width, 1)
        for xx in (x, end):
            b.area(kind, side, xx, z+1, y, 1, depth-2)
        b.area(kind, screen, x+1, front-1, y, width-2, 1)
        for xx in (x, end-1):
            if badge and row==8 and xx==end-1:
                b.put('3004', 'D', xx, front, y)
                decal(b,'tsmc','迎向前庭的深灰端柱上方',7,7)
            else:
                b.area(kind,'D',xx,front,y,2,1)
        for zz in range(z+6, front-1, 6):
            b.area(kind,'L',x+1,zz,y,width-2,1)
        y += 3 if kind=='brick' else 1
    b.step(f'{title} · 跨牆屋面','每排屋面薄板跨在後牆、承板肋或前牆之間。最後用光面長板勾出兩端突出的灰柱。')
    b.deck('L',x,z,y,width,depth-1)
    for xx in (x,end-1):
        b.area('tile','L',xx,front,y,2,1)
    b.step(f'{title} · 屋面輪廓','沿主體收白色屋緣。中央淺灰短台和格柵概括照片中的高低輪廓，保留兩側平整的屋面。')
    b.ring('tile','W',x,z,y+1,width,depth-1)
    box_w=width-8
    b.area('plate','L',x+4,z+2,y+1,box_w,2)
    b.area('tile','W',x+4,z+2,y+2,box_w,2)
    for xx in range(x+4,end-3,3):
        b.put('2412b','L',xx,z+depth-3,y+1)


def forest_strip(b, x, z, width, trees):
    b.area('plate','F',x,z,2,width,2)
    for xx in trees:
        b.canopy(xx,z+1,3)


def fab15a(Building):
    b=Building('fab15a','TC 01','台中晶圓十五 A 廠','Taichung Fab 15A',
               '從街道看向十五 A 廠，高玻璃棟的灰色角牆立著一條紅線，右側辦公翼較低。兩者之間架起挑高遮棚，後排廠房以植生屏和遮陽帶包覆。',
               44,28,[-.62,.64,1.22],['帶紅色豎線的高玻璃棟','高架中庭遮棚','植生立面與生態池'],'')
    building_views(b,'高棟在左，較低的長翼在右。兩棟間的遮棚下方留出行走空間。',
                   '金屬遮陽和植生屏構成後排廠房的外層。前排高棟以灰色角牆收住連續的玻璃窗。',
                   '模型保留前排兩棟的高低差與中庭開口。屋面構件和水池以代表性外觀取景，棟距依積木比例縮短。',-1)
    b.foundation('D','L')
    b.bag('後排植生立面與遮陽屋緣')
    screened_hall(b,2,2,36,10,'後排廠房')
    b.bag('紅色角線和辦公高棟')
    for floor in range(7):
        y=2+4*floor
        b.step(f'高棟玻璃與遮陽 · 窗帶 {floor+1}',
               '紅線與灰色角牆沿同一條鉛直線向上。藍色玻璃繞到寬立面的另一側，各排窗頂以薄板分層。')
        for kind,h,c in [('brick',y,'T'),('plate',y+3,'B')]:
            b.area(kind,'B',9,13,h,10,1)
            b.area(kind,'B',9,14,h,1,6)
            b.area(kind,c,18,14,h,1,6)
            b.area(kind,'R',9,20,h,1,1)
            b.area(kind,'D',10,20,h,2,1)
            b.area(kind,c,12,20,h,7,1)
    b.step('角牆樓冠與晶圓徽章','讓晶圓標誌面向街道，和灰色角牆對齊。在兩側牆間封頂，沿玻璃上緣加灰色壓頂。')
    b.ring('brick','L',9,13,30,10,8,True)
    # The grey blade continues above the normal roof and carries the logo.
    b.deck('B',9,13,33,10,8)
    b.put('3010','D',9,20,34)
    decal(b,'tsmc','辦公高棟灰色角牆頂端，朝向街道',7.5,7.5)
    b.area('tile','D',9,20,37,4,1)
    b.area('tile','L',9,13,34,10,1)
    b.bag('低層玻璃長翼與挑高中庭')
    for floor in range(5):
        y=2+4*floor
        b.step(f'低翼水平窗帶 {floor+1}','長翼低於高棟。灰色後牆與兩端立柱先砌，臨街一面留連續藍窗，在中間插入窄窗框。')
        b.area('brick','L',25,13,y,16,1)
        for xx in (25,40):b.area('brick','B',xx,14,y,1,5)
        for xx,ww in ((25,7),(33,8)):b.area('plate','T',xx,19,y,ww,2)
        for xx,ww in ((25,7),(33,8)):b.area('plate','T',xx,19,y+1,ww,2)
        for xx,ww in ((25,7),(33,8)):b.area('plate','B',xx,19,y+2,ww,2)
        b.put('3004','L',32,19,y,1)
        b.ring('plate','L',25,13,y+3,16,8,floor%2==0)
        b.area('plate','L',26,19,y+3,14,1)
    b.step('低翼平頂與露台','跨過進深八格的辦公棟後，壓上灰色輪廓線。在右端退入一格鋪設淺色屋頂平台。')
    b.deck('L',25,13,22,16,8)
    b.ring('tile','B',25,13,23,16,8)
    b.area('tile','L',32,15,23,7,3)
    b.step('中庭兩側結構柱','在高低兩翼之間立四根細灰柱，留出六格寬的中庭跨距。各柱疊七塊標準磚高，再架遮棚。')
    for floor in range(7):
        for xx in (19,24):
            for zz in (12,15):
                b.put('3005','D',xx,zz,2+3*floor)
    b.step('挑高遮棚的中央透光帶','兩片六格長板跨接左右柱列。前後加灰色屋緣，中央以透明板和窄片交錯表現採光帶。')
    for zz in (12,14):b.put('3795','D',19,zz,23)
    for zz in (12,15):b.area('tile','L',19,zz,24,6,1)
    b.area('plate','T',19,13,24,6,2)
    for xx in (19,23):b.put('2412b','L',xx,13,25)
    b.bag('街景樹列與生態池')
    b.step('路緣、步道與前庭水池','草地前端以透明淺藍積木表現生態池。寬水面前方接窄水面，岸線保留栽植空間。')
    b.area('plate','F',2,22,2,10,3)
    b.area('tile','T',3,22,3,8,2)
    b.area('tile','T',5,24,3,4,1)
    b.step('街樹與灌木層次','沿前庭分別栽入樹幹與灌木。小圓葉的高低差呼應大肚山麓的複層綠化。')
    forest_strip(b,13,24,26,(15,22,29,36))
    for xx in (13,19,27,33):b.plant(xx,24,3)
    for xx in (2,11):b.plant(xx,23,3)
    return b.finish()


def ribbon_floor(b, y, glass):
    """Plan of the L-shaped office. Two genuine quadrant plates round the tips."""
    c='T' if glass else 'L'
    curve='B' if glass else 'L'
    for x,z,w,d in [(22,10,13,4),(22,14,7,3),(22,17,3,4),(29,14,3,2)]:
        b.area('plate',c,x,z,y,w,d)
    b.put('30565',curve,35,10,y)
    b.put('30565',curve,25,17,y)


def fab15b(Building):
    b=Building('fab15b','TC 02','台中晶圓十五 B 廠','Taichung Fab 15B',
               '十五 B 廠的方正廠房以金綠色水平屏面和灰白條紋相接。中央較低的 L 形辦公棟以八道窗帶繞過兩處弧角，圍著前庭的樹影和水景。',
               44,28,[.75,.75,1.38],['金綠色屏面與灰白側牆','八道水平窗帶的 L 形辦公棟','兩處弧面轉角與景觀水池'],'')
    building_views(b,'左側量體有金綠色長屏和深灰端柱；右方辦公翼用八道窗帶收出較低的簷線。',
                   '從辦公棟一側可以看見兩翼的退進、圓弧角，以及廠房灰白相間的側牆。',
                   '兩個方正量體選取自公開空拍。辦公棟兩翼轉折包住水景，廠房間距和綠地依展示底板縮短。')
    b.foundation('D','L')
    b.bag('前方金綠屏面與灰白廠房')
    screened_hall(b,2,8,19,13,'前方廠房',gold=True,badge=True)
    b.bag('後方平行廠房與屋頂分層')
    screened_hall(b,15,1,25,7,'後方廠房',gold=True)
    b.bag('八層 L 形辦公棟與圓角')
    for floor in range(8):
        y=2+2*floor
        b.step(f'辦公棟第 {floor+1} 層 · 藍窗',
               '沿 L 形長翼鋪玻璃色薄板，短翼往前庭伸出。每翼末端接一片沙藍四分之一圓板，圓邊朝前庭。')
        ribbon_floor(b,y,True)
        b.step(f'辦公棟第 {floor+1} 層 · 銀灰窗帶',
               '以銀灰板覆在藍窗上方，兩個圓板朝向與下層一致。從側面可看見繞過轉角的連續銀灰色帶。')
        ribbon_floor(b,y+1,False)
    b.step('屋頂退台與弧形壓頂','在 L 形兩端的弧形凸點上壓銀灰圓弧光面。兩翼中段收窄一格鋪設退台。')
    # The annular tiles' curved rim coincides with the outside of each sector.
    for x,z in ((35,10),(25,17)):b.put('27507','L',x,z,18)
    b.area('tile','L',22,10,18,13,1)
    b.area('tile','L',22,11,18,1,10)
    b.area('plate','W',25,11,18,10,2)
    b.area('tile','L',25,11,19,10,2)
    b.bag('前庭景觀水池與大肚山綠帶')
    b.step('環灌木的前庭水池','在辦公棟下凹的轉角鋪綠地與藍色水面，水池外側以灌木留出步行空間。')
    b.area('plate','F',30,17,2,9,5)
    b.area('tile','T',31,18,3,6,2)
    b.area('tile','T',32,20,3,4,1)
    for xx,zz in ((30,18),(37,18),(38,20),(31,21)):b.plant(xx,zz,3)
    b.step('路緣與連續樹帶','以長草帶和不同高度的樹冠圍出前景，從低視角能同時看見曲線辦公棟和廠房的水平分層。')
    forest_strip(b,3,24,35,(5,11,18,25,33))
    for xx in (3,9,15,22,29,37):b.plant(xx,24,3)
    return b.finish()

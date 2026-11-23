"""The paired office frontage, perforated atrium canopy and screened fabrication buildings of Fab 15A."""
from collections import defaultdict

from design import local_cells
from industrial_models import building_views, decal
from taichung_giant import cover


def line(b, kind, col, x, z, y, n, across_z=False):
    if n:
        b.area(kind,col,x,z,y,1 if across_z else n,n if across_z else 1)


def bays(b, kind, col, x, z, y, n, module, across_z=False, shift=0):
    off=0
    while off<n:
        size=min(n-off,module-(off+shift)%module)
        line(b,kind,col,x+(0 if across_z else off),z+(off if across_z else 0),y,size,across_z)
        off+=size


def veneer(b,x,z,y,n,phase,axis=False,clear=False):
    """A continuous cool-blue ribbon ending in finely jointed panes at the corner."""
    if phase:
        # Transparent glass across the complete bay, under two narrow spandrel rows.
        for off in range(0,n,2):
            xx=x+(0 if axis else off);zz=z+(off if axis else 0)
            b.put('3024' if off==n-1 else '3023','T',xx,zz,y,int(axis))
        for off in (1,2):
            bays(b,'plate','B',x,z,y+off,n,5,axis,shift=off)
    else:
        for off in range(0,n,2):
            xx=x+(0 if axis else off);zz=z+(off if axis else 0)
            folded=clear and n<=4
            col='T' if folded else 'B'
            part='3005' if off==n-1 else '3065' if folded else '3004'
            b.put(part,col,xx,zz,y,int(axis))


def interior(b,x,z,y,w,d,kind):
    """Two transverse ribs give the roof and bands real supports without reproducing floor plans."""
    for zz in range(z+6,z+d-1,6):
        for xx in sorted(set(range(x+2,x+w-4,7))|{x+w-3}):
            b.area(kind,'L',xx,zz,y,2,1)


def roof_sheets(b,x,z,y,w,d):
    """Build the spanning beams first; the roof strips bear on each end."""
    for line_z in range(z+6,z+d-1,6):
        line(b,'plate','L',x+1,line_z,y,w-2)
    b.ring('plate','L',x,z,y,w,d)
    for off in range(0,d,6):
        for xx in range(x,x+w,4):
            b.area('plate','L',xx,z+off,y+1,min(4,x+w-xx),min(6,d-off))


def sheet_finish(b,x,z,y,w,d):
    for row,zz in enumerate(range(z,z+d,2)):
        depth=min(2,z+d-zz)
        for xx in range(x,x+w,4):
            width=min(4,x+w-xx)
            b.area('tile','L',xx,zz,y,width,depth)


def left_end(b,x,z,y,w,row):
    """Gray metal panels with the offset narrow silver strips of the street-end elevation."""
    accents={1:(8,15),3:(23,33),5:(15,28),7:(4,11),9:(29,41)}
    start,stop=accents.get(row,(0,0))
    line(b,'plate','D',x,z,y,start)
    line(b,'plate','L',x+start,z,y,stop-start)
    line(b,'plate','D',x+stop,z,y,w-stop)


def hall(b,x,w,screen):
    z=3;d=17;front=z+d-1
    title='右後植生屏廠房' if screen else '左後金屬端牆廠房'
    b.bag(title)
    studs=sorted(set(range(x+2,x+w-4,7))|{x+w-3})
    for lev in range(3):
        b.step(f'{title} · 下排立柱 {lev+1}','依俯視圖安裝雙層磚。此排立柱在中段會用長薄板連成一體，上方托住屋面。')
        for zz in (z+6,z+12):
            for xx in studs:b.put('3245c','L',xx,zz,2+lev*6)
    b.step(title+' · 支柱中段橫梁','將長薄板橫跨相鄰支柱，中間接頭壓在相鄰的柱頭上。')
    for zz in (z+6,z+12):line(b,'plate','L',x+1,zz,20,w-2)
    for lev in range(4):
        b.step(f'{title} · 上排立柱 {lev+1}','從中段橫梁向上疊柱，最上一排換成標準高度磚，使柱頭與兩側牆面齊平。')
        for zz in (z+6,z+12):
            for xx in studs:b.put('3245c' if lev<3 else '3004','L',xx,zz,21+lev*6)
    for row in range(10):
        y=2+4*row
        b.step(f'{title} · 牆板帶 {row+1}','沿兩側框住後牆。將承梁用的短柱放在圖示位置，前立面的板材接縫分段錯開。')
        cladding='L' if row in (2,3,6,7) else 'D'
        bays(b,'brick',cladding,x,z,y,w,6,shift=(row%2)*3)
        for xx in (x,x+w-1):
            bays(b,'brick',cladding,xx,z+1,y,d-2,6,True,shift=(row%2)*2)
        if screen:
            for off in range(0,w,2):
                xx=x+off;size=min(2,w-off)
                if off in (0,2,w-2,w-4) or row<2 or row>=8:
                    line(b,'brick','D',xx,front,y,size)
                elif (off//2)%7==1:
                    line(b,'brick','D',xx,front,y,size)
                elif row%3==0:
                    b.put('2877','G',xx,front,y,2)
                else:
                    b.put('3004','F' if row%3==1 else 'G',xx,front,y)
        else:
            # Keep the left-hand factory badge visible above the trees and beyond the tower.
            if row==8:
                b.put('3245c','D',x+5,front,y)
                decal(b,'tsmc','左後廠房端牆的晶圓徽章',14.4,14.4)
            for start,n in ((0,5),(7,w-7)) if row in (8,9) else ((0,w),):
                bays(b,'brick','D',x+start,front,y,n,7,shift=(row%2)*3)
            if row==9:
                b.area('plate','D',x+5,front,y+2,2,1)
        b.step(f'{title} · 遮陽腰線 {row+1}','壓住同一高度的立柱與牆板。沿立面錯開明亮的短線，植生屏的細挑簷則分跨伸出。')
        line(b,'plate',cladding,x,z,y+3,w)
        for xx in (x,x+w-1):line(b,'plate',cladding,xx,z+1,y+3,d-2,True)
        if screen:
            for xx in range(x,x+w,4):
                color='L' if row in (1,4,7,9) else 'D'
                b.area('plate',color,xx,front,y+3,min(4,x+w-xx),2 if row in (2,4,6,8) else 1)
        elif row in (8,9):
            for start,n in ((0,5),(7,w-7)) if row==8 else ((0,w),):
                line(b,'plate','D',x+start,front,y+3,n)
        else:left_end(b,x,front,y+3,w,row)
    b.step(title+' · 金屬屋面與承梁','先使橫梁跨接牆柱，再從後方向前蓋灰色屋板，每排接縫扣在橫梁上。')
    roof_sheets(b,x,z,42,w,d)
    b.step(title+' · 屋頂收邊','屋頂沿長邊抬起薄女兒牆；屋面的拼接和矮屋頂突出物依積木尺度排列。')
    b.ring('plate','L',x,z,44,w,d)
    b.ring('tile','D',x,z,45,w,d)
    raised=[(x+8,z+3,8,3),(x+w-14,z+2,8,4)]
    rooftop={(xx,zz) for px,pz,pw,pd in raised for xx in range(px,px+pw) for zz in range(pz,pz+pd)}
    field={(xx,zz) for xx in range(x+1,x+w-1) for zz in range(z+1,front)}
    cover(b,'tile','L',field-rooftop,44)
    b.step(title+' · 退入屋緣的低矮上蓋','屋面的矮上蓋避開女兒牆，灰色百葉向外，頂緣與大屋面形成兩道陰影。其配置為積木屋頂設計。')
    for px,pz,pw,pd in raised:
        b.area('plate','D',px,pz,44,pw,pd)
        b.ring('brick','L',px,pz,45,pw,pd)
        b.area('plate','W',px,pz,48,pw,pd)
        for xx in range(px,px+pw,2):
            b.put('2412b','L',xx,pz,49)
        b.area('tile','L',px,pz+1,49,pw,pd-1)


def office_side(b,tower,x,z,y,w,d,layer,floor):
    """Rear faces, cross-beam bearings and contrasting horizontal side glazing."""
    if layer=='plate':
        line(b,'plate','B',x,z,y,w)
        line(b,'plate','B',x+w-1,z+1,y,d-2,True)
        if tower and floor<8:
            for zz in range(z+1,z+d-1,4):
                length=min(4,z+d-1-zz)
                if floor==0:b.area('plate','B',x,zz,y,2,length)
                else:
                    b.area('plate','A',x-1,zz,y,3,length)
                    line(b,'tile','A',x-1,zz,y+1,length,True)
        else:line(b,'plate','B',x,z+1,y,d-2,True)
        interior(b,x,z,y,w,d,'plate')
        return
    bays(b,'brick','L',x,z,y,w,6,shift=floor%3)
    for xx in (x,x+w-1):
        if tower and xx==x and floor in range(1,8):
            veneer(b,x+1,z+1,y,d-2,layer=='upper',True)
            if layer=='lower':
                for zz in range(z+1,z+d-1,2):b.put('60592','L',x,zz,y,1)
        elif floor==0 or (xx==x+w-1 if tower else xx==x):
            veneer(b,xx,z+1,y,d-2,layer=='upper',True,True)
        else:
            veneer(b,xx,z+1,y,d-2,layer=='upper',True)
    interior(b,x,z,y,w,d,'brick')


def tower_batch(b,floors):
    x,z,w,d=22,23,22,18
    for floor in floors:
        y=2+floor*7
        b.step(f'高棟第 {floor+1} 道玻璃 · 轉角與紅線','窄紅線及深灰翼牆沿街連續向上，折一格的玻璃轉角相接。樓簷只涵蓋一般辦公窗帶，轉角保留通高玻璃。')
        for k,offset in enumerate((0,3)):
            yy=y+offset
            office_side(b,True,x,z,yy,w,d,'lower' if k==0 else 'upper',floor)
            # The folded curtain wall between the sign blade and office ribbons.
            b.put('3005','R',22,42,yy)
            line(b,'brick','D',23,42,yy,4)
            b.put('3005','D',22,40,yy)
            b.put('3005','D',22,41,yy)
            b.put('3005','B',27,42,yy)
            veneer(b,28,41,yy,4,k,clear=True)
            if floor in range(1,8):
                # Flat silver frames sit directly in front of the backing glazing.
                veneer(b,32,39,yy,10,k)
                veneer(b,42,40,yy,2,k)
                if k==0:
                    for xx in range(32,42,2):b.put('60592','L',xx,40,yy)
            else:veneer(b,32,40,yy,12,k,clear=True)
        b.step(f'高棟第 {floor+1} 道玻璃 · 窗簷','沿沙藍窗牆壓下窄簷，簷板前伸一格；深色窗線在轉角高玻璃帶旁收住。')
        yy=y+6
        office_side(b,True,x,z,yy,w,d,'plate',floor)
        b.put('3024','R',22,42,yy);line(b,'plate','D',23,42,yy,4)
        line(b,'plate','D',22,40,yy,2,True)
        b.put('3024','B',27,42,yy);line(b,'plate','B',28,41,yy,4)
        if floor==0:
            for xx in range(32,42,2):b.put('3022','B',xx,39,yy)
            line(b,'plate','B',42,40,yy,2)
        else:
            if floor<8:line(b,'plate','B',32,39,yy,10)
            for xx in range(32,44,4):
                b.area('plate','A' if floor<8 else 'B',xx,40,yy,4,2 if floor<8 else 1)
                if floor<8:b.put('2431','A',xx,41,yy+1)
    return 2+7*(floors[-1]+1)


def tower_roof(b):
    y=65
    b.step('塔樓玻璃冠與退入的平頂','先以橫梁接住內側短柱。頂層淺灰色壓頂退在薄翼牆後方，沿轉角玻璃完成較窄的收邊。')
    roof_sheets(b,22,23,y,22,18)
    # The first plate of the rectangular roof front also bears on the two ribs.
    for x,w in [(22,6),(28,4)]:
        line(b,'plate','B',x,41 if x==28 else 42,y,w)
        if x==28:line(b,'tile','L',x,41,y+1,w)
    b.step('塔冠晶圓徽章與外露紅邊','把晶圓徽章貼在直立灰磚上，再扣到灰翼牆朝街的位置。紅線在標誌旁收頭，翼牆頂略高於玻璃冠。')
    b.put('3005','R',22,42,y+1);b.put('3005','R',22,42,y+4)
    for off in (1,4):
        b.put('3010','D',23,42,y+off)
    decal(b,'tsmc-word','高棟灰色翼牆頂端的紅色 tsmc 字標',29,7.4)
    b.put('3005','D',27,42,y+1);b.put('3005','D',27,42,y+4)
    line(b,'tile','D',22,42,y+7,6)
    b.ring('plate','B',22,23,y+2,22,18)
    b.ring('tile','D',22,23,y+3,22,18)
    sheet_finish(b,23,24,y+2,20,16)


def low_wing(b):
    x,z,w,d=58,24,34,15;front=z+d-1
    for floor in range(5):
        y=2+floor*7
        b.step(f'辦公長翼第 {floor+1} 道窗帶','從深色端柱向長立面排玻璃。沿入口側放置真正的窗框，另一端繞向較窄的側牆。')
        for k,offset in enumerate((0,3)):
            yy=y+offset
            office_side(b,False,x,z,yy,w,d,'lower' if k==0 else 'upper',floor)
            line(b,'brick','D',x,front,yy,3)
            if floor in (1,2,3):
                veneer(b,x+3,front-1,yy,26,k)
                if k==0:
                    for xx in range(x+3,x+29,2):b.put('60592','L',xx,front,yy)
            else:veneer(b,x+3,front,yy,26,k,clear=True)
            line(b,'brick','B',x+29,front,yy,5)
            if floor==0:
                for xx in (x+5,x+9,x+13,x+17,x+21,x+25):
                    if k==0:b.put('60592','L',xx,front+1,yy)
        b.step(f'低翼第 {floor+1} 道細遮陽簷','用兩格深的細屋簷連接各段窗頭，簷口在兩端的深灰包板內收頭。')
        yy=y+6
        office_side(b,False,x,z,yy,w,d,'plate',floor)
        b.area('plate','D',x,front,yy,3,1)
        if floor==0:
            for xx in range(x+3,x+29,2):b.put('3022','B',xx,front-1,yy)
            line(b,'plate','A',x+29,front,yy,5)
        else:
            if floor<4:line(b,'plate','B',x+3,front-1,yy,26)
            for xx in range(x+3,x+w,4):
                b.area('plate','A',xx,front,yy,min(4,x+w-xx),2)
                line(b,'tile','A',xx,front+1,yy+1,min(4,x+w-xx))
    b.step('低翼頂層平台及連續街簷','橫梁從後方鋪到街面。前兩排銀灰板構成頂簷，其餘屋面退後一格，以光面板封頂。')
    roof_sheets(b,x,z,37,w,d)
    b.ring('plate','D',x,z,39,w,d)
    b.ring('tile','L',x,z,40,w,d)
    sheet_finish(b,x+1,z+1,39,w-2,d-2)


def atrium(b):
    b.bag('中庭入口和鏤空橢圓天棚')
    b.step('中庭步道及桁架支腳','先鋪設天棚下方的碎石色步道。兩側各有一前一後兩座支腳，中央預留通行空間。')
    for x,w,col in [(47,1,'L'),(48,6,'D'),(54,1,'L')]:
        for zz,length in ((21,6),(27,1),(28,5),(33,1),(34,7)):
            b.area('tile','L' if length==1 else col,x,zz,2,w,length)
    for xx in (44,56):
        for zz in (21,34):
            b.put('3022','D',xx,zz,2)
    for n in range(10):
        b.step(f'挑高棚的四座邊柱 · {n+1}','貼著兩翼的柱列往上疊。空出中央讓路面從廣場延伸至採光孔下方。')
        for xx in (44,56):
            for zz in (21,34):
                b.put('3003','D',xx,zz,3+n*3)
    b.step('桁架連梁、挑簷下弦','先把兩片十六格長板架在前後柱頭。短向橫梁的接頭從兩邊向跨中錯開。')
    for x in (44,56):b.put('4282','D',x,21,33,1)
    for z in (21,34):
        b.area('plate','D',44,z,34,8,2)
        b.area('plate','D',52,z,34,6,2)
    for x in (44,56):b.area('plate','D',x,23,34,2,11)
    b.step('外露三角桁架','把黑色斜撐框沿外圈正反交替排列。從正面看得到一串三角空隙，內部中央保持開放。')
    for z in (21,35):
        for x in range(44,58,2):
            b.put('3224','K',x,z,35,2 if (x//2)%2 else 0)
    for x in (44,45,56,57):
        for z in range(22,34,2):
            b.put('3224','K',x,z,35,3 if (z//2)%2 else 1)
        b.put('3005','D',x,34,35)
        for y in (38,39):b.put('3024','D',x,34,y)
    b.step('鏤空屋頂與橢圓天窗','每排銀灰屋板從支座向內挑出，在中央依圖逐排退讓。天窗的開口直接看得見下方步道。')
    # Four genuine 4 x 4 circular rim tiles are joined by straight pieces on both
    # sides. The lower deck is cut to the footprint of the arcs, also from below.
    arcs=[(47,23,2),(51,23,3),(47,31,1),(51,31,0)]
    rim=set()
    for x,z,r in arcs:
        rim.update(local_cells(dict(part='27507',x=x,z=z,r=r)))
    rim.update((x,z) for z in range(27,31) for x in (47,54))
    skin=set()
    for z in range(21,36):
        edge=sorted(x for x,zz in rim if zz==z)
        if edge:
            left=max(x for x in edge if x<51)+1
            right=min(x for x in edge if x>=51)
        else:left=50;right=50
        ranges=[(44,left),(right,58)]
        for start,end in ranges:
            skin.update((x,z) for x in range(start,end))
            length=end-start
            # The side truss holds this single bridge plate. Five- and seven-stud
            # arms are tied up from below by the return rail at the deck edge.
            if length in (5,7):
                if start==44:
                    line(b,'plate','L',start+1,z,40,length-1)
                    line(b,'plate','L',start,z,40,1)
                else:
                    line(b,'plate','L',start,z,40,length-1)
                    line(b,'plate','L',end-1,z,40,1)
            else:line(b,'plate','L',start,z,40,length)
    b.step('深灰圓弧天窗框與銀色棚面','四片真實圓弧光面拼成前後半圓，左右各加一段直邊，完整圈住中庭上方的開口。銀灰封板緊貼圓弧外緣。')
    for x,z,r in arcs:b.put('27507','D',x,z,41,r)
    for x in (47,54):b.put('2431','D',x,27,41,1)
    cover(b,'tile','L',skin-rim,41)


def landscape(b):
    b.bag('生態水景、街樹與弧形車道')
    front=defaultdict(set)
    for z in range(43,63):
        for x in range(2,104):
            # Approach photo: sweeping lawns either side of the drop-off, with the road beyond.
            pool=((x-14)/11)**2+((z-48)/3.7)**2
            island=((x-64)/24)**2+((z-49)/4.0)**2
            edge=((x-64)/28)**2+((z-49)/6.1)**2
            if z>=57:
                col='W' if z==59 and x%12<5 else 'D'
            elif z==56:col='N'
            elif pool<.67:col='T'
            elif pool<1.28:col='F'
            elif island<1:col='G'
            elif edge<1.05:col='D'
            else:col='L'
            front[col].add((x,z))
    for col,title in [('F','生態池的深綠岸帶'),('T','生態池的折線水岸'),('G','弧形迴車島'),('L','入口廣場鋪面'),('D','街道及環形車道'),('W','街面標線'),('N','人行道緣')]:
        b.step(title,'依圖逐段連接曲線邊界。道路的淺色標線與深色路面同高，島內預留樹穴。')
        kind='plate' if col in ('F','G') else 'tile'
        cover(b,kind,col,front[col],2)
    b.step('綠帶中的街樹、樹冠與灌木','入口前的樹冠交錯高低，池畔以低矮植栽圍岸。沿草地邊緣保留淺色鋪面和視線。')
    for x,z in [(44,49),(52,47),(57,50),(66,47),(75,50),(83,49)]:
        b.put('3062b','O',x,z,3)
        b.put('3062b','O',x,z,6)
        b.put('4032a','F',x,z-1,9)
        b.put('4032a','G',x-1,z-1,10);b.put('4032a','F',x+1,z-1,10)
        b.put('4073','G',x-1,z,11);b.put('32607','F',x+1,z,11)
    for x,z in [(5,47),(8,45),(15,45),(20,51),(23,49),(69,51),(61,48),(47,48),(80,48)]:
        if (x,z) in front['F']|front['G']:b.put('32607','F',x,z,3)
    b.step('後廠端牆前的分層樹帶','在前庭外側放置較高樹列，從街道仍可辨識深灰端牆的錯落短線與上方標誌。')
    for x,z in [(5,25),(10,28),(15,26),(5,35),(12,36),(18,33),(94,25),(94,34)]:
        b.area('plate','F',x-1,z-1,2,3,3)
        b.put('3062b','O',x,z,3);b.put('3062b','O',x,z,6)
        b.put('4032a','G',x,z-1,9);b.put('4032a','F',x-1,z-1,10)
        b.put('4032a','G',x+1,z-1,10);b.put('32607','F',x+1,z-1,11)
        b.put('4073','G',x-1,z-1,11)


def finish(b,target):
    b.pave('L')
    total=sum(len(s['pieces']) for p in b.info['bags'] for s in p['steps'])
    # The same flush stone pavers can be supplied in smaller standard modules.
    # Only surface detail is subdivided. Support spans and visible colors stay fixed.
    split={'87079':('3068b','3068b',2),'4162':('2431','2431',4),
           '6636':('63864','63864',3),'2431':('3069b','3069b',2),
           '63864':('3069b','3070b',2),'3068b':('3069b','3069b',1),
           '3069b':('3070b','3070b',1)}
    # The road and plaza have the narrow stone joints characteristic of the street view.
    candidates=[s for b0 in reversed(b.info['bags']) for s in b0['steps']]
    while total<target:
        old=total
        for s in candidates:
            new=[]
            for p in s['pieces']:
                part=p['part']
                if total>=target or part not in split:
                    new.append(p);continue
                first,second,ofs=split[part]
                cross=part=='3068b'
                ax=(p['r']%2==0) != cross
                new.extend([dict(p,part=first),dict(p,part=second,x=p['x']+(ofs if ax else 0),z=p['z']+(0 if ax else ofs))])
                total+=1
            s['pieces']=new
        if total==old:break
    if total!=target:raise ValueError(('fab15a edition quantity',total))
    marked=[]
    for phase in b.info['bags']:
        for s in phase['steps']:
            n=len(s['pieces'])
            for i in range(0,n,8):
                suffix=f'（{i//8+1}/{(n+7)//8}）' if n>8 else ''
                marked.append((phase['name'],dict(name=s['name']+suffix,hint=s['hint'],pieces=s['pieces'][i:i+8])))
    bags=[];pieces=0;pos=0
    for i in range(12):
        start=pos
        while pos<len(marked) and (pieces<500*(i+1) or i==11):
            pieces+=len(marked[pos][1]['pieces']);pos+=1
        phases=list(dict.fromkeys(n for n,_ in marked[start:pos]))
        bags.append(dict(name='、'.join(phases),steps=[s for _,s in marked[start:pos]]))
    b.info['bags']=bags
    return b.info


def fab15a6000(Building):
    b=Building('fab15a6000','TF 01','台積電 Fab 15A・中科街景典藏版','TSMC Fab 15A · Taichung',
               '依街景將帶紅色角線的玻璃塔放在前方，較低的長翼與高棟夾著挑高中庭。橢圓開口和鏤空桁架取自建築師遮棚底視；後排分別做出灰色錯縫端牆及橫向植生屏。',
               106,64,[-.44,.62,1.38],['紅色翼牆與連續窗簷','橢圓採光口及黑色斜桁架','兩座後排廠房及前庭弧形車道'],'台積電、潘冀聯合建築師事務所')
    building_views(b,'玻璃塔的標誌牆與紅邊高出街向翼樓，兩側之間保留跨越中庭的桁架遮棚。','從轉角看見紅線與沙藍窗面之間的高低，後方的灰金屬板帶則繞過廠房的端牆。','採光口位於兩棟辦公樓之間。廠房與前庭用縮短的棟距組成街景展示。',-1)
    b.info['views'] += [
        dict(id='blade',name='紅線與塔冠',direction=[-.42,.18,1],region=[18,45,25,44,30,75],note='細紅邊連到塔頂標誌牆，右側折一格的高玻璃帶接回逐層挑出的藍色窗簷。'),
        dict(id='atrium',name='天棚與採光口',direction=[.02,4.1,1],region=[42,59,20,37,32,43],note='兩棟之間的屋頂沿橢圓邊緣退讓。從格架之間能望見中庭地面，左右桁架由獨立柱頭承托。'),
        dict(id='court',name='挑高中庭',direction=[.016,.13,1],region=[40,62,26,36,2,43],note='從街口沿鋪面望入，細長步道穿過兩翼之間。黑色三角桁架架在左右柱頭上，中央保持淨空。'),
        dict(id='endwall',name='廠房端牆',direction=[-.45,.18,1],region=[3,24,16,21,8,41],note='端牆上的淺灰金屬短縫逐排錯開，靠上方的晶圓徽章與正面塔冠字標分別承貼在不同積木上。'),
        dict(id='screen',name='植生遮陽屏',direction=[.56,.23,.92],region=[91,104,15,22,7,42],note='金屬簷片在植生屏前分跨挑出，深灰直柱隔開數組水平綠帶。')]
    b.foundation('D','L')
    hall(b,3,44,False);hall(b,49,54,True)
    b.bag('高棟的折角玻璃與紅線');tower_batch(b,list(range(5)))
    b.bag('街向塔冠與屋頂');tower_batch(b,list(range(5,9)));tower_roof(b)
    b.bag('低層辦公翼與兩層入口');low_wing(b)
    atrium(b);landscape(b)
    return finish(b,6000)

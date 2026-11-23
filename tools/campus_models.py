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
                 '從入口圓形水景望去，白色長棟在左側向後延伸，較高的灰棟橫列在後方。右側的藍色空橋從廣場朝灰棟伸出，兩道藍框垂直接上灰牆。低玻璃門廳和紅色雨棚面向水景。',
                 24, 24, [1.02, .70, .83],
                 ['正交的灰、白兩棟', '垂直接入灰棟的雙框空橋', '晶圓水景與四處招牌'], '925877080')
    b.info['revision'] = 6
    b.info['views'] = [
        dict(id='front',name='廣場正面',direction=[0,.012,1],scope='all',
             note='白棟的窄端在左，灰棟在後；兩道藍框之間可見玻璃、中段白簷及低門廳。'),
        dict(id='side',name='綠帶側面',direction=[1,.012,0],scope='all',
             note='由樹列向內看，白棟的三道腰線沿長牆伸展，灰棟只露出窄端。兩道空橋藍框一直伸到灰牆，白棟靠入口的一端可見晶圓徽章。'),
        dict(id='plan',name='建築俯視',direction=[0,1,.001],scope='all',
             note='灰棟橫向，藍色空橋的兩道長框沿前後方向接入灰棟長牆。玻璃門廳、紅雨棚與圓形水景依序朝向廣場。'),
        dict(id='junction',name='灰棟與空橋接點',direction=[.53,.92,.82],bag=3,minHeight=32,
             note='沿兩道平行藍框往後看，框端抵住同一面灰色長牆。兩片埋入牆身的 1 × 4 薄板，將空橋屋頂扣在灰棟上。')]
    b.foundation('K','D')
    b.bag('白色長棟、轉角玻璃與晶圓徽章')
    # Plan measured in the publisher’s orthographic photograph: left block 8 × 20,
    # with its 6-stud front end extending two studs beyond the main inner wall.
    rows = [('brick','B'), ('brick','W'), ('brick','W'), ('plate','B'), ('brick','W'),
            ('plate','B'), ('brick','W'), ('plate','B')] + [('brick','W')]*4
    y = 2
    for n,(shape,color) in enumerate(rows):
        b.step('白棟外牆 · '+str(n+1),'先扣後端與外側牆，再沿面向中庭的右牆接合。窄端白牆挑前兩格，透明直窗與灰色直柱在它的右側。')
        b.area(shape,color,0,2,y,8,1)
        b.area(shape,color,0,3,y,1,16)
        if y in (23,26):
            b.area(shape,color,7,3,y,1,11)
            if y==23:
                b.put('3245c','W',7,14,y,1)
                apply_decal(b,'tsmc',14,15,'白棟內側長牆、轉角藍窗旁的晶圓徽章')
                b.current['pieces'][-1]['decal']['face']='right'
            b.area(shape,color,7,16,y,1,2)
        else:
            b.area(shape,color,7,3,y,1,15)
        b.area(shape,'T',7,18,y,1,3)
        b.area(shape,color,0,19,y,7,1)
        b.area(shape,color,0,20,y,6,2)
        b.area(shape,'L',6,20,y,1,1)
        y += 3 if shape=='brick' else 1
    b.step('白棟屋面','短向跨接左右牆面；窄端另鋪六格寬的屋面，最後以白色光面板勾出屋緣。')
    b.deck('W',0,2,y,8,18,'x')
    b.area('plate','W',0,20,y,6,2)
    b.area('plate','L',6,20,y,2,1)
    b.ring('tile','W',0,2,y+1,8,18)
    b.area('tile','W',0,21,y+1,6,1)
    b.area('tile','W',0,20,y+1,1,1)
    b.bag('後方灰棟與垂直接合的藍色空橋')
    # Leave the last two grey courses open so the ties can be installed from above.
    for level in range(11):
        b.step('後方灰棟 · '+str(level+1),'沿後緣砌十二格長、四格深的牆，逐層錯縫。先砌至空橋屋面高度，留下上方空間安裝接梁。')
        b.ring('brick','L',8,0,2+3*level,12,4,level%2==1)
    b.step('空橋與門廳的基座','將深灰磚扣在灰棟朝廣場的一面。九格寬的後緣緊貼灰牆，前方另接七格寬的低門廳基座。')
    b.area('brick','D',10,4,2,9,7)
    b.area('brick','D',12,11,2,7,5)
    y = 5
    for n,(shape,body) in enumerate([('brick','B')]*5+[('brick','T')]*2+[('plate','W')]+[('brick','T')]*2+[('plate','W')]):
        b.step('直交空橋牆與窗帶 · '+str(n+1),'後牆貼齊灰棟，兩側牆向廣場垂直伸出。面向廣場的一端留兩道沙藍直框，在窗帶之間壓上白色腰線。')
        b.area(shape,'B',10,4,y,9,1)
        b.area(shape,'B',10,5,y,1,5)
        b.area(shape,body,18,5,y,1,5)
        for x,w,c in [(10,1,'B'),(11,1,'R'),(12,1,'B'),(13,4,body),(17,1,'B'),(18,1,body)]:
            b.area(shape,c,x,9 if c=='R' else 10,y,w,1)
        y += 3 if shape=='brick' else 1
    b.step('空橋白簷與屋面','從空橋左右側牆跨接屋面。白色後簷貼齊灰棟，此時灰牆與白色屋面上的凸點同高。')
    b.deck('W',10,4,y,9,7,'x')
    b.step('把兩道藍框扣進灰牆','取兩片沙藍 1 × 4 薄板（3710）。各將最後一格扣入灰牆前緣，其餘三格朝廣場扣入空橋屋面。兩片平行，中心相隔五格。')
    for x in (12,17): b.put('3710','B',x,3,35,1)
    b.step('灰牆包住接梁','在兩片藍色接梁兩旁砌灰牆。每片接梁埋在牆內的那一格疊兩片灰色 1 × 1 薄板，再橫砌下一層灰磚壓住兩處接點。')
    b.area('brick','L',8,0,35,12,1)
    for x in (8,19): b.area('brick','L',x,1,35,1,2)
    for x,length in ((8,4),(13,4),(18,2)): b.area('brick','L',x,3,35,length,1)
    for level in (36,37):
        for x in (12,17): b.put('3024','L',x,3,level)
    b.ring('brick','L',8,0,38,12,4)
    b.step('空橋頂部的兩道藍框','在前端補一格框腳，再從灰牆往廣場架上兩道平行藍梁。用跨縫的光面板封頂，檢查兩個框端都抵住灰牆。')
    for x in (12,17):
        b.put('3024','B',x,10,35)
        b.put('3009','B',x,4,36,1)
        b.put('3005','B',x,10,36)
        b.put('3070b','B',x,4,39)
        b.put('6636','B',x,5,39,1)
    b.area('tile','W',13,4,35,4,7)
    b.area('tile','W',18,4,35,1,7)
    b.area('tile','B',10,4,35,2,7)
    b.step('灰棟凹頂','由上方裝入跨牆短板。圍起淺凹設備槽，以光面灰條收邊。')
    b.deck('L',8,0,41,12,4)
    b.ring('plate','L',8,0,42,12,4)
    b.ring('tile','L',8,0,43,12,4,True)
    b.bag('玻璃門廳、前廣場與雙語樓名')
    b.step('六格晶圓水景','在門前裝上六格淺灰圓碟，將深灰圓板鎖在碟心的凸點。以兩格圓片收住中央矮台，露出光滑的外圈。')
    b.put('44375b','L',13,16,2)
    b.put('4032a','D',15,18,4)
    b.put('4150','D',15,18,5)
    y = b.frame(12,11,5,7,4,[('brick','T')]*3+[('plate','T')],'入口玻璃門廳')
    b.step('門廳的灰色平頂','用薄板跨過四格進深的低門廳，加上淺灰檐口。門廳接在空橋前方，紅色雨棚朝向圓形廣場。')
    b.deck('L',12,11,y,7,4)
    b.ring('tile','L',12,11,y+1,7,4)
    b.step('紅雨棚與門套','在玻璃門前裝上兩側灰柱與中間的透明磚，再把紅色雨棚挑向水景。')
    for x in (14,17): column(b,'L',x,15,5,11)
    b.area('brick','T',15,15,5,2,1)
    b.area('plate','R',15,15,8,2,2)
    b.area('tile','R',15,15,9,2,2)
    b.area('plate','L',14,15,11,4,1)
    b.area('tile','L',14,15,12,4,1)
    b.step('入口牆徽與中英文大樓銘牌','沿白棟內側放置深灰入口牆。晶圓徽章朝中庭，長條樓名牌下方有一層紅色底座。')
    b.area('plate','D',8,13,2,2,8)
    b.area('plate','R',9,13,3,1,6)
    b.put('3009','L',9,13,4,1)
    apply_decal(b,'tsmc-sign',34,8.4,'中庭入口、紅色底座上方的中英文大樓銘牌')
    b.current['pieces'][-1]['decal']['face']='right'
    b.area('tile','D',9,13,7,1,6)
    b.area('brick','D',9,19,3,1,2)
    b.put('3245c','D',9,19,6,1)
    apply_decal(b,'tsmc',14,15,'中庭入口深灰牆上的晶圓徽章')
    b.current['pieces'][-1]['decal']['face']='right'
    b.area('tile','D',9,19,12,1,2)
    b.step('右側狹長綠帶與樹列','沿灰棟右端至前景鋪設綠帶，由後往前裝上小灌木、紅棕樹幹與交錯的枝葉。')
    b.area('plate','G',21,1,2,2,21)
    b.area('plate','G',19,18,2,2,4)
    for x,z in [(21,3),(22,5),(21,7)]: b.plant(x,z,3)
    for x,z in [(21,13),(21,16),(20,18)]:
        b.put('3062b','O',x,z,3)
        b.put('4032a','G',x,z-1,6)
        b.put('32607','G',x,z,7)
        b.put('24866','W',x+1,z-1,7)
    b.step('草地前緣的大樓名牌','從綠帶前端橫向立起淺灰名牌，使張忠謀大樓字樣面向廣場正前方。')
    b.put('3010','L',19,21,3)
    apply_decal(b,'campus-sign',26,7.2,'綠帶前端、靠近水景的張忠謀大樓名牌')
    b.area('tile','L',19,21,6,4,1)
    return b.finish()


def oval(Building):
    b = Building('arc','FAB 05','台積電南京園區','TSMC Nanjing Campus',
                 '池畔的白色研發棟橫跨五座鏤空 V 形支架，上下兩側的曲面在紅色 tsmc 端牌旁收圓。右側廠房以完整白色橢圓外環圍住斜置的沙藍機房，環下的灰色支墩之間可看見通廊。',
                 48, 32, [-.87,.75,1.04],
                 ['五座白色雙 V 斜撐','上下收圓的架空研發棟','二十四乘二十格的閉合橢圓外環'], '920718279')
    left_feet = [[16.5-3*i,4.5+4*i] for i in range(5)]
    right_feet = [[x+4,z+3] for x,z in left_feet]
    mounts = left_feet+right_feet
    b.info['pivot'] = dict(x=16.5,z=4.5,degrees=36.86989764584402,label='管形研發棟',mounts=mounts, rows=[left_feet,right_feet])
    b.info['revision'] = 4
    b.info['rearOverhang'] = dict(rows=4, minHeight=16)
    b.info['views'] = [
        dict(id='front',name='池畔正面',direction=[0,.055,1],scope='all',
             note='從池畔看向園區，研發棟的紅色端牌與圓盤管制中心在左，右側橢圓白牆圍住機房。'),
        dict(id='plan',name='園區俯視',direction=[0,1,.001],scope='all',
             note='白色管形研發棟斜跨園區，後端懸出底座，前端朝向蓮池。圓盤管制中心與橢圓廠房分居兩側。'),
        dict(id='supports',name='支撐側視',direction=[.12,.19,1.0],pivoted=True,
             note='五座支架各有兩個獨立落地支腳。成對的白色斜桿支撐上方縱梁，兩側倒圓弧磚包住樓板。'),
        dict(id='oval',name='橢圓俯視',direction=[0,1,.05],bag=2,
             note='沿白色外牆繞一圈，可見四道大半徑屋緣連成封閉外環，中央機房與成排冷卻箱相對底座斜放，與正面圓弧形成明顯的方向差。'),
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
    # The product's top view shows a square plant room set diagonally inside
    # the outer ring. Five single studs align on a 3-4-5 rotated grid.
    core_axis=dict(x=34.5,z=10.5,degrees=36.86989764584402,label='斜置中央機房',type='module')
    b.step('中央機房的五個定位點','在環內放好五顆深灰圓板，中央一顆、四周各一顆。後面的藍色機房會以這五點斜放，留出外圈檢修道。')
    for xx,zz in [(34,10),(30,7),(38,13),(37,6),(31,14)]:b.put('4073','D',xx,zz,2)
    core_start=len(b.info['bags'][-1]['steps'])
    b.step('機房旋轉底梁','依圖將三列底梁轉向約 36.87°，兩側長梁的扣點分別對準左、右圓座，中梁扣在前後圓座上。')
    for x,z in [(29,8),(39,7)]:b.put('3666','D',x,z,3,1)
    for z in [5,11]:b.put('3666','D',34,z,3,1)
    # One crosspiece on each row spans to a side rail or the centre rail.
    outline=[(5,33,35),(6,32,37)]+[(z,30,39) for z in range(7,13)]+[(13,29,38),(14,30,37),(15,32,37)]
    b.step('沿斜軸跨接機房底板','外側底板由左右兩端向中線壓住底梁，前後兩排向內縮，收出檢修平台的四個角。')
    for zz,left,right in outline:
        if right-left==9:
            if left==30:
                b.put('3666','L',30,zz,4);b.put('3710','L',36,zz,4)
            else:
                b.put('3710','L',29,zz,4);b.put('3666','L',33,zz,4)
        else:b.area('plate','L',left,zz,4,right-left+1,1)
    for level in range(3):
        b.step('斜置機房牆與承板肋 · '+str(level+1),'沿底板砌沙藍色外牆，用中央承板肋托住屋頂。機房的兩組平行邊斜跨底座方格。')
        y=5+3*level
        for zz,left,right in outline:
            if zz in (5,15):b.area('brick','B',left,zz,y,right-left+1,1)
            else:
                for xx in [left,right]:b.put('3005','B',xx,zz,y)
                b.put('3004','L',34,zz,y)
    b.step('斜置屋頂與藍色簷口','由兩側向中央承板肋鋪設屋面，四周收沙藍平邊。')
    for zz,left,right in outline:
        if right-left==9:
            if left==30:
                b.put('3666','L',30,zz,14);b.put('3710','L',36,zz,14)
            else:
                b.put('3710','L',29,zz,14);b.put('3666','L',33,zz,14)
        else:b.area('plate','L',left,zz,14,right-left+1,1)
        if zz in (5,15):b.area('tile','B',left,zz,15,right-left+1,1)
        else:
            for xx in [left,right]:b.put('3070b','B',xx,zz,15)
    b.step('平行冷卻箱、管道與設備井','白色長箱分成兩列，夾住中間管組。風機和較高的設備井安放在屋頂另一側，整組設備與機房同向。')
    for zz in [8,12]:
        b.area('plate','L',31,zz,15,5,2);b.area('tile','W',31,zz,16,5,2)
    for xx in [31,33,35]:b.put('2412b','L',xx,10,15)
    for zz in [8,10,12]:
        b.put('3062b','L',37,zz,15);b.put('98138','D',37,zz,18)
    b.put('3004','L',35,7,15);b.put('3004','L',35,7,18);b.put('3069b','L',35,7,21)
    for step in b.info['bags'][-1]['steps'][core_start:]:
        for piece in step['pieces']:piece['pivotAt']=core_axis
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
        for y in [13,14,15]:b.put('3666','W',16,zz,y)
    b.step('跨過五座支架的縱梁','從後端並排扣上三片 2 × 16 白色長板，每片跨在第一、第二座支架上。往池畔各接兩片 2 × 8，下一層交錯鎖縫。後端屋角伸出底座約四格。')
    for xx in [16,18,20]:
        b.put('4282','W',xx,-5,16,1)
        for zz in [11,19]:b.put('3034','W',xx,zz,16,1)
    b.step('兩側倒圓弧底殼','將白色 1750 的內側兩個扣位從上方扣在縱梁外排凸點。外側圓邊垂在樓板旁，兩邊鏡像；兩格一組，沿整條長廊排到池畔端。')
    for zz in range(-5,27,2):
        b.put('1750','W',15,zz,16,1);b.put('1750','W',21,zz,16,3)
    b.step('底殼內緣找平','兩側內緣各疊兩層白薄板：第一層補倒弧的落差，第二層扣入上弧高肩的凹口。這樣從池畔看端面會完整封閉。中間樓板交錯壓緊。')
    for y in [18,19]:
        for xx in [16,21]:b.area('plate','W',xx,-5,y,1,32)
    for y in [17,18]:
        for zz in range(-5,26,2):b.area('plate','W',17,zz,y,4,min(2,26-zz))
    b.step('池畔端板與紅色字標','在最後一排中央裝四格白色端板，紅色 tsmc 朝向水池，兩旁留給上下相接的弧形端角。')
    b.put('3010','W',17,26,17);apply_decal(b,'tsmc-word',24,6,'架空研發棟面向水池的圓角端面')
    b.step('配對上弧與下弧','把兩排 15068 的高肩朝向建築中央，靠在倒圓弧上方。沿兩側檢查外殼，池畔端可見上下收圓的長橢圓剖面。')
    for zz in range(-5,27,2):
        b.put('15068','W',15,zz,19,1);b.put('15068','W',21,zz,19,3)
    b.step('縱向屋面接縫','在中間四列鋪板至與端牌齊高，再沿長軸用細長白色平板壓住板縫。')
    for zz in range(-5,26,2):b.area('plate','W',17,zz,19,4,min(2,26-zz))
    for xx in range(17,21):b.area('tile','W',xx,-5,20,1,32)
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

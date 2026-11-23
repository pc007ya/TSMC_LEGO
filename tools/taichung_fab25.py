"""Taichung Fab 25 P1, an architectural miniature of the August 2026 steelwork milestone."""
from industrial_models import building_views, decal


def beam_grid(b, xs, zs, y):
    """Each six-stud span bears on opposite studs of two adjacent two-stud column heads."""
    b.step('架橫梁','每根六格薄板架在相鄰兩個柱頭上，兩端各壓一格。橫梁沿長邊排成平行列，在最外側補齊短邊。')
    for z in zs:
        for x in xs[:-1]:
            b.put('3795','O',x+1,z,y)
        for x in (xs[0],xs[-1]+1):
            b.put('3023','O',x,z,y,1)
    b.step('交叉扣合縱梁','把第二向的六格梁轉九十度，在上一層交點扣緊。從兩個側面看，縱橫梁之間保留方形透空。')
    for x in xs:
        for z in zs[:-1]:
            b.put('3795','D',x,z+1,y+1,1)
        for z in (zs[0],zs[-1]+1):
            b.put('3023','D',x,z,y+1)


def platform(b,xs,zs,y):
    """Deck rectangles span between the two adjacent longitudinal girders below."""
    for z in zs[:-1]:
        for x in xs[:-1]:
            b.put('3032','L',x+1,z+1,y)
            b.put('3795','L',x+1,z+5,y)
    for x in (xs[0],xs[-1]+1):
        b.area('plate','L',x,zs[0]+1,y,1,zs[-1]-zs[0])
    for z in (zs[0],zs[-1]+1):
        b.area('plate','L',xs[0],z,y,xs[-1]-xs[0]+2,1)


def fab25(Building):
    b=Building('fab25','TC 03','台中 F25 新廠・鋼構工程','Fab 25 P1 · Steelwork, August 2026',
               '取材自 2026 年 8 月 31 日的中科新廠會勘。紅棕色柱梁圍出透空的主體，局部樓板露出交叉梁格，前景保留遠眺工地時可見的綠坡。柱網、樓層與吊車按積木比例編排。',
               44,24,[.73,.63,1.25],['P1 主體鋼構階段','交叉梁與分段樓板','綠坡旁的工地遠景'],'taichung-fab25-p1')
    building_views(b,'以綠坡為前景，深色橫梁與較高柱頭勾出尚未封閉的廠房輪廓。',
                   '從右側可以看見前低後高的施工剖面、梁間透空與白色起重臂。',
                   '左半部鋪樓板，右半部露出規律的梁格。此為工程紀念模型的構圖。')
    b.info['revision']=1
    b.foundation('D','N')
    xs=(3,9,15,21,27)
    zs=(4,10,16)

    b.bag('土色場地、柱腳與第一層鋼架')
    b.step('土方工作面','以沙色板鋪出長形工作面，間隔插入紅棕土帶，兩側預留吊車位置與草坡。')
    for z,color in [(3,'N'),(7,'O'),(9,'N'),(13,'N'),(17,'O')]:
        b.area('plate',color,2,z,2,28,2 if z in (7,17) else 4)
    b.step('淺灰承台與鋼柱','三列柱腳各排五座；相鄰柱心相距六格。先扣淺灰方形承台，再疊兩塊紅棕方磚立起首層柱。')
    for z in zs:
        for x in xs:
            b.put('3022','L',x,z,3)
            b.put('3003','O',x,z,4)
            b.put('3003','O',x,z,7)
    beam_grid(b,xs,zs,10)
    b.step('局部鋪設樓板','先鋪左側四個開間，由柱列向兩邊架設樓板。右側留出開口，以淺灰短板收住其餘柱頭。')
    platform(b,xs[:3],zs,12)
    for z in zs:
        for x in xs[3:]:
            b.put('3022','L',x,z,12)

    b.bag('上層裸梁、斜撐與未封頂柱頭')
    b.step('上層細柱','兩格面的紅棕雙層磚立在柱頭前緣；在頂端裝上方形承板，供兩向橫梁扣合。')
    for z in zs:
        for x in xs:
            b.put('3245c','O',x,z,13)
            b.put('3022','O',x,z,19)
    b.step('正面兩組人字撐','前方兩個已有樓板的開間各裝兩件鏤空斜撐。兩件互為鏡像，使斜桿在中央上方會合。')
    for x in (5,11):
        b.put('3224','O',x,16,13,2)
        b.put('3224','O',x+2,16,13)
        b.put('3710','O',x,16,18)
    beam_grid(b,xs,zs,20)
    b.step('後排施工層','只給後方左側兩個開間鋪板。從正面朝內望，樓板前緣與敞開的梁格形成高低差。')
    platform(b,xs[:3],zs[:2],22)
    b.step('抬升最後一段屋架','在後排左半部再架一段鋼構。兩格高的柱身上扣方形柱頭，保留右側向上的短柱。')
    for z in zs[:2]:
        for x in xs[:3]:
            b.put('3245c','O',x,z,23)
            b.put('3022','O',x,z,29)
    for x,z in ((21,4),(27,4),(21,10),(27,10),(3,16),(15,16),(21,16)):
        b.put('3004','O',x,z,22)
    beam_grid(b,xs[:3],zs[:2],30)
    b.step('頂部接柱','在最高兩排的外角留下超出梁面的短柱頭，表現下一節鋼柱尚待吊裝的輪廓。')
    for x in (3,15):
        for z in (4,10):
            b.put('3004','O',x,z,32)

    b.bag('吊裝場景、前景綠坡與展示牌')
    b.step('示意塔吊底座','將寬四格的淺灰底板扣在梁架旁。先砌混凝土配重台，再在中央預留兩格寬的塔身扣點。')
    b.put('3031','L',34,7,2)
    b.area('brick','L',34,7,3,4,4)
    b.put('3031','D',34,7,6)
    mast_x,mast_z=35,8
    for n in range(6):
        y=7+6*n
        b.step(f'塔身桁架第 {n+1} 節','將兩片白色斜框背靠背扣在塔身。紅色方板壓住兩片框架；下一節轉九十度，讓不同方向的立面輪流受扣。')
        if n%2:
            for x,r in ((mast_x,1),(mast_x+1,3)):
                b.put('3224','W',x,mast_z,y,r)
        else:
            for z,r in ((mast_z,0),(mast_z+1,2)):
                b.put('3224','W',mast_x,z,y,r)
        b.put('3022','R',mast_x,mast_z,y+5)
    b.step('駕駛平台與平衡臂','兩格寬的平台自塔身向前伸出。用整片 2 × 16 白色長梁架住兩端，短端用灰色配重，長端朝鋼構。')
    b.put('3020','D',35,8,43,1)
    b.put('4282','W',26,8,44)
    b.put('3003','D',35,10,44)
    for z in (10,11):
        b.put('3023','T',35,z,47)
    b.put('3068b','R',35,10,48)
    b.put('3010','L',38,9,45)
    b.put('2431','D',38,9,48)
    b.step('透空起重臂','沿長梁後排交錯放置八片白框，最後以兩塊八格紅薄板從上方鎖住。前排留出配重及淨空。')
    for i in range(8):
        b.put('3224','W',26+i*2,8,45,2*(i%2))
    for x in (26,34):
        b.put('3460','R',x,8,50)
    b.step('待架鋼材','在兩對墊木上平放紅棕長料。堆料、吊車與承台都是展示用的縮尺構圖。')
    for x in (31,37):
        b.put('3623','N',x,16,2,1)
    for z in (16,18):
        b.put('3460','O',31,z,3)
    b.step('前景綠坡','沿前緣分段扣深綠板，第二層縮短並交錯放置圓角與弧面。由坡前看可把草帶、土方、鋼梁讀成三層。')
    for x,length in ((3,9),(14,10),(27,9)):
        b.area('plate','F',x,20,2,length,3)
        b.area('plate','G',x+2,20,3,length-4,2)
        b.put('15068','G',x+2,20,4)
        b.put('32607','G',x+5,21,4)
    b.step('工地紀念展示牌','將晶圓徽章居中貼在牌面朝觀者的平面，再把牌子扣入底座右前角。這是本模型的展示標記。')
    b.put('3020','D',38,20,2)
    b.put('3245c','W',39,21,3)
    decal(b,'tsmc','模型右前方的獨立工程紀念牌',12,12)
    b.put('3069b','D',39,21,9)
    return b.finish()

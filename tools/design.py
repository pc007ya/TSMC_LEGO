"""Author and validate five stud-grid architectural models. Run from any directory."""
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
stock = json.loads((DATA/'stock.json').read_text())
colors = {
    'W': ('白色','#f4f3ea',15), 'L': ('淺藍灰','#a1a7ab',71),
    'D': ('深藍灰','#585d64',72), 'K': ('黑色','#26272b',0),
    'T': ('透明淺藍','#69d5e6',41), 'B': ('沙藍','#748da7',379),
    'G': ('綠色','#29824b',2), 'F': ('深綠','#215443',288),
    'N': ('沙色','#d6be87',19), 'R': ('紅色','#c43830',4),
    'U': ('藍色','#1f6094',1), 'O': ('紅棕','#724735',70), 'A': ('深藍','#29405b',272)
}
parts={}
def register(shape, name, h, specs):
    for pid,w,d in specs:
        parts[pid]=dict(shape=shape,name=f'{name} {d}×{w}',w=w,d=d,h=h)
register('plate','薄板',1,[('3024',1,1),('3023',2,1),('3623',3,1),('3710',4,1),('3666',6,1),('3460',8,1),('3022',2,2),('3021',3,2),('3020',4,2),('3795',6,2),('3034',8,2),('3031',4,4),('3032',6,4),('3035',8,4),('3036',8,6),('41539',8,8)])
register('brick','磚',3,[('3005',1,1),('3004',2,1),('3622',3,1),('3010',4,1),('3009',6,1),('3008',8,1),('3003',2,2),('3002',3,2),('3001',4,2),('2456',6,2)])
register('tile','光面板',1,[('3070b',1,1),('3069b',2,1),('63864',3,1),('2431',4,1),('6636',6,1),('4162',8,1),('3068b',2,2),('87079',4,2)])
register('roundPlate','圓薄板',1,[('4073',1,1),('4032a',2,2),('60474',4,4)])
register('roundBrick','圓磚',3,[('3062b',1,1),('3941',2,2)])
register('roundTile','圓形光面板',1,[('98138',1,1),('4150',2,2)])
register('grille','格柵板',1,[('2412b',2,1)])
def dump(path,obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n')

class Building:
    def __init__(self,id,code,name,en,description,width,depth,camera,features,ref):
        self.info=dict(id=id,code=code,name=name,en=en,description=description,width=width,depth=depth,
                       camera=camera,features=features,reference=ref,bags=[])
    def bag(self,name):
        self.info['bags'].append(dict(name=name,steps=[]))
    def step(self,name,hint):
        self.current=dict(name=name,hint=hint,pieces=[])
        self.info['bags'][-1]['steps'].append(self.current)
    def put(self,part,color,x,z,y,r=0):
        if color not in stock[part]:
            raise ValueError(f'No catalogued color for {part}/{color} at {self.info["id"]} {x,z,y}')
        self.current['pieces'].append(dict(part=part,color=color,x=x,z=z,y=y,r=r))
    def area(self,shape,color,x,z,y,w,d):
        """Cover an axis-aligned rectangle using available designs in the chosen colour."""
        cells={(i,j) for j in range(z,z+d) for i in range(x,x+w)}
        choices=[]
        for pid,p in parts.items():
            if p['shape']!=shape or color not in stock[pid]: continue
            for r in range(1+(p['w']!=p['d'])):
                a,b=(p['d'],p['w']) if r else (p['w'],p['d'])
                if a<=w and b<=d: choices.append((a*b,-abs(a-b),a,pid,r,a,b))
        choices.sort(reverse=True)
        while cells:
            i,j=min(cells,key=lambda c:(c[1],c[0]))
            for _,__,___,pid,r,a,b in choices:
                required={(i+u,j+v) for u in range(a) for v in range(b)}
                if cells.issuperset(required):
                    self.put(pid,color,i,j,y,r)
                    cells-=required
                    break
            else: raise ValueError(f'unfillable {shape} {color} at {i,j}')
    def ring(self,shape,color,x,z,y,w,d,swap=False,thick=1):
        t=thick
        if swap:
            boxes=[(x,z,t,d),(x+w-t,z,t,d),(x+t,z,w-2*t,t),(x+t,z+d-t,w-2*t,t)]
        else:
            boxes=[(x,z,w,t),(x,z+d-t,w,t),(x,z+t,t,d-2*t),(x+w-t,z+t,t,d-2*t)]
        for i,j,a,b in boxes:
            if a>0 and b>0:self.area(shape,color,i,j,y,a,b)
    def frame(self,x,z,y,w,d,rows,base_name):
        for n,(kind,color) in enumerate(rows):
            self.step(base_name+' · '+str(n+1),'沿外框依序扣合四邊；前後兩層讓角位交錯。')
            self.ring(kind,color,x,z,y,w,d,n%2==1)
            y+=3 if kind=='brick' else 1
        return y
    def deck(self,color,x,z,y,w,d,along='z'):
        # Strips span between the two supporting perimeter walls.
        cross,span=(w,d) if along=='z' else (d,w)
        offset=0
        while offset<cross:
            n=min(2,cross-offset)
            if along=='z':self.area('plate',color,x+offset,z,y,n,span)
            else:self.area('plate',color,x,z+offset,y,span,n)
            offset+=n
    def foundation(self,edge,top):
        w,d=self.info['width'],self.info['depth']
        self.bag('底座與定位')
        self.step('併排底板','將底板凸點朝上、長邊對齊排在平桌。下一層會跨接板縫。')
        for z in range(0,d,4):
            for x in range(0,w,8):self.area('plate',edge,x,z,0,min(8,w-x),min(4,d-z))
        self.step('錯縫鎖底','上層相對底板橫移四格、縱移兩格。逐排按緊後，底座可整片拿起。')
        for z in range(-2,d,4):
            for x in range(-4,w,8):
                a,b=max(0,x),max(0,z)
                self.area('plate',top,a,b,1,min(w,x+8)-a,min(d,z+4)-b)
    def canopy(self,x,z,y,c='G'):
        self.put('3062b','O',x,z,y)
        self.put('4032a',c,x,z-1,y+3)
        self.put('4073',c,x,z-1,y+4)
        self.put('4073',c,x+1,z,y+4)
    def plant(self,x,z,y):
        self.put('4073','G',x,z,y)
    def equipment(self,x,z,y,w,d):
        self.area('plate','D',x,z,y,w,d)
        for i in range(x,x+w,2):
            for j in range(z,z+d):self.put('2412b','L',i,j,y+1)
    def tank(self,x,z,y,color='N'):
        self.put('3062b',color,x,z,y)
        self.put('98138','L',x,z,y+3)
    def pave(self,color):
        # Reserve the whole vertical approach around projecting façades and curved elements.
        w,d=self.info['width'],self.info['depth']
        free={(x,z) for x in range(1,w-1) for z in range(1,d-1)}
        for bag in self.info['bags']:
            for step in bag['steps']:
                for p in step['pieces']:
                    if p['y']<2:continue
                    spec=parts[p['part']]
                    a,b=(spec['d'],spec['w']) if p['r']%2 else (spec['w'],spec['d'])
                    free.difference_update((p['x']+i,p['z']+j) for i in range(a) for j in range(b))
        self.step('廣場鋪面收尾','沿建築外圍鋪設光面板，由後向前填滿步道，底座邊緣保留一格凸點。')
        options=sorted([(p['w']*p['d'],p['w'],key,r,a,b)
                        for key,p in parts.items() if p['shape']=='tile' and color in stock[key]
                        for r,a,b in [(0,p['w'],p['d']),(1,p['d'],p['w'])]],reverse=True)
        while free:
            x,z=min(free,key=lambda c:(c[1],c[0]))
            for _,__,key,r,a,b in options:
                cells={(x+i,z+j) for i in range(a) for j in range(b)}
                if cells<=free:
                    self.put(key,color,x,z,2,r)
                    free-=cells
                    break
    def finish(self):
        self.pave({'graphite':'N','twin':'D'}.get(self.info['id'],'L'))
        for bag in self.info['bags']:
            split=[]
            for s in bag['steps']:
                pieces=s['pieces']
                for n in range(0,len(pieces),8):
                    group=n//8+1
                    suffix=f'（{group}/{(len(pieces)+7)//8}）' if len(pieces)>8 else ''
                    split.append(dict(name=s['name']+suffix,hint=s['hint'],pieces=pieces[n:n+8]))
            bag['steps']=split
        return self.info

def twin():
    b=Building('twin','FAB 01','雙塔研發大樓','Twin Tower Campus','白色條帶主樓與灰色高塔圍出入口廣場。透明藍窗沿立面上升，紅雨棚標出抵達大廳的位置。',24,24,[-0.82,.74,1.2],['三道水平腰帶','層疊玻璃大廳','圓形入口廣場'],'925877080')
    b.foundation('K','D')
    b.bag('白色主樓與腰帶')
    x,z,w,d=1,2,16,6
    y=b.frame(x,z,2,w,d,[('brick','L'),('plate','K'),('brick','W'),('plate','K'),('brick','W'),('plate','K'),('brick','W'),('brick','W'),('brick','W'),('brick','W')],'主樓外牆')
    b.step('封上白色屋頂','薄板沿建築進深跨過兩道牆，在接縫處壓實。')
    b.deck('W',x,z,y,w,d)
    b.step('入口側的藍玻璃帶','在主樓左前角豎起一格深的透明柱，白色薄板封頂。')
    for yy in range(2,y-2,3): b.area('brick','T',2,8,yy,2,1)
    b.area('plate','W',2,8,2+3*len(range(2,y-2,3)),2,1)
    b.bag('灰塔與玻璃翼樓')
    y=b.frame(18,2,2,5,12,[('brick','L')]*10,'右塔立面')
    b.step('灰塔女兒牆','用短板橫跨五格寬度，最後在屋頂四周留出一圈凸起的框。')
    b.deck('L',18,2,y,5,12,'x'); b.ring('tile','L',18,2,y+1,5,12)
    y=b.frame(11,8,2,7,6,[('brick','B'),('brick','B'),('brick','B'),('brick','T'),('plate','W'),('brick','T'),('plate','W')],'翼樓窗帶')
    b.step('翼樓屋頂與雙框','先封閉屋頂，再沿兩側築起高出玻璃的沙藍色框架。')
    b.deck('W',11,8,y,7,6)
    for xx in [11,17]:
        b.area('brick','B',xx,8,y+1,1,6)
        b.area('tile','B',xx,8,y+4,1,6)
    b.bag('門廳、雨棚與廣場')
    y=b.frame(10,14,2,8,5,[('brick','T'),('brick','T'),('plate','W'),('brick','T')],'玻璃大廳')
    b.step('大廳收邊與雨棚','封住門廳屋頂，在正面門柱上安裝外伸一格的紅雨棚。')
    b.deck('L',10,14,y,8,5)
    b.step('翼樓立面雙框','由門廳屋頂起，將沙藍柱一層層向上延伸到翼樓的頂框。')
    for yy in [13,16,19,22]:
        for xx in [11,17]:b.put('3005','B',xx,14,yy)
    b.step('紅色雨棚','在入口設置兩根支柱，紅色頂板向步道外挑一格。')
    for xx in [12,15]:b.put('3005','L',xx,19,2);b.put('3005','L',xx,19,5)
    b.area('plate','R',12,19,8,4,2)
    b.step('圓形廣場','四格寬圓板作為廣場，中間再扣上圓形矮台。')
    b.put('60474','L',4,15,2);b.put('4032a','D',5,16,3);b.put('4150','L',5,16,4)
    b.step('園景與步道','將草地沿前緣鋪開，在樹位依序裝上樹幹及樹冠。')
    b.area('plate','G',1,21,2,22,2)
    for xx in [3,7,17,21]:b.canopy(xx,21,3)
    for xx in [1,5,9,13,17,21]:b.area('tile','L',xx,23,2,2,1)
    return b.finish()

def fins():
    b=Building('fins','FAB 02','直柵晶圓廠','Finwall Fab','白色直柵將透明窗分成窄條，兩側深色翼樓襯托中央大廳。屋頂天窗後方是開放式設備庭院。',32,24,[-.83,.76,1.18],['白色直柵立面','透光天窗','後側機電庭院'],'926523184')
    b.foundation('W','L')
    b.bag('設備庭院與側翼')
    y=b.frame(2,2,2,28,7,[('brick','L'),('brick','B')],'後棟設備基座')
    b.step('庭院樓板','沿七格進深橫架薄板，形成可安裝機組的設備層。')
    b.deck('L',2,2,y,28,7)
    b.step('設備圍牆','後方與兩端砌牆，朝向天窗的一側保留開口。')
    b.area('brick','W',2,2,y+1,28,1)
    for xx in [2,29]:b.area('brick','B',xx,3,y+1,1,6)
    b.step('安裝後排機組','格柵裝在深灰底板上，圓罐沿後牆排列。')
    for xx in [4,12,20]:b.equipment(xx,5,y+1,6,2);b.tank(xx,3,y+1)
    for xx in [1,25]:
        y=b.frame(xx,10,2,6,7,[('brick','D'),('plate','K'),('brick','D'),('plate','K')],'側翼水平帶')
        b.step('側翼平頂','兩端採相同屋頂高度，將灰色屋頂扣在黑色腰線上。')
        b.deck('D',xx,10,y,6,7)
    b.bag('直柵展廳')
    y=b.frame(7,9,2,18,9,[('brick','D'),('plate','W')],'展廳勒腳')
    b.step('中央承重基座','將承重牆接到底座，白色薄板和周邊窗台等高。')
    b.area('brick','L',8,13,2,16,2);b.area('plate','W',8,13,5,16,2)
    for level in range(3):
        b.step('直柵窗 · '+str(level+1),'正面白色窗柱與淺藍窗交錯，兩端用白磚收邊。')
        for xx in range(7,25):b.put('3005','W' if xx==24 or xx%2 else 'T',xx,17,y)
        b.area('brick','W',7,9,y,18,1)
        for xx in [7,24]:b.area('brick','W',xx,10,y,1,7)
        b.area('brick','W',8,13,y,16,2) if level==0 else b.area('brick','L',8,13,y,16,2)
        y+=3
    b.step('展廳屋頂與白框','前後分成四格與五格兩段，沿中間的承重牆鎖合。')
    for xx in range(7,25,2):
        b.area('plate','W',xx,9,y,2,5);b.area('plate','W',xx,14,y,2,4)
    b.ring('tile','W',7,9,y+1,18,9)
    b.bag('天窗、門廊與園景')
    b.step('線形天窗','沿天窗長邊交錯鋪設淺灰邊框及藍色透光條。')
    for xx in range(8,24):
        col='L' if xx%2 else 'T'
        b.area('tile',col,xx,10,y+1,1,7)
    b.step('入口小門廊','兩根門柱承托雨棚，淺藍簷口朝向前方。')
    for xx in [13,17]:b.put('3005','W',xx,19,2)
    b.area('plate','W',13,19,5,5,2);b.area('tile','T',13,20,6,5,1)
    b.step('鋪設廣場','將圓形筒體堆疊在側翼前，沿兩側草地放置小樹。')
    for yy in [2,3,4,5]:b.put('4032a','L' if yy%2 else 'D',3,18,yy)
    for xx in [1,26]:
        b.area('plate','G',xx,21,2,5,2)
        for off in [0,4]:b.canopy(xx+off,21,3)
    b.area('tile','W',10,21,2,12,2)
    return b.finish()

def ribbon():
    b=Building('ribbon','FAB 03','JASM 水平窗帶廠','JASM Ribbon Fab','白色生產棟與辦公棟並排。辦公棟的藍白水平帶、屋頂長管線、車列與草坪，構成低而長的輪廓。',40,16,[1.1,.78,1.17],['藍白水平窗帶','屋頂管線列','微型停車場'],'922961411')
    b.foundation('L','L')
    b.bag('生產棟與立柱')
    for i in range(3):
        y=2+3*i
        b.step('廠房外牆 · '+str(i+1),'沿外牆砌磚。中央的承重牆將屋頂分成前後兩跨。')
        b.ring('brick','D' if i==0 else 'W',1,1,y,20,10,i%2)
        b.area('brick','L',2,5,y,18,2)
        b.step('正面扶壁 · '+str(i+1),'在生產棟前緣加上六道突出的白色立柱。')
        for xx in range(2,20,3):b.put('3005','W',xx,11,y)
    b.step('設備屋頂','將兩排薄板跨至外牆和內部承重牆。')
    for xx in range(1,21,2):
        b.area('plate','W',xx,1,11,2,5);b.area('plate','W',xx,6,11,2,5)
    b.step('設備管路','在屋頂兩側排列成束的管線，將圓罐與散熱器固定在中央。')
    for zz in [2,8]:b.area('tile','L',2,zz,12,18,1)
    for xx in [2,9,16]:
        b.equipment(xx,4,12,4,2)
        b.tank(xx,7,12)
    b.bag('藍白窗帶辦公棟')
    # Plate courses preserve continuous horizontal glass bands in a purchasable colour.
    y=2
    for level in range(4):
        b.step('白色樓板 · '+str(level+1),'沿四邊連接白色板，交錯接縫以鎖住上一層窗帶。')
        b.ring('plate','W',24,3,y,13,8,level%2);y+=1
        b.step('透明窗帶 · '+str(level+1),'依模型四邊圍合透明淺藍薄板，保留辦公棟整圈可見的窗線。')
        for a in range(2): b.ring('plate','T',24,3,y,13,8,a==0);y+=1
        b.step('樓層收邊 · '+str(level+1),'沿窗頂覆蓋白色薄板，讓水平線延伸至轉角。')
        b.ring('plate','W',24,3,y,13,8,level%2==0);y+=1
    b.step('辦公棟屋頂','封上白色屋頂，再放上平行的深灰散熱片。')
    b.deck('W',24,3,y,13,8)
    for zz in [5,7]:b.area('tile','D',25,zz,y+1,10,1)
    b.bag('連廊、草坪與車列')
    b.step('架高連廊','在兩棟之間砌橋墩，長板跨過橋墩，再加白色牆身。')
    for xx in [21,23]:b.put('3005','D',xx,7,2)
    b.area('plate','W',21,7,5,3,2);b.area('brick','W',21,7,6,3,2)
    b.step('草坪及停車位','中央留出出入口，紅、藍、白車沿辦公棟外側排列。')
    for xx,ww in [(1,19),(25,13)]:b.area('plate','G',xx,13,2,ww,2)
    for zz,c in [(3,'R'),(6,'U'),(9,'W')]:
        b.put('3023','K',38,zz,2,1);b.put('3069b',c,38,zz,3,1)
    return b.finish()

def graphite():
    b=Building('graphite','FAB 04','石墨機電廠房','Graphite Utility Fab','深灰主廠房立在沙色基座上。平行鋪設的屋頂管路、成列儲罐和獨立設備翼，是從上方觀察的重點。',32,24,[-.63,.92,1.28],['沙色展示底座','金色機組與管路','獨立設備翼'],'923365290')
    b.foundation('N','N')
    b.bag('主廠房與扶壁')
    y=2
    for level in range(4):
        b.step('主廠房結構 · '+str(level+1),'沿主棟砌牆，在中線加承重牆。外圈立柱凸出正面一格。')
        b.ring('brick','K' if level==0 else 'L',2,3,y,17,16,level%2)
        b.area('brick','D',3,10,y,15,2)
        for xx in [3,9,16]:b.area('brick','D',xx,19,y,2,1)
        for zz in [4,10,16]:b.area('brick','K',1,zz,y,1,2)
        y+=3
    b.step('機電層樓板','前後各八格進深，長板在中央承重牆接合。')
    for xx in range(2,19,2):
        width=min(2,19-xx)
        for zz in [3,11]:b.area('plate','D',xx,zz,y,width,8)
    b.ring('tile','D',2,3,y+1,17,16)
    b.bag('屋頂機組與管線')
    b.step('平行輸送管線','銀灰管束沿長向排布，為兩列沙色機組留出空間。')
    for zz in [5,9,11,16]:b.area('tile','L',3,zz,15,15,1)
    b.step('兩列沙色機組','將機組本體放上屋頂，覆上沙色光面板。')
    for zz in [6,13]:
        for xx in [4,11]:
            b.area('plate','N',xx,zz,15,6,2)
            b.area('tile','N',xx,zz,16,6,2)
    b.step('圓罐與風扇','沿機組側面安放儲罐，裝上淺灰圓蓋。')
    for zz in [4,10,15]:
        for xx in [4,7,13,16]:b.tank(xx,zz,15)
    b.bag('側翼與連通廊')
    y=b.frame(23,6,2,7,11,[('brick','K'),('brick','D'),('brick','L')],'設備翼外牆')
    b.step('設備翼屋頂','薄板沿短邊跨接至兩側長牆，再依顏色分出風扇區與冷卻區。')
    b.deck('D',23,6,y,7,11,'x')
    b.area('plate','N',24,7,y+1,4,4)
    for xx in [24,26]:
        for zz in [7,9]:b.put('4032a','L',xx,zz,y+2)
    b.area('tile','T',24,12,y+1,5,3)
    b.step('兩棟間的連廊','架起通道的兩個支點，長板兩端鎖入橋墩。')
    for xx in [19,22]:b.area('brick','K',xx,11,2,1,2)
    b.area('plate','L',19,11,5,4,2);b.area('brick','D',19,11,6,4,2)
    b.area('tile','L',19,11,9,4,2)
    return b.finish()

register('curveBrick','四分之一圓弧磚',3,[('85080',2,2)])
register('sector','四分之一圓薄板',1,[('30565',4,4)])

def oval():
    b=Building('arc','FAB 05','弧庭研發園區','Arc Research Park','白色弧牆包圍藍灰色設備核心；前景的圓形展館、長形白色連廊與淺藍水池，向不同方向展開。',32,24,[-.76,.89,1.15],['白色弧形外牆','架高長廊與圓展館','水池與小橋'],'920718279')
    b.foundation('D','L')
    b.bag('弧形主樓與核心')
    x,z,w,d=14,2,16,13
    for layer in range(3):
        y=2+layer*3;c='D' if layer==0 else 'W'
        b.step('弧形外牆 · '+str(layer+1),'四個彎角的圓弧朝外，再把直牆接到彎角的兩端。')
        for xx,zz,r in [(x,z,2),(x+w-2,z,3),(x,z+d-2,1),(x+w-2,z+d-2,0)]:
            b.put('85080',c,xx,zz,y,r)
        for zz in [z,z+d-1]:b.area('brick',c,x+2,zz,y,w-4,1)
        for xx in [x,x+w-1]:b.area('brick',c,xx,z+2,y,1,d-4)
    # Inner roof sits on its own nested structure, with a support line under the roof seams.
    y=2
    for layer in range(4):
        b.step('內側設備核心 · '+str(layer+1),'內層向弧牆退縮，在內圈砌出沙藍色核心和中央屋頂支撐。')
        b.ring('brick','B',16,4,y,12,9,layer%2)
        b.area('brick','L',17,8,y,10,2);y+=3
    b.step('內圈屋頂設備','用兩排短跨樓板封頂，保留一圈藍色外框，在中央安裝兩座機組。')
    for xx in range(16,28,2):
        b.area('plate','B',xx,4,y,2,5);b.area('plate','B',xx,9,y,2,4)
    for zz in [5,9]:b.equipment(18,zz,y+1,6,2);b.tank(25,zz,y+1,'L')
    b.bag('圓展館與架高長廊')
    b.step('圓形展館','底層用圓板，四個中心凸點托住白色圓筒；屋頂圓板向外挑出。')
    b.put('60474','D',2,9,2);b.put('3941','W',3,10,3);b.put('3941','W',3,10,6)
    b.put('60474','W',2,9,9);b.put('4150','W',3,10,10)
    b.step('豎起長廊的支柱','四對支柱沿縱深排列。頂板跨在它們上方，形成架空的步行空間。')
    for zz in [3,7,8,14]:
        for xx in [8,11]:
            for yy in [2,5]:b.put('3005','L',xx,zz,yy)
    b.step('白色長廊','將長板跨在前、中、後三組柱位，覆以側牆及白色屋頂長條。')
    for zz,length in [(2,6),(8,8)]:b.area('plate','W',8,zz,8,4,length)
    for xx in [8,11]:b.area('brick','W',xx,2,9,1,14)
    for zz in [2,15]:b.area('brick','W',9,zz,9,2,1)
    for zz in range(2,16,2):b.area('plate','W',8,zz,12,4,2)
    for xx in range(8,12):b.area('tile','W',xx,2,13,1,14)
    b.bag('水池、過橋與綠帶')
    b.step('四片曲岸','四片圓弧底板的直角朝向池心，組成八格寬的池岸。')
    for xx,zz,r in [(12,15,2),(16,15,3),(12,19,1),(16,19,0)]:b.put('30565','L',xx,zz,2,r)
    b.step('池水與小橋','用透明淺藍薄板鋪滿中央水面，沿中線加窄橋。')
    for xx,zz,a,dd in [(14,17,4,4),(15,16,2,1),(15,21,2,1),(13,18,1,2),(18,18,1,2)]:
        b.area('plate','T',xx,zz,3,a,dd)
    b.area('tile','L',15,17,4,1,4)
    b.step('綠帶與前圍欄','將樹植在草帶上，沿前方步道以白色短磚排出圍欄。')
    for xx,ww in [(1,9),(22,8)]:
        b.area('plate','F',xx,17,2,ww,4)
        for dx in [1,ww-2]:b.canopy(xx+dx,18,3)
    for xx in [1,4,7,22,25,28]:b.area('brick','W',xx,22,2,2,1)
    return b.finish()

def silhouette(piece):
    p=parts[piece['part']]
    w,d=p['w'],p['d']
    cells={(x,z) for x in range(w) for z in range(d)}
    if piece['part']=='85080': cells={(1,0),(0,1)}
    if piece['part']=='30565': cells={(x,z) for z,n in enumerate([4,3,3,1]) for x in range(n)}
    if piece['part']=='60474': cells-={(0,0),(0,3),(3,0),(3,3)}
    for _ in range(piece['r']):
        cells={(d-1-z,x) for x,z in cells}
        w,d=d,w
    return {(piece['x']+x,piece['z']+z) for x,z in cells}

def validate(model):
    tops={}; solids=set(); parent=[]
    def root(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]]
            i=parent[i]
        return i
    for bag in model['bags']:
        for step in bag['steps']:
            for p in step['pieces']:
                i=len(parent);parent.append(i)
                shape=parts[p['part']]
                cells=silhouette(p);y=p['y'];top=y+shape['h']
                label=(model['id'],step['name'],p)
                assert all(0<=x<model['width'] and 0<=z<model['depth'] for x,z in cells),label
                assert all((x,z,v) not in solids for x,z in cells for v in range(y,top)),('collision',label)
                assert all(not any((x,z,v) in solids for v in range(top,42)) for x,z in cells),('blocked insertion',label)
                anchors={tops[(x,z,y)] for x,z in cells if (x,z,y) in tops}
                assert y==0 or anchors,('unsupported',label)
                for a in anchors:parent[root(a)]=root(i)
                for x,z in cells:
                    solids.update((x,z,v) for v in range(y,top))
                    if shape['shape'] not in ('tile','grille','roundTile'):tops[x,z,top]=i
    assert len({root(i) for i in range(len(parent))})==1,(model['id'],'disconnected assemblies')

if __name__=='__main__':
    models=[f() for f in [twin,fins,ribbon,graphite,oval]]
    for model in models:
        validate(model)
        print(model['id'], sum(len(s['pieces']) for b in model['bags'] for s in b['steps']), 'pieces,',sum(len(b['steps']) for b in model['bags']),'steps')
    dump(DATA/'models.json',models)
    dump(DATA/'catalog.json',dict(parts=parts,colors={key:dict(name=n,hex=c,ldraw=i) for key,(n,c,i) in colors.items()}))

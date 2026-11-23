"""Author and validate five stud-grid architectural models. Run from any directory."""
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
stock = json.loads((DATA/'stock.json').read_text())
colors = {
    'W': ('白色','#f4f3ea',15), 'L': ('淺藍灰','#a1a7ab',71),
    'D': ('深藍灰','#585d64',72), 'K': ('黑色','#26272b',0),
    'S': ('透明煙棕','#51483e',40), 'T': ('透明淺藍','#069eb2',41), 'B': ('沙藍','#748da7',379),
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
register('tallBrick','雙層磚',6,[('3245c',2,1)])
register('curvedSlope','弧面斜磚',2,[('11477',2,1),('15068',2,2)])
register('invertedCurve','倒圓弧磚',3,[('1750',2,2)])
register('diagonalFrame','鏤空斜撐框',5,[('3224',2,1)])
# The 1750 inside lip grips studs a plate above its lowest curved edge.
# Its inner top studs sit one plate below the outer top studs.
parts['15068'].update(bottom=['..','##'],raisedBottom=['##','..'])
parts['1750'].update(bottom=['##','..'], studs=['..','##'], recessed=['##','..'], bottomRise=1)

register('arcWall','弧形牆磚',3,[('58846',10,10),('48092',4,4)])
register('arcTile','弧形光面板',1,[('27507',4,4)])
register('handle','側把手薄板',1,[('2540',2,1)])
register('flower','五瓣花薄板',1,[('24866',1,1)])
register('leaves','三葉枝',1,[('32607',1,1)])
register('openRound','開孔圓薄板',1,[('85861',1,1)])
register('hollowBar','中空立管圓板',2,[('20482',1,1)])
register('roundPlate','圓薄板',1,[('11213',6,6)])
register('curveBrick','四分之一圓弧磚',3,[('85080',2,2)])
register('sector','四分之一圓薄板',1,[('30565',4,4)])
parts['58846']['body'] = ['####......', '####......', '####......', '.######...', '.######...', '..#####...', '..########', '...#######', '.....#####', '.......###']
parts['58846']['studs'] = ['..##......', '...#......', '...#......', '...####...', '....###...', '.....##...', '......####', '.........#', '..........', '..........']
parts['48092']['body'] = ['...#', '...#', '..#.', '##..']
parts['48092']['studs'] = ['...#', '....', '..#.', '#...']
parts['27507']['body'] = ['...#', '...#', '..#.', '##..']
parts['27507']['studs'] = ['....', '....', '....', '....']
parts['30565']['body'] = ['####', '####', '###.', '##..']
parts['30565']['studs'] = ['####', '###.', '###.', '#...']
parts['85080']['body'] = ['.#', '#.']
parts['85080']['studs'] = ['.#', '#.']
parts['60474']['body'] = ['.##.', '####', '####', '.##.']
parts['60474']['studs'] = ['.##.', '####', '####', '.##.']

register('dish','圓頂碟',2,[('44375b',6,6)])
register('roundBrick','圓磚',3,[('87081',4,4)])
parts['11213']['body'] = ['.####.', '######', '######', '######', '######', '.####.']
parts['11213']['studs'] = ['..##..', '.####.', '######', '######', '.####.', '..##..']
parts['44375b']['body'] = ['.####.', '######', '######', '######', '######', '.####.']
parts['44375b']['studs'] = ['......', '......', '..##..', '..##..', '......', '......']
parts['87081']['body'] = ['.##.', '####', '####', '.##.']
parts['87081']['studs'] = ['.##.', '####', '####', '.##.']
parts['3224']['directions'] = ['斜桿左高右低','斜桿後高前低','斜桿右高左低','斜桿前高後低']
parts['1750']['directions'] = ['扣位朝後','扣位朝右','扣位朝前','扣位朝左']
parts['15068']['directions'] = ['高肩朝後','高肩朝右','高肩朝前','高肩朝左']
parts['58846']['directions'] = ['圓心右後','圓心右前','圓心左前','圓心左後']
parts['44375b']['bottom'] = parts['44375b']['studs']

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
                    w0,d0=(spec['d'],spec['w']) if p['r']%2 else (spec['w'],spec['d'])
                    # Keep the route clear even at corners of hollow or curved pieces.
                    for u in range(w0):
                        for v in range(d0):
                            free.difference_update(grid_buckets(world_cell(self.info,p,p['x']+u,p['z']+v)))
                    for cx,cz in local_cells(p):
                        free.difference_update(grid_buckets(world_cell(self.info,p,cx,cz)))
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

def local_cells(piece, layer='body'):
    spec=parts[piece['part']]
    w,d=spec['w'],spec['d']
    if layer=='studs' and spec['shape'] in {'tile','grille','roundTile','arcTile','curvedSlope','hollowBar'}:
        return set()
    mask=spec.get(layer,spec.get('body'))
    cells={(x,z) for z in range(d) for x in range(w) if mask is None or mask[z][x]=='#'}
    if layer=='body' and piece['part']=='2540':
        cells.update([(0,1),(1,1)])
    for _ in range(piece['r']):
        cells={(d-1-z,x) for x,z in cells};w,d=d,w
    return {(piece['x']+x,piece['z']+z) for x,z in cells}

def silhouette(piece):
    return local_cells(piece)

def world_cell(model,piece,x,z):
    """Return the centre and orientation of a one-stud cell on the assembled model."""
    x+=.5;z+=.5
    pivot=piece.get('pivotAt') or (model['pivot'] if piece.get('pivoted') else None)
    if pivot is None:return (x,z,1.,0.)
    angle=math.radians(pivot['degrees'])
    c,s=math.cos(angle),math.sin(angle)
    a,b=x-pivot['x'],z-pivot['z']
    return (pivot['x']+a*c-b*s,pivot['z']+a*s+b*c,c,s)

def overlap(a,b):
    """Separating-axis test for two one-stud squares, accepting edge contact."""
    x,z=a[0]-b[0],a[1]-b[1]
    for i,j in ((a,b),(b,a)):
        c,s=i[2:];co,so=j[2:]
        radius=(1+abs(c*co+s*so)+abs(c*so-s*co))*.5-1e-7
        if abs(x*c+z*s)>=radius or abs(z*c-x*s)>=radius:return False
    return True

def grid_buckets(cell):
    x,z,c,s=cell
    if c==1 and s==0:return [(math.floor(x),math.floor(z))]
    radius=(abs(c)+abs(s))*.5-1e-7
    return [(i,j) for i in range(math.floor(x-radius),math.floor(x+radius)+1)
                  for j in range(math.floor(z-radius),math.floor(z+radius)+1)
                  if overlap(cell,(i+.5,j+.5,1.,0.))]

def validate(model):
    tops={};occupied=defaultdict(list);parent=[]
    def root(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]]
            i=parent[i]
        return i
    def interface(piece,layer,y):
        return {(round(a,6),round(b,6),y) for x,z in local_cells(piece,layer)
                for a,b,_,_ in [world_cell(model,piece,x,z)]}
    for bag in model['bags']:
        for step in bag['steps']:
            for p in step['pieces']:
                i=len(parent);parent.append(i)
                spec=parts[p['part']]
                y=p['y'];top=y+spec['h']
                label=(model['id'],step['name'],p)
                assert p['color'] in stock[p['part']],label
                anchors={tops[q] for q in interface(p,'bottom',y+spec.get('bottomRise',0)) if q in tops}
                raised_bottom=set()
                if 'raisedBottom' in spec:
                    raised_bottom=local_cells(p,'raisedBottom')
                    anchors.update(tops[q] for q in interface(p,'raisedBottom',y+1) if q in tops)
                assert y==0 or anchors,('unsupported',label)
                for a in anchors:parent[root(a)]=root(i)
                for q in interface(p,'studs',top):tops[q]=i
                recessed=set()
                if 'recessed' in spec:
                    recessed=local_cells(p,'recessed')
                    for q in interface(p,'recessed',top-1):tops[q]=i
                new=[]
                for x,z in local_cells(p):
                    inner=(x,z) in recessed
                    cell_bottom=y+(1 if (x,z) in raised_bottom else spec.get('bottomRise',0) if inner else 0)
                    cell_top=top-1 if inner else top
                    cell=world_cell(model,p,x,z)
                    for key in grid_buckets(cell):
                        assert 0<=key[0]<model['width'] and 0<=key[1]<model['depth'],('outside',label,key)
                        for other,old_top,old_p in occupied[key]:
                            if old_top>cell_bottom and overlap(cell,other):
                                raise ValueError(('collision or blocked vertical approach',label,old_p))
                        new.append((key,cell,cell_top))
                for key,cell,cell_top in new:occupied[key].append((cell,cell_top,p))
                if 'decal' in p:
                    d=p['decal'];w,dp=(spec['d'],spec['w']) if p['r']%2 else (spec['w'],spec['d'])
                    face_width=w if d['face'] in ('front','back') else dp
                    assert d['widthMM']+2*abs(d.get('du',0)) < face_width*8,('decal width',label)
                    assert d['heightMM']+2*abs(d.get('dv',0)) < spec['h']*3.2,('decal height',label)
    assert len({root(i) for i in range(len(parent))})==1,(model['id'],'disconnected assemblies')

if __name__=='__main__':
    from campus_models import twin, oval
    from industrial_models import fins, ribbon, graphite
    models=[f(Building) for f in [twin,fins,ribbon,graphite,oval]]
    for model in models:
        validate(model)
        print(model['id'], sum(len(s['pieces']) for b in model['bags'] for s in b['steps']), 'pieces,',sum(len(b['steps']) for b in model['bags']),'steps')
    dump(DATA/'models.json',models)
    dump(DATA/'catalog.json',dict(parts=parts,colors={key:dict(name=n,hex=c,ldraw=i) for key,(n,c,i) in colors.items()}))

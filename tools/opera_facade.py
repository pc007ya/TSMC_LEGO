"""Stud-scale elevations of the National Taichung Theater.

Stations on the fountain elevation were measured against the venue's inclined
aerial photograph, rectified using the corners of the facade plane. Heights
are plates above the foundation. The two glazed openings and the white cave
are deliberately independent profiles.
"""
from itertools import groupby
from math import cos, pi

from industrial_models import decal


# Height, left/right edges of the first glazed cut, the main entrance and the
# sculptural cave, in studs from the left edge of the fountain elevation.
FRONT = [
    (0, 8.4,22.5, 29.9,45.8, 52.9,64.0),
    (4, 8.7,22.2, 30.2,45.4, 53.1,63.8),
    (8, 9.1,21.6, 30.7,45.1, 53.6,63.0),
    (12,10.1,20.4, 31.9,43.9, 54.4,62.4),
    (15,11.1,19.2, 33.9,42.4, 55.2,61.5),
    (20,11.6,18.6, 34.9,41.8, 55.8,61.0),
    (27,11.7,18.4, 35.1,41.6, 55.9,60.9),
    (33,11.3,18.5, 34.8,41.8, 55.8,61.0),
    (38,10.7,19.1, 33.6,42.4, 55.3,61.7),
    (40,10.0,19.6, 32.5,43.0, 54.8,62.6),
    (42, 8.8,20.4, 30.8,44.1, 54.1,64.1),
    (44, 7.2,21.6, 29.5,45.5, 52.9,65.5),
    (46, 6.5,22.1, 29.0,46.1, 52.3,65.9),
    (48, 6.6,21.9, 29.0,46.1, 52.3,65.7),
    (50, 7.5,21.1, 29.9,45.2, 52.9,65.1),
    (52, 9.2,19.7, 32.0,43.4, 54.1,63.6),
    (55,10.6,18.0, 33.5,42.0, 55.5,61.6),
    (60,11.4,17.2, 34.1,41.5, 56.5,60.6),
]

# On the return a broad corner window beneath the rolled eave is followed
# by one much narrower, full-height glazed cut approaching the front corner.
# Stations run from the rear of the side wall toward the fountain.
SIDE = [
    (0, -3.0,15.2, 23.5,36.9), (7, -3.0,14.6, 24.0,36.4),
    (14,-3.0,13.1, 25.7,34.8), (24,-3.0,11.9, 26.8,34.0),
    (33,-3.0,12.0, 26.5,34.1), (39,-3.0,12.5, 25.4,35.3),
    (44,-3.0,13.7, 23.0,37.4), (48,-3.0,14.0, 22.2,37.9),
    (51,-3.0,13.4, 22.8,37.1), (55,-3.0,12.3, 24.7,35.7),
    (60,-3.0,11.4, 25.4,35.2),
]


def section(stations, h):
    for lower, upper in zip(stations, stations[1:]):
        if h <= upper[0]:
            t = (h - lower[0]) / (upper[0] - lower[0])
            return [a + t*(b-a) for a,b in zip(lower[1:],upper[1:])]
    return stations[-1][1:]


def corner_height(side, u):
    if side:
        return 60 if u < 38 else [59,56,52,48,46][u-38]
    if u < 6:
        return [46,46,47,49,53,56][u]
    if u >= 68:
        return [55,51,48,46,46,46][u-68]
    return 60


def glass_profile(n, side, across, h, band):
    if band:
        return 'L',1
    # Smoked glass is confined to the shadow at the window foot and side
    # reveals. Clear gallery glazing shows the real structure behind the facade.
    if h<3 or (side and n==0 and h<10 and across<.23):
        return 'S',1
    return 'C',1


def profile(side, u, h, band):
    """Material and depth of the visible face, from the constant bearing row."""
    point = u+.5
    if h >= corner_height(side,u):
        return None, 0
    edge = section(SIDE if side else FRONT,h)
    if not side and h > 45 and ((u < 10 and point<edge[0]) or (u>64 and point>edge[-1])):
        # The high shoulder of the first/last bottle transitions to a lower
        # parapet, instead of a strip of wall closing the sky above the corner.
        return None, 0
    for n,(left,right) in enumerate(zip(edge[::2],edge[1::2])):
        if left-.65 <= point < left or right <= point < right+.65:
            return 'W',3
        if not left <= point < right:
            continue
        across = (point-left)/(right-left)
        if not side and n==2:
            # Here the visible centre is a white, doubly curved throat. Its
            # ascending shell bridges across the glazed cave at pavement level.
            foot = 8 + 6*(1-(abs(2*across-1))**3)
            if h >= foot:
                if 44 < h < 49 and (across<.18 or across>.81):
                    return 'S',1
                inward = .5+.5*cos(2*pi*across)
                depth = 1 + round(2*(.70*inward+.30*(abs(h-31)/31)))
                return 'W', depth
        if side and n==0 and h>53 + 6*(1-across):
            return 'W',2
        return glass_profile(n,side,across,h,band)
    return 'body',3


def coords(side, u, v, w, d):
    if side:
        return 83+v,9+u,d,w
    return 12+u,52+v,w,d


def lay(b, side, shape, color, u, v, y, w, d):
    x,z,width,depth = coords(side,u,v,w,d)
    b.area(shape,color,x,z,y,width,depth)


def part(b, side, pid, color, u, v, y, turned=False):
    x,z,_,_ = coords(side,u,v,1,1)
    b.put(pid,color,x,z,y,int(bool(side)^turned))


def glass(b, side, color, u, length, h, height):
    x,z,w,d = coords(side,u,0,length,1)
    if height==1 or color not in ('S','C'):
        b.area('plate' if height==1 else 'brick',color,x,z,2+h,w,d)
    else:
        for pos in range(0,length,2):
            part(b,side,'3005' if pos+1==length else '3065',color,u+pos,0,2+h)


def stroke(b,side,shape,color,u,n,depth,y):
    # Across the two one-stud reveals, longitudinal strips alternate with
    # transverse ties. Changing ribbon widths then bear on the continuous
    # back row, including the thin outward tips of the concrete shoulders.
    if depth==3 and n>=3:
        lay(b,side,shape,color,u,0,y,n,2)
        lay(b,side,shape,color,u,2,y,n,1)
    else:
        lay(b,side,shape,color,u,0,y,n,depth)


def pierce(b,side,u,h):
    # Real horizontal Technic bores give the wall a few representative circular
    # breathing holes. On the bright plaza face their backing stays pale.
    part(b,side,'3700','W',u,2,2+h)
    lay(b,side,'brick','D' if side else 'W',u,0,2+h,2,1)


def frames(side,courses):
    """Pair narrow real window frames over crosswise, studded sill plates."""
    width = 43 if side else 74
    sills, windows = {},{}
    for h,starts in [(3,(4,)),(12,(13,19)),(26,(27,33)),(40,(41,)),(51,(52,))]:
        for u in range(0,width-1,2):
            if not side and u>=52:
                continue
            if h==3:
                if side or not ((10<=u and u+1<21) or (32<=u and u+1<44)):
                    continue
                if u in (34,36,38):
                    continue  # the bilingual sign occupies this entrance bay
            for start in starts:
                # Only a complete pair of studs within the receding opening
                # will receive a frame; a nearby concrete shoulder stays free.
                heights=[y+(z-y)/2 for y,z in zip(courses,courses[1:]) if y<start+6 and z>h]
                if not all(profile(side,i,y,False)[0] in ('S','C') for i in (u,u+1) for y in heights):
                    break
                windows.setdefault(start,[]).append(u)
                if start==starts[0]:
                    sills.setdefault(h,set()).update((u,u+1))
    return sills,windows


def cave_section(u,h,band,ordinary):
    """Visible material and occupied depth from the deeper bearing at z=50."""
    left,right=section(FRONT,h)[-2:]
    x=u+.5
    if x<left or x>=right:
        return ordinary,5
    across=(x-left)/(right-left)
    foot=8+6*(1-abs(2*across-1)**3)
    if h<foot:
        return glass_profile(2,False,across,h,band)[0],1
    if 43<h<50 and (across < .18 or across > .82):
        return 'S',1
    # The centre of the throat recedes four studs from the front plane. The
    # shell rolls forward at either lip and again at the roof and pavement.
    spread=abs(2*across-1)
    section_curve=.8*spread**1.55+.2*(abs(h-30)/30)**1.6
    return 'W',1+round(4*section_curve)


def cave_stroke(b,shape,color,u,n,depth,y,tie=False):
    if color=='body':
        color='W'
    if depth==1 and shape=='brick' and color in ('S','C'):
        for i in range(0,n,2):
            part(b,False,'3005' if i+1==n else '3065',color,u+i,-2,y)
    elif depth==5 and tie:
        part(b,False,'3009' if shape=='brick' else '3666',color,u,-3,y,turned=True)
    elif depth==5:
        lay(b,False,shape,color,u,-2,y,n,1)
        lay(b,False,shape,color,u,-1,y,n,4)
    else:
        lay(b,False,shape,color,u,-2,y,n,depth)


def row(b,side,h,height,previous,sill):
    width = 43 if side else 74
    band = height==1 and h in (12,26,40,51)
    run = [profile(side,u,h+height*.5,band) for u in range(width)]
    shape = 'plate' if height==1 else 'brick'
    # Use separate crosswise ties for additions to the outer two layers. Every
    # tie reaches a stud on the previous, recessed course.
    tags = []
    for u,(color,depth) in enumerate(run):
        new_edge = depth>previous[u] and h>0
        if not side and 53<=u<66:
            shade,d=cave_section(u,h+height*.5,band,color)
            run[u]=(shade,d)
            tag=('cave',shade,d,u) if h and d>previous[u] else ('cave',shade,d)
        elif not side and h==3 and ((10<=u<21) or (32<=u<44)):
            tag=('canopy',)
        elif not side and h==4 and 34<=u<40:
            tag=('sign','K')
        elif u in sill:
            tag=('sill',)
        elif depth==1 and color in ('C','L','S'):
            tag=('glass',color)
        elif new_edge:
            tag=('tie',color,depth,u)
        else:
            tag=('face',color,depth)
        tags.append(tag)
    offset=0
    for tag,values in groupby(tags):
        n=sum(1 for _ in values)
        if tag[0]=='cave':
            if tag[1]:
                cave_stroke(b,shape,tag[1],offset,n,tag[2],2+h,
                            len(tag)==4 and previous[offset]<2 and h<54)
        elif tag[0]=='sign':
            assert n==6
            part(b,False,'3009','K',offset,0,2+h)
            decal(b,'ntt-entry','噴泉側中央玻璃入口上方的中英文字標',43.2,3.6)
        elif tag[0]=='canopy':
            # Each cantilever plate grips studs at the rear. The smooth front
            # lip remains visible one stud beyond the outer concrete plane.
            for u in range(offset,offset+n):
                part(b,False,'3710','D',u,0,2+h,turned=True)
        elif tag[0]=='sill':
            lay(b,side,'plate','L',offset,0,2+h,n,2)
        elif tag[0]=='glass':
            glass(b,side,tag[1],offset,n,h,height)
        elif tag[1]:
            color,depth=tag[1:3]
            # Small groups of openings concentrate in the walls between the
            # bottles, with occasional holes in the flanking wall.
            holes=[]
            if height==3 and color=='body' and depth==3 and n>=5:
                for u in range(offset+1,offset+n-2):
                    daylight_front=(u,h) in ((25,16),(22,27),(29,33),(48,33))
                    if daylight_front and not side or side and (u*13+h*7+3)%19==0:
                        holes.append(u)
            first=offset
            for u in holes:
                if u>first:stroke(b,side,shape,'W' if color=='body' else color,first,u-first,depth,2+h)
                pierce(b,side,u,h)
                first=u+2
            if first<offset+n:
                stroke(b,side,shape,'W' if color=='body' else color,first,offset+n-first,depth,2+h)
        offset+=n
    return [4 if not side and h==3 and ((10<=u<21) or (32<=u<44)) else depth
            for u,(_,depth) in enumerate(run)]


def opera_facades(b):
    # More than one elevation per brick is sampled around the broad shoulder
    # where the curve changes direction rapidly; the straight waist uses bricks.
    courses=[0,3,4,7,10,11,12,13,16,19,22,25,26,27,30,33,36,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,57,60]
    for side in (False,True):
        previous=[3]*(43 if side else 74)
        sills,windows=frames(side,courses)
        for h,stop in zip(courses,courses[1:]):
            if h==0:
                b.bag('北側玻璃轉角與帶孔曲牆' if side else '噴泉立面：雙入口、玻璃腰部與白色涵洞')
            if not side and h==33:
                b.bag('噴泉立面：三組曲牆肩部與白色收邊')
            if h==0:label='窗腳'
            elif h<13:label='入口與下端外張'
            elif h<39:label='收窄的腰身'
            elif h<52:label='向兩側展開的曲牆肩部'
            else:label='上緣收束'
            b.step(f'{"北側" if side else "噴泉側"} · {label} · 第 {h+1} 層薄板高',
                   '由左向右依圖扣合。深色窗面向內退，白色收邊磚跨接到背排。圓孔朝外；依圖留空，保留窗洞的深度。')
            previous=row(b,side,h,stop-h,previous,sills.get(h,set()))
            for u in windows.get(h,[]):
                part(b,side,'60592','L',u,1,2+h)

"""Incremental orthographic instruction drawings using the website's measured LDraw meshes."""
import base64
from functools import lru_cache
from io import BytesIO
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from manuals import pivot_point, size, yaw

PIXELS = 14  # Source pixels per stud. Only the local installation area is printed.
FIGURE = (476, 294)
PAPER = (246, 248, 246)
INK = (37, 74, 74)
EDGE = (169, 78, 34)
BADGE = ImageFont.load_default(size=15)


def unit(vector):
    return vector / np.linalg.norm(vector)


def image_bytes(im, fmt, **options):
    out = BytesIO()
    im.save(out, format=fmt, **options)
    return out.getvalue()


class Meshes:
    def __init__(self, root, entries):
        self.data = (root/'assets/parts/geometry.bin').read_bytes()
        self.entries = entries

    @lru_cache(maxsize=None)
    def load(self, part):
        record = self.entries[part]
        po, _, io = record['offsets']
        positions = np.frombuffer(self.data, '<i2', record['vertices']*3, po).reshape(-1, 3)/2048
        indices = np.frombuffer(self.data, '<u2' if record['indexBytes']==2 else '<u4', record['indices'], io)
        return positions, indices.reshape(-1, 3)


class View:
    """Cache one lit depth sprite per part/orientation and accumulate prior construction once."""
    def __init__(self, meshes, model, catalog, pieces, plan=False):
        self.meshes, self.model, self.catalog, self.plan = meshes, model, catalog, plan
        if plan:
            self.axes = np.array([[1,0,0],[0,0,1],[0,1,0]], dtype=float)
        else:
            x,y,z = model['camera']
            sight = unit(np.array([x,max(y,.77),z]))
            right = unit(np.array([sight[2],0,-sight[0]]))
            self.axes = np.stack((right,np.cross(right,sight),sight))
        self.light = unit(np.array([-.4,.85,.55]))
        self.sprite = lru_cache(maxsize=None)(self._sprite)
        self.placed = {}
        for p in pieces:
            w,d = size(p,catalog)
            x,z = pivot_point(model,p,p['x']+w/2,p['z']+d/2)
            position = self.axes @ np.array([x,p['y']*.4,z])
            gray, depth, offset = self.sprite(p['part'],round(yaw(model,p),6))
            xy = np.rint(position[:2]*PIXELS).astype(int)+offset
            self.placed[id(p)] = (xy,position[2],gray,depth)
        x0,y0 = np.min([v[0] for v in self.placed.values()],axis=0)
        x1,y1 = np.max([v[0]+v[2].shape[::-1] for v in self.placed.values()],axis=0)
        self.origin = np.array([x0-3,y0-3])
        self.depth = np.full((y1-y0+6,x1-x0+6), -np.inf, np.float32)
        self.shade = np.full(self.depth.shape, 247, np.uint8)

    def _sprite(self, part, angle):
        verts, triangles = self.meshes.load(part)
        a=math.radians(angle)
        c,s=math.cos(a),math.sin(a)
        rotated=verts @ np.array([[c,0,s],[0,1,0],[-s,0,c]])
        screen=rotated @ self.axes.T
        low=np.floor(screen[:,:2].min(axis=0)*PIXELS).astype(int)-1
        xy=screen[:,:2]*PIXELS-low
        width,height=np.ceil(xy.max(axis=0)).astype(int)+2
        depth=np.full((height,width),-np.inf,np.float32)
        shade=np.zeros((height,width),np.float32)
        tri=rotated[triangles]
        normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
        norms=np.linalg.norm(normals,axis=1)
        normals/=np.where(norms>1.e-8,norms,1)[:,None]
        for idx in np.flatnonzero(normals@self.axes[2]>.005):
            t=triangles[idx]
            pts=xy[t]
            x0,y0=np.maximum(np.floor(pts.min(axis=0)).astype(int),0)
            x1,y1=np.minimum(np.ceil(pts.max(axis=0)).astype(int)+1,[width,height])
            if x0==x1 or y0==y1:
                continue
            grid_x=np.arange(x0,x1)+.5-pts[0,0]
            grid_y=(np.arange(y0,y1)+.5-pts[0,1])[:,None]
            edge1,edge2=pts[1]-pts[0],pts[2]-pts[0]
            det=edge1[0]*edge2[1]-edge1[1]*edge2[0]
            if abs(det)<1.e-7:
                continue
            u=(grid_x*edge2[1]-grid_y*edge2[0])/det
            v=(grid_y*edge1[0]-grid_x*edge1[1])/det
            heights=screen[t,2]
            h=heights[0]+u*(heights[1]-heights[0])+v*(heights[2]-heights[0])
            buf=depth[y0:y1,x0:x1]
            visible=(u>=-.0001)&(v>=-.0001)&(u+v<=1.0001)&(h>=buf)
            buf[visible]=h[visible]
            shade[y0:y1,x0:x1][visible]=.65+.35*max(0,np.dot(normals[idx],self.light))
        if self.plan:
            # A vertical stud wall is edge-on in plan. Trace its actual height
            # change on the top surface so the stud grid can be counted.
            depth_map = np.where(np.isfinite(depth), depth, np.float32(1e4))
            neighbor_min = cv2.erode(depth_map, np.ones((3,3), np.uint8))
            raised_edge = np.isfinite(depth) & (depth - neighbor_min > .10)
            shade[raised_edge] *= .82
        return shade,depth,low

    def offline_atlas(self,pieces):
        """Serialize each lit depth stamp once for the browser's offline assembly renderer."""
        sprites=[]
        keys={}
        placements=[]
        for p in pieces:
            key=(p['part'],round(yaw(self.model,p),6))
            xy,anchor,shade,depth=self.placed[id(p)]
            if key not in keys:
                mask=np.isfinite(depth)
                encoded=np.zeros((*mask.shape,4),np.uint8)
                q=np.rint(depth[mask]*256).astype(np.int32)+32768
                if np.any((q<0)|(q>65535)):
                    raise ValueError('Part depth exceeds the manual stamp format')
                encoded[:,:,0][mask]=q%256
                encoded[:,:,1][mask]=q//256
                encoded[:,:,2][mask]=np.rint(shade[mask]*255).astype(np.uint8)
                encoded[:,:,3][mask]=255
                blob=image_bytes(Image.fromarray(encoded),'PNG',compress_level=8)
                keys[key]=len(sprites)
                sprites.append('data:image/png;base64,'+base64.b64encode(blob).decode('ascii'))
            x,y=xy-self.origin
            placements.append([keys[key],int(x),int(y),round(anchor*256)])
        return dict(sprites=sprites,placements=placements,width=self.shade.shape[1],
                    height=self.shade.shape[0],origin=self.origin.tolist(),unit=PIXELS)

    def thumbnail(self, part, color):
        shade,depth,_=self.sprite(part,0)
        ink=np.frombuffer(bytes.fromhex(self.catalog['colors'][color]['hex'][1:]),np.uint8)
        pixels=np.full((*shade.shape,3),255,np.uint8)
        visible=np.isfinite(depth)
        pixels[visible]=np.clip(shade[visible,None]*ink,0,255).astype(np.uint8)
        im=Image.fromarray(pixels)
        im.thumbnail((82,45),Image.Resampling.LANCZOS)
        return im

    def _mark(self,p):
        xy,z,shade,depth=self.placed[id(p)]
        x,y=xy-self.origin
        h,w=shade.shape
        old=self.depth[y:y+h,x:x+w]
        new=(depth+z).astype(np.float32)
        visible=np.isfinite(depth)&(new>=old-.001)
        old[visible]=new[visible]
        gray=self.shade[y:y+h,x:x+w]
        gray[visible]=(125+103*shade[visible]).astype(np.uint8)
        mask=(visible.astype(np.uint8)*255)
        edge=visible & (cv2.erode(mask,np.ones((3,3),np.uint8))==0)
        gray[edge]=177
        return xy,shade,visible

    def figure(self, group):
        bounds=[]
        for _,p in group:
            xy,_,gray,_=self.placed[id(p)]
            bounds.extend((xy,xy+gray.shape[::-1]))
        lo=np.min(bounds,axis=0);hi=np.max(bounds,axis=0)
        center=(lo+hi)/2
        span=(hi-lo)+PIXELS*(5 if self.plan else 6)
        factor=min(FIGURE[0]/span[0],FIGURE[1]/span[1],3)
        crop_wh=np.ceil(np.array(FIGURE)/factor).astype(int)
        crop_lo=np.floor(center-crop_wh/2).astype(int)
        width,height=crop_wh
        background=np.full((height,width),247,np.uint8)
        start=np.maximum(crop_lo,self.origin);stop=np.minimum(crop_lo+crop_wh,self.origin+self.shade.shape[::-1])
        x0,y0=start-crop_lo;x1,y1=stop-crop_lo;sx,sy=start-self.origin
        if x1>x0 and y1>y0:
            background[y0:y1,x0:x1]=self.shade[sy:sy+y1-y0,sx:sx+x1-x0]
        pixels=cv2.cvtColor(background,cv2.COLOR_GRAY2RGB)
        if self.plan:
            for axis in range(2):
                start_grid=int(math.ceil(crop_lo[axis]/PIXELS))*PIXELS
                for g in range(start_grid,crop_lo[axis]+crop_wh[axis],PIXELS):
                    i=g-crop_lo[axis];strip=pixels[:,i] if axis==0 else pixels[i,:]
                    empty=(strip[:,0]==247)
                    strip[empty]=(220,227,224)
        centers=[]
        for number,p in group:
            xy,shade,visible=self._mark(p)
            x,y=xy-crop_lo;h,w=visible.shape
            surface=pixels[y:y+h,x:x+w]
            ink=np.frombuffer(bytes.fromhex(self.catalog['colors'][p['color']]['hex'][1:]),np.uint8)
            surface[visible]=np.clip(shade[visible,None]*ink,0,255).astype(np.uint8)
            mask=(visible.astype(np.uint8)*255)
            border=visible & (cv2.erode(mask,np.ones((3,3),np.uint8))==0)
            surface[border]=INK if self.plan else EDGE
            if np.any(visible):
                distances=cv2.distanceTransform(mask,cv2.DIST_L2,3)
                iy,ix=np.unravel_index(np.argmax(distances),distances.shape)
            else:
                ix,iy=w/2,h/2
            centers.append((number,(x+ix)*FIGURE[0]/width,(y+iy)*FIGURE[1]/height))
        im=Image.fromarray(cv2.resize(pixels,FIGURE,interpolation=cv2.INTER_AREA if width>FIGURE[0] else cv2.INTER_CUBIC))
        if self.plan:
            draw=ImageDraw.Draw(im);used=[]
            for number,x,y in centers:
                offsets=[(0,0),(0,-18),(0,18),(-18,0),(18,0),(-20,-16),(20,-16),(-20,16),(20,16),(0,-36),(0,36)]
                choices=[(max(10,min(FIGURE[0]-10,x+dx)),max(10,min(FIGURE[1]-10,y+dy))) for dx,dy in offsets]
                best=next((pt for pt in choices if all(math.dist(pt,u)>18 for u in used)),choices[0])
                bx,by=best;used.append(best)
                draw.line([(x,y),(bx,by)],fill=INK,width=2)
                draw.ellipse((bx-9,by-9,bx+9,by+9),fill=INK,outline='white',width=1)
                draw.text((bx,by),str(number),font=BADGE,fill='white',anchor='mm')
        return im

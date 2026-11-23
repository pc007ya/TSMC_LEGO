"""Top-down instruction silhouettes traced from the physical LDraw meshes."""
import cv2
import numpy as np

def build(catalog, manifest, binary):
    symbols=[]
    labels={}
    data=binary.read_bytes()
    for part,defn in catalog['parts'].items():
        mesh=manifest[part];po,_,io=mesh['offsets']
        vertices=np.frombuffer(data,dtype='<i2',count=mesh['vertices']*3,offset=po).reshape(-1,3)/2048
        indices=np.frombuffer(data,dtype='<u2' if mesh['indexBytes']==2 else '<u4',count=mesh['indices'],offset=io).reshape(-1,3)
        flat=vertices[:,[0,2]];lo=flat.min(axis=0)-.12;hi=flat.max(axis=0)+.12;scale=40
        size=np.ceil((hi-lo)*scale).astype(int)+1
        mask=np.zeros((size[1],size[0]),dtype=np.uint8)
        xy=np.round((flat-lo)*scale).astype(np.int32)
        for tri in xy[indices]:cv2.fillConvexPoly(mask,tri,255)
        contours,_=cv2.findContours(mask,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
        lines=[]
        for contour in contours:
            path=cv2.approxPolyDP(contour,.85,True)
            if len(path)<3:continue
            points=path[:,0,:]/scale+lo
            lines.append('M'+' '.join(f'{x:.3f},{z:.3f}' for x,z in points)+'z')
        symbols.append(f'<path id="part{part}" fill-rule="evenodd" d="{"".join(lines)}"/>')
        # Locate irregular parts on a point that is actually inside the element.
        dist=cv2.distanceTransform(mask,cv2.DIST_L2,5)
        m=dist.max()
        yy,xx=np.nonzero(dist>=m*.87)
        i=np.argmin(((xx-size[0]/2)**2+(yy-size[1]/2)**2))
        labels[part]=(xx[i]/scale+lo[0],yy[i]/scale+lo[1])
    defs='<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'+''.join(symbols)+'</defs></svg>'
    return defs,labels

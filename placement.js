// X points right, Z points forward. Dimensions use studs horizontally and plate heights vertically.
export function positionOf(model, spec, p) {
  const w=p.r%2?spec.d:spec.w, d=p.r%2?spec.w:spec.d;
  const localX=p.x+w/2,localZ=p.z+d/2;
  const axis=p.pivotAt||(p.pivoted?model.pivot:null);
  const a=axis?axis.degrees*Math.PI/180:0, c=Math.cos(a),s=Math.sin(a);
  const x=axis?axis.x+(localX-axis.x)*c-(localZ-axis.z)*s:localX;
  const z=axis?axis.z+(localX-axis.x)*s+(localZ-axis.z)*c:localZ;
  return {x:x-model.width/2,y:p.y*.4,z:z-model.depth/2,w,d,angle:a,yaw:-p.r*Math.PI/2-a};
}
const faceDirections={front:[0,1],back:[0,-1],left:[-1,0],right:[1,0]};
export const artRatios={'giant-emblem':41.5/40,'giant-word':185.5/29.5,'giant':236/40.5,'giant-group':236/56,'tsmc':1,'tsmc-word':500/128,'rd-center':2.326,'jasm':3,'tsmc-sign':3.293,'campus-sign':3.75};
export function decalPose(model,spec,p){
  const loc=positionOf(model,spec,p),d=p.decal;
  const [hx,hz]=faceDirections[d.face],c=Math.cos(loc.angle),s=Math.sin(loc.angle);
  const nx=hx*c-hz*s,nz=hz*c+hx*s;
  const side=(hx?loc.w:loc.d)*.5+.004;
  const paperW=d.widthMM/8,paperH=d.heightMM/8;
  const width=Math.min(paperW,paperH*artRatios[d.art]),height=width/artRatios[d.art];
  return {x:loc.x+nx*side+nz*(d.du||0)/8,y:loc.y+spec.h*.2+(d.dv||0)/8,
    z:loc.z+nz*side-nx*(d.du||0)/8,nx,nz,width,height,yaw:Math.atan2(nx,nz)};
}

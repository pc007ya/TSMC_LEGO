// Offline orthographic illustrations from the same physical meshes as the exhibit.
import * as T from '../assets/vendor/three.module.min.js';
import {positionOf,decalPose} from '../placement.js';
import {loadPartGeometries} from '../assets/parts/library.js';

export async function paperStudio(catalog) {
  const geometry=await loadPartGeometries(T);
  const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});
  const W=590,H=350;
  renderer.setSize(W,H,false);
  renderer.setClearColor(0xffffff);
  const scene=new T.Scene(), cam=new T.OrthographicCamera(-1,1,1,-1,.1,400);
  scene.add(new T.HemisphereLight(0xffffff,0x8a9ba0,1.55));
  const light=new T.DirectionalLight(0xfff9ed,2.0);
  light.position.set(-24,43,31);
  scene.add(light);
  const old=new T.MeshStandardMaterial({color:0xbdc7c7,roughness:.64});
  const mats=Object.fromEntries(Object.entries(catalog.colors).map(([k,v])=>[k,new T.MeshStandardMaterial({
    color:v.hex,roughness:.42,metalness:.03,transparent:k==='T',opacity:k==='T'?.80:1
  })]));
  const outlineMaterial=new T.LineBasicMaterial({color:0xbe491d,transparent:true,opacity:.78,depthTest:false,depthWrite:false});
  const outlineShape=new T.EdgesGeometry(new T.BoxGeometry(1,1,1));
  const root=new T.Group(), highlights=new T.Group(),decals=new T.Group();
  scene.add(root,highlights,decals);
  let pieces=[],buckets=new Map(),mount,m;
  const textures=new Map();
  async function load(model){
    root.children.forEach(o=>o.dispose());root.clear();highlights.clear();
    for(const plane of decals.children){plane.geometry.dispose();plane.material.dispose()}decals.clear();
    m=model;mount=m.pivot;
    pieces=m.bags.flatMap(b=>b.steps.flatMap(s=>s.pieces));
    const freq=new Map();
    for(const p of pieces){freq.set(p.part,(freq.get(p.part)||0)+1)}
    buckets=new Map();
    for(const [id,n] of freq){
      const mesh=new T.InstancedMesh(geometry.get(id),old,n);
      mesh.frustumCulled=false;mesh.count=0;root.add(mesh);
      buckets.set(id,{mesh,indices:[]})
    }
    const dummy=new T.Object3D();
    for(const [i,p] of pieces.entries()){
      const def=catalog.parts[p.part],pose=positionOf(m,def,p);
      p.h=def.h*.4;p.w=pose.w;p.d=pose.d;p.freeAngle=pose.angle;
      p.base=new T.Vector3(pose.x+m.width/2,pose.y,pose.z+m.depth/2);
      dummy.position.copy(p.base);dummy.rotation.set(0,pose.yaw,0);
      dummy.scale.set(.995,.995,.995);dummy.updateMatrix();p.matrix=dummy.matrix.clone();
      const pool=buckets.get(p.part);pool.mesh.setMatrixAt(pool.indices.length,p.matrix);pool.indices.push(i);
      if(p.decal){
        const dec=p.decal,sign=decalPose(m,def,p);
        if(!textures.has(dec.art)){
          const tex=await new T.TextureLoader().loadAsync('../assets/decals/'+dec.art+'.svg');tex.colorSpace=T.SRGBColorSpace;
          textures.set(dec.art,tex);
        }
        const plane=new T.Mesh(new T.PlaneGeometry(sign.width,sign.height),new T.MeshBasicMaterial({map:textures.get(dec.art),transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-2}));
        plane.rotation.y=sign.yaw;
        plane.position.set(sign.x+m.width/2,sign.y,sign.z+m.depth/2);
        plane.userData.idx=i;decals.add(plane);
      }
    }
    for(const {mesh} of buckets.values()){mesh.instanceMatrix.needsUpdate=true}
  }
  const v=new T.Vector3();
  function render(start,end){
    const active=pieces.slice(start,end);
    for(const obj of [...highlights.children]){
      if(obj.isInstancedMesh)obj.dispose();highlights.remove(obj);
    }
    for(const {mesh,indices} of buckets.values()){
      let low=0,high=indices.length;
      while(low<high){const mid=(low+high)>>1;if(indices[mid]<start)low=mid+1;else high=mid}
      mesh.count=low;mesh.visible=low>0;
    }
    const groups=new Map();
    for(const p of active){const key=p.part+'-'+p.color;if(!groups.has(key))groups.set(key,[]);groups.get(key).push(p)}
    for(const list of groups.values()){
      const mesh=new T.InstancedMesh(geometry.get(list[0].part),mats[list[0].color],list.length);
      list.forEach((p,i)=>mesh.setMatrixAt(i,p.matrix));mesh.instanceMatrix.needsUpdate=true;mesh.frustumCulled=false;highlights.add(mesh)
    }
    for(const p of active){
      const edge=new T.LineSegments(outlineShape,outlineMaterial);edge.position.copy(p.base);edge.position.y+=p.h/2;
      edge.scale.set(p.w,p.h,p.d);edge.rotation.y=-p.freeAngle;
      edge.renderOrder=5;highlights.add(edge)
    }
    decals.children.forEach(plane=>{plane.visible=plane.userData.idx<end});
    const box=new T.Box3();
    const signed=active.find(p=>p.decal);
    for(const p of (signed?[signed]:active))box.expandByPoint(v.copy(p.base).add(new T.Vector3(-p.w/2,0,-p.d/2))).expandByPoint(v.copy(p.base).add(new T.Vector3(p.w/2,p.h,p.d/2)));
    const center=box.getCenter(new T.Vector3()),extent=box.getSize(new T.Vector3());
    const [xDir,yDir,zDir]=m.camera;
    let x=Math.abs(center.x/m.width-.5)>.12?Math.abs(xDir)*Math.sign(center.x/m.width-.5):xDir;
    let z=Math.abs(center.z/m.depth-.5)>.12?Math.abs(zDir)*Math.sign(center.z/m.depth-.5):zDir;
    let rise=Math.max(.85,yDir);
    if(signed){
      const face=decalPose(m,catalog.parts[signed.part],signed);
      x=1.55*face.nx+.20*face.nz;z=1.55*face.nz-.20*face.nx;rise=.45;
    }
    const target=center.clone();
    cam.position.copy(target).addScaledVector(new T.Vector3(x,rise,z).normalize(),112);
    cam.lookAt(target);cam.updateMatrixWorld();
    // Context includes the mounting surfaces around this page's new pieces.
    const frame=new T.Box3();
    for(const sx of [-1,1])for(const sy of [-1,1])for(const sz of [-1,1]){
      v.copy(center);v.x+=sx*(extent.x/2+3.5);v.y+=sy*(extent.y/2+2.5);v.z+=sz*(extent.z/2+3.5);
      frame.expandByPoint(v.applyMatrix4(cam.matrixWorldInverse))
    }
    const span=Math.max((frame.max.x-frame.min.x)*H/W,frame.max.y-frame.min.y,9);
    cam.left=-span*W/H/2;cam.right=-cam.left;cam.top=span/2;cam.bottom=-cam.top;cam.updateProjectionMatrix();
    renderer.render(scene,cam);
    return {side:(z>0?'前':'後')+(x>0?'右':'左'),detail:!!signed,jpeg:renderer.domElement.toDataURL('image/jpeg',.82)};
  }
  return {load,render}
}

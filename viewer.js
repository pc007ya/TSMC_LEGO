import * as THREE from 'three';
import { OrbitControls } from './assets/vendor/OrbitControls.js';
import { RoomEnvironment } from './assets/vendor/RoomEnvironment.js';
import { loadPartGeometries } from './assets/parts/library.js';
import { studioPass } from './studio.js';
import { positionOf, decalPose, artRatios } from './placement.js';

const cameraAxes = dir => {
  const right=new THREE.Vector3(dir.z,0,-dir.x).normalize();
  return {right,up:new THREE.Vector3().crossVectors(dir,right).normalize()};
};

export async function createViewer(host,catalog,place) {
  const geometries=await loadPartGeometries(THREE);
  const renderer=new THREE.WebGLRenderer({antialias:true,alpha:false,preserveDrawingBuffer:true,powerPreference:'high-performance'});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));
  renderer.shadowMap.enabled=true;
  renderer.shadowMap.autoUpdate=false;
  renderer.shadowMap.type=THREE.VSMShadowMap;
  renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.toneMapping=THREE.NeutralToneMapping;
  renderer.toneMappingExposure=.91;
  host.append(renderer.domElement);
  const scene=new THREE.Scene();
  scene.background=new THREE.Color(0xe1e1db);
  const studio=new RoomEnvironment(),pmrem=new THREE.PMREMGenerator(renderer);
  scene.environment=pmrem.fromScene(studio,.035).texture;
  scene.environmentIntensity=.29;
  pmrem.dispose();studio.dispose();
  const camera=new THREE.OrthographicCamera(-20,20,20,-20,.08,500);
  const controls=new OrbitControls(camera,renderer.domElement);
  controls.enablePan=true;controls.minPolarAngle=.045;controls.maxPolarAngle=Math.PI*.495;
  controls.minZoom=.42;controls.maxZoom=22;
  const key=new THREE.DirectionalLight(0xfffbf6,1.8);
  key.position.set(-32,65,13);key.castShadow=true;key.shadow.mapSize.set(1024,1024);key.shadow.radius=8;key.shadow.blurSamples=12;key.shadow.intensity=.75;
  key.shadow.normalBias=.018;key.shadow.bias=-.00012;
  scene.add(key,new THREE.HemisphereLight(0xf1faff,0x91969a,.64));
  const rim=new THREE.DirectionalLight(0xe4f3ff,.69);rim.position.set(35,28,-26);scene.add(rim);
  const ground=new THREE.Mesh(new THREE.PlaneGeometry(420,420),new THREE.MeshStandardMaterial({color:0xc7c9ca,roughness:.95}));
  ground.rotation.x=-Math.PI/2;ground.position.y=-.028;ground.receiveShadow=true;scene.add(ground);
  const mat=new Map();
  for(const [id,c] of Object.entries(catalog.colors)){
    const glass=id==='T'||id==='S';
    const props={color:id==='T'?0x008198:c.hex,roughness:glass?.1:.39,metalness:0,envMapIntensity:glass?1.3:.65};
    mat.set(id,glass?new THREE.MeshPhysicalMaterial({...props,clearcoat:1,clearcoatRoughness:.09,
      transparent:true,opacity:id==='T'?.81:.89,ior:1.56,specularIntensity:1}):new THREE.MeshStandardMaterial(props));
  }
  const loader=new THREE.TextureLoader();
  const decals=new Map(await Promise.all(Object.keys(artRatios).map(async id=>{
    const texture=await loader.loadAsync('./assets/decals/'+id+'.svg');
    texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=renderer.capabilities.getMaxAnisotropy();
    return [id,new THREE.MeshBasicMaterial({map:texture,transparent:true,alphaTest:.055,
      depthWrite:false,polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-2,toneMapped:false})];
  })));
  const plane=new THREE.PlaneGeometry(1,1);
  const guideMat=new THREE.MeshBasicMaterial({color:0xe68b38,transparent:true,opacity:.31,depthWrite:false});
  const markMat=new THREE.LineBasicMaterial({color:0xa63e0d,transparent:true,opacity:.96,depthTest:false});
  const partsGroup=new THREE.Group(),signs=new THREE.Group(),guides=new THREE.Group();
  scene.add(partsGroup,signs,guides);
  const dummy=new THREE.Object3D(),mouse=new THREE.Vector2(),ray=new THREE.Raycaster();
  const buckets=new Map(),signMap=new Map();
  let model,all=[],active=null,hoverMesh=null,profileHeight=30,profileWidth=40,downPoint,flight=0,token=0;
  const renderStudio=renderer.extensions.has('EXT_color_buffer_float')?studioPass(renderer):((s,c)=>renderer.render(s,c));
  let queued=0;
  function draw(){if(queued)cancelAnimationFrame(queued);queued=0;renderStudio(scene,camera)}
  function scheduleDraw(){if(!queued)queued=requestAnimationFrame(draw)}
  function logicalHeight(){
    return Math.max(profileHeight,profileWidth*host.clientHeight/Math.max(1,host.clientWidth));
  }
  function resize(){
    const w=host.clientWidth,h=host.clientHeight;if(!w||!h)return;
    renderer.setSize(w,h,false);
    const height=logicalHeight(),ratio=w/h;
    camera.left=-height*ratio/2;camera.right=-camera.left;camera.top=height/2;camera.bottom=-camera.top;
    camera.updateProjectionMatrix();draw();
  }
  function frame(direction,pieces){
    if(!model)return;
    const dir=new THREE.Vector3(...direction).normalize(),{right,up}=cameraAxes(dir);
    let l=Infinity,r=-Infinity,b=Infinity,t=-Infinity,near=Infinity,far=-Infinity;
    for(const p of pieces){
      const sp=catalog.parts[p.part],v=positionOf(model,sp,p),c=Math.cos(v.angle),s=Math.sin(v.angle);
      for(const u of [-v.w/2,v.w/2])for(const f of [-v.d/2,v.d/2])for(const h of [0,sp.h*.4+.18]){
        const pt=new THREE.Vector3(v.x+u*c-f*s,v.y+h,v.z+u*s+f*c);
        const xx=pt.dot(right),yy=pt.dot(up),zz=pt.dot(dir);
        l=Math.min(l,xx);r=Math.max(r,xx);b=Math.min(b,yy);t=Math.max(t,yy);
        near=Math.min(near,zz);far=Math.max(far,zz);
      }
    }
    const target=right.multiplyScalar((l+r)/2).addScaledVector(up,(b+t)/2).addScaledVector(dir,(near+far)/2);
    controls.target.copy(target);camera.position.copy(target).addScaledVector(dir,Math.max(105,(far-near)*.55+15));
    camera.zoom=1;profileHeight=(t-b)*1.16;profileWidth=(r-l)*1.12;
    controls.update();resize();
  }
  function home(){if(model)frame(model.camera,all)}
  function inspect(view){
    if(view.region){
      const [x0,x1,z0,z1,y0,y1]=view.region;
      const selected=all.filter(p=>{
        const sp=catalog.parts[p.part], w=p.r%2?sp.d:sp.w, d=p.r%2?sp.w:sp.d;
        const x=p.x+w/2,z=p.z+d/2,y=p.y+sp.h/2;
        return x>=x0&&x<=x1&&z>=z0&&z<=z1&&y>=y0&&y<=y1;
      });
      frame(view.direction,selected.length?selected:all);
      return;
    }
    const pieces=view.scope==='all'?all:view.pivoted?all.filter(p=>p.pivoted):model.bags[view.bag-1].steps.flatMap(step=>step.pieces);
    const target=view.minHeight==null?pieces:pieces.filter(p=>p.y>=view.minHeight);
    frame(view.direction,target.length?target:pieces);
  }
  function assignPose(mesh,p){
    const v=positionOf(model,catalog.parts[p.part],p);
    mesh.position.set(v.x,v.y,v.z);mesh.rotation.y=v.yaw;
  }
  function setModel(m){
    for(const mesh of buckets.values()){partsGroup.remove(mesh);mesh.dispose()}
    signs.clear();signMap.clear();buckets.clear();
    model=m;all=m.bags.flatMap(b=>b.steps.flatMap(s=>s.pieces));token++;
    const byMaterial=Map.groupBy?Map.groupBy(all,p=>p.part+'/'+p.color):all.reduce((map,p)=>{
      const k=p.part+'/'+p.color;if(!map.has(k))map.set(k,[]);map.get(k).push(p);return map},new Map());
    for(const [k,list] of byMaterial){
      const first=list[0],mesh=new THREE.InstancedMesh(geometries.get(first.part),mat.get(first.color),list.length);
      list.forEach((p,i)=>{assignPose(dummy,p);dummy.scale.set(.995,.997,.995);dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix)});
      mesh.castShadow=true;mesh.receiveShadow=true;mesh.frustumCulled=false;partsGroup.add(mesh);buckets.set(k,mesh);
    }
    for(const p of all.filter(p=>p.decal)){
      const v=decalPose(m,catalog.parts[p.part],p),mesh=new THREE.Mesh(plane,decals.get(p.decal.art));
      mesh.scale.set(v.width,v.height,1);mesh.position.set(v.x,v.y,v.z);mesh.rotation.y=v.yaw;
      mesh.renderOrder=2;signs.add(mesh);signMap.set(p,mesh);
    }
    const radius=Math.hypot(m.width,m.depth)*.68;
    const lightScale=m.series==='collector'?Math.max(1,radius/43):1;
    key.position.set(-32*lightScale,65*lightScale,13*lightScale);
    Object.assign(key.shadow.camera,{left:-radius,right:radius,top:radius,bottom:-radius,near:.1,far:170*lightScale});
    key.shadow.camera.updateProjectionMatrix();renderer.shadowMap.needsUpdate=true;home();
  }
  function clearGuides(){
    token++;if(flight)cancelAnimationFrame(flight);
    for(const obj of [...guides.children]){guides.remove(obj);if(obj.userData.ownedGeometry)obj.geometry.dispose()}
    active=null;hoverMesh=null;
  }
  function show(pieces,next=null,stickerReady=false){
    clearGuides();
    for(const mesh of buckets.values())mesh.count=0;
    for(const mesh of signMap.values())mesh.visible=false;
    for(const p of pieces){
      buckets.get(p.part+'/'+p.color).count++;
      if(p.decal)signMap.get(p).visible=true;
    }
    for(const mesh of buckets.values())mesh.visible=mesh.count>0;
    if(next){
      active=next;
      if(stickerReady&&next.decal)signMap.get(next).visible=true;
      const sp=catalog.parts[next.part],loc=positionOf(model,sp,next);
      hoverMesh=new THREE.Mesh(geometries.get(next.part),guideMat);assignPose(hoverMesh,next);guides.add(hoverMesh);
      const hw=sp.w/2,hd=sp.d/2,h=sp.h*.4+.04;
      const rect=[[-hw,-hd],[hw,-hd],[hw,hd],[-hw,hd],[-hw,-hd]].map(([x,z])=>new THREE.Vector3(x,h,z));
      const outline=new THREE.Line(new THREE.BufferGeometry().setFromPoints(rect),markMat);
      outline.position.set(loc.x,loc.y,loc.z);outline.rotation.y=loc.yaw;outline.userData.ownedGeometry=true;outline.renderOrder=5;guides.add(outline);
    }
    renderer.shadowMap.needsUpdate=true;scheduleDraw();
  }
  function animatePlace(p,done){
    if(!p||matchMedia('(prefers-reduced-motion: reduce)').matches)return done();
    clearGuides();const run=token,mesh=new THREE.Mesh(geometries.get(p.part),mat.get(p.color));
    assignPose(mesh,p);const base=mesh.position.y;mesh.castShadow=true;guides.add(mesh);
    if(p.decal){
      const installed=signMap.get(p),moving=installed.clone();
      installed.visible=false;guides.add(moving);mesh.attach(moving);
    }
    const start=performance.now();
    function tick(now){
      if(run!==token)return;const f=Math.max(0,1-(now-start)/240);
      mesh.position.y=base+f*f*3;renderer.shadowMap.needsUpdate=true;draw();
      if(f>0)flight=requestAnimationFrame(tick);else{flight=0;done()}
    }
    tick(start);
  }
  function focusPiece(){
    if(!active)return;
    const v=positionOf(model,catalog.parts[active.part],active);
    const offset=camera.position.clone().sub(controls.target);
    controls.target.set(v.x,v.y,v.z);camera.position.copy(controls.target).add(offset);camera.zoom=2.55;camera.updateProjectionMatrix();controls.update();draw();
  }
  function focusDecal(p){
    if(!p?.decal)return;
    const v=decalPose(model,catalog.parts[p.part],p),width=Math.max(8,v.width*2.9);
    controls.target.set(v.x,v.y,v.z);
    camera.position.copy(controls.target).add(new THREE.Vector3(v.nx+v.nz*.11,.16,v.nz-v.nx*.11).normalize().multiplyScalar(6));
    camera.zoom=THREE.MathUtils.clamp(logicalHeight()/width,1.2,16);camera.updateProjectionMatrix();controls.update();draw();
  }
  function zoom(f){camera.zoom=THREE.MathUtils.clamp(camera.zoom*f,.42,22);camera.updateProjectionMatrix();draw()}
  function rotate(){const offset=camera.position.clone().sub(controls.target).applyAxisAngle(new THREE.Vector3(0,1,0),Math.PI/9);camera.position.copy(controls.target).add(offset);controls.update();draw()}
  renderer.domElement.addEventListener('pointerdown',e=>{downPoint=[e.clientX,e.clientY]});
  renderer.domElement.addEventListener('pointerup',e=>{
    if(!hoverMesh||!downPoint||Math.hypot(e.clientX-downPoint[0],e.clientY-downPoint[1])>5)return;
    const b=renderer.domElement.getBoundingClientRect();mouse.set((e.clientX-b.left)/b.width*2-1,1-(e.clientY-b.top)/b.height*2);
    ray.setFromCamera(mouse,camera);if(ray.intersectObject(hoverMesh).length)place();
  });
  controls.addEventListener('change',scheduleDraw);new ResizeObserver(resize).observe(host);
  return {setModel,show,home,inspect,rotate,zoom,focusPiece,focusDecal,animatePlace,draw};
}

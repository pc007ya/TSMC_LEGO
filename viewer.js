import * as THREE from 'three';
import { OrbitControls } from './assets/vendor/OrbitControls.js';
import { loadPartGeometries } from './assets/parts/library.js';

export async function createViewer(host, catalog, place) {
  const geometries = await loadPartGeometries(THREE);
  const renderer = new THREE.WebGLRenderer({antialias:true,alpha:false,preserveDrawingBuffer:true});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,1.65));
  renderer.setClearColor(0xdce9e5);
  renderer.shadowMap.enabled=true;
  renderer.shadowMap.type=THREE.PCFSoftShadowMap;
  renderer.outputColorSpace=THREE.SRGBColorSpace;
  host.append(renderer.domElement);
  const scene=new THREE.Scene();
  const camera=new THREE.OrthographicCamera(-20,20,20,-20,.1,400);
  const controls=new OrbitControls(camera,renderer.domElement);
  controls.enablePan=true;
  controls.minPolarAngle=.09;controls.maxPolarAngle=Math.PI*.52;
  controls.minZoom=.42;controls.maxZoom=12;
  controls.target.set(0,4,0);
  const ambient=new THREE.HemisphereLight(0xf8fcff,0xb9c4c6,1.62);
  scene.add(ambient);
  const key=new THREE.DirectionalLight(0xfffcf7,1.85);
  key.position.set(-29,54,32);key.castShadow=true;
  key.shadow.mapSize.set(2048,2048);
  Object.assign(key.shadow.camera,{left:-35,right:35,top:34,bottom:-34,near:1,far:125});
  key.shadow.normalBias=.027;key.shadow.bias=-.00015;key.shadow.radius=3;
  scene.add(key);
  const rim=new THREE.DirectionalLight(0xe0f4ff,1.05);rim.position.set(25,28,-21);scene.add(rim);
  const ground=new THREE.Mesh(new THREE.PlaneGeometry(400,400),new THREE.MeshStandardMaterial({color:0xc3d4d0,roughness:.94}));
  ground.rotation.x=-Math.PI/2;ground.position.y=-.045;ground.receiveShadow=true;scene.add(ground);
  const grid=new THREE.GridHelper(220,110,0x9faea0,0x9faea0);
  grid.material.transparent=true;grid.material.opacity=.18;grid.material.depthWrite=false;grid.position.y=-.04;scene.add(grid);
  const materials=new Map(Object.entries(catalog.colors).map(([id,c])=>[id,new THREE.MeshStandardMaterial({
    color:c.hex,roughness:id==='T'?.17:.46,metalness:id==='T'?.10:.025,transparent:id==='T',opacity:id==='T'?.8:1
  })]));
  const guideMat=new THREE.MeshBasicMaterial({color:0xe07832,transparent:true,opacity:.27,depthWrite:false});
  const markMat=new THREE.LineBasicMaterial({color:0xb2421f,transparent:true,opacity:.93,depthTest:false});
  const batch=new THREE.Group();scene.add(batch);
  const guides=new THREE.Group();scene.add(guides);
  const dummy=new THREE.Object3D(),ray=new THREE.Raycaster(),mouse=new THREE.Vector2();
  let model,all=[],active=null,hoverMesh=null,profileHeight=30,downPoint,flight=0,token=0;
  function coords(p) {
    const part=catalog.parts[p.part],swapped=p.r%2===1;
    return new THREE.Vector3(p.x+(swapped?part.d:part.w)/2-model.width/2,p.y*.4,p.z+(swapped?part.w:part.d)/2-model.depth/2);
  }
  function draw(){renderer.render(scene,camera)}
  function resize(){
    const w=host.clientWidth,h=host.clientHeight;if(!w||!h)return;
    renderer.setSize(w,h,false);
    const aspect=w/h, extent=Math.max(profileHeight, (model?Math.hypot(model.width,model.depth):40)*1.06/aspect);
    camera.left=-extent*aspect/2;camera.right=-camera.left;camera.top=extent/2;camera.bottom=-camera.top;
    camera.updateProjectionMatrix();draw()
  }
  function home(){
    if(!model)return;
    const high=Math.max(...all.map(p=>(p.y+catalog.parts[p.part].h)*.4));
    const target=new THREE.Vector3(0,high*.38,0);
    const dir=new THREE.Vector3(...model.camera).normalize();
    controls.target.copy(target);camera.position.copy(target).addScaledVector(dir,85);
    camera.zoom=1;profileHeight=Math.max(18,Math.hypot(model.width,model.depth)*.56+high*.77);
    controls.update();resize();
  }
  function setModel(m){
    model=m;all=m.bags.flatMap(b=>b.steps.flatMap(s=>s.pieces));token++;home()
  }
  function clearGuides(){
    token++;if(flight)cancelAnimationFrame(flight);
    for(const obj of [...guides.children]){guides.remove(obj);if(obj.userData.ownedGeometry)obj.geometry.dispose()}
    active=null;hoverMesh=null;
  }
  function show(pieces,next=null){
    clearGuides();
    for(const obj of [...batch.children]){batch.remove(obj);obj.dispose()}
    const buckets=new Map();
    for(const p of pieces){const key=p.part+'-'+p.color;if(!buckets.has(key))buckets.set(key,[]);buckets.get(key).push(p)}
    for(const list of buckets.values()){
      const p=list[0],mesh=new THREE.InstancedMesh(geometries.get(p.part),materials.get(p.color),list.length);
      list.forEach((v,i)=>{dummy.scale.set(.995,.995,.995);dummy.position.copy(coords(v));dummy.rotation.set(0,-v.r*Math.PI/2,0);dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix)});
      mesh.castShadow=true;mesh.receiveShadow=true;mesh.frustumCulled=false;batch.add(mesh);
    }
    if(next){
      active=next;
      const geom=geometries.get(next.part),pt=coords(next);
      hoverMesh=new THREE.Mesh(geom,guideMat);hoverMesh.position.copy(pt);hoverMesh.rotation.y=-next.r*Math.PI/2;guides.add(hoverMesh);
      const p=catalog.parts[next.part],w=next.r%2?p.d:p.w,d=next.r%2?p.w:p.d;
      const h=p.h*.4;
      const rect=[[0,0],[w,0],[w,d],[0,d],[0,0]].map(([x,z])=>new THREE.Vector3(pt.x+x-w/2,pt.y+h+.05,pt.z+z-d/2));
      const outline=new THREE.Line(new THREE.BufferGeometry().setFromPoints(rect),markMat);
      outline.userData.ownedGeometry=true;outline.renderOrder=5;guides.add(outline);
    }
    draw();
  }
  function animatePlace(p,done){
    if(!p)return done();
    if(matchMedia('(prefers-reduced-motion: reduce)').matches)return done();
    clearGuides();
    const run=token,mesh=new THREE.Mesh(geometries.get(p.part),materials.get(p.color));
    const base=coords(p);mesh.rotation.y=-p.r*Math.PI/2;mesh.castShadow=true;guides.add(mesh);
    const start=performance.now();
    function tick(now){
      if(run!==token)return;
      const f=Math.max(0,1-(now-start)/240);
      mesh.position.copy(base);mesh.position.y+=f*f*3.0;draw();
      if(f>0)flight=requestAnimationFrame(tick);else{flight=0;done()}
    }
    tick(start);
  }
  function focusPiece(){
    if(!active)return;
    const pt=coords(active),offset=camera.position.clone().sub(controls.target);
    controls.target.copy(pt);camera.position.copy(pt).add(offset);camera.zoom=2.5;camera.updateProjectionMatrix();controls.update();draw();
  }
  function zoom(f){camera.zoom=THREE.MathUtils.clamp(camera.zoom*f,.42,12);camera.updateProjectionMatrix();draw()}
  function rotate(){const offset=camera.position.clone().sub(controls.target).applyAxisAngle(new THREE.Vector3(0,1,0),Math.PI/9);camera.position.copy(controls.target).add(offset);controls.update();draw()}
  renderer.domElement.addEventListener('pointerdown',e=>{downPoint=[e.clientX,e.clientY]});
  renderer.domElement.addEventListener('pointerup',e=>{
    if(!hoverMesh||!downPoint||Math.hypot(e.clientX-downPoint[0],e.clientY-downPoint[1])>5)return;
    const b=renderer.domElement.getBoundingClientRect();
    mouse.set((e.clientX-b.left)/b.width*2-1,1-(e.clientY-b.top)/b.height*2);
    ray.setFromCamera(mouse,camera);if(ray.intersectObject(hoverMesh).length)place()
  });
  controls.addEventListener('change',draw);
  new ResizeObserver(resize).observe(host);
  return {setModel,show,home,rotate,zoom,focusPiece,animatePlace,draw};
}

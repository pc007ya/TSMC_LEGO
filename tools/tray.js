export async function renderTray(){
 const THREE=await import('three');
 const {loadPartGeometries}=await import('../assets/parts/library.js');
 const geometries=await loadPartGeometries(THREE), models=await(await fetch(new URL('../data/models.json',import.meta.url))).json(),catalog=await(await fetch(new URL('../data/catalog.json',import.meta.url))).json();
 const keys=[...new Set(models.flatMap(m=>m.bags.flatMap(b=>b.steps.flatMap(s=>s.pieces.map(p=>p.part+'-'+p.color)))))].sort();
 const col=12,row=Math.ceil(keys.length/col),cell=88;
 const target=document.createElement('canvas');target.width=col*cell;target.height=row*cell;
 const ctx=target.getContext('2d');
 const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,preserveDrawingBuffer:true});renderer.setClearColor(0,0);renderer.setSize(cell,cell,false);
 const scene=new THREE.Scene(),camera=new THREE.OrthographicCamera(-1,1,1,-1,.01,60);
 scene.add(new THREE.HemisphereLight(0xffffff,0xb6c2b9,1.7));
 const key=new THREE.DirectionalLight(0xffffff,1.8);key.position.set(-3,7,5);scene.add(key);
 keys.forEach((k,i)=>{
   const [id,c]=k.split('-'),def=catalog.parts[id];
   const mat=new THREE.MeshStandardMaterial({color:catalog.colors[c].hex,roughness:.42,transparent:c==='C',opacity:c==='C'?.65:1});
   const mesh=new THREE.Mesh(geometries.get(id),mat);scene.add(mesh);
   const center=new THREE.Vector3(0,def.h*.2,0);camera.position.copy(center).add(new THREE.Vector3(7,7,10));camera.lookAt(center);camera.updateMatrixWorld();
   const bbox=geometries.get(id).boundingBox;
   const bound=new THREE.Box3();for(const x of [bbox.min.x,bbox.max.x])for(const y of [bbox.min.y,bbox.max.y])for(const z of [bbox.min.z,bbox.max.z])bound.expandByPoint(new THREE.Vector3(x,y,z).applyMatrix4(camera.matrixWorldInverse));
   const mid=bound.getCenter(new THREE.Vector3());
   const span=Math.max(bound.max.x-bound.min.x,bound.max.y-bound.min.y)*.62;
   camera.left=mid.x-span;camera.right=mid.x+span;camera.top=mid.y+span;camera.bottom=mid.y-span;camera.updateProjectionMatrix();
   renderer.render(scene,camera);ctx.drawImage(renderer.domElement,(i%col)*cell,Math.floor(i/col)*cell);scene.remove(mesh);mat.dispose();
 });
 renderer.dispose();return {keys,col,row,data:target.toDataURL('image/webp',.93).split(',')[1]};
}

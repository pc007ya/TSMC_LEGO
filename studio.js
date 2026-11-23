import * as THREE from 'three';

// Local contact shadows distinguish stud bases, abutting panels, and machinery feet.
// The orthographic depth buffer is linear, so sampling distances are expressed in studs.
export function studioPass(renderer){
  const depth=new THREE.DepthTexture(1,1,THREE.UnsignedIntType);
  const target=new THREE.WebGLRenderTarget(1,1,{type:THREE.HalfFloatType,depthTexture:depth,samples:2});
  const uniforms={beauty:{value:target.texture},depthTex:{value:depth},texel:{value:new THREE.Vector2(1,1)},scale:{value:1},viewRange:{value:1}};
  const shader=new THREE.ShaderMaterial({uniforms,depthTest:false,depthWrite:false,
    vertexShader:'varying vec2 pos; void main(){pos=uv;gl_Position=vec4(position.xy,0.,1.);}',
    fragmentShader:`
      uniform sampler2D beauty,depthTex;
      uniform vec2 texel;
      uniform float scale,viewRange;
      varying vec2 pos;
      float distanceAt(vec2 uv){return texture2D(depthTex,uv).x*viewRange;}
      void main(){
        vec3 color=texture2D(beauty,pos).rgb;
        float h=distanceAt(pos), shade=0.;
        vec2 slope=clamp(vec2(dFdx(h),dFdy(h)),vec2(-.22),vec2(.22));
        for(int i=0;i<12;i++){
          float phi=(float(i)+.2)*2.39996323;
          float rad=(i<6?.38:1.45);
          vec2 delta=vec2(cos(phi),sin(phi))*max(1.,min(38.,scale*rad));
          float obstruction=h+dot(delta,slope)-distanceAt(pos+texel*delta);
          shade+=smoothstep(.06,.32,obstruction)*(1.-smoothstep(rad,rad*2.6,obstruction));
        }
        gl_FragColor=vec4(color*(1.-.55*shade/12.),1.);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`
  });
  const scene=new THREE.Scene();scene.add(new THREE.Mesh(new THREE.PlaneGeometry(2,2),shader));
  const flat=new THREE.OrthographicCamera(-1,1,1,-1,0,1),size=new THREE.Vector2();
  function render(content,camera){
    renderer.getDrawingBufferSize(size);
    if(target.width!==size.x||target.height!==size.y)target.setSize(size.x,size.y);
    uniforms.texel.value.set(1/size.x,1/size.y);uniforms.viewRange.value=camera.far-camera.near;
    uniforms.scale.value=size.y*camera.zoom/(camera.top-camera.bottom);
    renderer.setRenderTarget(target);renderer.render(content,camera);
    renderer.setRenderTarget(null);renderer.render(scene,flat);
  }
  return render;
}

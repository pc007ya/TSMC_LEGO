// Each art stamp stores a lit surface and its depth in the common orthographic frame.
async function decodeStamp(url) {
  const image = new Image();
  image.src = url;
  await image.decode();
  const canvas = document.createElement('canvas');
  const w = canvas.width = image.width, h = canvas.height = image.height;
  const ctx = canvas.getContext('2d', {willReadFrequently:true});
  ctx.drawImage(image, 0, 0);
  const rgba = ctx.getImageData(0, 0, w, h).data;
  const samples = [];
  for (let i=0; i<w*h; i++) {
    if (!rgba[4*i+3]) continue;
    const edge = !((i%w)>0 && (i%w)<w-1 && i>=w && i<(h-1)*w &&
      rgba[4*(i-1)+3] && rgba[4*(i+1)+3] && rgba[4*(i-w)+3] && rgba[4*(i+w)+3]);
    samples.push(i%w, Math.floor(i/w), rgba[4*i]+256*rgba[4*i+1]-32768, rgba[4*i+2], edge?1:0);
  }
  return {w, h, samples:new Int32Array(samples)};
}

async function buildView(atlas, plan, colors) {
  const sprites=await Promise.all(atlas.sprites.map(decodeStamp));
  const depth = new Int32Array(atlas.width*atlas.height);
  const shade = new Uint8Array(depth.length);
  let index=0;
  function reset() {depth.fill(-2147483648); shade.fill(247); index=0}
  reset();
  function place(i, draw) {
    const [key,x,y,z] = atlas.placements[i], stamp=sprites[key];
    const p=stamp.samples;
    let center=null, nearest=Infinity;
    for (let j=0; j<p.length; j+=5) {
      const px=x+p[j], py=y+p[j+1], k=py*atlas.width+px, newDepth=z+p[j+2];
      if (newDepth<depth[k]-1) continue;
      depth[k]=newDepth;
      shade[k]=p[j+4]?177:Math.round(125+103*p[j+3]/255);
      if (!draw) continue;
      draw(px,py,p[j+3],p[j+4]);
      const distance=(p[j]-(stamp.w-1)/2)**2+(p[j+1]-(stamp.h-1)/2)**2;
      if (distance<nearest){nearest=distance;center=[px,py]}
    }
    return center || [x+stamp.w/2,y+stamp.h/2];
  }
  return function drawFigure(target,page) {
    if (index>page.start) reset();
    while(index<page.start) place(index++,null);
    const active=atlas.placements.slice(index,index+page.rows.length);
    let x0=Infinity,x1=-Infinity,y0=Infinity,y1=-Infinity;
    for(const [key,x,y] of active) {
      x0=Math.min(x0,x);y0=Math.min(y0,y);x1=Math.max(x1,x+sprites[key].w);y1=Math.max(y1,y+sprites[key].h);
    }
    const destW=720,destH=444,pad=(plan?5:6)*atlas.unit;
    const factor=Math.min(destW/(x1-x0+pad),destH/(y1-y0+pad),4.5);
    const w=Math.ceil(destW/factor),h=Math.ceil(destH/factor);
    const left=Math.floor((x0+x1-w)/2),top=Math.floor((y0+y1-h)/2);
    const local=document.createElement('canvas');local.width=w;local.height=h;
    const ctx=local.getContext('2d'),frame=ctx.createImageData(w,h),rgba=frame.data;
    for(let y=0;y<h;y++) for(let x=0;x<w;x++) {
      const ax=x+left,ay=y+top;
      const v=ax>=0&&ay>=0&&ax<atlas.width&&ay<atlas.height?shade[ay*atlas.width+ax]:247,k=(y*w+x)*4;
      const grid=plan&&v===247&&((ax+atlas.origin[0])%atlas.unit===0||(ay+atlas.origin[1])%atlas.unit===0);
      rgba[k]=grid?220:v;rgba[k+1]=grid?227:v;rgba[k+2]=grid?224:v;rgba[k+3]=255;
    }
    const centers=[];
    for(const row of page.rows) {
      const color=colors[row[1]],edge=plan?[37,74,74]:[169,78,34];
      const [mx,my]=place(index++,(px,py,brightness,border)=>{
        const k=((py-top)*w+px-left)*4;
        for(let c=0;c<3;c++) rgba[k+c]=border?edge[c]:Math.round(color[c]*brightness/255);
      });
      centers.push([row[0],(mx-left)*destW/w,(my-top)*destH/h]);
    }
    ctx.putImageData(frame,0,0);
    target.width=destW;target.height=destH;
    const out=target.getContext('2d');out.drawImage(local,0,0,destW,destH);
    if (!plan) return;
    const used=[];
    for(const [n,x,y] of centers) {
      const candidates=[[0,0],[0,-29],[0,29],[-29,0],[29,0],[-31,-24],[31,-24],[-31,24],[31,24],[0,-53],[0,53]];
      let best;
      for(const [dx,dy] of candidates){
        best=[Math.max(15,Math.min(destW-15,x+dx)),Math.max(15,Math.min(destH-15,y+dy))];
        if(used.every(([u,v])=>Math.hypot(best[0]-u,best[1]-v)>28))break;
      }
      const [bx,by]=best;used.push(best);
      out.strokeStyle='#254a4a';out.lineWidth=2;out.beginPath();out.moveTo(x,y);out.lineTo(bx,by);out.stroke();
      out.beginPath();out.arc(bx,by,13,0,2*Math.PI);out.fillStyle='#254a4a';out.fill();out.strokeStyle='white';out.stroke();
      out.font='bold 17px sans-serif';out.textAlign='center';out.textBaseline='middle';out.fillStyle='white';out.fillText(n,bx,by+1);
    }
  }
}

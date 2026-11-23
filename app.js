import { positionOf } from './placement.js';
const $=s=>document.querySelector(s), pad=n=>String(n).padStart(2,'0');
const icons={
  book:'<path d="M3 4.8c3-1 6.5-.7 9 1.4 2.4-2.1 6-2.4 9-1.4v14c-3-.8-6.6-.6-9 1.2-2.4-1.8-6-2-9-1.2zM12 6v14"/>',
  download:'<path d="M12 3v12m-5-5 5 5 5-5M4 16v4h16v-4"/>',
  expand:'<path d="M4 9V4h5m6 0h5v5m0 6v5h-5m-6 0H4v-5"/>',
  minus:'<path d="M5 12h14"/>',plus:'<path d="M5 12h14m-7-7v14"/>',
  rotate:'<path d="M20 11a8 8 0 1 0-2 7m2-14v7h-7"/>',
  homeview:'<path d="m4 8 8-4 8 4-8 4zM4 8v8l8 4 8-4V8m-8 4v8"/>',
  box:'<path d="m3 7 9-4 9 4-9 4zM3 7v10l9 4 9-4V7m-9 4v10M8 5l9 4"/>',
  bag:'<path d="M6.5 4h11l-.8 4 2.3 10a2 2 0 0 1-2 2.5H7a2 2 0 0 1-2-2.5L7.3 8zM7 8h10M9.5 13h5"/>',
  list:'<path d="M8 6h12M8 12h12M8 18h12M4 6h.1M4 12h.1M4 18h.1"/>',
  x:'<path d="m6 6 12 12M18 6 6 18"/>',check:'<path d="m4 12 5 5L20 6"/>',
  pin:'<circle cx="12" cy="12" r="6"/><path d="M12 2v4m0 12v4M2 12h4m12 0h4"/>',
  file:'<path d="M5 3h9l5 5v13H5zM14 3v6h5"/>'
};
const icon=n=>'<i data-icon="'+n+'"></i>';
function paintIcons(root=document){for(const el of root.querySelectorAll('i[data-icon]:empty'))el.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true">'+(icons[el.dataset.icon]||'')+'</svg>'}
const button=(action,label,name='',type='')=>'<button class="button '+type+'" data-action="'+action+'">'+(name?icon(name):'')+label+'</button>';
let models,catalog,tray,references,model,steps,all,bags,labels=[],focusedLabel=null,viewer=null,fallback=false,state,mode='overview',busy=false,epoch=0;
const seriesNames={collection:'晶圓建築',taichung:'台中規劃',collector:'6,000 件版'};
const seriesOf=m=>m.series||'collection';
const mem=new Map(),storeKey=id=>'fabform-build-v'+(model.revision||2)+'-'+id;
function readState(){
  let value=mem.get(model.id);
  try{value=JSON.parse(localStorage.getItem(storeKey(model.id)))||value}catch{}
  if(value&&typeof value==='object'){
    const {stage,step,piece}=value;
    if(['box','bag','build','done'].includes(stage)&&Number.isInteger(step)&&steps[step]&&Number.isInteger(piece)&&piece>=0&&piece<steps[step].pieces.length){
      if(stage==='bag'&&(steps[step].within!==0||piece!==0))return null;
      return {stage,step,piece,stickerReady:stage==='build'&&Boolean(steps[step].pieces[piece].decal)&&value.stickerReady===true};
    }
  }
  return null;
}
function save(){mem.set(model.id,{...state});try{localStorage.setItem(storeKey(model.id),JSON.stringify(state))}catch{}}
function choose(id,scroll=false){
  const next=models.find(m=>m.id===id)||models[0];
  epoch++;busy=false;model=next;
  steps=[];all=[];bags=model.bags.map((bag,idx)=>{
    const start=steps.length;let count=0;
    for(const [within,s] of bag.steps.entries()){steps.push({...s,bag:idx,within,start:all.length});all.push(...s.pieces);count+=s.pieces.length}
    return {...bag,start,count}
  });
  labels=all.filter(p=>p.decal);focusedLabel=null;
  state=readState();mode='overview';viewer?.setModel(model);
  const cover=new Image();cover.src='./assets/previews/'+model.id+'.webp';
  $('#set-count').textContent=models.length+' 款建築模型';
  $('#models').innerHTML=Object.entries(seriesNames).map(([id,name])=>{
    const members=models.filter(m=>seriesOf(m)===id);
    if(!members.length)return '';
    const tabs=members.map((m,i)=>'<button class="model-tab" data-model="'+m.id+'" aria-current="'+(m===model)+'"><span class="mono">'+pad(i+1)+'</span>'+(m.tabName||m.name)+'</button>').join('');
    return '<div class="series-row"><span class="series-name">'+name+'</span><div class="series-tabs" role="group" aria-label="'+name+'">'+tabs+'</div></div>';
  }).join('');
  const u=new URL(location.href);u.searchParams.set('set',model.id);if(scroll)u.searchParams.delete('view');history.replaceState(null,'',u);
  if(scroll)$('#models [aria-current=true]').scrollIntoView({block:'nearest',inline:'nearest',behavior:'smooth'});
  render()
}
function thumbnail(p){
  const i=tray.keys.indexOf(p.part+'-'+p.color);
  if(i<0)return '';
  const x=100*(i%tray.col)/(tray.col-1),y=100*Math.floor(i/tray.col)/(tray.row-1);
  return '<span aria-hidden="true" class="part-thumb" style="background-size:'+tray.col*100+'% '+tray.row*100+'%;background-position:'+x+'% '+y+'%"></span>';
}
function countParts(items){
  const lookup=new Map();
  for(const p of items){const key=p.part+'/'+p.color;const prev=lookup.get(key);if(prev)prev.count++;else lookup.set(key,{...p,count:1})}
  return [...lookup.values()]
}
const swatch=c=>'<b class="swatch" style="background:'+catalog.colors[c].hex+'"></b>';
const stats=()=>'<div class="stats">'+[[all.length,'本版積木'],[bags.length,'零件袋'],[steps.length,'步驟']].map(([n,s])=>'<div><strong>'+n+'</strong><small>'+s+'</small></div>').join('')+'</div>';
const code=()=>'<span class="model-code">'+model.code+'</span>';
function stickerNumber(p){return 'S'+pad(labels.indexOf(p)+1)}
const labelImage=p=>'<img class="label-art" src="./assets/decals/'+p.decal.art+'.svg" alt="">';
const faceNames={front:'前面',back:'背面',left:'左面',right:'右面'};
function labelInfo(p){
  const d=p.decal;
  return stickerNumber(p)+' · '+d.widthMM+' × '+d.heightMM+' mm · '+faceNames[d.face];
}
const backShow=()=>'<button class="text-button" data-action="overview">回到完成模型</button>';
function stagePiece(){return mode==='build'?steps[state.step].pieces[state.piece]:null}
function completedCount(){if(!state||state.stage==='box')return 0;if(state.stage==='done')return all.length;return steps[state.step].start+state.piece}
function viewButtons(){
  if(!model.views)return '';
  const choices=[{id:'all',name:'全景'},...model.views];
  return '<div class="structure-views" role="group" aria-label="建築視角">'+choices.map(v=>'<button data-view="'+v.id+'" aria-pressed="'+(v.id==='all')+'">'+v.name+'</button>').join('')+'</div>';
}
function inspectView(id){
  const view=model.views?.find(v=>v.id===id);
  if(!model.views||mode!=='overview')return;
  focusedLabel=null;
  if(viewer){if(view)viewer.inspect(view);else viewer.home()}
  else if(fallback){
    const img=$('#viewport .poster');
    if(img){img.src='./assets/previews/'+model.id+(view?'-'+view.id:'')+'.webp';img.alt=model.name+' '+(view?.name||'全景')}
  }
  document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===(view?.id||'all'))));
  const url=new URL(location.href);
  if(view)url.searchParams.set('view',view.id);else url.searchParams.delete('view');
  history.replaceState(null,'',url);
  const note=$('#view-note');if(note){note.hidden=!view;note.textContent=view?.note||''}
  $('#stage-caption').textContent=view?view.name:fallback?'完成模型預覽':'拖曳旋轉 · 滾動縮放';
}
function overview(){
  const ref=references[model.id];
  const sourceLabel=!ref.boxCode?ref.edition+' · 建築依據與取捨':'原盒 '+ref.boxPieces+' 件 · 對照商品三視圖';
  const alternate=model.standardId?models.find(m=>m.id===model.standardId):models.find(m=>m.standardId===model.id);
  const editionLink=alternate?'<a class="edition-link" href="?set='+alternate.id+'" data-edition="'+alternate.id+'">'+(model.standardId?'看原版 · '+alternate.bags.reduce((n,b)=>n+b.steps.reduce((k,s)=>k+s.pieces.length,0),0).toLocaleString('en-US')+' 件':'看 6,000 件高精度版')+'</a>':'';
  return code()+'<h2>'+model.name+'</h2>'+editionLink+'<p class="english" lang="en">'+model.en+'</p><p class="desc">'+model.description+'</p>'+viewButtons()+'<p id="view-note" class="view-note" hidden></p>'+stats()+'<button class="source-summary" data-action="references">'+sourceLabel+' ›</button>'+button('start',state?.stage==='done'?'重新組裝':state?'繼續組裝':'開始組裝','box','primary')+button('bom','查看零件表','list');
}
function sealedBox(){
  return '<button class="kitbox" data-action="openbox" aria-label="打開模型盒"><img src="./assets/previews/'+model.id+'.webp" alt=""><span class="box-top">FABFORM</span><span class="box-label"><strong>'+model.name+'</strong><em>'+model.code+'</em></span></button>'
}
function bagObject(idx){
  const bag=bags[idx],picks=countParts(bag.steps.flatMap(s=>s.pieces)).slice(0,6);
  const packet='<button class="pack" data-action="openbag" aria-label="拆開第 '+(idx+1)+' 袋"><em>FABFORM / '+model.code+'</em><strong>'+pad(idx+1)+'</strong><div class="mini-bricks">'+picks.map(thumbnail).join('')+'</div><span>'+bag.count+' 件 · '+bag.steps.length+' 步</span></button>';
  const other=bags.map((b,i)=>i===idx?'':'<button class="stored-bag '+(i<idx?'used':'')+'" data-bag="'+i+'" aria-label="檢視第 '+(i+1)+' 袋"><span>'+pad(i+1)+'</span>'+icon(i<idx?'check':'bag')+'</button>').join('');
  return '<div class="carton"><div class="carton-wall"></div>'+packet+'<div class="carton-right"><button class="booklet" data-action="manual"><span>'+icon('book')+' FABFORM</span><img src="./assets/previews/'+model.id+'.webp" alt=""><strong>組裝手冊</strong></button><div class="stored-bags'+(bags.length>6?' packed':'')+'">'+other+'</div></div></div>'
}
function guide(){
  const step=steps[state.step],idx=step.bag,bag=bags[idx];
  if(mode==='box')return code()+'<h2>打開模型盒</h2><p class="english">'+model.name+'</p><p class="desc">盒內有一本組裝手冊和 '+bags.length+' 袋編號零件。點盒面打開包裝，從第 01 袋開始。</p>'+stats()+button('openbox','打開盒蓋','box','primary')+backShow();
  if(mode==='bag')return code()+'<h2>第 '+pad(idx+1)+' 袋</h2><p class="english">'+bag.name+'</p><p class="desc">取出本袋的 '+bag.count+' 件積木，依 '+bag.steps.length+' 個步驟組合。點零件袋拆封，就能看見第一個安裝位置。</p>'+button('openbag','拆開第 '+pad(idx+1)+' 袋','bag','primary')+button('bagparts','核對本袋零件','list')+backShow();
  if(mode==='done')return code()+'<h2>組裝完成</h2><p class="english">'+model.name+' / '+all.length+' 件已就位</p><p class="desc">拖曳模型查看完成後的每一面，或打開手冊重看任何步驟。</p>'+stats()+button('overview','欣賞完成模型','check','primary')+button('manual','開啟組裝手冊','book');
  const p=stagePiece(),part=catalog.parts[p.part],color=catalog.colors[p.color];
  const instruction=p.decal?'<div class="apply-label">'+labelImage(p)+'<span><strong>'+labelInfo(p)+'</strong><br>'+p.decal.label+' · '+(state.stickerReady?'已貼妥':'先將貼紙貼在這件積木上')+'</span></div>':'';
  const local=p.pivotAt?p.pivotAt.label+'定位圖':p.pivoted?'斜廊組件定位圖':'底座';
  const placeText=p.decal&&!state.stickerReady?'貼上 '+stickerNumber(p)+' 貼紙':'裝上這一件';
  const progress=(completedCount()/all.length*100).toFixed(1);
  return '<div class="build-panel"><span class="model-code">'+model.code+' ／ 第 '+pad(idx+1)+' 袋</span><div class="progress-track" aria-label="完成 '+progress+'%"><b style="width:'+progress+'%"></b></div><span class="status-slug">步驟 '+(state.step+1)+' / '+steps.length+'</span><h2>'+step.name+'</h2><p class="hint">'+step.hint+'</p><ul class="step-list">'+countParts(step.pieces).map(p=>'<li title="'+catalog.colors[p.color].name+' '+catalog.parts[p.part].name+'">'+thumbnail(p)+p.part+' ×'+p.count+'</li>').join('')+'</ul><strong>'+swatch(p.color)+color.name+' '+part.name+'</strong><p class="coords">本步第 '+(state.piece+1)+' / '+step.pieces.length+' 件 · 料號 '+p.part+'<br>'+local+'由左第 '+(p.x+1)+' 格、'+(p.z<0?'第一排後方 '+(-p.z)+' 格':'由後第 '+(p.z+1)+' 格')+'，底高 '+p.y+' 層薄板。'+(part.directions?part.directions[p.r]+'。':part.w!==part.d?(p.r%2?'長邊前後向。':'長邊左右向。'):'')+'</p>'+instruction+'<div class="action-pair">'+(fallback?'':button('locate','定位','pin','minor'))+button('place',placeText,'plus','primary')+'</div><div class="action-pair step-actions">'+button('undo','上一步')+button('step','完成本步')+'</div>'+backShow()+'</div>';
}
function flatView(items,next){
  const host=$('#viewport');host.replaceChildren();
  if(!next){const img=new Image();img.className='poster';img.src='./assets/previews/'+model.id+'.webp';img.alt=model.name;host.append(img)}
  else{
    const canvas=document.createElement('canvas');canvas.width=800;canvas.height=510;host.append(canvas);
    const back=model.rearOverhang?.rows||0,depth=model.depth+back;
    const ctx=canvas.getContext('2d'),s=Math.min(680/model.width,405/depth),ox=(800-s*model.width)/2,oz=(510-s*depth)/2+back*s;
    ctx.fillStyle='#dce9e5';ctx.fillRect(0,0,800,510);
    for(const [i,p] of [...items,next].entries()){
      const part=catalog.parts[p.part],w=(p.r%2?part.d:part.w)*s,d=(p.r%2?part.w:part.d)*s;
      ctx.fillStyle=i===items.length?'#ebac60':catalog.colors[p.color].hex;
      ctx.strokeStyle=i===items.length?'#b24520':'#75857b';ctx.lineWidth=i===items.length?3:1;
      const loc=positionOf(model,part,p);
      ctx.save();ctx.translate(ox+(loc.x+model.width/2)*s,oz+(loc.z+model.depth/2)*s);
      ctx.rotate(loc.angle);ctx.fillRect(-w/2,-d/2,w,d);ctx.strokeRect(-w/2,-d/2,w,d);ctx.restore();
    }
  }
}
function scene(){
  if(!model)return;
  const items=(mode==='overview'||mode==='done'||mode==='box')?all:all.slice(0,completedCount());
  if(viewer)viewer.show(items,stagePiece(),mode==='build'&&state.stickerReady);else if(fallback)flatView(items,stagePiece());
}
function render(){
  if(mode!=='overview'&&mode!=='done')focusedLabel=null;
  $('#stage-stickers').hidden=!labels.length||!['overview','done'].includes(mode);
  $('#stage-stickers').textContent='貼紙特寫 · '+labels.length;
  $('#detail').innerHTML=mode==='overview'?overview():guide();
  const layer=$('#object-layer'),packaging=mode==='box'||mode==='bag';
  layer.hidden=!packaging;layer.classList.remove('unbox');
  layer.innerHTML=mode==='box'?sealedBox():mode==='bag'?bagObject(steps[state.step].bag):'';
  $('.camera-controls').hidden=packaging||fallback;
  $('#mode-label').textContent=({overview:fallback?'模型預覽':'3D 模型',box:'盒裝模型',bag:'零件袋',build:fallback?'俯視定位圖':'組裝視圖',done:'完成模型'})[mode];
  $('#stage-caption').textContent=packaging?'點擊包裝拆封':mode==='build'?'橘色框為本件位置':fallback?'完成模型預覽':'拖曳旋轉 · 滾動縮放';
  $('#bag-summary').textContent=bags.length+' 袋 ／ '+all.length+' 件';
  $('#bag-list').innerHTML=bags.map((b,i)=>'<button class="bag-card" data-bag="'+i+'"><span class="bag-glyph">'+icon('bag')+'</span><span><strong>'+b.name+'</strong><small>BAG '+pad(i+1)+' · '+b.count+' 件</small></span></button>').join('');
  if(mode==='build'&&state.step===0&&state.piece===0) $('[data-action="undo"]').disabled=true;
  if(focusedLabel)$('#stage-caption').textContent=stickerNumber(focusedLabel)+' · '+focusedLabel.decal.label;
  paintIcons();scene()
}
function start(){viewer?.home();if(!state||state.stage==='done')state={stage:'box',step:0,piece:0};mode=state.stage;save();render()}
function openPackage(next){
  if(busy)return;busy=true;const currentEpoch=epoch;
  $('#object-layer').classList.add('unbox');
  setTimeout(()=>{if(epoch!==currentEpoch)return;busy=false;state.stage=next;mode=next;save();render()},matchMedia('(prefers-reduced-motion: reduce)').matches?0:360)
}
function advance(whole){
  if(mode!=='build'||busy)return;
  const step=steps[state.step],p=step.pieces[state.piece],currentEpoch=epoch;
  if(!whole&&p.decal&&!state.stickerReady){state.stickerReady=true;save();render();return}
  busy=true;
  function finish(){
    if(currentEpoch!==epoch)return;
    busy=false;
    state.stickerReady=false;
    if(!whole&&state.piece+1<step.pieces.length)state.piece++;
    else if(state.step===steps.length-1){state={stage:'done',step:state.step,piece:0};mode='done';viewer?.home()}
    else{
      state.step++;state.piece=0;
      if(steps[state.step].bag!==step.bag){state.stage='bag';mode='bag';viewer?.home()}
    }
    save();render()
  }
  if(viewer&&!whole)viewer.animatePlace(p,finish);else finish()
}
function undo(){
  if(mode!=='build'||busy)return;
  state.stickerReady=false;
  if(state.piece>0)state.piece--;
  else if(state.step>0){state.step--;state.piece=0}
  save();render()
}
function dialog(title,body){
  $('#dialog-code').textContent=model.code+' ／ '+model.name;
  $('#dialog-title').textContent=title;$('#dialog-body').innerHTML=body;paintIcons($('#dialog'));if(!$('#dialog').open)$('#dialog').showModal()
}
function fileLink(file,title,kind,open=false){
  return '<a class="file-link" href="./downloads/'+model.id+'/'+file+'" '+(open?'target="_blank" rel="noopener"':'download')+'><span>'+title+'</span><small>'+kind+'</small></a>'
}
function referenceDialog(){
  const ref=references[model.id];
  const original=Boolean(ref.boxCode);
  const prefix=seriesOf(model);
  const setName=prefix==='collector'?'6,000 件版':'台中系列';
  const sources=original?[[ref.photo,'商品正面、側面、俯視與盒面'],[ref.product,'TShop 商品規格'],[ref.buildingSource,ref.buildingCredit]]:ref.sources.map(s=>[s.url,s.label]);
  const links=sources.map(([href,title])=>'<a class="file-link" href="'+href+'" target="_blank" rel="noopener"><span>'+title+'</span><small>開啟 ↗</small></a>').join('');
  if(!original){
    dialog('建築依據與設計取捨','<h3>'+ref.edition+'</h3><p>'+ref.observation+'</p><h3>積木如何取捨</h3><p>'+ref.interpretation+'</p><dl class="reference-spec"><div><dt>模型底座</dt><dd>'+model.width+' × '+model.depth+' 凸點</dd></div><div><dt>設計用量</dt><dd>'+all.length+' 件積木＋'+labels.length+' 枚貼紙</dd></div></dl><div class="file-links">'+links+'<a class="file-link" href="./downloads/'+prefix+'-plan.pdf" target="_blank" rel="noopener"><span>閱讀'+setName+'圖文設計提案</span><small>PDF</small></a><a class="file-link" href="./downloads/'+prefix+'-plan.md" download><span>'+setName+'規劃與分袋用量</span><small>MD</small></a></div>');
    return;
  }
  dialog('原盒與重建對照','<p>'+ref.observation+'</p><dl class="reference-spec"><div><dt>TShop 原盒 '+ref.boxCode+'</dt><dd>'+ref.boxPieces+' 件</dd></div><div><dt>商品標示尺寸</dt><dd>'+ref.dimensionsCm+' 公分</dd></div><div><dt>本版分袋 BOM</dt><dd>'+all.length+' 件積木＋'+labels.length+' 枚貼紙</dd></div><div><dt>本版底座</dt><dd>'+model.width+' × '+model.depth+' 凸點</dd></div></dl><p class="hint">本版依照片重建，使用標準 8 mm 凸點間距。實體備料請按本版 BOM 計算。</p><div class="file-links">'+links+'<a class="file-link" href="./downloads/reference-guide.md" download><span>五款來源與件數對照</span><small>MD</small></a></div>');
}
function files(){
  const prefix=seriesOf(model),plan=prefix!=='collection';
  dialog('設計檔案','<p class="hint">本款模型的零件、定位及步驟皆可下載。</p><div class="file-links">'+fileLink('model.ldr','三維模型與組裝順序','LDraw')+fileLink('manual.pdf','列印版組裝說明書','PDF')+fileLink('manual.html','圖解說明書（離線列印版）','HTML')+fileLink('manual.md','逐件座標與手冊備份','MD')+fileLink('stickers.pdf','原尺寸貼紙與定位清單','PDF')+fileLink('bom.csv','分袋零件採購表','CSV')+'<a class="file-link" href="./downloads/'+prefix+'-bom.csv" download><span>本系列合計採購表</span><small>CSV</small></a><a class="file-link" href="./downloads/'+prefix+'-decals.csv" download><span>本系列貼紙清單</span><small>CSV</small></a><a class="file-link" href="./downloads/'+(plan?prefix+'-plan.md':'reference-guide.md')+'" download><span>'+(plan?'系列建築規劃與用量':'五款照片來源與件數對照')+'</span><small>MD</small></a></div>')
}
function stickerGuide(){
  const entries=labels.map((p,i)=>{
    const d=p.decal,st=steps.find(s=>s.pieces.includes(p)),stepNo=steps.indexOf(st)+1;
    return '<div class="decal-entry">'+labelImage(p)+'<div><strong>'+d.label+'</strong><small>'+labelInfo(p)+'<br>第 '+pad(st.bag+1)+' 袋 · 步驟 '+stepNo+' · 料號 '+p.part+'</small></div>'+(viewer?'<button class="quiet" data-label-focus="'+i+'">看位置</button>':'')+'</div>'
  }).join('');
  dialog('貼紙與位置',entries+'<div class="file-links">'+fileLink('stickers.pdf','下載本款原尺寸貼紙 · A4 以 100% 列印','PDF')+'<a class="file-link" href="./downloads/'+seriesOf(model)+'-stickers.pdf" download><span>下載本系列原尺寸貼紙</span><small>PDF</small></a></div>');
}
function manual(){
  dialog('組裝手冊','<p class="hint">圖解手冊逐步標出新增零件與落點，可離線閱讀，亦可用瀏覽器列印成 A4。</p><div class="file-links">'+fileLink('manual.html','閱讀圖解說明書','開啟',true)+fileLink('manual.pdf','下載列印版手冊','PDF')+fileLink('manual.md','下載完整逐件說明','MD')+fileLink('stickers.pdf','下載原尺寸貼紙','PDF')+'</div><h3>分袋目錄</h3>'+bags.map((b,i)=>'<p class="coords">第 '+pad(i+1)+' 袋　'+b.name+' · 步驟 '+(b.start+1)+'–'+(b.start+b.steps.length)+'</p>').join(''))
}
function bom(bag=-1){
  const items=bag<0?all:bags[bag].steps.flatMap(s=>s.pieces);
  const rows=countParts(items).sort((a,b)=>a.part.localeCompare(b.part,undefined,{numeric:true})||a.color.localeCompare(b.color));
  dialog('零件表','<label class="bom-filter">範圍 <select id="bom-select"><option value="-1">整盒</option>'+bags.map((b,i)=>'<option value="'+i+'" '+(i===bag?'selected':'')+'>第 '+pad(i+1)+' 袋 · '+b.name+'</option>').join('')+'</select></label><p class="subtle">'+rows.length+' 種零件與顏色組合，共 '+items.length+' 件。另附 '+items.filter(p=>p.decal).length+' 枚貼紙。</p><div class="file-links">'+fileLink('bom.csv','下載整盒與各袋用量','CSV')+'</div><table class="bom-table"><thead><tr><th>料號</th><th>零件</th><th>顏色</th><th>件數</th></tr></thead><tbody>'+rows.map(p=>'<tr><td><span class="table-part">'+thumbnail(p)+p.part+'</span></td><td>'+catalog.parts[p.part].name+'</td><td>'+swatch(p.color)+catalog.colors[p.color].name+'</td><td>'+p.count+'</td></tr>').join('')+'</tbody></table>');
  $('#bom-select').onchange=e=>bom(Number(e.target.value))
}
function bagInfo(idx){
  const b=bags[idx];
  dialog('第 '+pad(idx+1)+' 袋 · '+b.name,'<p class="hint">'+b.count+' 件 ／ '+b.steps.length+' 步。從「'+b.steps[0].name+'」開始，到「'+b.steps.at(-1).name+'」完成本袋。</p>'+button('inspectbag','檢視本袋零件','list')+'<div class="file-links">'+fileLink('manual.html','閱讀整本圖解手冊','HTML',true)+'</div>');
  $('#dialog [data-action="inspectbag"]').onclick=()=>bom(idx)
}
function expand(){
  const stage=$('#stage'),open=stage.classList.toggle('expanded');
  $('[data-action="expand"]').setAttribute('aria-label',open?'還原模型大小':'放大模型');
}
document.addEventListener('click',e=>{
  const tab=e.target.closest('[data-model],[data-edition]');if(tab){if(tab.matches('a')&&(e.ctrlKey||e.metaKey||e.shiftKey||e.altKey))return;e.preventDefault();choose(tab.dataset.model||tab.dataset.edition,true);return}
  const b=e.target.closest('[data-bag]');if(b){bagInfo(Number(b.dataset.bag));return}
  const view=e.target.closest('[data-view]');if(view){inspectView(view.dataset.view);return}
  const pick=e.target.closest('[data-label-focus]');
  if(pick){const p=labels[Number(pick.dataset.labelFocus)];if(p&&viewer){$('#dialog').close();focusedLabel=p;document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed','false'));viewer.focusDecal(p);$('#stage-caption').textContent=stickerNumber(p)+' · '+p.decal.label;$('#stage').scrollIntoView({block:'nearest'})}return}
  const action=e.target.closest('[data-action]')?.dataset.action;
  if(!model||!action)return;
  const handlers={
    start,openbox:()=>mode==='box'&&openPackage('bag'),openbag:()=>mode==='bag'&&openPackage('build'),
    overview:()=>{epoch++;busy=false;mode='overview';viewer?.home();render()},
    undo,place:()=>advance(false),step:()=>advance(true),zoomout:()=>viewer?.zoom(.82),zoomin:()=>viewer?.zoom(1.22),
    locate:()=>viewer?.focusPiece(),resetview:()=>{if(model.views&&mode==='overview'){inspectView('all');return}focusedLabel=null;viewer?.home();$('#stage-caption').textContent=mode==='build'?'橘色框為本件位置':'拖曳旋轉 · 滾動縮放'},rotate:()=>viewer?.rotate(),expand,
    manual,files,references:referenceDialog,stickers:stickerGuide,bom:()=>bom(),bagparts:()=>bom(steps[state.step].bag),close:()=>$('#dialog').close()
  };
  handlers[action]?.();
});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!$('#dialog').open&&$('#stage').classList.contains('expanded'))expand()});
$('#dialog').addEventListener('click',e=>{if(e.target===$('#dialog')){const r=e.target.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)e.target.close()}});
async function main(){
  const get=async f=>{const r=await fetch('./data/'+f+'.json');if(!r.ok)throw Error(f);return r.json()};
  [catalog,models,tray,references]=await Promise.all([get('catalog'),get('models'),get('tray'),get('references')]);
  choose(new URL(location.href).searchParams.get('set'));paintIcons();
  try{
    const {createViewer}=await import('./viewer.js');
    viewer=await createViewer($('#viewport'),catalog,()=>advance(false));viewer.setModel(model);scene();
    document.documentElement.dataset.renderer='three';
  }catch(error){
    console.warn('3D 預覽載入失敗',error);fallback=true;render();
    document.documentElement.dataset.renderer='plan';
    const notice=document.createElement('span');notice.className='fallback-note';notice.textContent='此裝置使用模型預覽與俯視組裝圖。';$('#stage').append(notice)
  }
  const selectedView=new URL(location.href).searchParams.get('view');
  if(selectedView&&model.views?.some(v=>v.id===selectedView))inspectView(selectedView);
}
main().catch(()=>{$('#detail').innerHTML='<p>模型資料載入失敗。請重新整理頁面。</p>'});

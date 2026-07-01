import json
import os
HERE=os.path.dirname(os.path.abspath(__file__)); PKG=os.path.dirname(HERE)
hk5m=json.load(open(os.path.join(PKG,"data","lantau-hk5m.json")))
srtm=json.load(open(os.path.join(PKG,"data","lantau-srtm30.json")))
DATASETS={
 "hk5m":{"label":"HK 5 m LiDAR — Lands Dept","note":"5 m grid · ±5 m · 2020 LiDAR survey (EPSG:2326)","data":hk5m},
 "srtm30":{"label":"SRTM ~30 m — AWS Terrarium","note":"~30 m global composite · Mapzen/Tilezen tiles","data":srtm},
}
TPL=r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Lantau Island — 3D terrain</title>
<style>
  html,body{margin:0;height:100%;background:#0e1116;color:#e8e6df;font-family:-apple-system,Segoe UI,Roboto,'Noto Serif CJK TC',serif;overflow:hidden}
  #app{position:fixed;inset:0}
  #panel{position:fixed;top:14px;left:14px;background:rgba(18,22,28,.80);backdrop-filter:blur(6px);
         border:1px solid #2a3340;border-radius:10px;padding:12px 14px;font-size:13px;line-height:1.5;max-width:260px}
  #panel h1{font-size:14px;margin:0 0 6px;letter-spacing:.04em;font-weight:600}
  #panel .sub{color:#9aa6b3;font-size:11px;margin-bottom:10px;min-height:28px}
  .row{display:flex;align-items:center;gap:8px;margin:7px 0}
  .row label{flex:0 0 74px;color:#aeb8c4}
  input[type=range]{flex:1}
  select{flex:1;background:#26303d;color:#e8e6df;border:1px solid #3a4654;border-radius:6px;padding:4px 6px;font-size:12px}
  button{background:#26303d;color:#e8e6df;border:1px solid #3a4654;border-radius:6px;padding:5px 9px;cursor:pointer;font-size:12px}
  button:hover{background:#33414f}
  .hint{position:fixed;bottom:12px;left:50%;transform:translateX(-50%);color:#8893a0;font-size:11px;
        background:rgba(18,22,28,.7);padding:5px 12px;border-radius:20px;border:1px solid #2a3340}
  .lbl{position:fixed;transform:translate(-50%,-100%);pointer-events:none;font-size:12px;white-space:nowrap;
       color:#fff;text-shadow:0 1px 3px #000,0 0 2px #000;font-weight:600}
  .lbl small{display:block;font-weight:400;color:#cfd6de;font-size:10px;text-align:center}
  .lbl:before{content:'';position:absolute;left:50%;top:100%;width:1px;height:9px;background:#fff;opacity:.6;transform:translateX(-50%)}
</style>
</head>
<body>
<div id="app"></div>
<div id="panel">
  <h1>大嶼山 · Lantau Island</h1>
  <div class="sub" id="note"></div>
  <div class="row"><label>Data source</label><select id="src"></select></div>
  <div class="row"><label>Vertical ×</label><input id="ve" type="range" min="1" max="6" step="0.1" value="2.6"><span id="vev">2.6</span></div>
  <div class="row"><label>Spin</label><input id="spin" type="checkbox" checked></div>
  <div class="row"><label>Labels</label><input id="lab" type="checkbox" checked></div>
  <div class="row"><label>Water</label><input id="water" type="checkbox" checked></div>
  <div class="row"><button id="south">South view</button><button id="top">Top‑down</button></div>
</div>
<div class="hint">drag · scroll · right‑drag to pan</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const DATASETS = __DATASETS__;
let VE=2.6, spin=true, showLabels=true, curKey=Object.keys(DATASETS)[0];

const app=document.getElementById('app');
const scene=new THREE.Scene();
scene.background=new THREE.Color(0x0e1116);
const camera=new THREE.PerspectiveCamera(45, innerWidth/innerHeight, 10, 1e6);
const renderer=new THREE.WebGLRenderer({antialias:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight);
app.appendChild(renderer.domElement);
scene.add(new THREE.AmbientLight(0xffffff,0.55));
const sun=new THREE.DirectionalLight(0xfff4e2,1.05); sun.position.set(-1,1.4,-0.6); scene.add(sun);
const fill=new THREE.DirectionalLight(0x88aaff,0.25); fill.position.set(1,0.6,1); scene.add(fill);

function hyps(e,zmax){
  const t=Math.max(0,Math.min(1,e/zmax));
  const s=[[0,[46,92,58]],[0.18,[78,110,60]],[0.42,[150,140,96]],[0.68,[140,110,80]],[0.86,[170,150,128]],[1,[235,232,224]]];
  for(let i=0;i<s.length-1;i++){const a=s[i],b=s[i+1];
    if(t>=a[0]&&t<=b[0]){const u=(t-a[0])/(b[0]-a[0]);
      return [a[1][0]+(b[1][0]-a[1][0])*u,a[1][1]+(b[1][1]-a[1][1])*u,a[1][2]+(b[1][2]-a[1][2])*u];}}
  return s[s.length-1][1];
}

let terrain=null, sea=null, base=null, W,H,cell,elev,zmax;
let labels=[];
const target=new THREE.Vector3(0,60,0);
let theta=Math.PI, phi=1.12, radius=1000;

function clearLabels(){ labels.forEach(l=>l.div.remove()); labels=[]; }

function build(key){
  curKey=key;
  const d=DATASETS[key].data;
  W=d.w; H=d.h; cell=d.cell; elev=d.elev; zmax=d.zmax;
  if(terrain){ scene.remove(terrain); terrain.geometry.dispose(); terrain.material.dispose(); }
  if(sea){ scene.remove(sea); sea.geometry.dispose(); sea.material.dispose(); }
  const geo=new THREE.BufferGeometry();
  const pos=new Float32Array(W*H*3), col=new Float32Array(W*H*3);
  for(let r=0;r<H;r++)for(let c=0;c<W;c++){const i=r*W+c,e=elev[i];
    pos[i*3]=(c-W/2)*cell; pos[i*3+1]=e; pos[i*3+2]=(r-H/2)*cell;
    const cc=hyps(e,zmax); col[i*3]=cc[0]/255; col[i*3+1]=cc[1]/255; col[i*3+2]=cc[2]/255;}
  const idx=[];
  for(let r=0;r<H-1;r++)for(let c=0;c<W-1;c++){const a=r*W+c,b=a+1,dd=a+W,e=dd+1; idx.push(a,dd,b,b,dd,e);}
  geo.setAttribute('position',new THREE.BufferAttribute(pos,3));
  geo.setAttribute('color',new THREE.BufferAttribute(col,3));
  geo.setIndex(idx);
  base=pos.slice();
  applyVE(geo);
  terrain=new THREE.Mesh(geo,new THREE.MeshStandardMaterial({vertexColors:true,roughness:0.95,metalness:0,flatShading:false}));
  scene.add(terrain);
  const seaGeo=new THREE.PlaneGeometry(cell*W*1.8, cell*H*1.8);
  sea=new THREE.Mesh(seaGeo,new THREE.MeshStandardMaterial({color:0x2b5d78,transparent:true,opacity:0.62,roughness:0.4}));
  sea.rotation.x=-Math.PI/2; sea.position.y=0.5; sea.visible=document.getElementById('water').checked; scene.add(sea);
  // labels
  clearLabels();
  d.peaks.forEach(p=>{
    const x=(p.col-W/2)*cell, z=(p.row-H/2)*cell, y=elev[p.row*W+p.col];
    const div=document.createElement('div'); div.className='lbl';
    div.innerHTML=p.name+'<small>'+p.elev+' m</small>';
    document.body.appendChild(div); labels.push({div,x,y,z});
  });
  scene.fog=new THREE.Fog(0x0e1116, cell*W*0.9, cell*W*2.4);
  camera.far=cell*W*5; camera.updateProjectionMatrix();
  target.set(0, zmax*VE*0.18, 0);
  radius=cell*W*1.05;
  document.getElementById('note').textContent=DATASETS[key].label+" — "+DATASETS[key].note;
}
function applyVE(geo){ geo=geo||terrain.geometry; const p=geo.attributes.position.array;
  for(let i=0;i<W*H;i++)p[i*3+1]=base[i*3+1]*VE; geo.attributes.position.needsUpdate=true; geo.computeVertexNormals(); }

function update(){
  camera.position.set(target.x+radius*Math.sin(phi)*Math.sin(theta),
                      target.y+radius*Math.cos(phi),
                      target.z+radius*Math.sin(phi)*Math.cos(theta));
  camera.lookAt(target);
}
// controls
let dragging=false,panning=false,px=0,py=0,lt=null;
renderer.domElement.addEventListener('mousedown',e=>{dragging=e.button===0;panning=e.button===2;px=e.clientX;py=e.clientY;});
addEventListener('mouseup',()=>{dragging=panning=false;});
addEventListener('mousemove',e=>{const dx=e.clientX-px,dy=e.clientY-py;px=e.clientX;py=e.clientY;
  if(dragging){theta-=dx*0.005;phi=Math.max(0.12,Math.min(1.54,phi-dy*0.005));}
  else if(panning){const s=radius*0.0013;const right=new THREE.Vector3(Math.cos(theta),0,-Math.sin(theta));
    target.addScaledVector(right,-dx*s);target.y+=dy*s;}});
renderer.domElement.addEventListener('wheel',e=>{e.preventDefault();radius*=(1+Math.sign(e.deltaY)*0.08);
  radius=Math.max(cell*W*0.25,Math.min(cell*W*2.6,radius));},{passive:false});
renderer.domElement.addEventListener('contextmenu',e=>e.preventDefault());
renderer.domElement.addEventListener('touchstart',e=>{if(e.touches.length){px=e.touches[0].clientX;py=e.touches[0].clientY;}
  lt=e.touches.length===2?Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY):null;},{passive:true});
renderer.domElement.addEventListener('touchmove',e=>{
  if(e.touches.length===1){const dx=e.touches[0].clientX-px,dy=e.touches[0].clientY-py;px=e.touches[0].clientX;py=e.touches[0].clientY;
    theta-=dx*0.005;phi=Math.max(0.12,Math.min(1.54,phi-dy*0.005));}
  else if(e.touches.length===2){const dd=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);
    if(lt)radius*=lt/dd; lt=dd; radius=Math.max(cell*W*0.25,Math.min(cell*W*2.6,radius));}},{passive:true});

// UI
const sel=document.getElementById('src');
Object.keys(DATASETS).forEach(k=>{const o=document.createElement('option');o.value=k;o.textContent=DATASETS[k].label;sel.appendChild(o);});
sel.value=curKey;
sel.onchange=()=>build(sel.value);
const veEl=document.getElementById('ve'),vev=document.getElementById('vev');
veEl.oninput=()=>{VE=parseFloat(veEl.value);vev.textContent=VE.toFixed(1);applyVE();target.y=zmax*VE*0.18;};
document.getElementById('spin').onchange=e=>spin=e.target.checked;
document.getElementById('lab').onchange=e=>{showLabels=e.target.checked;};
document.getElementById('water').onchange=e=>{if(sea)sea.visible=e.target.checked;};
document.getElementById('south').onclick=()=>{theta=Math.PI;phi=1.12;radius=cell*W*1.05;};
document.getElementById('top').onclick=()=>{theta=Math.PI;phi=0.18;radius=cell*W*1.15;};
addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);});

build(curKey);
const v=new THREE.Vector3();
function tick(){
  if(spin&&!dragging&&!panning)theta+=0.0016;
  update();
  labels.forEach(l=>{v.set(l.x,l.y*VE,l.z).project(camera);
    const ok=v.z<1&&showLabels; l.div.style.display=ok?'':'none';
    if(ok){l.div.style.left=(v.x*0.5+0.5)*innerWidth+'px';l.div.style.top=(-v.y*0.5+0.5)*innerHeight+'px';}});
  renderer.render(scene,camera);
  requestAnimationFrame(tick);
}
tick();
</script>
</body>
</html>"""
html=TPL.replace("__DATASETS__", json.dumps(DATASETS))
open(os.path.join(PKG,"index.html"),"w").write(html)
print("dual-source viewer bytes:", len(html))

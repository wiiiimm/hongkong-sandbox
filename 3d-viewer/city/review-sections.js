import * as THREE from '../vendor/three.module.js';
import {prepareReviewSections,reviewCounts,REVIEW_GATES,REVIEW_LABELS,REVIEW_STATES,sectionAt} from './review-sections-data.js';
const $=id=>document.getElementById(id);
export class ReviewSections {
 constructor({scene,sampler,onVisit,onSelect=()=>{}}){
  Object.assign(this,{sampler,onVisit,onSelect});this.group=new THREE.Group();this.group.name='Project review section borders';this.group.visible=false;scene.add(this.group);
  this.sections=[];this.enabled=false;this.pending=false;this.error=null;this.selected=null;this.labelEntries=[];this.segments=new Map();this.lastLabels=0;this.focusPoint=new THREE.Vector3();this.point=new THREE.Vector3();
  this.labels=$('section-labels');this.panel=$('section-review');this.select=$('section-select');
  $('section-grid-toggle').addEventListener('click',()=>this.setEnabled(!this.enabled));$('layer-sections').addEventListener('change',e=>this.setEnabled(e.target.checked));
  $('section-retry').addEventListener('click',()=>this.load());this.select.addEventListener('change',()=>this.selectSection(this.select.value));
  $('section-visit').addEventListener('click',()=>{const s=this.sections.find(s=>s.id===this.selected);if(s)this.onVisit(s);});
  $('section-overview').addEventListener('click',()=>{if(this.sections.length)this.onVisit({overview:true,bounds:this.sections.reduce((b,s)=>[Math.min(b[0],s.bounds[0]),Math.min(b[1],s.bounds[1]),Math.max(b[2],s.bounds[2]),Math.max(b[3],s.bounds[3])],[Infinity,Infinity,-Infinity,-Infinity])});});
 }
 async setEnabled(value){
  this.enabled=value;this.group.visible=value&&this.sections.length>0;this.labels.hidden=!value;this.panel.hidden=!value;document.body.classList.toggle('review-grid-on',value);
  $('layer-sections').checked=value;$('section-grid-toggle').setAttribute('aria-pressed',String(value));$('layer-count').textContent=`${document.querySelectorAll('.layers input:checked').length} LAYERS`;
  if(value){this.onSelect();if(!this.sections.length)await this.load();}
 }
 async load(){
  if(this.pending)return;this.pending=true;this.error=null;$('section-loading').textContent='Loading 132 review sections…';$('section-retry').hidden=true;
  try{
   const read=async url=>{const r=await fetch(url);if(!r.ok)throw Error('Section data HTTP '+r.status);return r.json();};
   const [geometry,readiness]=await Promise.all([read('city/data/review-sections.json'),read('city/data/section-readiness.json')]);
   this.sections=prepareReviewSections(geometry,readiness);this.build();this.counts=reviewCounts(this.sections);this.updatedAt=readiness.updatedAt;this.boundaryVersion=geometry.boundaryVersion;
   const c=this.counts;$('section-summary').textContent=`${c.ready} ready · ${c.close} close to ready · ${c.reviewing} under review · ${c.base} base mapped`;
   $('section-version').textContent=`Approximate project boundaries · ${geometry.boundaryVersion} · review ${readiness.updatedAt.slice(0,10)}`;$('section-loading').textContent='Choose a number on the map or in the list.';
   this.select.replaceChildren();for(const s of this.sections){const option=document.createElement('option');option.value=s.id;option.textContent=`${s.id} · ${s.name}`;this.select.append(option);}
   this.select.disabled=false;$('section-visit').disabled=false;$('section-overview').disabled=false;this.selectSection(this.sections.find(s=>s.id===this.selected)?.id||sectionAt(this.sections,this.focusPoint.x,this.focusPoint.z)?.id||this.sections[0].id);
   this.group.visible=this.enabled;
  }catch(error){this.sections=[];this.labels.replaceChildren();this.labelEntries=[];this.segments.clear();for(const child of this.group.children){child.geometry?.dispose();child.material?.dispose();}this.group.clear();this.error=error.message;$('section-loading').textContent='Section overlay could not load. The city is still available.';$('section-retry').hidden=false;}
  finally{this.pending=false;}
 }
 build(){
  const bins=new Map();
  for(const section of this.sections){
   const vertices=[];for(const polygon of section.polygons)for(const ring of polygon.rings)for(let i=1;i<ring.length;i++){
    const a=ring[i-1],b=ring[i],steps=Math.max(1,Math.ceil(Math.hypot(b[0]-a[0],b[1]-a[1])/100));
    for(let j=0;j<steps;j++)for(const t of [j/steps,(j+1)/steps]){const x=a[0]+(b[0]-a[0])*t,z=a[1]+(b[1]-a[1])*t;vertices.push(x,Math.max(1.5,this.sampler.height(x,z))+5,z);}
   }
   this.segments.set(section.id,vertices);const status=section.review.status;if(!bins.has(status))bins.set(status,[]);for(const v of vertices)bins.get(status).push(v);
   const el=document.createElement('button');el.className='section-number';el.textContent=section.id;el.dataset.section=section.id;el.dataset.status=status;el.setAttribute('aria-label',`${section.id} ${section.name} — ${REVIEW_STATES[status].label}`);el.title=`${section.id} · ${section.name}`;el.hidden=true;
   el.addEventListener('pointerdown',e=>e.stopPropagation());el.addEventListener('click',e=>{e.stopPropagation();this.selectSection(section.id);this.onSelect(section);});this.labels.append(el);
   const [x,z]=section.label;this.labelEntries.push({el,section,pos:new THREE.Vector3(x,Math.max(1.5,this.sampler.height(x,z))+30,z)});
  }
  for(const [status,vertices]of bins){const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));const mesh=new THREE.LineSegments(geometry,new THREE.LineBasicMaterial({color:REVIEW_STATES[status].colour,transparent:true,opacity:.85,depthTest:false,depthWrite:false,toneMapped:false,fog:false}));mesh.renderOrder=20;mesh.frustumCulled=false;this.group.add(mesh);}
  this.highlight=new THREE.LineSegments(new THREE.BufferGeometry(),new THREE.LineBasicMaterial({color:'#ffdd78',depthTest:false,depthWrite:false,toneMapped:false,fog:false}));this.highlight.renderOrder=21;this.highlight.frustumCulled=false;this.group.add(this.highlight);
 }
 selectSection(id){
  const s=this.sections.find(s=>s.id===id);if(!s)return;this.selected=id;this.select.value=id;this.highlight.geometry.dispose();this.highlight.geometry=new THREE.BufferGeometry();this.highlight.geometry.setAttribute('position',new THREE.Float32BufferAttribute(this.segments.get(id),3));
  for(const {el,section}of this.labelEntries)el.setAttribute('aria-pressed',String(section.id===id));
  $('section-name').textContent=`${id} · ${s.name}`;$('section-state').textContent=REVIEW_STATES[s.review.status].label;$('section-state').dataset.status=s.review.status;$('section-note').textContent=s.review.note;
  $('section-boundary-note').textContent='Internal borders are approximate; district areas include coastal waters.'+(s.sourceNotes?.some(n=>n.includes('neighbouring official district'))?' Some saved destinations lie across the official district boundary; their source coordinates are unchanged.':'');
  $('section-checks').replaceChildren();for(const key of REVIEW_GATES){const check=s.review.checks[key],li=document.createElement('li'),label=document.createElement('span'),state=document.createElement('span');label.textContent=REVIEW_LABELS[key];state.textContent=check?.state==='verified'&&check.scope==='section'&&check.evidence?.length?'Verified':check?.state==='partial'?'Partial':'Pending';li.append(label,state);li.title=check?.note||'';$('section-checks').append(li);}
  $('section-issues').replaceChildren();for(const issue of s.review.issues){const a=document.createElement('a');a.href=`https://linear.app/stealth-company/issue/${issue}`;a.textContent=issue+' ↗';a.target='_blank';a.rel='noopener';$('section-issues').append(a);}
 }
 update(camera,focus,now,{suppressed=false}={}){
  this.focusPoint.copy(focus);if(!this.enabled||!this.sections.length)return;this.group.visible=!suppressed;this.labels.hidden=suppressed;if(suppressed||now-this.lastLabels<80)return;this.lastLabels=now;camera.updateMatrixWorld();
  const occupied=[],w=innerWidth,h=innerHeight,mobile=w<=760,expanded=document.body.classList.contains('controls-expanded');
  const exclusions=['#location-title','.minimap','.view-tools','#flight-controls','#stream-status','#explorer'].flatMap(q=>{const el=document.querySelector(q);if(!el||el.hidden||!el.getClientRects().length)return [];const r=el.getBoundingClientRect();return [{left:r.left-26,right:r.right+26,top:r.top-24,bottom:r.bottom+24}];});
  const entries=[...this.labelEntries].sort((a,b)=>(b.section.id===this.selected)-(a.section.id===this.selected)||camera.position.distanceToSquared(a.pos)-camera.position.distanceToSquared(b.pos));
  for(const entry of entries){const {el,pos}=entry;this.point.copy(pos).project(camera);const x=(this.point.x*.5+.5)*w,y=(-this.point.y*.5+.5)*h;
   const off=this.point.z<0||this.point.z>1||x<24||x>w-24||y<82||y>h-(mobile?215:115)||(expanded&&(mobile?y>h*.3:x<350))||(x>w-205&&y<157);
   const blocked=exclusions.some(r=>x>=r.left&&x<=r.right&&y>=r.top&&y<=r.bottom);
   const overlap=occupied.some(([a,b])=>Math.abs(a-x)<58&&Math.abs(b-y)<44);el.hidden=off||blocked||overlap;if(!el.hidden){el.style.left=x+'px';el.style.top=y+'px';occupied.push([x,y]);}
  }
 }
 get state(){return {enabled:this.enabled,pending:this.pending,error:this.error,total:this.sections.length,counts:this.counts||null,selected:this.selected,boundaryVersion:this.boundaryVersion,visibleLabels:this.labelEntries.filter(x=>!x.el.hidden&&!this.labels.hidden).map(x=>x.section.id),lineVertices:[...this.segments.values()].reduce((n,x)=>n+x.length/3,0)};}
}

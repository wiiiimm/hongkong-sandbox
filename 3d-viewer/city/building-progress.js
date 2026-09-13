const percentText=value=>value===null?'Not available':`${value.toLocaleString('en-HK',{minimumFractionDigits:2,maximumFractionDigits:2})}%`;
export function coveragePresentation(data){
 if(data?.version!==3||data.status!=='available'||data.unit!=='source-building-form'||!Number.isSafeInteger(data.totalForms)||data.totalForms<0||!Number.isFinite(Date.parse(data.updatedAt)))return null;
 const keys=['enhanced','goodToGo','enhancementRequired','unassessed'],breakdown=data.breakdown,g=data.government;
 const count=n=>Number.isSafeInteger(n)&&n>=0;
 if(!breakdown||keys.some(k=>!count(breakdown[k]))||keys.reduce((n,k)=>n+breakdown[k],0)!==data.totalForms)return null;
 if(!g||['available','enhanced','goodToGo','ready','remaining','noMatchedSource','enhancedOutside','goodToGoOutside'].some(k=>!count(g[k]))||
  g.available+g.noMatchedSource!==data.totalForms||g.enhanced+g.goodToGo!==g.ready||g.ready+g.remaining!==g.available||
  g.enhanced+g.enhancedOutside!==breakdown.enhanced||g.goodToGo+g.goodToGoOutside!==breakdown.goodToGo||
  g.enhancedOutside+g.goodToGoOutside>g.noMatchedSource)return null;
 const percent=g.available?g.ready/g.available*100:null;
 return{total:data.totalForms,enhanced:breakdown.enhanced,ready:g.ready,breakdown,government:g,percent,
  sourcePending:g.noMatchedSource-g.enhancedOutside-g.goodToGoOutside,
  date:new Date(data.updatedAt).toLocaleDateString('en-HK',{day:'numeric',month:'short',year:'numeric',timeZone:'Asia/Hong_Kong'}),percentage:percentText(percent)};
}
export async function bindBuildingProgress(manifest,{doc=document,fetcher=fetch}={}){
 const dialog=doc.getElementById('building-progress'),open=doc.getElementById('progress-open'),close=doc.getElementById('progress-close');
 open.addEventListener('click',()=>dialog.showModal());close.addEventListener('click',()=>dialog.close());
 dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}});
 const unavailable=message=>{doc.getElementById('progress-status').textContent=message;doc.getElementById('progress-values').hidden=true;doc.getElementById('progress-chip').textContent='Updating';doc.getElementById('progress-chip-total').textContent='Statistics unavailable';open.setAttribute('aria-label','Model progress: statistics unavailable');};
 try{
  const response=await fetcher('city/data/building-progress.json',{cache:'no-cache'});if(!response.ok)throw Error('Statistics unavailable');
  const data=await response.json(),p=coveragePresentation(data);if(!p)throw Error('Statistics unavailable');
  const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(JSON.stringify(manifest))),actual=[...new Uint8Array(digest)].map(x=>x.toString(16).padStart(2,'0')).join('');
  if(actual!==data.manifestDigest){unavailable('Statistics are being updated for this map version.');return;}
  const number=n=>n.toLocaleString('en-HK'),compact=n=>n.toLocaleString('en-HK',{notation:'compact',maximumFractionDigits:1}).toLowerCase(),g=p.government;
  doc.getElementById('progress-total').textContent=number(p.total);
  doc.getElementById('progress-available').textContent=number(g.available);
  doc.getElementById('progress-enhanced').textContent=number(g.ready);
  doc.getElementById('progress-remaining').textContent=number(g.remaining);
  doc.getElementById('progress-percent').textContent=p.percent===null?p.percentage:`${p.percentage} done`;
  doc.getElementById('progress-ratio').textContent=`${number(g.ready)} of ${number(g.available)} models with a matched government source are complete.${g.goodToGo?` Includes ${number(g.goodToGo)} already recorded as good to go.`:''}`;
  const meter=doc.getElementById('progress-meter');meter.max=g.available||1;meter.value=g.ready;meter.hidden=p.percent===null;
  meter.setAttribute('aria-valuetext',`${p.percentage}: ${number(g.ready)} of ${number(g.available)} government-source upgrades complete`);
  const outside=doc.getElementById('progress-outside');outside.hidden=g.enhancedOutside===0;
  outside.textContent=`Another ${number(g.enhancedOutside)} enhanced models are outside this government-source group. They are included in the map total above.`;
  const tiers=[['enhanced','Enhanced on map',p.enhanced],['goodToGo','Good to go',p.breakdown.goodToGo],['remaining','Government upgrades remaining',g.remaining],['sourcePending','Other models awaiting sources',p.sourcePending]];
  for(const [key,label,value] of tiers){
   const bar=doc.getElementById('progress-bar-'+key);bar.max=p.total||1;bar.value=value;
   bar.setAttribute('aria-valuetext',`${label}: ${number(value)} of ${number(p.total)} models on the map`);
   doc.getElementById('progress-count-'+key).textContent=number(value);
   bar.closest('.progress-tier').hidden=key==='goodToGo'&&value===0;
  }
  doc.getElementById('progress-date').textContent=p.date;
  doc.getElementById('progress-chip').textContent=`${number(g.ready)} of ${number(g.available)} · ${p.percent===null?'—':p.percentage}`;
  doc.getElementById('progress-chip-total').textContent=`${compact(p.total)} total · ${compact(g.available)} enhanceable`;
  open.setAttribute('aria-label',`Model progress: ${number(p.total)} total models, ${number(g.available)} can use government detail, ${number(g.ready)} completed; ${p.percentage} done`);
  doc.getElementById('progress-status').textContent=`${number(g.ready)} verified government upgrades are available on this map.`;
  doc.getElementById('progress-values').hidden=false;
 }catch{unavailable('Building statistics are temporarily unavailable. You can still explore the city.');}
}

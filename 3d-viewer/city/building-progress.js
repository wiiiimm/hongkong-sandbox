export function coveragePresentation(data){
 if(data?.version!==2||data.status!=='available'||data.unit!=='source-building-form'||!Number.isInteger(data.totalForms)||data.totalForms<0||!Number.isFinite(Date.parse(data.updatedAt)))return null;
 const keys=['enhanced','goodToGo','enhancementRequired','unassessed'],breakdown=data.breakdown;
 if(!breakdown||keys.some(k=>!Number.isInteger(breakdown[k])||breakdown[k]<0)||keys.reduce((n,k)=>n+breakdown[k],0)!==data.totalForms)return null;
 const ready=breakdown.enhanced+breakdown.goodToGo,percent=data.totalForms?ready/data.totalForms*100:null;
 return{total:data.totalForms,enhanced:breakdown.enhanced,ready,breakdown,percent,date:new Date(data.updatedAt).toLocaleDateString('en-HK',{day:'numeric',month:'short',year:'numeric',timeZone:'Asia/Hong_Kong'}),percentage:percent===null?'Not available':`${percent.toLocaleString('en-HK',{maximumFractionDigits:2,minimumFractionDigits:2})}%`};
}
export async function bindBuildingProgress(manifest,{doc=document,fetcher=fetch}={}){
 const dialog=doc.getElementById('building-progress'),open=doc.getElementById('progress-open'),close=doc.getElementById('progress-close');open.addEventListener('click',()=>dialog.showModal());close.addEventListener('click',()=>dialog.close());dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}});
 const unavailable=message=>{doc.getElementById('progress-status').textContent=message;doc.getElementById('progress-values').hidden=true;doc.getElementById('progress-chip').textContent='Updating';};
 try{const response=await fetcher('city/data/building-progress.json',{cache:'no-cache'});if(!response.ok)throw Error('Statistics unavailable');const data=await response.json(),p=coveragePresentation(data);if(!p)throw Error('Statistics unavailable');const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(JSON.stringify(manifest))),actual=[...new Uint8Array(digest)].map(x=>x.toString(16).padStart(2,'0')).join('');if(actual!==data.manifestDigest){unavailable('Statistics are being updated for this map version.');return;}
  const number=n=>n.toLocaleString('en-HK');
  doc.getElementById('progress-total').textContent=number(p.total);
  doc.getElementById('progress-enhanced').textContent=number(p.ready);
  doc.getElementById('progress-percent').textContent=p.percentage;
  doc.getElementById('progress-ratio').textContent=`${number(p.ready)} of ${number(p.total)} forms are enhanced or good to go. No further enhancement is planned for these forms.`;
  const meter=doc.getElementById('progress-meter');meter.max=p.total||1;meter.value=p.ready;
  meter.setAttribute('aria-valuetext',`${p.percentage}: ${number(p.ready)} of ${number(p.total)} source building forms are enhanced or good to go`);meter.hidden=p.percent===null;
  for(const [key,label]of[['enhancementRequired','Enhancement required'],['enhanced','Enhanced'],['goodToGo','Good to go'],['unassessed','Not screened']]){
   const count=p.breakdown[key],bar=doc.getElementById('progress-bar-'+key),percent=p.total?count/p.total*100:0;
   doc.getElementById('progress-count-'+key).textContent=`${number(count)} · ${percent.toLocaleString('en-HK',{maximumFractionDigits:2})}%`;
   bar.max=p.total||1;bar.value=count;bar.setAttribute('aria-valuetext',`${label}: ${number(count)} of ${number(p.total)} source building forms`);
  }
  doc.getElementById('progress-date').textContent=p.date;
  doc.getElementById('progress-chip').textContent=`${p.percentage} ready · ${number(p.ready)}`;
  open.setAttribute('aria-label',`Model progress: ${p.percentage} ready, ${number(p.ready)} of ${number(p.total)} forms enhanced or good to go`);
  doc.getElementById('progress-status').textContent='Keep what works. Enhance what needs it.';
  doc.getElementById('progress-values').hidden=false;
 }catch{unavailable('Building statistics are temporarily unavailable. You can still explore the city.');}
}

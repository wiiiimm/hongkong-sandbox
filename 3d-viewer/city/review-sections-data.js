import {inPolygon} from './geo.js';
export const REVIEW_GATES=['ground','buildings','routes','exploration','presentation','provenance'];
export const REVIEW_LABELS={ground:'Ground & water',buildings:'Buildings & skyline',routes:'Streets & public space',exploration:'Walking & flight',presentation:'Day, night & mobile',provenance:'Sources & review evidence'};
export const REVIEW_STATES={base:{label:'Base mapped',colour:'#28778a'},reviewing:{label:'Under review',colour:'#c78414'},close:{label:'Close to ready',colour:'#9268c8'},ready:{label:'Ready',colour:'#298252'}};
export function readinessFor(record){
 const checks=record?.checks||{},verified=REVIEW_GATES.filter(key=>checks[key]?.state==='verified'&&checks[key]?.scope==='section'&&checks[key]?.evidence?.length);
 const blocked=(record?.blockers||[]).length>0;
 const status=verified.length===6&&!blocked?'ready':verified.length>=4&&verified.includes('ground')&&verified.includes('buildings')&&!blocked?'close':record?.phase==='active'||verified.length?'reviewing':'base';
 return {status,verified:verified.length,checks,remaining:REVIEW_GATES.filter(key=>!verified.includes(key)),note:record?.note||'Detailed section review is pending.',issues:record?.issues||[]};
}
export function prepareReviewSections(geometry,readiness,{expectedCount=132}={}){
 if(geometry?.schemaVersion!==1||readiness?.schemaVersion!==1||geometry.sections?.length!==expectedCount||readiness.sections?.length!==expectedCount)throw Error('Section inventories are incomplete');
 const records=new Map(readiness.sections.map(r=>[r.id,r]));if(records.size!==expectedCount)throw Error('Duplicate readiness ID');
 const seen=new Set();return geometry.sections.map(section=>{
  if(!/^\d{2}\.\d+$/.test(section.id)||seen.has(section.id)||!records.has(section.id)||!Array.isArray(section.label)||section.label.length!==2||!section.label.every(Number.isFinite)||!section.polygons?.length||section.polygons.some(p=>!p.rings?.length||p.rings.some(r=>r.length<4||r.some(p=>p.length!==2||!p.every(Number.isFinite))||r[0].some((v,i)=>v!==r.at(-1)[i]))))throw Error('Invalid review section '+section.id);
  if(!Array.isArray(section.bounds)||section.bounds.length!==4||!section.bounds.every(Number.isFinite)||section.bounds[0]>=section.bounds[2]||section.bounds[1]>=section.bounds[3]||!section.polygons.some(p=>inPolygon(...section.label,p.rings)))throw Error('Invalid bounds or label '+section.id);
  seen.add(section.id);return {...section,review:readinessFor(records.get(section.id))};
 });
}
export function reviewCounts(sections){return sections.reduce((counts,s)=>(counts[s.review.status]++,counts),{ready:0,close:0,reviewing:0,base:0});}
export function sectionAt(sections,x,z){return sections.find(s=>x>=s.bounds[0]&&x<=s.bounds[2]&&z>=s.bounds[1]&&z<=s.bounds[3]&&s.polygons.some(p=>inPolygon(x,z,p.rings)))||null;}

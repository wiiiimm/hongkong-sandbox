/** Counting units are source-form UIDs, never inferred physical buildings. */
import {validScreening} from './screening.mjs';
export function countCoverage({forms,models,reviews,suppressed=[],screenings=[],governmentSources=null}){
 const hidden=new Set(suppressed),all=new Set(forms.filter(f=>!hidden.has(f.uid)).map(f=>f.uid)),installed=new Map(),decisions=new Map(reviews.map(r=>[r.uid,r]));
 for(const m of models){if(hidden.has(m.uid))continue;all.add(m.uid);const previous=installed.get(m.uid);if(previous&&previous.sha256!==m.sha256)throw Error('Conflicting deployed sources for '+m.uid);installed.set(m.uid,m);}
 const enhanced=[];for(const [uid,m]of installed){const r=decisions.get(uid);if(r?.review_state==='installed-verified'&&r.source_sha256===m.sha256)enhanced.push(uid);}
 const enhancedSet=new Set(enhanced),formMap=new Map(forms.map(f=>[f.uid,f])),screenMap=new Map();
 for(const row of screenings){if(screenMap.has(row.uid))throw Error('Duplicate screening decision: '+row.uid);screenMap.set(row.uid,row);}
 const states=new Map(),breakdown={enhanced:0,goodToGo:0,enhancementRequired:0,unassessed:0};
 for(const uid of all){
  const form=formMap.get(uid),row=screenMap.get(uid),valid=form&&validScreening(row,form);
  // Current rework decisions override historical enhancement credit.
  const state=valid&&row.decision==='enhancement-required'?'enhancementRequired'
   :enhancedSet.has(uid)?'enhanced':valid&&row.decision==='good-to-go'?'goodToGo':'unassessed';
  breakdown[state]++;states.set(uid,state);
 }
 const ready=breakdown.enhanced+breakdown.goodToGo;
 let government=null;
 if(governmentSources!==null){
  if(!Array.isArray(governmentSources))throw Error('Invalid government source proof');
  const available=new Set(),seenSources=new Set();
  for(const row of governmentSources){
   if(!Array.isArray(row)||row.length!==2||row.some(v=>typeof v!=='string'||!v)||seenSources.has(row[0]))throw Error('Duplicate or invalid government source identity');
   const [uid,sourceId]=row;seenSources.add(uid);
   const form=formMap.get(uid)||installed.get(uid);
   if(all.has(uid)&&form?.buildingCSUID===sourceId)available.add(uid);
  }
  const enhanced=[...available].filter(uid=>states.get(uid)==='enhanced').length;
  const goodToGo=[...available].filter(uid=>states.get(uid)==='goodToGo').length;
  government={available:available.size,enhanced,goodToGo,ready:enhanced+goodToGo,
   remaining:available.size-enhanced-goodToGo,percent:available.size?(enhanced+goodToGo)/available.size*100:null,
   noMatchedSource:all.size-available.size,enhancedOutside:breakdown.enhanced-enhanced,goodToGoOutside:breakdown.goodToGo-goodToGo};
 }
 return{government,unit:'source-building-form',totalForms:all.size,reviewedEnhancedForms:enhanced.length,percent:all.size?enhanced.length/all.size*100:null,unreviewedOrBasicForms:all.size-enhanced.length,breakdown,readyForms:ready,readyPercent:all.size?ready/all.size*100:null,uniquePhysicalBuildings:null,wholeBuildingCompletion:null};
}

/** Counting units are source-form UIDs, never inferred physical buildings. */
import {validScreening} from './screening.mjs';
export function countCoverage({forms,models,reviews,suppressed=[],screenings=[]}){
 const hidden=new Set(suppressed),all=new Set(forms.filter(f=>!hidden.has(f.uid)).map(f=>f.uid)),installed=new Map(),decisions=new Map(reviews.map(r=>[r.uid,r]));
 for(const m of models){if(hidden.has(m.uid))continue;all.add(m.uid);const previous=installed.get(m.uid);if(previous&&previous.sha256!==m.sha256)throw Error('Conflicting deployed sources for '+m.uid);installed.set(m.uid,m);}
 const enhanced=[];for(const [uid,m]of installed){const r=decisions.get(uid);if(r?.review_state==='installed-verified'&&r.source_sha256===m.sha256)enhanced.push(uid);}
 const enhancedSet=new Set(enhanced),formMap=new Map(forms.map(f=>[f.uid,f])),screenMap=new Map();
 for(const row of screenings){if(screenMap.has(row.uid))throw Error('Duplicate screening decision: '+row.uid);screenMap.set(row.uid,row);}
 const breakdown={enhanced:0,goodToGo:0,enhancementRequired:0,unassessed:0};
 for(const uid of all){
  const form=formMap.get(uid),row=screenMap.get(uid),valid=form&&validScreening(row,form);
  // Current rework decisions override historical enhancement credit.
  if(valid&&row.decision==='enhancement-required')breakdown.enhancementRequired++;
  else if(enhancedSet.has(uid))breakdown.enhanced++;
  else if(valid&&row.decision==='good-to-go')breakdown.goodToGo++;
  else breakdown.unassessed++;
 }
 const ready=breakdown.enhanced+breakdown.goodToGo;
 return{unit:'source-building-form',totalForms:all.size,reviewedEnhancedForms:enhanced.length,percent:all.size?enhanced.length/all.size*100:null,unreviewedOrBasicForms:all.size-enhanced.length,breakdown,readyForms:ready,readyPercent:all.size?ready/all.size*100:null,uniquePhysicalBuildings:null,wholeBuildingCompletion:null};
}

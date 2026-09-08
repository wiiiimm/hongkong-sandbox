/** Counting units are source-form UIDs, never inferred physical buildings. */
export function countCoverage({forms,models,reviews,suppressed=[]}){
 const hidden=new Set(suppressed),all=new Set(forms.filter(f=>!hidden.has(f.uid)).map(f=>f.uid)),installed=new Map(),decisions=new Map(reviews.map(r=>[r.uid,r]));
 for(const m of models){if(hidden.has(m.uid))continue;all.add(m.uid);const previous=installed.get(m.uid);if(previous&&previous.sha256!==m.sha256)throw Error('Conflicting deployed sources for '+m.uid);installed.set(m.uid,m);}
 const enhanced=[];for(const [uid,m]of installed){const r=decisions.get(uid);if(r?.review_state==='installed-verified'&&r.source_sha256===m.sha256)enhanced.push(uid);}
 return{unit:'source-building-form',totalForms:all.size,reviewedEnhancedForms:enhanced.length,percent:all.size?enhanced.length/all.size*100:null,unreviewedOrBasicForms:all.size-enhanced.length,uniquePhysicalBuildings:null,wholeBuildingCompletion:null};
}

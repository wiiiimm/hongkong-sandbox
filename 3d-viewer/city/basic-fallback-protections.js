// Reviewed source/compound pairs may keep their own BASIC fallback while the
// compound remains active. This never replaces either model's geometry.
const HASH=/^[0-9a-f]{64}$/;
const KEYS=['buildingCSUID','sourceSHA256','suppressorSourceSHA256','suppressorUid','uid'];
export function prepareBasicFallbackProtections(rows){
 const result=new Map(),seen=new Set();
 if(rows===undefined)return result;
 if(!Array.isArray(rows))throw new Error('Invalid BASIC fallback protections');
 for(const row of rows){
  if(!row||Array.isArray(row)||typeof row!=='object'||JSON.stringify(Object.keys(row).sort())!==JSON.stringify(KEYS)||
     ![row.uid,row.suppressorUid,row.buildingCSUID].every(v=>typeof v==='string'&&v.length>0&&v.length<=200)||
     row.uid===row.suppressorUid||![row.sourceSHA256,row.suppressorSourceSHA256].every(v=>typeof v==='string'&&HASH.test(v)))throw new Error('Invalid BASIC fallback protection');
  const key=JSON.stringify([row.uid,row.suppressorUid]);
  if(seen.has(key))throw new Error('Duplicate BASIC fallback protection');
  seen.add(key);const entries=result.get(row.uid)||[];entries.push(Object.freeze({...row}));result.set(row.uid,entries);
 }
 return result;
}
export function basicFallbackIsProtected(protections,building,suppressor){
 if(!building||!suppressor?.entry||!suppressor?.record)return false;
 const sourceSHA256=suppressor.entry.sourceSha256??suppressor.entry.sha256;
 return (protections.get(building.uid)||[]).some(p=>p.buildingCSUID===building.buildingCSUID&&p.suppressorUid===suppressor.record.uid&&p.suppressorSourceSHA256===sourceSHA256);
}

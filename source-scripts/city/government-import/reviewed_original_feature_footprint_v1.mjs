/** Exact source-identity scope for a reviewed complete original feature.
 * Preparation only: this module is not wired into the production viewer.
 */
const hash=/^[a-f0-9]{64}$/;
export const featureForm = b => b&&({uid:b.uid,objectId:b.objectId,buildingCSUID:b.buildingCSUID,
  parent:b.parent??null,osmRefs:b.osmRefs??null,rings:b.rings,
  baseHeightHKPD:b.baseHeightHKPD??null,topHeightHKPD:b.topHeightHKPD??null});
export function reviewedOriginalFeatureFootprint(entry,building,scopes){
  const s=scopes[entry.footprintScope];
  const fail=()=>{throw new Error('Unverified complete original feature scope');};
  if(!s||s.policy!=='reviewed-original-feature-v1'||s.identityReviewed!==true||
     entry.variantId||(entry.suppressesBuildingUids??[]).length||
     s.uid!==entry.uid||s.modelId!==entry.modelId||s.sha256!==entry.sha256||!hash.test(s.sha256)||
     JSON.stringify(featureForm(building))!==JSON.stringify(s.form)||
     JSON.stringify(entry.worldBounds)!==JSON.stringify(s.worldBounds)||
     !s.sourceReview?.path?.startsWith('docs/astra-city/government-import/')||
     s.sourceReview.path.includes('..')||!hash.test(s.sourceReview.sha256))fail();
  const ring=s.boundary,b=s.worldBounds;
  if(!Array.isArray(ring)||ring.length<3||!ring.every(p=>Array.isArray(p)&&p.length===2&&p.every(Number.isFinite)))fail();
  const x=ring.map(p=>p[0]),z=ring.map(p=>p[1]);
  if([Math.min(...x)-b[0][0],Math.max(...x)-b[1][0],Math.min(...z)-b[0][2],Math.max(...z)-b[1][2]].some(v=>Math.abs(v)>.002))fail();
  let area=0;for(let i=0;i<ring.length;i++){const a=ring[i],c=ring[(i+1)%ring.length];area+=a[0]*c[1]-c[0]*a[1];}
  if(!Number.isFinite(area)||area===0)fail();
  return ring.map(p=>[...p]);
}

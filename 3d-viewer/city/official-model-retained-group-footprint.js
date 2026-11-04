import {retainedGroupScopes} from './official-model-retained-group-data.js';
const selected=b=>b&&({uid:b.uid,objectId:b.objectId,buildingCSUID:b.buildingCSUID,parent:b.parent,osmRefs:b.osmRefs??null,rings:b.rings});
/** Full geographic context for exact originals; never suppress another component. */
export function retainedGroupFootprint(entry,building,getBuilding){
 const scope=retainedGroupScopes[entry.footprintScope];
 if(!scope||scope.uid!==entry.uid||scope.modelId!==entry.modelId||scope.sha256!==entry.sha256||building.uid!==scope.uid||typeof getBuilding!=='function')throw new Error('Unverified retained model footprint scope');
 if((entry.suppressesBuildingUids??[]).length)throw new Error('Retained model footprint cannot suppress components');
 const primary=scope.forms.find(b=>b.uid===scope.uid);
 if(!primary?.parent||!primary.osmRefs?.length)throw new Error('Retained footprint has no source parent');
 for(const form of scope.forms){
  if(form.parent!==primary.parent||!form.osmRefs?.some(r=>primary.osmRefs.includes(r)))throw new Error('Retained footprint ownership differs');
  const current=form.uid===building.uid?building:getBuilding(form.uid);
  if(JSON.stringify(selected(current))!==JSON.stringify(form))throw new Error('Retained footprint source changed or unavailable: '+form.uid);
 }
 return scope.forms.flatMap(b=>b.rings[0].map(p=>[...p]));
}

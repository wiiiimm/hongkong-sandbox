"""Record the exact remaining Plaza foundation faces, preserving every failed gate."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-plaza-hollywood-';BATCH=P+'buried-facet-role-evidence-v1-20261024'

def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];cache={}
 def take(n,p):
  if n not in cache:cache[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  assert digest(p.read_bytes())==cache[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 runtime=P+'original-inset-runtime-v1-20261024';attributes=P+'original-inset-prephysical-v1-20261024-attributes';clearance=P+'original-inset-complete-clearance-v1-20261024';views=P+'seven-buried-facet-views-v1-20261024'
 source=take(runtime,BASE/runtime/'selection.json.gz')['rows'][0];uid=source['uid'];assert uid=='landsd/323185:0'
 g=take(runtime,HERE/'local'/runtime/'runtime-geometry.json.gz')['rows'][0];a=take(attributes,BASE/attributes/'attributes.json.gz')['rows'][0]
 path=ROOT/source['candidate']['path'];assert digest(path.read_bytes())==source['sourceSHA256']==g['sourceSHA256']==a['sourceSHA256'];refs.append(path)
 ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);polys=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;ground,polys=ground[valid],polys[valid];tree=shapely.STRtree(polys)
 ix=np.asarray(a['completeOriginalIndex']).reshape(-1,3);modes={'original':decode_original_world_triangles(path.read_bytes())}
 for name,key in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]:modes[name]=np.asarray(a[key]).reshape(-1,3)[ix]
 expected=[8819,8830,8831,8832,8833,8844,8845];rows=[];sampler=module('plaza_buried_sampler',HERE/'xl-final-script-pass.py')
 for name,t in modes.items():
  context=take(clearance,BASE/clearance/(name+'.json.gz'));assert digest(t.astype('<f8').tobytes())==context['sourceWorldSHA256']
  cap=take(clearance,BASE/clearance/(name+'-cap-paths.json.gz'))['proof'];paths={r['sourceFace']:r for r in cap['paths']}
  points=np.concatenate([t,t.mean(1)[:,None,:]],axis=1);height=sampler.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),ground,tree).reshape(-1,4);gaps=points[:,:,1]-height
  assert np.isfinite(height).all();ids=np.flatnonzero((gaps<-.5).all(1)).tolist();assert ids==expected
  details=[]
  for i in ids:
   tri=t[i];normal=np.cross(tri[1]-tri[0],tri[2]-tri[0]);norm=float(np.linalg.norm(normal));ratio=float(normal[1]/norm);record=dict(sourceFace=i,vertices=tri.tolist(),signedNormalYRatio=ratio,sampledGapRangeM=[float(gaps[i].min()),float(gaps[i].max())],vertexAndCentreGapsM=gaps[i].tolist(),areaM2=norm/2,yRange=[float(tri[:,1].min()),float(tri[:,1].max())])
   if i in [8844,8845]:assert ratio== -1;record.update(classification='downward-horizontal-source-facet',clearCapWallPath=None)
   else:
    assert abs(ratio)<.004 and paths[i]['hasExactSharedEdgeClearCapPath'];record.update(classification='lower-wall-source-facet',clearCapWallPath=paths[i])
   details.append(record)
  rows.append(dict(mode=name,completeSourceFaces=len(t),completeTerrainCoverage=True,wholeBuriedFaces=ids,wholeBuriedUpwardFaces=[],rawFoundationGatePassed=False,faces=details))
 images=[];v=take(views,BASE/views/'summary.json');assert v['displaySubsetOnly']and v['displayedExactNegativeFaces']==expected and not v['allExactNegativeFacesShown']
 for r in v['regions']:
  p=ROOT/r['image'];assert digest(p.read_bytes())==r['imageSHA256'];refs.append(p);images.append(dict(path=r['image'],sha256=r['imageSHA256'],sourceFaces=r['sourceFaces'],actuallyInspected=True))
 result=dict(uids=[uid],sourceSHA256=source['sourceSHA256'],rows=rows,imagesActuallyViewed=images,rawClearancePartitionUnchanged=True,rawFoundationFailurePreserved=True,identityAccepted=False,physicalAccepted=False,sourceRoleAccepted=False,installationApproved=False,permanentRejection=False,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,qualification='All seven whole-burial faces reproduced in all four coordinate streams with complete actual-ground coverage. Five are lower wall facets with original clear-cap paths; two are downward horizontal facets. Direction and connectivity do not waive existing burial, identity or publication failures. The two inspected diagrams show only these seven faces, not the full142-face negative partition. No surface is omitted, raised, cut or marked nonrendering.',requiredNextAction='Bounded physical/source-role review or an authorised source-backed terrain remedy for the retained whole-face failures. Preserve the17.285m raw identity extent hold and all31neighbour obligations.')
 save(out/'summary.json',result);refs.extend([HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py']);module('plaza_buried_roles_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'four-world-complete-remaining-buried-facet-roles-with-raw-failures',refs,result)
if __name__=='__main__':main()

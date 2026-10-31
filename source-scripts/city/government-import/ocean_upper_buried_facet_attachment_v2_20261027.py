"""Finite original-surface paths for every flagged upper facet's vertices/centroid."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_face_attachment_minimax_v2_20261024 import attachment_paths
P='government-xl-after-waterfront-ocean-';BATCH='government-xl-ocean-upper-buried-facet-attachment-v2-20261027';UID='landsd/156599:0'
def main():
 base=ROOT/'docs/astra-city/government-import';out=base/BATCH;assert not out.exists();pins={};refs=[Path(__file__),HERE/'original_face_attachment_minimax_v2_20261024.py',HERE/'pool_incident_wall_contacts_v1_20261017.py'];records=[]
 def take(name,path):
  if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
  assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 runtime=P+'four-corrected-runtime-v1-20261027';attrs=P+'four-attributes-v1-20261027';selection=take(runtime,base/runtime/'selection.json.gz');source=next(r for r in selection['rows']if r['uid']==UID);attributes=take(attrs,base/attrs/'attributes.json.gz');assert attributes['startEndAllInputsVerified'];a=next(r for r in attributes['rows']if r['uid']==UID);asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256']==a['sourceSHA256'];refs.append(asset)
 index=np.asarray(a['completeOriginalIndex']).reshape(-1,3);worlds=dict(original=decode_original_world_triangles(asset.read_bytes()))
 for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(a[field],dtype='<f8').reshape(-1,3)[index]
 old=P+'pair-support-v1-20261027';current=P+'four-corrected-upper-support-v1-20261027';previous=take(old,base/old/'summary.json');fresh=take(current,base/current/'summary.json')
 views=take('government-xl-ocean-upper-compound-role-views-v1-20261027',base/'government-xl-ocean-upper-compound-role-views-v1-20261027/summary.json');groups={i:r['componentRepresentative']for r in views['rows']for i in r['completeComponentFaceIds']}
 for mode,tri in worlds.items():
  context=P+'pair-compound-context-v1-20261027';raw=take(context,base/context/(mode+'.json.gz'));assert raw['sourceWorldSHA256']==digest(tri.tobytes());ids=[r['sourceFace']for r in raw['faces']];assert len(ids)==50
  before=next(r for r in previous['rows']if r['mode']==mode);after=next(r for r in fresh['rows']if r['mode']==mode);assert before['compoundFoundation']==after['compoundFoundation']and before['sourceWorldSHA256ByUid']==after['sourceWorldSHA256ByUid'];assert after['sourceWorldSHA256ByUid'][UID]==digest(tri.tobytes())
  attachment=P+'pair-rim-attachment-v1-20261027';terminals=take(attachment,base/attachment/(mode+'.json.gz'))['terminals'];assert all(t['peerUid']=='landsd/234188:0'for t in terminals)
  targets=[]
  for face in ids:
   assert np.array_equal(tri[face],np.asarray(next(r for r in raw['faces']if r['sourceFace']==face)['vertices']))
   for label,point in [(str(i),tri[face,i])for i in range(3)]+[('centroid',tri[face].mean(0))]:targets.append(dict(incidentFaces=[face],witness=dict(position=point.tolist(),sourceFace=face,pointKind=label)))
  paths=attachment_paths(tri,dict(targets=targets,proof=dict(contacts=terminals)),[])
  for path in paths:
   if path['hasUnrestrictedFiniteAttachment']:assert all(groups[i]==groups[path['witness']['sourceFace']]for i in path['faces'])
  save(out/(mode+'.json.gz'),dict(mode=mode,sourceWorldSHA256=digest(tri.tobytes()),rows=paths))
  records.append(dict(mode=mode,facets=50,witnesses=len(paths),finitePaths=sum(p['hasUnrestrictedFiniteAttachment']for p in paths),withinEndpointHeight=sum(p.get('passesExistingEndpointHeight',False)for p in paths),maximumResidualM=max(p.get('maximumResidualM',0)for p in paths),maximumRiseM=max(p.get('riseAboveEndpointsM',0)for p in paths),failedWitnesses=[p['witness']for p in paths if not p.get('passesExistingEndpointHeight',False)],intercomponentJoins=0));print({k:v for k,v in records[-1].items()if k!='failedWitnesses'},flush=True)
 result=dict(uids=[UID,'landsd/234188:0'],sourceSHA256ByUid=fresh['sourceSHA256ByUid'],rows=records,allWitnessesAttachedWithinEndpointHeight=all(r['witnesses']==r['finitePaths']==r['withinEndpointHeight']==200 for r in records),sourceGeometryChanges=0,physicalAcceptance=False,sourceRoleAccepted=False,installationApproved=False,publication=False,qualification='All three vertices and centroid of every50compound-flagged facet have explicit source-owned paths or retained failures. Existing exact-shared-edge-only graph, positive finite original podium terminals,1mm incidence and zero extra rise gate unchanged. No intercomponent joins or arbitrary root. These finite witnesses do not alone prove architectural role, full-facet support or engineering adequacy.')
 save(out/'summary.json',result);module('ocean_upper_buried_attachment_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'all-upper-compound-facet-vertices-centroids-to-original-podium-v1',refs,result)
if __name__=='__main__':main()

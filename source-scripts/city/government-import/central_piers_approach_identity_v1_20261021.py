"""Exact source-specific pier approach extent review; no physical exemptions."""
from pathlib import Path
from copy import deepcopy
import uuid,numpy as np,shapely
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-central-piers-approach-identity-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/213352:0','landsd/285475:0'];EXTENT={'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent'}
def compose(raw,tri,form,binding):
 assert raw['uid']==form['uid']==binding['uid'] and raw['sourceSHA256']==binding['sourceSHA256']
 assert digest(np.asarray(tri,dtype='<f8').tobytes())==raw['worldTrianglesSHA256']==binding['worldSHA256']
 foot=shapely.Polygon(form['rings'][0],form['rings'][1:]);dist=shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),foot).reshape(-1,3)
 assert np.flatnonzero(dist.max(1)>10).tolist()==binding['farFaceIds']
 assert raw['originalOwnership']['sourceGraphVerified']
 assert raw['freshCurrentIdentity']['targetCoveredBySourceProjection']>=.95
 assert raw['freshCurrentIdentity']['sourceExcessCoveredByUnrelatedFormsM2']<=1
 assert EXTENT <= set(raw['reasons'])
 out=deepcopy(raw);out.update(rawIdentityRetained=deepcopy(raw),policy='exact-central-pier7-pier8-original-landward-approach-extent-v1',sourceSpecificExtentFaceIds=binding['farFaceIds'],physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,physicalSupportExemption=False,reviewer='Codex ROOT',usesAISourceInterpretation=True,aiGeometryModelling=False,qualification='Only the exact original landward approach-platform faces are interpreted. ROOT inspected full original plan/elevations, official TD2018 location plan and independently georeferenced government seawall/steps/pedestrian/footbridge overlay. Low source extensions correspond to the mapped approach infrastructure. No surveyed vertical registration, engineering or physical exemption. All original faces and raw extent measurements retained.')
 out['reasons']=[r for r in raw['reasons']if r not in EXTENT];out['passed']=not out['reasons'];out['proof']={k:out['passed']for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']}
 return out

def main():
 assert not DOC.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];refs=[Path(__file__)];pins={}
 try:
  def take(n,p):
   _,ps=authenticate(BASE/n);k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([BASE/n/'result.json',p]);return read(p)
  pn='government-xl-central-piers-primary-plan-v1-20261021';bindings=take(pn,BASE/pn/'source-bindings.json')['rows']
  for n,f in [(pn,'source-extent-views.png'),(pn,'central-pier8-plan.png'),(pn,'provenance.json'),('government-xl-central-piers-vector-overlay-v1-20261021','approach-overlay.png'),('government-xl-central-piers-vector-overlay-v1-20261021','summary.json')]:
   _,ps=authenticate(BASE/n);p=BASE/n/f;k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([BASE/n/'result.json',p])
  sn='government-xl-next-twenty-current-terrain-v6-20261021';rows=take(sn,BASE/sn/'selection.json.gz')['rows'];final=module('pier_identity_context',HERE/'xl-final-script-pass.py');results=[];tests=[]
  for uid in UIDS:
   row=next(r for r in rows if r['uid']==uid);binding=next(r for r in bindings if r['uid']==uid);p=ROOT/row['candidate']['path'];assert digest(p.read_bytes())==binding['sourceSHA256'];refs.append(p);tri=decode_original_world_triangles(p.read_bytes());lo=tri.min((0,1));hi=tri.max((0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);form=next(b for b,_,_ in forms if b['uid']==uid);assert form==row['source']['building'];tiles={t:digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in forms};context=dict(sourceSHA256=row['sourceSHA256'],identity=final.identity_context(row,tri,forms),neighbourTileHashes=tiles)
   raw=verify_files(row,context,LOCAL/uid.split('/')[1]);out=compose(raw,tri,form,binding);save(DOC/(uid.split('/')[1]+'.json'),out);results.append(dict(uid=uid,passed=out['passed'],reasons=out['reasons']))
   for name in ['source','world','faces']:
    bad=deepcopy(binding)
    if name=='source':bad['sourceSHA256']='bad'
    elif name=='world':bad['worldSHA256']='bad'
    else:bad['farFaceIds']=bad['farFaceIds'][:-1]
    try:compose(raw,tri,form,bad)
    except AssertionError:tests.append(dict(uid=uid,case=name,rejected=True))
    else:raise AssertionError('invalid binding accepted')
   bad=deepcopy(raw);bad['reasons'].append('independent-failure');assert not compose(bad,tri,form,binding)['passed'];tests.append(dict(uid=uid,case='independent-failure',retained=True))
   for t,h in tiles.items():assert digest((ROOT/'3d-viewer'/t).read_bytes())==h;refs.append(ROOT/'3d-viewer'/t)
  for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
  assert reservations.owns(lease);save(DOC/'checks.json',tests);save(DOC/'summary.json',dict(rows=results,installationApproved=False))
  refs.extend(p for p in LOCAL.rglob('*')if p.is_file());refs.extend([HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-final-script-pass.py'])
  r=module('pier_approach_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-landward-approach-identity-review',list(dict.fromkeys(refs)),dict(uids=UIDS,rows=results,installationApproved=False,sourceGeometryChanges=0));print(dict(jobId=r['jobId'],rows=results),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()

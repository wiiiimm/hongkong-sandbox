"""Complete final-terrain podium surface context; no acceptance or geometry changes."""
from pathlib import Path
import json,uuid,numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from original_face_ground_crossing_v2_20261009 import face_ground_context
from original_degenerate_ground_context_20261009 import degenerate_ground_context
from exact_projection_coverage_fallback_context_20261009 import apply_exact_coverage
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-wave-verdant-podium-grade-context-v3-20261018';DOC=BASE/BATCH
UIDS=['landsd/301560:0','landsd/304885:0']
def main():
 assert not DOC.exists();prior=BASE/'government-xl-wave-verdant-retained-contacts-v3-20261018/result.json';r=read(prior);pins={};refs=[Path(__file__),prior]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 sources={}
 for n in ['government-xl-wave-all-original-support-distance-v1-20261017','government-xl-wave-verdant-podium-support-v1-20261017']:
  p=BASE/n/'support-inputs.json';refs.append(p);sources.update({x['uid']:x for x in read(p)['sources']})
 attrs={}
 for n in ['government-xl-wave-actual-render-attributes-v1-20261017','government-xl-wave-verdant-actual-render-attributes-v1-20261017']:
  p=BASE/n/'attributes.json.gz';refs.append(p);attrs.update({x['uid']:x for x in read(p)['rows']})
 gp=BASE/'government-xl-wave-verdant-current-ground-capture-v5-20261018/after-ground.json.gz';refs.append(gp);ground=np.asarray(read(gp)['completeRelevantDrawnTriplets'],dtype='<f8').reshape(-1,3,3);ground_sha=digest(ground.tobytes());polygons=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10;excluded=int((~valid).sum());ground,polygons=ground[valid],polygons[valid];tree=shapely.STRtree(polygons)
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation'];save(DOC/'lease.json',json.loads(json.dumps(lease,default=str)))
 summary=[];seen={}
 try:
  for uid in UIDS:
   row=sources[uid];raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];a=attrs[uid];assert a['sourceSHA256']==row['sourceSHA256'];idx=np.asarray(a['completeOriginalIndex']).reshape(-1,3)
   worlds={'original':decode_original_world_triangles(raw)}
   for mode,key in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(a[key]).reshape(-1,3)[idx]
   for mode,tri in worlds.items():
    tri=np.asarray(tri,dtype='<f8');assert len(tri)==row['native']['model']['triangles'];sha=digest(tri.tobytes());key=(uid,sha);contexts=[];reuse=seen.get(key)
    normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);lengths=np.linalg.norm(normals,axis=1);ratio=np.divide(normals[:,1],lengths,out=np.zeros(len(tri)),where=lengths>0)
    if reuse:contexts=read(DOC/reuse)['faces']
    else:
     for i,t in enumerate(tri):
      c=face_ground_context(t,ground,polygons,tree)if lengths[i]>0 else degenerate_ground_context(t,ground,polygons,tree);c=apply_exact_coverage(c,t,ground);contexts.append(dict(c,sourceFace=i,normalYRatio=float(ratio[i])if lengths[i]>0 else None))
      if i%500==0:print(dict(uid=uid,mode=mode,checked=i,total=len(tri)),flush=True)
    negative=[c['sourceFace']for c in contexts if c['minimum']and c['minimum']['minimumGapM']<-.5];upward=[i for i in negative if ratio[i]>.25];unexposed=[i for i in negative if contexts[i].get('maximumObservedGapM')is None or contexts[i]['maximumObservedGapM']<0]
    name=uid.split('/')[1]+'-'+mode+'.json.gz';out=dict(uid=uid,mode=mode,sourceSHA256=row['sourceSHA256'],completeWorldSHA256=sha,completeDrawnGroundSHA256=ground_sha,wholeSourceFaces=len(tri),faces=contexts,continuousNegativeFaceIds=negative,negativeUpwardFaceIds=upward,negativeWithoutExposedWitness=unexposed,uncoveredFaces=[i for i,c in enumerate(contexts)if not c['groundProjectionCovered']],heightIndexExcludedGroundFaces=excluded,reusedIdenticalWorldFrom=reuse,installationApproved=False)
    save(DOC/name,out);seen[key]=name;summary.append({k:v for k,v in out.items()if k!='faces'});save(DOC/'partial-summary.json',dict(rows=summary,fullAcceptance=False));print(dict(uid=uid,mode=mode,negative=len(negative),upward=len(upward),withoutExposedWitness=len(unexposed),uncovered=len(out['uncoveredFaces'])),flush=True)
  save(DOC/'summary.json',dict(rows=summary,fullAcceptance=False,qualification='Complete final drawn-terrain context, all authored source faces, four coordinate modes. Continuous minima are diagnostic floating intersection arithmetic with explicit complete coverage fallback. No generic threshold changed; no installation approval.'))
  for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
  assert reservations.owns(lease)
  refs.extend(HERE/n for n in ['original_face_ground_crossing_v2_20261009.py','original_face_ground_crossing_20261009.py','original_degenerate_ground_context_20261009.py','exact_projection_coverage_fallback_context_20261009.py','exact_original_projection_coverage_20261009.py','exact_packed_world_geometry_20261009.py'])
  out=module('wave_final_podium_context',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-original-podium-final-terrain-complete-face-context-v3',list(set(refs)),dict(uids=UIDS,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

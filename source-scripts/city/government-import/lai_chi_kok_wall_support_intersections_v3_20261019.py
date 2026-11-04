"""Exact finite facet contacts along original wall paths; source geometry unchanged."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-wall-support-intersections-v3-20261019';DOC=BASE/BATCH;PATHS=BASE/'government-xl-lai-chi-kok-component-wall-paths-v1-20261019';ATTR=BASE/'government-xl-lai-chi-kok-eight-render-attributes-v1-20261019';CAP=BASE/'government-xl-lai-chi-kok-eight-runtime-v4-20261019'
def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'exact_original_shell_intersections_20261009.py'];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [PATHS,CAP]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 sources=read(ATTR/'selection.json.gz')['rows'];captures={r['uid']:r for r in read(ATTR/'attributes.json.gz')['rows']};worlds={'original':{r['uid']:decode_original_world_triangles((ROOT/r['candidate']['path']).read_bytes())for r in sources}}
 for mode,field in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]={u:np.asarray(a[field],dtype='<f8').reshape(-1,3)[np.asarray(a['completeOriginalIndex']).reshape(-1,3)]for u,a in captures.items()}
 runtime=read(HERE/'local'/CAP.name/'runtime-geometry.json.gz')['rows'];ground=np.asarray(runtime[0]['drawnGroundGeometry']).reshape(-1,3,3);summaries=[]
 for mode,world in worlds.items():
  support=np.concatenate([ground,world['landsd/281463:0']]);lo=support.min(1);hi=support.max(1);support_cache={};norm=np.cross(support[:,1]-support[:,0],support[:,2]-support[:,0]);support_valid=np.any(norm!=0,axis=1)
  for row in sources[1:]:
   uid=row['uid'];tri=world[uid];proof=read(PATHS/(uid.split('/')[1]+'-'+mode+'.json'))['proof'];assert digest(np.asarray(tri,dtype='<f8').tobytes())==proof['coordinateSHA256'];contacts={};out=[];tests=0
   for path in proof['rows']:
    hits=[]
    for fi in path['sourceSharedEdgePath']:
     if fi not in contacts:
      face=tri[fi];a=face.min(0);b=face.max(0);candidates=np.flatnonzero(support_valid&np.all(hi>=a,axis=1)&np.all(lo<=b,axis=1));rf=rational_face(face);found=[]
      for sj in candidates:
       j=int(sj)
       if j not in support_cache:support_cache[j]=rational_face(support[j])
       points=intersection_points(rf,support_cache[j]);tests+=1
       if len(points)>1:found.append(dict(supportFace=j,supportKind='terrain'if j<len(ground)else'original-platform',points=[[float(v)for v in p]for p in sorted(points)]))
      contacts[fi]=found
     if contacts[fi]:hits.append(dict(sourceFace=fi,contacts=contacts[fi]))
    out.append(dict(affectedFace=path['faceId'],sourcePath=path['sourceSharedEdgePath'],positiveDimensionalSupportContacts=hits,hasContact=bool(hits)))
   summary=dict(uid=uid,mode=mode,affected=len(out),withFiniteSupportContact=sum(r['hasContact']for r in out),exactFacetPairTests=tests,collapsedSupportFacesExcluded=int((~support_valid).sum()),installationApproved=False);summaries.append(summary);save(DOC/(uid.split('/')[1]+'-'+mode+'.json'),dict(summary=summary,paths=out));print(summary,flush=True)
 save(DOC/'summary.json',dict(rows=summaries,qualification='Exact positive-dimensional contacts on the recorded original shared-edge paths; no replacement of rim, exposure or acceptance tests.',installationApproved=False))
 module('wall_contact_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-connected-wall-exact-finite-support-contacts',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in sources],rows=summaries,installationApproved=False))
if __name__=='__main__':main()

"""Complete finite source/ground crossing evidence; no role acceptance or publication."""
from pathlib import Path
import numpy as np,shapely,json,sys,uuid,subprocess
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from original_face_ground_crossing_v2_20261009 import face_ground_context
from original_degenerate_ground_context_20261009 import degenerate_ground_context
from exact_projection_coverage_fallback_context_20261009 import apply_exact_coverage
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-central-library-full-grade-context-v1-20261019';DOC=BASE/BATCH
CAP=BASE/'government-xl-central-library-actual-render-attributes-v2-20261019';PHYS=BASE/'government-xl-central-library-private-ground-v1-20261019'
def owned():
 lease=read(HERE/'local'/BATCH/'reservation.json');assert reservations.owns(lease)
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 for d in [CAP,PHYS]:
  r=read(d/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
  refs.append(d/'result.json')
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 from exact_packed_world_geometry_20261009 import decode_original_world_triangles
 row=read(PHYS/'selection.json.gz')['rows'][0];uid=row['uid'];raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];worlds={'original':{uid:decode_original_world_triangles(raw)}}
 attrs=read(CAP/'attributes.json.gz')['rows'];assert len(attrs)==1 and attrs[0]['uid']==uid;attr=attrs[0]
 for mode,field in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]={uid:np.asarray(attr[field],dtype='<f8').reshape(-1,3)[np.asarray(attr['completeOriginalIndex']).reshape(-1,3)]}
 rtpath=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';runtime={g['uid']:g for g in read(rtpath)['rows']};summary=[];seen={}
 for uid in ['landsd/232240:0']:
  g=runtime[uid];ground=np.asarray(g['drawnGroundGeometry'],float).reshape(-1,3,3);polygons=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10;ground,polygons=ground[valid],polygons[valid];tree=shapely.STRtree(polygons)
  for mode,values in worlds.items():
   tri=np.asarray(values[uid],dtype='<f8');key=(uid,digest(tri.tobytes()));reuse=seen.get(key);contexts=[]
   normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normal,axis=1);ratio=np.divide(normal[:,1],length,out=np.zeros(len(tri)),where=length>0)
   if reuse:contexts=read(DOC/reuse)['faces']
   else:
    for i,t in enumerate(tri):
     c=face_ground_context(t,ground,polygons,tree)if length[i]>0 else degenerate_ground_context(t,ground,polygons,tree);c=apply_exact_coverage(c,t,ground);contexts.append(dict(c,sourceFace=i,normalYRatio=float(ratio[i])if length[i]>0 else None))
     if i%200==0:print(dict(uid=uid,mode=mode,checked=i,total=len(tri)),flush=True)
   negative=[c['sourceFace']for c in contexts if c['minimum']and c['minimum']['minimumGapM']<-.5];upward=[i for i in negative if ratio[i]>.25];unexposed=[i for i in negative if contexts[i].get('maximumObservedGapM')is None or contexts[i]['maximumObservedGapM']<0]
   name=uid.split('/')[1]+'-'+mode+'.json.gz';entry=dict(uid=uid,mode=mode,sourceSHA256=g['sourceSHA256'],completeWorldSHA256=key[1],completeDrawnGroundSHA256=digest(np.asarray(g['drawnGroundGeometry'],dtype='<f8').tobytes()),wholeSourceFaces=len(tri),faces=contexts,continuousNegativeFaceIds=negative,negativeUpwardFaceIds=upward,negativeWithoutExposedWitness=unexposed,uncoveredFaces=[i for i,c in enumerate(contexts)if not c['groundProjectionCovered']],reusedIdenticalWorldFrom=reuse,installationApproved=False,qualification='Continuous pair minima and observed exposed witnesses only. No new structural-root requirement, no source-role acceptance and no tolerance change. Ground minimum helper is diagnostic floating intersection arithmetic; retained exact-coverage fallback is explicit.')
   save(DOC/name,entry);seen[key]=name;summary.append({k:v for k,v in entry.items()if k not in ['faces','qualification']});print({k:entry[k]for k in ['uid','mode','continuousNegativeFaceIds','negativeUpwardFaceIds','negativeWithoutExposedWitness','uncoveredFaces']},flush=True)
 save(DOC/'summary.json',dict(rows=summary,fullAcceptance=False));refs.extend([rtpath,HERE/'original_face_ground_crossing_v2_20261009.py',HERE/'original_face_ground_crossing_20261009.py',HERE/'original_degenerate_ground_context_20261009.py',HERE/'exact_projection_coverage_fallback_context_20261009.py',HERE/'exact_original_projection_coverage_20261009.py']);out=module('namcheong244683_grade_context_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'all-original-podium-community-finite-ground-context-four-modes-v1',list(set(refs)),dict(uids=['landsd/232240:0'],summary=summary,fullAcceptance=False));print(out['jobId'],flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:landsd/232240:0','terrain-patch:landsd/232240:0'],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];path=HERE/'local'/BATCH/'reservation.json';save(path,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()


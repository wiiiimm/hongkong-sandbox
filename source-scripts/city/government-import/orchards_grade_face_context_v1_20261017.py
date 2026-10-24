"""Complete finite source/ground crossing evidence; no role acceptance or publication."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from original_face_ground_crossing_v2_20261009 import face_ground_context
from original_degenerate_ground_context_20261009 import degenerate_ground_context
from exact_projection_coverage_fallback_context_20261009 import apply_exact_coverage
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-orchards-grade-face-context-v1-20261017';DOC=BASE/BATCH
CAP=BASE/'government-xl-orchards-assembly-four-world-v1-20261017';PHYS=BASE/'government-xl-orchards-assembly-terrain-candidate-v1-20261017'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 for d in [CAP,PHYS]:
  r=read(d/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
  refs.append(d/'result.json')
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 worlds=read(CAP/'world-triangles.json.gz');rtpath=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';runtime={g['uid']:g for g in read(rtpath)['rows']};summary=[];seen={}
 for uid in ['landsd/233002:0','landsd/256434:0']:
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
 save(DOC/'summary.json',dict(rows=summary,fullAcceptance=False));refs.extend([rtpath,HERE/'original_face_ground_crossing_v2_20261009.py',HERE/'original_face_ground_crossing_20261009.py',HERE/'original_degenerate_ground_context_20261009.py',HERE/'exact_projection_coverage_fallback_context_20261009.py',HERE/'exact_original_projection_coverage_20261009.py']);out=module('orchards_grade_context_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'all-original-podium-community-finite-ground-context-four-modes-v1',list(set(refs)),dict(uids=['landsd/233002:0','landsd/256434:0'],summary=summary,fullAcceptance=False));print(out['jobId'],flush=True)
if __name__=='__main__':main()

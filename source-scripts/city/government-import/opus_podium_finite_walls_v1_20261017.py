"""Complete original podium finite clearance and exact coplanar wall diagnosis."""
from pathlib import Path
from fractions import Fraction
import uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_original_paired_finite_clearance_v3_20261011 import verify
from original_bound_facet_wall_context_v2_20261010 import exposure_at_vertex
from original_bound_facet_wall_context_20261010 import down
from original_coplanar_exterior_continuation_20261009 import diagnose
BASE=ROOT/'docs/astra-city/government-import';WORLD=BASE/'government-xl-opus-four-world-contacts-v1-20261017';GROUND=BASE/'government-xl-opus-preserved-neighbours-v1-20261016';BATCH='government-xl-opus-podium-finite-walls-v1-20261017';DOC=BASE/BATCH;UID='landsd/248432:0'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [WORLD,GROUND]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for x in r['evidenceRefs']:pins.setdefault(x['path'],set()).add(x['sha256'])
 def consume(p):
  assert digest(p.read_bytes()) in pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 worlds=consume(WORLD/'world-triangles.json.gz');gpath=HERE/'local'/GROUND.name/'runtime-geometry.json.gz';ground=np.concatenate([np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3) for g in consume(gpath)['rows']]);cache={};summaries=[]
 claim=reservations.claim('opus-finite-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir()
  for mode,w in worlds.items():
   tri=np.array(w[UID]);assert len(tri)==967;sha=digest(tri.tobytes());reused=None
   if sha in cache:reused,faces,ctx,continuation=cache[sha]
   else:
    faces=[];ctx=[]
    for i,t in enumerate(tri):
     proof=verify(t,ground);faces.append(dict(sourceFace=i,proof=proof));bound=Fraction(proof['exactCertifiedLowerClearanceM']);covered=proof['groundProjectionCovered'];exposure=None
     if covered:exposure=exposure_at_vertex(t[int(np.argmax(t[:,1]))],ground)
     ctx.append(dict(sourceFace=i,groundProjectionCovered=covered,minimum=dict(minimumGapM=down(bound)),maximumObservedGapM=exposure['maximumObservedGapM'] if exposure else None,exactVertexExposure=exposure))
     if i%50==0:assert reservations.heartbeat(lease)['ok'];print(mode,i,len(tri),flush=True)
    normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normal,axis=1);affected=[i for i,c in enumerate(ctx) if c['groundProjectionCovered'] and c['maximumObservedGapM'] is not None and c['maximumObservedGapM']<=0 and c['minimum']['minimumGapM']<-.5 and length[i]>0 and abs(normal[i,1]/length[i])<=.25]
    continuation=diagnose(tri,ctx,affected);cache[sha]=(mode,faces,ctx,continuation)
   save(DOC/(mode+'.json.gz'),dict(worldSHA256=sha,groundSHA256=digest(ground.tobytes()),reusedByteIdenticalWorld=reused,faces=faces,contexts=ctx,continuation=continuation,fullAcceptance=False))
   summaries.append(dict(mode=mode,sourceFaces=len(faces),uncovered=[r['sourceFace'] for r in faces if not r['proof']['groundProjectionCovered']],ordinaryFailures=[r['sourceFace'] for r in faces if not r['proof']['existingOrdinaryClearanceBoundProved']],continuation=continuation));print(mode,'complete',flush=True)
  save(DOC/'summary.json',dict(rows=summaries,fullAcceptance=False,newlyInstalled=0))
  refs += [HERE/n for n in ['exact_original_paired_finite_clearance_v3_20261011.py','exact_original_paired_finite_clearance_v2_20261010.py','exact_original_triangle_pair_column_gap_20261010.py','exact_original_projection_coverage_v2_20261010.py','original_bound_facet_wall_context_v2_20261010.py','original_bound_facet_wall_context_20261010.py','original_coplanar_exterior_continuation_20261009.py','exact_original_shell_intersections_20261009.py']]
  out=module('opus_finite_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-opus-complete-podium-finite-wall-diagnostic-v1',refs,dict(uids=[UID],fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId']),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

"""Refine only coarse unproved bounds; all earlier raw proofs stay immutable."""
import argparse,importlib.util,json,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_paired_finite_clearance_20261010 import verify
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--physical',required=True);p.add_argument('--clearance',required=True);p.add_argument('--batch',required=True);a=p.parse_args();physical=ROOT/a.physical;old=ROOT/a.clearance;doc=ROOT/'docs/astra-city/government-import'/a.batch;assert not doc.exists();prior=read(old/'diagnostic.json.gz');receipt=read(old/'result.json');runtime_path=HERE/'local'/physical.name/'runtime-geometry.json.gz';runtime=read(runtime_path);selection=read(physical/'selection.json.gz')
 with connect() as con:
  con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for r in receipt['evidenceRefs']:assert ref(ROOT/r['path'])==r
 refs=[ref(p) for p in [Path(__file__),old/'diagnostic.json.gz',old/'result.json',runtime_path,physical/'selection.json.gz',HERE/'exact_original_paired_finite_clearance_20261010.py',HERE/'test_exact_original_paired_finite_clearance_20261010.py']];results=[]
 claim=reservations.claim('conservative-clearance-refinement-'+str(uuid.uuid4()),['immutable-source-proof:'+a.batch],batch=a.batch,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  for row,cached in zip(selection['rows'],prior['rows']):
   asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']==cached['sourceSHA256'];tri=decode_original_world_triangles(raw);r=next(r for r in runtime['rows'] if r['uid']==row['uid']);world=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];ground=np.asarray(r['drawnGroundGeometry']).reshape(-1,3,3)
   assert digest(tri.tobytes())==cached['completeOriginalWorldSHA256'] and digest(world.tobytes())==cached['completeActualRenderedWorldSHA256'] and digest(ground.tobytes())==cached['completeGroundSHA256'] and len(cached['allFaces'])==len(tri)
   final=[]
   for i,c in enumerate(cached['allFaces']):
    assert c['sourceFace']==i and c['coarseOriginalAndRenderedProofVerbatim']['completeOriginal']['sourceFaceSHA256']==digest(tri[i].tobytes()) and c['coarseOriginalAndRenderedProofVerbatim']['actualRendered']['sourceFaceSHA256']==digest(world[i].tobytes())
    original=None if c['completeOriginalBoundProved'] else verify(tri[i],ground);rendered=None if c['completeActualRenderedBoundProved'] else verify(world[i],ground)
    final.append(dict(sourceFace=i,priorClippedConservativeProofVerbatim=c,pairedExactOriginalFiniteBound=original,pairedExactActualRenderedFiniteBound=rendered,completeOriginalBoundProved=c['completeOriginalBoundProved'] or bool(original and original['existingOrdinaryClearanceBoundProved']),completeActualRenderedBoundProved=c['completeActualRenderedBoundProved'] or bool(rendered and rendered['existingOrdinaryClearanceBoundProved'])))
    if i%300==0:assert reservations.heartbeat(lease)['ok']
   results.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],completeOriginalFaces=len(tri),completeOriginalWorldSHA256=digest(tri.tobytes()),completeActualRenderedWorldSHA256=digest(world.tobytes()),completeGroundSHA256=digest(ground.tobytes()),allFaces=final,unprovedOriginalFaces=[r['sourceFace'] for r in final if not r['completeOriginalBoundProved']],unprovedActualRenderedFaces=[r['sourceFace'] for r in final if not r['completeActualRenderedBoundProved']]));refs.append(ref(asset))
  result=dict(rows=results,allWholeOriginalAndRenderedBoundsProved=all(not r['unprovedOriginalFaces'] and not r['unprovedActualRenderedFaces'] for r in results),rawPriorDiagnosticChanged=False,earlierCoarseBoundFailuresPreserved=True,pairedClippedSourceHeights=True,sourceGeometryChanges=0,fullAcceptance=False,installationApproved=False,evidenceRefs=refs);save(doc/'diagnostic.json.gz',result)
  spec=importlib.util.spec_from_file_location('strict_clipped_clearance_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(a.batch,'complete-original-rendered-paired-exact-finite-clearance-v1',[ROOT/r['path'] for r in refs],dict(uids=[r['uid'] for r in results],completeOriginalFaces=sum(r['completeOriginalFaces'] for r in results),allWholeOriginalAndRenderedBoundsProved=result['allWholeOriginalAndRenderedBoundsProved'],unprovedOriginal={r['uid']:r['unprovedOriginalFaces'] for r in results},unprovedRendered={r['uid']:r['unprovedActualRenderedFaces'] for r in results},rawPriorDiagnosticChanged=False,fullAcceptance=False))
  print(json.dumps(dict(allWholeBoundsProved=result['allWholeOriginalAndRenderedBoundsProved'],unprovedOriginal={r['uid']:r['unprovedOriginalFaces'] for r in results},unprovedRendered={r['uid']:r['unprovedActualRenderedFaces'] for r in results})),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()

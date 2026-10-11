"""All35,006 current original/rendered faces, immutable podium reuse + upper18."""
import importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_paired_finite_clearance_v2_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261010-festival-pair-finite-column-v1';DOC=BASE/BATCH
COARSE=BASE/'xl-terrain-recovery-20261010-festival-pair-current-finite-clearance-v1'
PODIUM=BASE/'xl-terrain-recovery-20261010-festival-collapsed-column-current-v1'
PHYS=BASE/'government-xl-terrain-recovery-festival-pair-original-terrain-current-v1-20261010'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();old=read(COARSE/'diagnostic.json.gz');pod=read(PODIUM/'diagnostic.json.gz')
 for folder in [COARSE,PODIUM,PHYS]:
  receipt=read(folder/'result.json')
  with connect() as con:
   con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for r in receipt['evidenceRefs']:assert ref(ROOT/r['path'])==r
 runtime_path=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';runtime=read(runtime_path);selection=read(PHYS/'selection.json.gz');results=[];assets=[]
 for row in selection['rows']:
  asset=ROOT/row['candidate']['path'];assets.append(asset);raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];tri=decode_original_world_triangles(raw);r=next(r for r in runtime['rows'] if r['uid']==row['uid']);world=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];ground=np.asarray(r['drawnGroundGeometry']).reshape(-1,3,3);cached=next(r for r in old['rows'] if r['uid']==row['uid']);assert digest(tri.tobytes())==cached['completeOriginalWorldSHA256'] and digest(world.tobytes())==cached['completeActualRenderedWorldSHA256'] and digest(ground.tobytes())==cached['completeGroundSHA256']
  if row['uid']=='landsd/91827:0':
   assert row['sourceSHA256']==pod['sourceSHA256'] and cached['completeOriginalWorldSHA256']==pod['completeOriginalWorldSHA256'] and cached['completeActualRenderedWorldSHA256']==pod['completeActualRenderedWorldSHA256'] and cached['completeGroundSHA256']==pod['completeGroundSHA256'];final=pod['allFaces'];reuse=ref(PODIUM/'diagnostic.json.gz')
  else:
   final=[];reuse=None
   for i,c in enumerate(cached['allFaces']):
    assert c['sourceFace']==i and c['completeOriginal']['sourceFaceSHA256']==digest(tri[i].tobytes()) and c['actualRendered']['sourceFaceSHA256']==digest(world[i].tobytes());a=None if c['completeOriginal']['existingOrdinaryClearanceBoundProved'] else verify(tri[i],ground);b=None if c['actualRendered']['existingOrdinaryClearanceBoundProved'] else verify(world[i],ground);final.append(dict(sourceFace=i,priorCoarseBoundProofVerbatim=c,exactOriginalColumnRefinement=a,exactActualRenderedColumnRefinement=b,completeOriginalBoundProved=c['completeOriginal']['existingOrdinaryClearanceBoundProved'] or bool(a and a['existingOrdinaryClearanceBoundProved']),completeActualRenderedBoundProved=c['actualRendered']['existingOrdinaryClearanceBoundProved'] or bool(b and b['existingOrdinaryClearanceBoundProved'])))
    if a or b:print(json.dumps(dict(uid=row['uid'],face=i,original=float(a['exactCertifiedLowerClearanceM'].split('/')[0])/float(a['exactCertifiedLowerClearanceM'].split('/')[1]) if a and '/' in a['exactCertifiedLowerClearanceM'] else None,passed=final[-1]['completeOriginalBoundProved'] and final[-1]['completeActualRenderedBoundProved'])),flush=True)
  assert len(final)==len(tri) and [r['sourceFace'] for r in final]==list(range(len(tri)));results.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],completeOriginalFaces=len(tri),completeOriginalWorldSHA256=digest(tri.tobytes()),completeActualRenderedWorldSHA256=digest(world.tobytes()),completeGroundSHA256=digest(ground.tobytes()),allFaces=final,reusedImmutableProof=reuse,unprovedOriginalFaces=[r['sourceFace'] for r in final if not r['completeOriginalBoundProved']],unprovedActualRenderedFaces=[r['sourceFace'] for r in final if not r['completeActualRenderedBoundProved']]))
 refs=[ref(p) for p in [Path(__file__),COARSE/'diagnostic.json.gz',COARSE/'result.json',PODIUM/'diagnostic.json.gz',PODIUM/'result.json',PHYS/'result.json',PHYS/'selection.json.gz',runtime_path,*assets,HERE/'exact_original_triangle_pair_column_gap_20261010.py',HERE/'exact_original_paired_finite_clearance_v2_20261010.py',HERE/'test_exact_original_triangle_pair_column_gap_20261010.py',HERE/'test_exact_original_triangle_pair_column_gap_actual_20261010.py',HERE/'exact_original_paired_finite_clearance_20261010.py',HERE/'exact_original_projection_coverage_v2_20261010.py']];save(DOC/'diagnostic.json.gz',dict(uids=[r['uid'] for r in results],rows=results,rawPriorFailuresRetained=True,sourceGeometryChanges=0,fullAcceptance=False,evidenceRefs=refs));spec=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'all-original-rendered-finite-column-clearance-v1',[ROOT/r['path'] for r in refs],dict(uids=[r['uid'] for r in results],completeOriginalFaces=sum(r['completeOriginalFaces'] for r in results),unprovedOriginal={r['uid']:r['unprovedOriginalFaces'] for r in results},unprovedRendered={r['uid']:r['unprovedActualRenderedFaces'] for r in results},fullAcceptance=False));print([(r['uid'],r['unprovedOriginalFaces'],r['unprovedActualRenderedFaces']) for r in results],flush=True)
if __name__=='__main__':main()

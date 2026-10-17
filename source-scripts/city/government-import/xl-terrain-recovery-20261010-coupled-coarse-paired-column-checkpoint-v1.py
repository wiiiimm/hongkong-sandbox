"""Fresh exact paired finite refinement, complete rows and resumable face work."""
import argparse,importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_paired_finite_clearance_v2_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--coarse',required=True);p.add_argument('--physical',required=True);p.add_argument('--batch',required=True);a=p.parse_args();doc=BASE/a.batch;assert not doc.exists();coarse=ROOT/a.coarse;physical=ROOT/a.physical;old=read(coarse/'diagnostic.json.gz');receipts=[]
 for folder in [coarse,physical]:
  receipt=read(folder/'result.json')
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  receipts.append(ref(folder/'result.json'))
 assert ref(coarse/'diagnostic.json.gz') in read(coarse/'result.json')['evidenceRefs']
 runtime_path=HERE/'local'/physical.name/'runtime-geometry.json.gz';runtime=read(runtime_path);selection=read(physical/'selection.json.gz');results=[];assets=[]
 for row in selection['rows']:
  asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];tri=decode_original_world_triangles(raw);r=next(r for r in runtime['rows'] if r['uid']==row['uid']);world=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];ground=np.asarray(r['drawnGroundGeometry']).reshape(-1,3,3);cached=next(r for r in old['rows'] if r['uid']==row['uid']);assert cached['sourceSHA256']==row['sourceSHA256'] and digest(tri.tobytes())==cached['completeOriginalWorldSHA256'] and digest(world.tobytes())==cached['completeActualRenderedWorldSHA256'] and digest(ground.tobytes())==cached['completeGroundSHA256'];assets.append(asset)
  checkpoint=HERE/'local'/a.batch/(row['uid'].replace('/','-').replace(':','-')+'-paired-partial.json.gz');binding=dict(producer=ref(Path(__file__)),coarse=ref(coarse/'diagnostic.json.gz'),currentRuntime=ref(runtime_path),sourceSHA256=row['sourceSHA256'],worldSHA256=digest(tri.tobytes()),renderedSHA256=digest(world.tobytes()),groundSHA256=digest(ground.tobytes()),kernels=[ref(HERE/n) for n in ['exact_original_paired_finite_clearance_v2_20261010.py','exact_original_triangle_pair_column_gap_20261010.py','exact_original_paired_finite_clearance_20261010.py','exact_original_projection_coverage_v2_20261010.py']]);saved=read(checkpoint) if checkpoint.exists() else None;assert saved is None or saved['binding']==binding;refinements={} if saved is None else saved['refinements'];final=[];computed=0
  for i,c in enumerate(cached['allFaces']):
   assert c['sourceFace']==i and c['completeOriginal']['sourceFaceSHA256']==digest(tri[i].tobytes()) and c['actualRendered']['sourceFaceSHA256']==digest(world[i].tobytes());k=str(i)
   if k in refinements:aa,bb=refinements[k]
   else:
    aa=None if c['completeOriginal']['existingOrdinaryClearanceBoundProved'] else verify(tri[i],ground);bb=None if c['actualRendered']['existingOrdinaryClearanceBoundProved'] else aa if np.array_equal(tri[i],world[i]) else verify(world[i],ground)
    if aa is not None or bb is not None:
     refinements[k]=[aa,bb];computed+=1
     if computed%20==0:save(checkpoint,dict(binding=binding,refinements=refinements,complete=False));print(json.dumps(dict(uid=row['uid'],face=i,refinedFaces=len(refinements))),flush=True)
   final.append(dict(sourceFace=i,priorCoarseBoundProofVerbatim=c,exactOriginalColumnRefinement=aa,exactActualRenderedColumnRefinement=bb,completeOriginalBoundProved=c['completeOriginal']['existingOrdinaryClearanceBoundProved'] or bool(aa and aa['existingOrdinaryClearanceBoundProved']),completeActualRenderedBoundProved=c['actualRendered']['existingOrdinaryClearanceBoundProved'] or bool(bb and bb['existingOrdinaryClearanceBoundProved'])))
  save(checkpoint,dict(binding=binding,refinements=refinements,complete=True));assert len(final)==len(tri) and [v['sourceFace'] for v in final]==list(range(len(tri)));results.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],completeOriginalFaces=len(tri),completeOriginalWorldSHA256=digest(tri.tobytes()),completeActualRenderedWorldSHA256=digest(world.tobytes()),completeGroundSHA256=digest(ground.tobytes()),allFaces=final,unprovedOriginalFaces=[v['sourceFace'] for v in final if not v['completeOriginalBoundProved']],unprovedActualRenderedFaces=[v['sourceFace'] for v in final if not v['completeActualRenderedBoundProved']]))
 refs=receipts+[ref(p) for p in [Path(__file__),coarse/'diagnostic.json.gz',physical/'selection.json.gz',runtime_path,*assets,HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_paired_finite_clearance_v2_20261010.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py',HERE/'test_exact_original_triangle_pair_column_gap_20261010.py',HERE/'test_exact_original_triangle_pair_column_gap_actual_20261010.py',HERE/'exact_original_paired_finite_clearance_20261010.py',HERE/'exact_original_projection_coverage_v2_20261010.py']];save(doc/'diagnostic.json.gz',dict(uids=[r['uid'] for r in results],rows=results,rawPriorCoarseFailuresRetained=True,sourceGeometryChanges=0,fullAcceptance=False,evidenceRefs=refs));s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(a.batch,'all-current-original-rendered-exact-paired-finite-column-clearance-checkpoint-v1',[ROOT/r['path'] for r in refs],dict(uids=[r['uid'] for r in results],completeOriginalFaces=sum(r['completeOriginalFaces'] for r in results),unprovedOriginal={r['uid']:r['unprovedOriginalFaces'] for r in results},unprovedRendered={r['uid']:r['unprovedActualRenderedFaces'] for r in results},fullAcceptance=False));print([(r['uid'],r['unprovedOriginalFaces'],r['unprovedActualRenderedFaces']) for r in results],flush=True)
if __name__=='__main__':main()

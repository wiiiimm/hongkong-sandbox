"""Complete rational area/interval/point gap witnesses, immutable raw failures."""
import importlib.util,json,time,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_projected_uncovered_regions_20261010 import diagnose
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261010-festival-exact-gap-regions-v1';DOC=BASE/BATCH;CACHE=HERE/'local'/BATCH/'partial.json.gz'
FINITE=BASE/'xl-terrain-recovery-20261010-festival-pair-finite-column-v1';PHYS=BASE/'government-xl-terrain-recovery-festival-pair-original-terrain-current-v1-20261010'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();finite=read(FINITE/'diagnostic.json.gz');receipt=read(FINITE/'result.json')
 with connect() as con:
  con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for r in receipt['evidenceRefs']:assert ref(ROOT/r['path'])==r
 runtime_path=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';runtime=read(runtime_path);selection=read(PHYS/'selection.json.gz');inputs=[ref(p) for p in [Path(__file__),FINITE/'diagnostic.json.gz',FINITE/'result.json',PHYS/'selection.json.gz',PHYS/'result.json',runtime_path,HERE/'exact_original_projected_uncovered_regions_20261010.py',HERE/'test_exact_original_projected_uncovered_regions_20261010.py',HERE/'exact_original_projection_coverage_v2_20261010.py']];binding=digest(json.dumps(inputs,sort_keys=True,separators=(',',':')).encode());done=[];cache={}
 if CACHE.exists():
  saved=read(CACHE);assert saved['binding']==binding;done=saved['rows'];cache=saved['projectedRegionsCache']
 claim=reservations.claim('festival-exact-gaps-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  for row in selection['rows']:
   asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];tri=decode_original_world_triangles(raw);r=next(r for r in runtime['rows'] if r['uid']==row['uid']);world=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];ground=np.asarray(r['drawnGroundGeometry']).reshape(-1,3,3);cached=next(r for r in finite['rows'] if r['uid']==row['uid']);assert digest(tri.tobytes())==cached['completeOriginalWorldSHA256'] and digest(world.tobytes())==cached['completeActualRenderedWorldSHA256'] and digest(ground.tobytes())==cached['completeGroundSHA256'];inputs.append(ref(asset))
   for kind,faces,geometry in [('completeOriginal',cached['unprovedOriginalFaces'],tri),('actualRendered',cached['unprovedActualRenderedFaces'],world)]:
    for i in faces:
     key=(row['uid'],kind,i)
     if any((d['uid'],d['kind'],d['sourceFace'])==key for d in done):continue
     projected_key=digest(json.dumps(sorted(geometry[i][:,[0,2]].tolist()),separators=(',',':')).encode())+cached['completeGroundSHA256']
     if projected_key in cache:
      gap={**cache[projected_key],'sourceFaceSHA256':digest(geometry[i].tobytes()),'exactSameUnorderedSourceProjectionReused':True}
     else:
      gap=diagnose(geometry[i],ground);cache[projected_key]=gap
     assert not gap['exactProjectionCovered'];done.append(dict(uid=row['uid'],kind=kind,sourceFace=i,sourceSHA256=row['sourceSHA256'],completeSourceWorldSHA256=cached['completeOriginalWorldSHA256'] if kind=='completeOriginal' else cached['completeActualRenderedWorldSHA256'],exactProjectionAndCompleteGroundCacheKey=projected_key,gap=gap));save(CACHE,dict(binding=binding,rows=done,projectedRegionsCache=cache,completeProof=False));assert reservations.heartbeat(lease)['ok'];print(json.dumps(dict(uid=row['uid'],kind=kind,face=i,regions=len(gap['allExactUncoveredRegions']),method=gap['method'])),flush=True)
  wanted=sum(len(r['unprovedOriginalFaces'])+len(r['unprovedActualRenderedFaces']) for r in finite['rows']);assert len(done)==wanted;save(DOC/'diagnostic.json.gz',dict(uids=[r['uid'] for r in finite['rows']],rows=done,completeOriginalAndRenderedUncoveredFaces=wanted,completeExactGapRegions=sum(len(r['gap']['allExactUncoveredRegions']) for r in done),rawPriorFailuresRetained=True,sourceGeometryChanges=0,fullAcceptance=False,evidenceRefs=inputs));spec=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'every-current-exact-area-interval-point-gap-region-v1',[ROOT/r['path'] for r in inputs],dict(uids=[r['uid'] for r in finite['rows']],completeOriginalAndRenderedUncoveredFaces=wanted,sourceGeometryChanges=0,fullAcceptance=False))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()

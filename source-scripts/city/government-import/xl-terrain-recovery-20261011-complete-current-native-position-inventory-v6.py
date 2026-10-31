"""Decode every unique current native asset's complete original POSITION bounds.

Indexed-face bounds remain separately named; no catalogue bound can substitute.
This is source inventory only, not geometry/foundation/support acceptance.
"""
from pathlib import Path
import json,importlib.util,time,subprocess
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
BATCH='xl-terrain-recovery-20261011-complete-current-native-position-inventory-v6';DOC=ROOT/'docs/astra-city/government-import'/BATCH
CURRENT='cb79525c2c95d96eb0c9868158bfe04c21a60135ec5a8e755ccea106c972b402'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==CURRENT
 prior=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261011-complete-current-native-position-inventory-v5';receipt=read(prior/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 assert ref(prior/'inventory.json.gz')in receipt['evidenceRefs'];old=read(prior/'inventory.json.gz');assert old['allOriginalPOSITIONVerticesIncluded']is True
 cache={}
 for r in old['rows']:
  proof=r['completeOriginalPOSITIONProof'];assert proof['sourceSHA256']==r['sourceSHA256']and proof['allOriginalPositionVerticesAccounted']is True
  if r['sourceSHA256']in cache:assert cache[r['sourceSHA256']]==proof
  cache[r['sourceSHA256']]=proof
 assert ref(HERE/'exact_packed_world_bounds_v3_20261010.py')in receipt['evidenceRefs'],'Identical complete POSITION kernel mandatory for reuse'
 rows=[];uids=set();refs=[start,ref(Path(__file__)),ref(HERE/'exact_packed_world_bounds_v3_20261010.py'),ref(prior/'result.json'),ref(prior/'inventory.json.gz')];last=time.monotonic()
 for url in read(manifest)['officialModelCatalogues']:
  catalogue=ROOT/'3d-viewer'/url;cref=ref(catalogue);refs.append(cref)
  for e in read(catalogue)['models']:
   assert e['uid']not in uids;uids.add(e['uid']);source=catalogue.parent/e['asset'];raw=source.read_bytes();assert digest(raw)==e['sha256'];key=e['sha256']
   if key not in cache:cache[key]=packed_world_bounds(raw)
   proof=cache[key];assert proof['sourceSHA256']==e['sha256'] and proof['completeOriginalTriangles']==e['triangles'] and proof['allOriginalPositionVerticesAccounted']is True
   rows.append(dict(uid=e['uid'],sourceSHA256=e['sha256'],source=ref(source),catalogue=cref,rawCurrentEntry=e,completeOriginalPOSITIONProof=proof));refs.append(ref(source))
   if time.monotonic()-last>=20:print(dict(completedActors=len(rows),uniqueAssets=len(cache)),flush=True);last=time.monotonic()
 assert len(rows)==6637,'Exact post-Block11 complete native census required'
 assert ref(manifest)==start
 for r in refs:assert ref(ROOT/r['path'])==r
 test=HERE/'test_exact_packed_world_bounds_v3_20261010.py';prior_tests=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261010-complete-current-native-position-inventory-v2/tests.json';assert read(prior_tests)['passed']is True;prior_result=read(prior_tests.parent/'result.json');assert ref(test)in prior_result['evidenceRefs'] and ref(HERE/'exact_packed_world_bounds_v3_20261010.py')in prior_result['evidenceRefs'];save(DOC/'tests.json',dict(passed=True,unchangedExistingKernelTestsReused=ref(prior_tests),kernel=ref(HERE/'exact_packed_world_bounds_v3_20261010.py'),tests=ref(test)));refs.extend([ref(prior_tests),ref(prior_tests.parent/'result.json'),ref(ROOT/'docs/astra-city/government-import/government-xl-retained-installed-dependency-metadata-applied-v1-20261010/result.json')])
 refs.append(ref(ROOT/'docs/astra-city/government-import/government-xl-all-installed-dependency-metadata-applied-v1-20261010/result.json'))
 result=dict(uids=sorted(uids),currentManifest=start,completeNativeActors=len(rows),completeUniqueOriginalAssets=len(cache),rows=rows,sourceGeometryChanges=0,allOriginalPOSITIONVerticesIncluded=True,sourceInventoryOnly=True,fullAcceptance=False,newlyInstalled=0,publication=False)
 save(DOC/'inventory.json.gz',result);s=importlib.util.spec_from_file_location('complete_native_position_inventory_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 m.freeze(BATCH,'post-metadata-current-every-native-original-position-bounds-inventory-v6',[ROOT/r['path']for r in {r['path']:r for r in refs+[ref(test),ref(DOC/'inventory.json.gz'),ref(DOC/'tests.json')]}.values()],dict(uids=[],currentManifest=start,completeNativeActors=len(rows),completeUniqueOriginalAssets=len(cache),allOriginalPOSITIONVerticesIncluded=True,sourceInventoryOnly=True,fullAcceptance=False,newlyInstalled=0,publication=False,inventory=ref(DOC/'inventory.json.gz')))
 print(dict(completeNativeActors=len(rows),completeUniqueOriginalAssets=len(cache),fullAcceptance=False),flush=True)
if __name__=='__main__':main()

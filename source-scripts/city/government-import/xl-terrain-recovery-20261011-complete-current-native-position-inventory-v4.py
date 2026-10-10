"""Decode every unique current native asset's complete original POSITION bounds.

Indexed-face bounds remain separately named; no catalogue bound can substitute.
This is source inventory only, not geometry/foundation/support acceptance.
"""
from pathlib import Path
import json,importlib.util,time,subprocess
from run import ROOT,HERE,read,save,digest
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
BATCH='xl-terrain-recovery-20261011-complete-current-native-position-inventory-v4';DOC=ROOT/'docs/astra-city/government-import'/BATCH
CURRENT='3a2f56f7980954ff3493aba5e8a015ca79153f81da55bb580e26bf5b2cdb2ee8'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==CURRENT
 rows=[];uids=set();cache={};refs=[start,ref(Path(__file__)),ref(HERE/'exact_packed_world_bounds_v3_20261010.py')];last=time.monotonic()
 for url in read(manifest)['officialModelCatalogues']:
  catalogue=ROOT/'3d-viewer'/url;cref=ref(catalogue);refs.append(cref)
  for e in read(catalogue)['models']:
   assert e['uid']not in uids;uids.add(e['uid']);source=catalogue.parent/e['asset'];raw=source.read_bytes();assert digest(raw)==e['sha256'];key=e['sha256']
   if key not in cache:cache[key]=packed_world_bounds(raw)
   proof=cache[key];assert proof['sourceSHA256']==e['sha256'] and proof['completeOriginalTriangles']==e['triangles'] and proof['allOriginalPositionVerticesAccounted']is True
   rows.append(dict(uid=e['uid'],sourceSHA256=e['sha256'],source=ref(source),catalogue=cref,rawCurrentEntry=e,completeOriginalPOSITIONProof=proof));refs.append(ref(source))
   if time.monotonic()-last>=20:print(dict(completedActors=len(rows),uniqueAssets=len(cache)),flush=True);last=time.monotonic()
 assert ref(manifest)==start
 for r in refs:assert ref(ROOT/r['path'])==r
 test=HERE/'test_exact_packed_world_bounds_v3_20261010.py';prior_tests=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261010-complete-current-native-position-inventory-v2/tests.json';assert read(prior_tests)['passed']is True;prior_result=read(prior_tests.parent/'result.json');assert ref(test)in prior_result['evidenceRefs'] and ref(HERE/'exact_packed_world_bounds_v3_20261010.py')in prior_result['evidenceRefs'];save(DOC/'tests.json',dict(passed=True,unchangedExistingKernelTestsReused=ref(prior_tests),kernel=ref(HERE/'exact_packed_world_bounds_v3_20261010.py'),tests=ref(test)));refs.extend([ref(prior_tests),ref(prior_tests.parent/'result.json'),ref(ROOT/'docs/astra-city/government-import/government-xl-retained-installed-dependency-metadata-applied-v1-20261010/result.json')])
 refs.append(ref(ROOT/'docs/astra-city/government-import/government-xl-all-installed-dependency-metadata-applied-v1-20261010/result.json'))
 result=dict(uids=sorted(uids),currentManifest=start,completeNativeActors=len(rows),completeUniqueOriginalAssets=len(cache),rows=rows,sourceGeometryChanges=0,allOriginalPOSITIONVerticesIncluded=True,sourceInventoryOnly=True,fullAcceptance=False,newlyInstalled=0,publication=False)
 save(DOC/'inventory.json.gz',result);s=importlib.util.spec_from_file_location('complete_native_position_inventory_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 m.freeze(BATCH,'post-metadata-current-every-native-original-position-bounds-inventory-v4',[ROOT/r['path']for r in {r['path']:r for r in refs+[ref(test),ref(DOC/'inventory.json.gz'),ref(DOC/'tests.json')]}.values()],dict(uids=[],currentManifest=start,completeNativeActors=len(rows),completeUniqueOriginalAssets=len(cache),allOriginalPOSITIONVerticesIncluded=True,sourceInventoryOnly=True,fullAcceptance=False,newlyInstalled=0,publication=False,inventory=ref(DOC/'inventory.json.gz')))
 print(dict(completeNativeActors=len(rows),completeUniqueOriginalAssets=len(cache),fullAcceptance=False),flush=True)
if __name__=='__main__':main()

"""Freeze narrow runtime roof binding and tested unchanged fallback safeguards."""
from pathlib import Path
import shutil
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-peninsula-runtime-roof-binding-checkpoint-v1-20261029'
def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];reviews={}
    for name in ['government-xl-peninsula-exact-source-association-review-v1-20261029','government-xl-peninsula-private-group-roof-review-v1-20261029']:
        receipt,pins=authenticate(BASE/name);reviews[name]=receipt['jobId'];refs.append(BASE/name/'result.json');p=BASE/name/'summary.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p)
    files=['3d-viewer/city/official-model-reviewed-osm-roof.js','3d-viewer/city/official-model-assets.js','3d-viewer/city/streaming.js','3d-viewer/city/official-models.js','3d-viewer/city/app.js','3d-viewer/city.html','3d-viewer/city/tests/official-model-reviewed-osm-roof.test.js','3d-viewer/city/tests/fixtures/peninsula-reviewed-osm-roof.json'];refs.extend(ROOT/p for p in files)
    out.mkdir()
    for source,name in [('/tmp/astra-peninsula-osm-roof-runtime-tests-20261029.log','runtime-tests.log'),('/tmp/astra-peninsula-osm-roof-portable-tests-20261029.log','portable-fixture-tests.log')]:
        p=out/name;shutil.copyfile(source,p);refs.append(p)
    assert 'tests 61'in (out/'runtime-tests.log').read_text()and 'fail 0'in (out/'runtime-tests.log').read_text();assert 'pass 6'in (out/'portable-fixture-tests.log').read_text()
    result=dict(uids=['landsd/270876:0','landsd/266543:0'],status='runtime-contract-tested-awaiting-full-private-browser-lifecycle-and-physical-acceptance',sourceGeometryChanges=0,sourcePoseChanges=0,terrainChanges=0,approvalFlagsPromoted=False,newlyInstalled=0,installationApproved=False,publication=False,reviewEvidence=reviews,runtimeTestsPassed=61,portableFixtureRerunTestsPassed=6,qualification='LandsD suppression validation unchanged. Only exact Peninsula owner/revision/modelId/CSUID/zero-offset plus a pinned declaration may nominate exact OSM roof709674357. Runtime checks every original roof form field before suppressing; changed geometry, height, levels, part flag or missing owner keeps the actual BASIC visible. New source revision, pose, arbitrary OSM target or extra declaration fields reject. Legacy BASIC support protections remain after this check. No new catalogue/model, physical, source/placement, device-performance or publication approval; browser and atomic failure/Base/Auto/eviction checks remain pending.')
    save(out/'summary.json',result);module('peninsula_runtime_binding_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'source-bound-original-OSM-roof-runtime-binding-and-portable-regression-tests',refs,result)
if __name__=='__main__':main()

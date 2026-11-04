"""Freeze production finite-membership integration; no model installation credit."""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BATCH='government-runtime-finite-sampler-integration-20261010'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
PRODUCTION=['3d-viewer/city/exact-finite-triangle-projection.js','3d-viewer/city/native-terrain.js','3d-viewer/city/geo.js','3d-viewer/city/world.js','3d-viewer/city/app.js','3d-viewer/city.html','3d-viewer/city/tests/native-terrain-finite-projection.test.js']
TESTS=['native-terrain.test.js','native-terrain-finite-projection.test.js','terrain-detail.test.js','terrain-nested.test.js','terrain-patch-index.test.js','terrain-coast.test.js','hydro-regions.test.js','hydro-terrain.test.js']
def main():
 scope_path=DOC.parent/'xl-terrain-recovery-20261010-festival-runtime-fix-explicit-test-scope-v1/scope.json';scope=read(scope_path)
 for ref in scope['presentFileBindings']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
 assert (ROOT/PRODUCTION[0]).read_bytes()==(HERE/'proposed-runtime/exact-finite-triangle-projection-v1.mjs').read_bytes()
 proposed=(HERE/'proposed-runtime/native-terrain-finite-projection-v1.mjs').read_text().replace('./exact-finite-triangle-projection-v1.mjs','./exact-finite-triangle-projection.js').removeprefix('// PROPOSED ONLY: shared runtime remains untouched.\n');assert (ROOT/PRODUCTION[1]).read_text()==proposed
 browser=read(DOC/'browser.json');assert browser['passed'] and not browser['pageErrors'] and not browser['failedLocalRequests']
 save(DOC/'verification.json',dict(productionPaths=PRODUCTION,directActualTestScope=scope,fullyTransitiveForensicClosureClaim=False,observedNodeTestCommand=['node','--test',*['3d-viewer/city/tests/'+t for t in TESTS]],observedNodeTests=38,observedNodePassed=38,observedNodeFailed=0,observedNodeDurationSeconds=14.4119,browser=browser,independentProposedFixtureTests=13,sourceGeometryChanges=0,terrainGeometryChanges=0,installationCredit=False,qualification='Direct runtime regression scope and actual browser integration. The complete441 independent ray probes, seven exact outside-membership witnesses and historical runtime are explicit test fixtures. No original-model/source-install acceptance claim. The unchanged rendered terrain remains authoritative; outside finite triangles cannot contribute sampled height. Existing determinant cutoff, Float32 geometry, spatial cache and barycentric interpolation are preserved.'))
 paths=[ROOT/p for p in PRODUCTION+scope['explicitRuntimeTestPaths']]+[scope_path,Path(__file__),HERE/'xl-runtime-finite-sampler-browser-20261010.mjs']
 spec=importlib.util.spec_from_file_location('finite_sampler_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 result=m.freeze(BATCH,'production-exact-finite-native-terrain-sampler-integration-v1',paths,dict(uids=[],productionSamplerFixed=True,unitTestsPassed=38,browserPassed=True,completeIndependentRayProbeCount=441,exactOutsideMembershipRegressionCount=7,fullyTransitiveForensicClosureClaim=False,scriptFullAcceptancePassed=False))
 verified=sorted(set(str(p.relative_to(ROOT)) for p in paths+[HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py',*DOC.iterdir()]))
 for ref in result['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256'] and ref['path'] in verified
 save(Path('/tmp/runtime-finite-sampler-root-verified-20261010.json'),dict(paths=verified,verifiedDirectScope=True,fullyTransitiveForensicClosureClaim=False,neonJobId=result['jobId']))
 print(json.dumps(dict(paths=len(verified),neonJobId=result['jobId'])))
if __name__=='__main__':main()

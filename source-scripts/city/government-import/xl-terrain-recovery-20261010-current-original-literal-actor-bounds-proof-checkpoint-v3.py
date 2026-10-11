"""Fence read-only actual/native original-vs-literal/F32 bounds evidence; no acceptance."""
from pathlib import Path
import importlib.util,numpy as np,subprocess
from run import ROOT,HERE,read,save,digest
BATCH='xl-terrain-recovery-20261010-current-original-literal-actor-bounds-proof-v3';DOC=ROOT/'docs/astra-city/government-import'/BATCH
OLD=HERE/'local/government-xl-terrain-recovery-hkdi-complete-original-current-probe-v1-20261010/runtime-geometry.json.gz'
def main():
 assert not(DOC/'actual-fixture-proof.json').exists();bounds=read(DOC/'bounds.json');assert bounds['acceptance']is False and bounds['geometryChanges']==0
 closure=bounds['productionModuleClosure'];assert closure['completeAuditedLiteralImportClosure'] is True and closure['unsupportedDynamicImports']==0 and len(closure['modules'])==len(closure['inputHashes'])
 assert {'3d-viewer/city/official-model-assets.js','3d-viewer/vendor/three.module.js','3d-viewer/vendor/GLTFLoader.js','3d-viewer/city/world.js','3d-viewer/city/native-terrain.js'}.issubset(closure['modules'])
 assert set(closure['inputHashes']).issubset(bounds['inputHashes'])
 for path,sha in bounds['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
 assert len(bounds['rows'])==1;row=bounds['rows'][0];assert row['uid']=='landsd/22089:0' and row['sourceSHA256']=='5cd70cb3bdb879ca96528fd1ff6ce29cc3b61c054b70456ec169fc9cf4831c40' and row['completeOriginalTriangles']==3965
 old=next(r for r in read(OLD)['rows']if r['uid']==row['uid']);positions=np.asarray(old['position'],np.float64);indices=np.asarray(old['index'],np.uint32);assert digest(positions.tobytes())==row['completeLiteralWorldPositionSHA256'] and digest(indices.tobytes())==row['completeLiteralIndexSHA256'];assert old['sourceSHA256']==row['sourceSHA256']
 test=HERE/'test_original_literal_complete_actor_bounds_20261010.mjs';closuretest=HERE/'test_literal_production_module_dependency_closure_20261010.mjs';raw=subprocess.check_output(['node','--test',str(test),str(closuretest)],cwd=ROOT,text=True);assert 'pass 20'in raw and 'fail 0'in raw;save(DOC/'tests.json',dict(command=['node','--test',str(test.relative_to(ROOT)),str(closuretest.relative_to(ROOT))],returnCode=0,stdout=raw))
 out=dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],all3965FacesAndEveryOriginalVertexAccounted=True,completeLiteralPositionAndIndexExactlyMatchFrozenProductionProbe=True,completeLiteralWorldBounds=row['completeLiteralWorldBounds'],completeFloat32CastWorldBounds=row['completeFloat32CastWorldBounds'],completeLiteralAndFloat32Bounds=row['completeLiteralAndFloat32Bounds'],observedManifest=bounds['manifest'],observedDuringUnrelatedProvisionalPublication=False,completeProductionModuleClosure=bounds['productionModuleClosure'],readOnly=True,fullAcceptance=False,nativeReacceptance=False,newlyInstalled=0,modelGeometryChanges=0,qualification='Diagnostic complete-source bounds only, no native/support/current-installation acceptance. Original provider source decodes via production loader and every loaded vertex is bounded in literal F64 and cast F32; actual position/index bytes equal the previously frozen complete production probe. A stable global manifest and all source/current gates are independently required by any future regional rebind.')
 save(DOC/'actual-fixture-proof.json',out);s=importlib.util.spec_from_file_location('literal_bounds_checkpoint_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 m.freeze(BATCH,'diagnostic-complete-current-original-literal-float32-native-bounds-proof-v3',[Path(__file__),test,closuretest,OLD,DOC/'input.json',DOC/'bounds.json',DOC/'tests.json',*[ROOT/p for p in bounds['inputHashes']]],out)
if __name__=='__main__':main()

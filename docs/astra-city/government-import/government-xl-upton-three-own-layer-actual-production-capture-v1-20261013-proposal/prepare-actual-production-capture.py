from pathlib import Path
import sys,json,subprocess
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_three_own_layer_actual_production_capture_draft_v1_20261013 as a
P=Path(__file__).parent;pins=a.read(P/'draft-pins.json');refs=pins['codeRefs']+pins['inputRefs']+[a.ref(P/'draft-pins.json'),a.ref(Path(__file__))]
assert len(pins['codeRefs'])>=55 and len(pins['inputRefs'])>=117
for q in refs:a.check(q)
assert not a.DOC.exists()and not a.LOCAL.exists();commands=[]
def run(cmd,name):
 path=P/name;assert not path.exists();r=subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);path.write_bytes(r.stdout)
 commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(path)));assert r.returncode==0,(cmd,r.returncode,path)
run([sys.executable,str(ROOT/'source-scripts/city/government-import/test_upton_own_layer_saved_nomination_binding_v1_20261013.py')],'actual-synthetic-binding-tests-v2.log')
run([sys.executable,'-c',"import sys;sys.path.insert(0,'source-scripts/city/government-import');import upton_three_own_layer_actual_production_capture_draft_v1_20261013;print('isolated import PASS; no worker/lease/production import')"],'actual-isolated-import-v2.log')
run([sys.executable,str(Path(a.__file__)),'--schema-only'],'actual-schema-only-v2.log')
schema=json.loads((P/'actual-schema-only-v2.log').read_text());assert schema['passed']and schema['completeNativeFacets']==11580 and schema['expectedClosedDomainDrawnFacets']==11608 and schema['new11577To11580MappingComplete']and schema['all11574OtherRawProvenanceAliasesAnd68ProtectedByteEqual']and schema['cumulativeOriginalMappingComplete']
script="""import assert from 'node:assert/strict';import {writeFileSync} from 'node:fs';import {pathToFileURL} from 'node:url';import {snapshotModuleClosure,verifyModuleClosure} from './source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';const root=pathToFileURL(process.cwd()+'/'),entry=new URL('source-scripts/city/government-import/upton_three_own_layer_actual_production_runtime_draft_v1_20261013.mjs',root),c=snapshotModuleClosure(entry,root);assert.equal(c.schema,'exact-literal-static-dynamic-resource-closure-v1');assert(c.computedImportsRejected&&c.completeAuditedLiteralImportClosure&&c.opaqueResourcesAreNotParsedModules);assert.equal(c.unsupportedDynamicImports,0);assert.equal(c.entryPath,'source-scripts/city/government-import/upton_three_own_layer_actual_production_runtime_draft_v1_20261013.mjs');verifyModuleClosure(c,root);writeFileSync(new URL('docs/astra-city/government-import/government-xl-upton-three-own-layer-actual-production-capture-v1-20261013-proposal/literal-runtime-closure-preflight.json',root),JSON.stringify(c,null,2)+'\\n',{flag:'wx'});console.log(JSON.stringify({passed:true,entryPath:c.entryPath,inputFiles:Object.keys(c.inputHashes).length,schema:c.schema,computedImportsRejected:true,noProductionImport:true}));"""
run(['node','--input-type=module','-e',script],'actual-literal-runtime-closure-v2.log')
closure=a.read(P/'literal-runtime-closure-preflight.json');closureRefs=[dict(path=k,sha256=v)for k,v in closure['inputHashes'].items()]
for q in refs+closureRefs:a.check(q)
assert a.ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==a.legacy.CURRENT
assert not a.DOC.exists()and not a.LOCAL.exists()
summary=dict(passed=True,caller=a.ref(Path(a.__file__)),runtime=a.ref(a.RUNTIME),driver=a.ref(Path(__file__)),commands=commands,schemaVerbatim=schema,allFrozenCodeInputPinsVerifiedBeforeAndEnd=True,codePinCount=len(pins['codeRefs']),inputPinCount=len(pins['inputRefs']),currentManifestSHA256=a.legacy.CURRENT,noWorkerLeaseDBOrProductionImport=True,evidenceRefs=[a.ref(Path(__file__)),a.ref(P/'draft-pins.json'),a.ref(P/'literal-runtime-closure-preflight.json')]+[r['log']for r in commands]+closureRefs)
a.save(P/'actual-readonly-preparation.json',summary);print(json.dumps(summary,sort_keys=True))

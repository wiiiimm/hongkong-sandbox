from pathlib import Path
import sys,json,subprocess,ast
import numpy as np
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_certified6170_actual_production_capture_v1_20261014 as a
P=Path(__file__).parent;codeonly='--code-only'in sys.argv
assert codeonly or '--bind-completed-nomination-readonly'in sys.argv
assert not a.DOC.exists() and not a.LOCAL.exists()
commands=[];prefix='code-only-'if codeonly else 'actual-'
def run(cmd,name,cwd=ROOT):
 path=P/(prefix+name);assert not path.exists();r=subprocess.run(cmd,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);path.write_bytes(r.stdout)
 commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(path)));assert r.returncode==0,(cmd,r.returncode,path)
run(['node','--check',str(a.RUNTIME)],'runtime-syntax.log')
run([sys.executable,'-m','unittest','-v',a.TEST,'test_upton_certified_float32_parent_enclosure_v1_20261014','test_upton_append_four_saved_current_triangles_v1_20261014'],'binding-and-existing-kernel-fixtures.log',a.HERE)
name=prefix+'literal-runtime-closure-preflight.json'
script="import assert from 'node:assert/strict';import {writeFileSync} from 'node:fs';import {pathToFileURL} from 'node:url';import {snapshotModuleClosure,verifyModuleClosure} from './source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';const root=pathToFileURL(process.cwd()+'/'),entry=new URL('source-scripts/city/government-import/upton_certified6170_actual_production_runtime_v1_20261014.mjs',root),c=snapshotModuleClosure(entry,root);assert(c.computedImportsRejected&&c.completeAuditedLiteralImportClosure);assert.equal(c.unsupportedDynamicImports,0);assert(verifyModuleClosure(c,root));writeFileSync(new URL("+json.dumps(str((P/name).relative_to(ROOT)))+",root),JSON.stringify(c,null,2)+'\\n',{flag:'wx'});console.log(JSON.stringify({passed:true,entryPath:c.entryPath,files:Object.keys(c.inputHashes).length,noProductionImport:true}));"
run(['node','--input-type=module','-e',script],'literal-runtime-closure.log')
closure=a.read(P/name);literal=[dict(path=k,sha256=v)for k,v in closure['inputHashes'].items()];assert len(literal)==24
folders=[a.HERE,a.HERE.parent/'shared-modelling',a.HERE.parent/'citywide-native',a.HERE.parent/'island-detail-integration',ROOT/'docs/astra-city/mui-wo-buildings/review',a.HERE.parent/'assembly-support-review']
todo=[Path(a.__file__)];seen=set();transitive=[]
while todo:
 path=todo.pop().resolve()
 if path in seen:continue
 seen.add(path);transitive.append(a.ref(path))
 for n in ast.walk(ast.parse(path.read_text())):
  names=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[q.name for q in n.names]if isinstance(n,ast.Import)else[]
  for mod in names:
   for folder in folders:
    q=folder/(mod.replace('.','/')+'.py')
    if q.is_file():todo.append(q)
refs=literal+transitive+[a.ref(Path(__file__)),a.ref(P/'METHOD.md'),a.ref(P/name)]+[q['log']for q in commands]
for q in refs:a.check(q)
if codeonly:
 assert not (P/'draft-pins.json').exists() and not (P/'actual-readonly-preparation.json').exists()
 a.save(P/'code-only-preparation.json',dict(passed=True,caller=a.ref(Path(a.__file__)),runtime=a.ref(a.RUNTIME),commands=commands,transitiveLocalPythonImports=transitive,strictLiteralDependencyRefs=literal,evidenceRefs=refs,finalCandidateReceiptCountHashMappingsNotYetBound=True,notReadyForWorker=True,noDBLeaseProductionArraysOrImport=True))
 print(json.dumps(dict(passed=True,codeOnly=True,pythonClosure=len(transitive),literalClosure=len(literal),finalCandidateNotBound=True)));raise SystemExit
receipt=a.read(a.NOM_DOC/'result.json');verified=a.read(a.NOM_DOC/'ROOT-VERIFIED.json');assert verified['jobId']==receipt['jobId'] and verified['exactNeonReadback'] and verified['allEvidenceHashesVerified'] and verified['leaseReleased']
nom=a.read(a.NOM_DOC/'private-three-safe-current-certified-6170-nomination.json.gz');assert not nom['physicalAccepted'] and not nom['installationApproved']
raw=np.asarray(nom['candidateRawPositionTriplets'],dtype='<f8');pos=np.asarray(nom['newNativeMesh']['position'],dtype='<f8').reshape(-1,3)
old=a.read(a.nomination.PROPOSAL/'draft-pins.json');codes={q['path']:q for q in old['codeRefs']};inputs={q['path']:q for q in old['inputRefs']}
for q in transitive+literal:codes[q['path']]=q
for path in [a.RUNTIME,a.VALIDATOR,a.HERE/'test_upton_certified6170_saved_nomination_binding_v1_20261014.py']:q=a.ref(path);codes[q['path']]=q
for folder,names in [(a.NOM_DOC,['result.json','ROOT-VERIFIED.json','private-three-safe-current-certified-6170-nomination.json.gz','fresh-only6170-residuals-and-certified-enclosures.json.gz','complete-whole-scope-actual-enclosure-compatibility-and12-coverage.json.gz']),(a.previous_capture.DOC,['result.json','private-native-terrain-candidate.json.gz','actual-production-replay.json.gz']),(a.nomination.PROPOSAL,['draft-pins.json','actual-readonly-preparation.json'])]:
 for name in names:q=a.ref(folder/name);inputs[q['path']]=q
previous=a.read(a.previous_capture.DOC/'actual-production-replay.json.gz');assert len(previous['after']['closedDomainDrawnTriplets'])==11634
pins=dict(caller=a.ref(Path(a.__file__)),runtime=a.ref(a.RUNTIME),completedNominationJob=receipt['jobId'],completeNewNativeFacets=len(raw),completeNewPositionVertices=len(pos),completeNewRawSHA256=a.nomination.sha(raw),expectedClosedDomainDrawnFacets=len(previous['after']['closedDomainDrawnTriplets'])+len(raw)-11606,codeRefs=sorted(codes.values(),key=lambda q:q['path']),inputRefs=sorted(inputs.values(),key=lambda q:q['path']),sourceOnly=True,physicalAccepted=False)
assert not (P/'draft-pins.json').exists();a.save(P/'draft-pins.json',pins)
for q in pins['codeRefs']+pins['inputRefs']:a.check(q)
run([sys.executable,str(Path(a.__file__)),'--schema-only'],'schema-only.log');schema=json.loads((P/'actual-schema-only.log').read_text());assert schema['passed'] and schema['completeNativeActorScope']==6650 and schema['completeBasicRecords']==1911 and schema['wholeAffectedBasicActors']==52 and schema['all11606OldRawProvenancePositionIndexPrefixesAnd68ProtectedUnchanged']
for q in pins['codeRefs']+pins['inputRefs']+refs:a.check(q)
assert a.ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==a.legacy.CURRENT and not a.DOC.exists() and not a.LOCAL.exists()
refs+=[a.ref(P/'draft-pins.json')]+[q['log']for q in commands]
a.save(P/'actual-readonly-preparation.json',dict(passed=True,caller=a.ref(Path(a.__file__)),runtime=a.ref(a.RUNTIME),driver=a.ref(Path(__file__)),method=a.ref(P/'METHOD.md'),commands=commands,schemaVerbatim=schema,transitiveLocalPythonImports=transitive,strictLiteralDependencyRefs=literal,allCodeInputPinsVerifiedBeforeAndEnd=True,evidenceRefs=refs,noProductionCaptureDBLeaseOrSourceCalculation=True))
print(json.dumps(dict(passed=True,completedNominationJob=receipt['jobId'],newFacets=len(raw),codePins=len(codes),inputPins=len(inputs),pythonClosure=len(transitive),literalClosure=len(literal))))

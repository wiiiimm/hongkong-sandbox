import os,sys,json,subprocess,hashlib,pathlib
ROOT=pathlib.Path.cwd();HERE=ROOT/'source-scripts/city/government-import';P=ROOT/'docs/astra-city/government-import/government-xl-citywalk134332-supervisor-freezer-wiring-proposal-v1-20261013';manifest='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
sys.path.insert(0,str(HERE))
import citywalk134332_surviving_native_supervised_draft_v1_20261013 as W
import citywalk134332_freeze_surviving_native_interfaces_draft_v1_20261013 as F
import db
assert db.CONFIG['project_id']=='billowing-surf-67227217' and db.CONFIG['branch_id']=='br-icy-silence-b3wjwz0q' and db.CONFIG['database']=='neondb' and db.CONFIG['schema']=='astra_modelling'
assert not W.LOCAL.exists() and not W.Q.D.exists()
plan=W.verified_plan();pins=plan['codeAndHistoricalPins']+[W.ref(P/'wiring-plan.json'),plan['completedPreparationValidation']]
validation=W.read(ROOT/plan['completedPreparationValidation']['path'])
for e in validation['refs']:pins.append(e)
def fence():
 for e in pins:assert W.ref(ROOT/e['path'])==e
fence();print(json.dumps(dict(actualVenvCallerFreezerImportsPassed=True,pinnedModellingDBGuardPassed=True)),flush=True)
cmd=[sys.executable,str(HERE/'citywalk134332_surviving_native_supervised_draft_v1_20261013.py'),'--expected-manifest',manifest,'--preflight-only']
r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);log=P/'actual-wrapper-readonly-preflight-v1.log';assert not log.exists();log.write_text(r.stdout+r.stderr);print(r.stdout,end='',flush=True);assert r.returncode==0,r.stderr
from types import SimpleNamespace
before=W.inputs(SimpleNamespace(expected_manifest=manifest));assert len(before['uids'])==19 and len(before['resources'])==21 and len(before['completeNativeSurvivalInventory'])==6650
state=P/'actual-readonly-shared-state-v1.json';assert not state.exists();W.save(state,before)
js="""import {writeFileSync,existsSync} from 'node:fs';import assert from 'node:assert/strict';import {snapshotModuleClosure,verifyModuleClosure} from './source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';const root=new URL('./',import.meta.url);const entry=new URL('source-scripts/city/government-import/citywalk134332_actual_surviving_native_attributes_draft_v1_20261013.mjs',root);const closure=snapshotModuleClosure(entry,root);assert(verifyModuleClosure(closure,root));const out=new URL('docs/astra-city/government-import/government-xl-citywalk134332-supervisor-freezer-wiring-proposal-v1-20261013/actual-proposal-exporter-entry-module-closure-v1.json',root);assert(!existsSync(out));writeFileSync(out,JSON.stringify(closure,null,2)+'\n');console.log(JSON.stringify({strictExporterClosurePassed:true,inputFiles:Object.keys(closure.inputHashes).length,modules:closure.modules.length,resources:closure.resources.length,noExporterImport:true}));"""
jsfile=P/'actual-proposal-closure-preparation-v1.mjs';assert not jsfile.exists();jsfile.write_text(js)
r2=subprocess.run(['node','--input-type=module','-e',js],cwd=ROOT,capture_output=True,text=True);log2=P/'actual-proposal-exporter-closure-v1.log';assert not log2.exists();log2.write_text(r2.stdout+r2.stderr);print(r2.stdout,end='',flush=True);assert r2.returncode==0,r2.stderr
fence();after=W.inputs(SimpleNamespace(expected_manifest=manifest));assert after==before;assert not W.LOCAL.exists() and not W.Q.D.exists()
closure=P/'actual-proposal-exporter-entry-module-closure-v1.json';cd=W.read(closure)
refs=list({(e['path'],e['sha256']):e for e in pins+[W.ref(state),W.ref(log),W.ref(log2),W.ref(jsfile),W.ref(closure),W.ref(pathlib.Path(__file__))]}.values())
result=dict(actualImportsPassed=True,wrapperPreflightExitCode=r.returncode,closureExitCode=r2.returncode,observedProtectedReviewRecords=before['observedProtectedReviewRecords'],contextUIDs=before['uids'],numericActorUIDs=[W.Q.UID,*W.Q.ACTORS],canonicalBuildingResources=19,totalSupervisedResources=21,resources=before['resources'],currentManifest=before['currentManifest'],currentSourceReviewPointer=before['sourcePointer'],globalNativeEntries=6650,survivingNativeEntries=sum(e['survives']for e in before['completeNativeSurvivalInventory']),globalSuppressedUIDs=len(before['globalSuppressionInventory']),closureInputFiles=len(cd['inputHashes']),closureModules=len(cd['modules']),closureResources=len(cd['resources']),beforeAfterExact=True,noWorker=True,noLease=True,noRendererImport=True,noGeometryOrFiniteMath=True,evidenceRefs=refs)
output=P/'actual-wrapper-import-preflight-closure-validation-v1.json';assert not output.exists();W.save(output,result);print(json.dumps(dict(validation=W.ref(output),observedProtectedReviewRecords=result['observedProtectedReviewRecords'],resources=21,allCurrentPinsUnchanged=True)),flush=True)

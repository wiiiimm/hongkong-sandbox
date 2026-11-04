from pathlib import Path
import json,gzip,hashlib,subprocess,sys,ast,inspect,time
r=Path.cwd();h=r/'source-scripts/city/government-import';b=r/'docs/astra-city/government-import';p=b/'government-xl-complete-native-actual-position-post-nam-delta-v1-20261013-proposal';batch='government-xl-complete-native-actual-position-post-nam-delta-v1-20261013'
def ref(q):return dict(path=str(q.resolve().relative_to(r)),sha256=hashlib.sha256(q.read_bytes()).hexdigest())
def read(q):return json.loads(gzip.decompress(q.read_bytes())if str(q).endswith('.gz')else q.read_bytes())
def save(q,v):assert not q.exists();q.write_text(json.dumps(v,indent=2)+'\n')
pins=read(p/'draft-pins.json')
for q in pins['codeRefs']+pins['inputRefs']:assert ref(r/q['path'])==q
command=['/tmp/astra-city-venv/bin/python','-m','unittest','-v','test_upton_post_nam_current_binding_v1_20261013'];x=subprocess.run(command,cwd=h,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);log=p/'actual-pure-bindings-tests.log';assert not log.exists();log.write_text(x.stdout);assert x.returncode==0,x.stdout;assert x.stdout.count(' ... ok')==18
save(p/'pure-bindings-helper-validation.json',dict(exitCode=x.returncode,passedTests=18,failedTests=0,executedCodeRefs=[ref(h/'upton_post_nam_current_binding_v1_20261013.py'),ref(h/'test_upton_post_nam_current_binding_v1_20261013.py'),ref(h/'actual_native_bounds_baseline_rebind_20261011.py')],log=ref(log),command=command,noActorDecodeDBLeaseOrCapture=True))
print('actual pure fixtures18 PASS/exit0',flush=True)
smoke="import sys,importlib.util;from pathlib import Path;h=Path('source-scripts/city/government-import').resolve();sys.path.insert(0,str(h));p=h/'xl-complete-native-actual-position-post-nam-delta-draft-v1-20261013.py';s=importlib.util.spec_from_file_location('nam_delta_preparation_only',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);print('Actual caller import PASS; no main/claim/DB/capture')"
x=subprocess.run(['/tmp/astra-city-venv/bin/python','-c',smoke],cwd=r,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);log=p/'actual-import-smoke.log';assert not log.exists();log.write_text(x.stdout);assert x.returncode==0,x.stdout;save(p/'actual-import-smoke.json',dict(passed=True,exitCode=x.returncode,caller=pins['caller'],log=ref(log),noClaimOrDB=True))
js="import assert from 'node:assert/strict';import {snapshotModuleClosure,verifyModuleClosure} from './source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';const root=new URL('file://'+process.cwd()+'/');const c=snapshotModuleClosure(new URL('source-scripts/city/government-import/xl-complete-native-actual-position-post-nam-delta-draft-v1-20261013.mjs',root),root);assert(c.computedImportsRejected&&c.unsupportedDynamicImports===0);assert(verifyModuleClosure(c,root));console.log(JSON.stringify(c));"
x=subprocess.run(['node','--input-type=module','-e',js],cwd=r,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);log=p/'actual-literal-exporter-closure.log';assert not log.exists();log.write_text(x.stdout);assert x.returncode==0,x.stdout;closure=json.loads(x.stdout);save(p/'literal-exporter-closure-preflight.json',closure);print('actual import/literal exporter closure PASS',flush=True)
# Pure helper import/actual saved metadata audit only, not the capture producer.
sys.path.insert(0,str(h));from upton_post_nam_current_binding_v1_20261013 import historical_ref,manifest_delta,census,CURRENT,OLD
prev=b/'government-xl-complete-current-native-actual-position-matrix-bounds-v4-20261012';old=prev/'captured-manifest.json';live=r/'3d-viewer/city/data/manifest.json';assert ref(live)['sha256']==CURRENT and ref(old)['sha256']==OLD
cert=b/'government-xl-nam-fung79099-unchanged-installed-v1-20261013/root-independent-installed-readback.json';installed=read(cert);newurl=str((r/installed['catalogue']['path']).relative_to(r/'3d-viewer'));assert manifest_delta(read(old),read(live),newurl)
prior=read(prev/'input.json.gz');inventory=read(prev/'inventory.json.gz');assert len(prior['rows'])==len(inventory['rows'])==6649 and inventory['completeNativeActors']==6649 and not inventory['errors'];assert all(x['wholeUnusedPositionVerticesIncluded']and x['sourceFacesOmitted']==0 for x in inventory['rows'])
models={}
for url in read(live)['officialModelCatalogues']:
 for e in read(r/'3d-viewer'/url)['models']:assert e['uid']not in models;models[e['uid']]=e
assert census([q['uid']for q in prior['rows']],list(models));new=models['landsd/79099:0'];assert new['sha256']==installed['sourceSHA256']and new['triangles']==13061
# Every configured receipt family ref version is hashed; one exact historical
# live-manifest version resolves to the real old captured-manifest bytes only.
import importlib.util
s=importlib.util.spec_from_file_location('nam_readonly_schema',h/'xl-complete-native-actual-position-post-nam-delta-draft-v1-20261013.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
cache={};rows=[];resolved=[];started=time.monotonic()
for family in [prev.name]+m.FAMILIES:
 folder=b/family;receipt=read(folder/'result.json');bad=[];versions=[]
 for q in receipt['evidenceRefs']:
  actual=(old if q['path']=='3d-viewer/city/data/manifest.json'and q['sha256']==OLD else r/q['path']);key=str(actual.resolve())
  if key not in cache:cache[key]=ref(actual)
  assert cache[key]['sha256']==q['sha256'],dict(family=family,expected=q,actual=cache[key])
  if str(actual.relative_to(r))!=q['path']:resolved.append(dict(original=q,actualByteVersion=cache[key]))
  versions.append(dict(originalReceiptRef=q,actualByteVersion=cache[key]))
 rows.append(dict(family=family,jobId=receipt['jobId'],result=ref(folder/'result.json'),completeRefs=len(versions),allRefsPassed=True,bindings=versions));print(json.dumps(dict(phase='saved-family-ref-audit',family=family,refs=len(versions),uniqueFiles=len(cache),seconds=time.monotonic()-started)),flush=True)
for path,sha in inventory['completeRecursiveProductionModuleClosure']['inputHashes'].items():assert ref(r/path)['sha256']==sha
resources=['building:landsd/79099:0','building:landsd/45779:0','immutable-source-proof:'+batch]
supervisor=h.parent/'shared-modelling/reservations.py';freezer=h/'xl-popcorn-source-investigations-checkpoints-20261009.py';supervisor_text=supervisor.read_text();freezer_text=freezer.read_text();assert 'reservations.py' in (h/'xl-complete-native-actual-position-post-nam-delta-draft-v1-20261013.py').read_text();assert 'finally' in supervisor_text and 'release(reservation)' in supervisor_text and 'heartbeat' in supervisor_text;assert "finally:assert reservations.release(lease)['ok']"in freezer_text
assert not (b/batch).exists()and not (h/'local'/batch).exists()
readiness=dict(canonicalResources=resources,canonicalResourceCount=3,supervisor=ref(supervisor),freezer=ref(freezer),freezerAdditionalResource='source-context:'+batch,TTLSeconds=3600,maintainedSupervisorAndFinallyReleaseContractPresent=True,actualDatabaseOwnershipNotQueried=True,outputAndLocalPathsAbsent=True,noActiveClaimCreated=True)
save(p/'canonical-supervisor-freezer-readiness.json',readiness)
save(p/'actual-current-family-ref-preflight.json',dict(passed=True,currentManifest=ref(live),historicalManifest=ref(old),NamInstalledRootCertificate=ref(cert),soleNamedManifestAppendVerified=True,completeCurrentUIDs=6650,exactOldUIDs=6649,actualNewUID='landsd/79099:0',newFaces=13061,oldOriginalAndActualSourceTuplesNotDecoded=True,families=rows,uniqueVerifiedInputFiles=len(cache),historicalResolutions=resolved,currentOriginalProductionClosureExact=True,pinnedNeonNotQueried=True,canonicalReadiness=readiness,noLeaseDBWorkerOrCapture=True))
# All start-configured preparation code/input pins rehashed at end too.
for q in pins['codeRefs']+pins['inputRefs']:assert ref(r/q['path'])==q
assert ref(live)['sha256']==CURRENT
for name in ['pure-bindings-helper-validation.json','actual-pure-bindings-tests.log','actual-import-smoke.json','literal-exporter-closure-preflight.json','canonical-supervisor-freezer-readiness.json','actual-current-family-ref-preflight.json']:print(name,ref(p/name)['sha256'])
print('ALL preparation terminal PASS; no database query, resource claim, source decode or capture worker.',flush=True)

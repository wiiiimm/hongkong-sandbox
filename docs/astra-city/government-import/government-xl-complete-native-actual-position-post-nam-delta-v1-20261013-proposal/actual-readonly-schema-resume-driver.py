from pathlib import Path
import json,gzip,hashlib,subprocess,sys,ast,inspect,time
r=Path.cwd();h=r/'source-scripts/city/government-import';b=r/'docs/astra-city/government-import';p=b/'government-xl-complete-native-actual-position-post-nam-delta-v1-20261013-proposal';batch='government-xl-complete-native-actual-position-post-nam-delta-v1-20261013'
def ref(q):return dict(path=str(q.resolve().relative_to(r)),sha256=hashlib.sha256(q.read_bytes()).hexdigest())
def read(q):return json.loads(gzip.decompress(q.read_bytes())if str(q).endswith('.gz')else q.read_bytes())
def save(q,v):assert not q.exists();q.write_text(json.dumps(v,indent=2)+'\n')
pins=read(p/'draft-pins.json')
for q in pins['codeRefs']+pins['inputRefs']:assert ref(r/q['path'])==q
validation=read(p/'pure-bindings-helper-validation.json');assert validation['exitCode']==0 and validation['passedTests']==18 and validation['failedTests']==0
for q in validation['executedCodeRefs']+[validation['log']]:assert ref(r/q['path'])==q
assert read(p/'actual-import-smoke.json')['passed']
closure=read(p/'literal-exporter-closure-preflight.json');assert closure['computedImportsRejected']and closure['unsupportedDynamicImports']==0
for path,hsh in closure['inputHashes'].items():assert ref(r/path)['sha256']==hsh
print('Reusing exact completed18 fixture/import/literal-closure results; no repeat',flush=True)
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
caller_tree=ast.parse((h/'xl-complete-native-actual-position-post-nam-delta-draft-v1-20261013.py').read_text());families=ast.literal_eval(next(n.value for n in caller_tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='FAMILIES'for t in n.targets)))
cache={};rows=[];resolved=[];started=time.monotonic()
for family in [prev.name]+families:
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

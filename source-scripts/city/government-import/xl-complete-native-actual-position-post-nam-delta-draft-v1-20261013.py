"""UNEXECUTED exact6649 reuse + freshNam79099 actual unused attributes/matrix bounds.
No old runtime alias, actor re-decode, scene/terrain/publication or acceptance.
"""
from pathlib import Path
import importlib.util,json,re,subprocess,sys,time,uuid,hashlib
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from upton_post_nam_current_binding_v1_20261013 import manifest_delta,census,actor_binding,historical_ref,CURRENT,OLD,DELTA
BATCH='government-xl-complete-native-actual-position-post-nam-delta-v1-20261013'
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';PROPOSAL=BASE/(BATCH+'-proposal')
PREVIOUS=BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v4-20261012'
INSTALLED=BASE/'government-xl-nam-fung79099-unchanged-installed-v1-20261013'
EXPORTER=HERE/'xl-complete-native-actual-position-post-nam-delta-draft-v1-20261013.mjs'
METHOD=PROPOSAL/'METHOD.md';HELPER=HERE/'upton_post_nam_current_binding_v1_20261013.py'
FAMILIES=['government-xl-upton-whole-parent-current-domain-capture-v2-20261012','government-xl-upton-whole-parent-original-tin-regression-v2-20261012','government-xl-upton-six-basic-saved-current-ground-feasibility-v1-20261012','government-xl-upton-six-basic-existing-guard-samples-full-source-columns-v1-20261012','government-xl-upton-main12728-four-world-grade-cap-interfaces-v1-20261012','government-xl-upton-746-residual-saved-source-role-reconciliation-v1-20261012','government-xl-upton-two-original-whole-current-facet-protection-v3-20261012']
def ref(p):return dict(path=str(p.resolve().relative_to(ROOT)),sha256=digest(p.read_bytes()))
def canonical(value):return digest(json.dumps(value,sort_keys=True,separators=(',',':')).encode())
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 refs=[]
 for q in pins['codeRefs']+pins['inputRefs']:
  p=ROOT/q['path'];assert ref(p)==q;refs.append(p)
 closure=read(PROPOSAL/'literal-exporter-closure-preflight.json');assert closure['schema']=='exact-literal-static-dynamic-resource-closure-v1'and closure['computedImportsRejected']and closure['unsupportedDynamicImports']==0 and closure['entryPath']==str(EXPORTER.relative_to(ROOT))
 for path,h in closure['inputHashes'].items():assert ref(ROOT/path)['sha256']==h;refs.append(ROOT/path)
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifestpath);assert start['sha256']==CURRENT;manifest=read(manifestpath)
 prior=read(PREVIOUS/'input.json.gz');inventory=read(PREVIOUS/'inventory.json.gz');oldmanifest=PREVIOUS/'captured-manifest.json';assert ref(oldmanifest)['sha256']==OLD
 install=read(INSTALLED/'root-independent-installed-readback.json');assert ref(INSTALLED/'root-independent-installed-readback.json')['sha256']=='b9159fcc1cd68eb302237c7f2a42d219629b672425d1161f3725a4b7eb594505'and install['independentlyVerified']and install['previousNativeEntriesPreserved']==6649 and install['nativeAssets']==6650 and install['currentManifest']==start
 newurl=str((ROOT/install['catalogue']['path']).relative_to(ROOT/'3d-viewer'));assert manifest_delta(read(oldmanifest),manifest,newurl)
 receipt=read(PREVIOUS/'result.json');assert receipt['jobId']=='8614ecb76819b66f4dc97e0a840fc17532f25896d54e971d3c060332d644085e'and ref(PREVIOUS/'result.json')['sha256']=='23343a25c467135ca4300acbf7963c08b2006deb7671f660bbe66d838168a33c'
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for q in receipt['evidenceRefs']:refs.append(historical_ref(q,ROOT,oldmanifest));pulse()
 assert inventory['completeNativeActors']==inventory['successfullyCapturedActors']==6649 and not inventory['errors']and inventory['startAndEndInputHashesVerified']
 required=inventory['completeRecursiveProductionModuleClosure'];assert required['computedImportsRejected']and required['unsupportedDynamicImports']==0
 for path,h in required['inputHashes'].items():assert ref(ROOT/path)['sha256']==h;refs.append(ROOT/path)
 models={};sources={};catalogues=[];requested=set()
 for url in manifest['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;q=ref(path);catalogues.append(dict(**q,originalPath=q['path']));refs.append(path)
  for e in read(path)['models']:
   assert e['uid']not in models;models[e['uid']]=e;sources[e['uid']]=path.parent/e['asset']
   for dep in e.get('supportDependencies',[]):requested.add(dep if isinstance(dep,str)else dep['uid'])
 assert census([r['uid']for r in prior['rows']],list(models));requested.update(models)
 dependencies={}
 for module in (ROOT/'3d-viewer/city').glob('official-model-*.js'):
  q=ref(module);dependencies[q['path']]=q['sha256'];requested.update(re.findall(r'landsd/\d+:0',module.read_text()));refs.append(module)
 assert dependencies==prior['declaredDependencyUIDSourceHashes']
 forms={};tiles={}
 for tile in manifest['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];hits=[b for b in read(path)['buildings']if b['uid']in requested]
  if hits:
   tiles[str(path.relative_to(ROOT))]=ref(path)['sha256'];refs.append(path)
   for b in hits:assert b['uid']not in forms;forms[b['uid']]=b
 assert set(models)<=set(forms)
 new_dependencies={q if isinstance(q,str)else q['uid']for q in models[DELTA].get('supportDependencies',[])};assert new_dependencies<=set(forms)
 actual={r['uid']:r for r in inventory['rows']};reuse=[]
 for row in prior['rows']:
  uid=row['uid'];pin=ref(sources[uid]);assert actor_binding(row,actual[uid],models[uid],forms[uid],pin,pin['sha256'])==actual[uid]
  reuse.append(dict(uid=uid,source=pin,currentRawEntrySHA256=canonical(models[uid]),currentViewerFormSHA256=canonical(forms[uid]),unchangedActualBoundsSHA256=canonical(actual[uid]),baselineInventory=ref(PREVIOUS/'inventory.json.gz')));refs.append(sources[uid]);pulse()
 fresh=models[DELTA];source=sources[DELTA];assert ref(source)==install['asset']and fresh['sha256']==install['sourceSHA256']
 proof=packed_world_bounds(source.read_bytes());assert proof['allOriginalPositionVerticesAccounted']and proof['completeOriginalTriangles']==fresh['triangles']==13061
 row=dict(uid=DELTA,source=ref(source),rawCurrentEntry=fresh,currentBuilding=forms[DELTA],completeOriginalPOSITIONProof=proof)
 DOC.mkdir(parents=True);(DOC/'captured-current-manifest.json').write_bytes(manifestpath.read_bytes())
 save(DOC/'input.json.gz',dict(currentBoundOnly=True,currentActualBoundsDeltaOnly=True,currentManifest=start,completeNativeActors=6650,currentCatalogueRefs=catalogues,currentNativeViewerTileHashes=tiles,currentAllNativeSourceForms=forms,declaredDependencyUIDSourceHashes=dependencies,requiredUnchangedProductionClosure=required['inputHashes'],rows=[row],evidenceRefs=[ref(PREVIOUS/'result.json'),ref(PREVIOUS/'inventory.json.gz'),ref(PREVIOUS/'input.json.gz'),ref(oldmanifest),ref(INSTALLED/'root-independent-installed-readback.json')]))
 save(DOC/'dependency-form-census.json',dict(requestedDependencyUIDs=sorted(requested-set(models)),missingLegacyDeclaredUIDs=sorted(requested-set(forms)),newNamDependencies=sorted(new_dependencies),allNewNamDependenciesPresent=True,notNativeReacceptance=True))
 save(DOC/'complete-unchanged6649-current-bindings.json.gz',dict(currentManifest=start,completeOldActorsRebound=6649,rows=reuse,oldRuntimeRowsNotRecomputed=True,exactAllSourceFormEntryLoaderTuples=True))
 family_rows=[]
 for family in FAMILIES:
  folder=BASE/family;rc=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(rc['jobId'],)).fetchone()==('complete',rc)
  bindings=[]
  for q in rc['evidenceRefs']:
   actualpath=historical_ref(q,ROOT,oldmanifest);refs.append(actualpath);bindings.append(dict(originalReceiptRef=q,actualByteVersion=ref(actualpath),historicalManifestOnly=(q['path']=='3d-viewer/city/data/manifest.json')));pulse()
  refs.append(folder/'result.json');family_rows.append(dict(family=family,jobId=rc['jobId'],originalReceipt=ref(folder/'result.json'),completeBoundVersions=bindings,onlyHistoricalManifestPathResolved=True,currentInputEqualityByAllOtherRefs=True,noAutomaticPhysicsSupportOrAcceptanceCredit=True))
 save(DOC/'upton-per-family-exact-current-reuse-bindings.json.gz',dict(currentManifest=start,historicalManifest=ref(oldmanifest),families=family_rows,terrainCurrentSourceAndProductionOtherInputsByteExact=True))
 proc=subprocess.run(['node','--expose-gc',str(EXPORTER)],cwd=ROOT,capture_output=True,text=True);save(DOC/'export-log.json',dict(exitCode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr));assert proc.returncode==0,proc.stderr
 delta=read(DOC/'inventory.json.gz');assert delta['successfullyCapturedActors']==1 and not delta['errors']and delta['startAndEndInputHashesVerified']and [r['uid']for r in delta['rows']]==[DELTA]
 assert delta['completeRecursiveProductionModuleClosure']['inputHashes']==required['inputHashes']
 d=delta['rows'][0];bounds=[d['completeOriginalPOSITIONProof']['originalWholeSourceBounds'],d['completeLiteralBounds'],d['completeLeftAssociatedF32Bounds'],d['completeBalancedF32Bounds']];domain=[-2477.5,-37.5,-2267.5,102.5]
 separated=[(q[1][0]<domain[0]or q[0][0]>domain[2]or q[1][2]<domain[1]or q[0][2]>domain[3])for q in bounds]
 save(DOC/'composition.json.gz',dict(currentManifest=start,completeCurrentNativeActors=6650,completeOldActorsExactlyRebound=6649,baselineInventory=ref(PREVIOUS/'inventory.json.gz'),exactBaselineCurrentBinding=ref(DOC/'complete-unchanged6649-current-bindings.json.gz'),actualNewDelta=ref(DOC/'inventory.json.gz'),newUID=DELTA,allFourUnusedWorldBounds=bounds,uptonWholeParentDomain=domain,allFourBoundsStrictlyOutsideUptonDomain=all(separated),perWorldStrictSeparation=separated,overlapRequiresFullActualStreams=not all(separated),physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 assert ref(manifestpath)==start and reservations.owns(lease)
 for path,h in delta['inputHashes'].items():assert ref(ROOT/path)['sha256']==h;refs.append(ROOT/path)
 for path in refs:assert path.is_file()
 refs +=[METHOD,HELPER,Path(__file__),EXPORTER,PROPOSAL/'draft-pins.json',PROPOSAL/'literal-exporter-closure-preflight.json',PREVIOUS/'result.json',PREVIOUS/'input.json.gz',PREVIOUS/'inventory.json.gz',oldmanifest,INSTALLED/'root-independent-installed-readback.json',source,*[q for q in DOC.rglob('*')if q.is_file()]]
 # All current bound input/source bytes are rechecked at end; old-manifest archive
 # stays historical, never substituted into actual current runtime inputs.
 for q in catalogues:assert ref(ROOT/q['path'])=={k:q[k]for k in ['path','sha256']}
 for q in reuse:assert ref(ROOT/q['source']['path'])==q['source'];pulse()
 for path,h in tiles.items():assert ref(ROOT/path)['sha256']==h
 for fr in family_rows:
  for q in fr['completeBoundVersions']:assert ref(ROOT/q['actualByteVersion']['path'])==q['actualByteVersion'];pulse()
 # Final preparation/code/input/current fences run again immediately before
 # freeze; begin-only pin validation is insufficient after a long rebind.
 for q in pins['codeRefs']+pins['inputRefs']:
  assert ref(ROOT/q['path'])==q;refs.append(ROOT/q['path']);pulse()
 for path,h in closure['inputHashes'].items():assert ref(ROOT/path)['sha256']==h;refs.append(ROOT/path)
 for path,h in delta['inputHashes'].items():assert ref(ROOT/path)['sha256']==h;refs.append(ROOT/path)
 assert ref(manifestpath)==start and reservations.owns(lease);pulse(True)
 s=importlib.util.spec_from_file_location('nam_delta_source_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 result=m.freeze(BATCH,'post-nam-exact6649-current-tuple-reuse-plus-one-fresh-unused-attribute-matrix-bounds-delta',list(dict.fromkeys(refs)),dict(uids=[DELTA],currentManifest=start,completeNativeActors=6650,completeOldActorsExactlyRebound=6649,freshActualDeltaActors=1,sourceOnly=True,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 print(json.dumps(dict(jobId=result['jobId'],completeNativeActors=6650,freshActualDeltaActors=1)),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert '--capture-nam-delta-only'in sys.argv and not DOC.exists()and not LOCAL.exists()
 resources=['building:landsd/79099:0','building:landsd/45779:0','immutable-source-proof:'+BATCH]
 claim=reservations.claim('post-nam-native-delta-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()

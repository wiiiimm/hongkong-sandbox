"""UNEXECUTED existing raw physical guards on the exact overlap-reviewed candidate.
No construction; no full finite/ray/overlap replay; no body-role or install credit.
"""
from pathlib import Path
import copy,json,sys,time,uuid,subprocess
import numpy as np
from shapely.geometry import Polygon
from upton_exact_actual_history_archive_bindings_draft_v1_20261011 import load_contract,exact_ref
from run import ROOT,HERE,read,save,connect,reservations
from upton_geometry_bound_inherited_overlap_replay_draft_v1_20261012 import ref,check,module,code_paths,CURRENT,UIDS,FOREIGN,FREEZER
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-three-original-qualified-candidate-raw-physical-v2-20261012';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';PROPOSAL=BASE/(BATCH+'-proposal')
OWNED=UIDS[:3];RETAINED=UIDS[3]
META=BASE/'government-xl-upton-geometry-bound-inherited-overlap-replay-v1-20261012'
CAP=BASE/'government-xl-upton-whole-parent-current-domain-capture-v2-20261012'
RUNTIME=BASE/'government-xl-upton-three-original-complete-current-runtime-capture-v4-20261012'
AUD=BASE/'government-xl-upton-actual-candidate-clearance-measured-overlap-v2-20261012'
FINITE=BASE/'government-xl-upton-three-original-complete-current-finite-ground-v5-20261012'
IDENTITY=BASE/'government-xl-upton12728-12662-current-source-identification-rebind-v1-20261011'
TOOLS=[HERE/'acceptance-metrics.mjs',HERE.parent/'building-batch/validate_candidates.mjs',HERE/'check-neighbours.mjs',HERE/'check-native-neighbours.mjs',HERE/'native-neighbour-policy.mjs',HERE/'xl-final-script-pass.py']
HISTORY=dict(path='docs/astra-city/government-import/government-xl-upton-post-integration-current-capture-finite-proposal-v1-20261012/actual-before-integration-history-contract.json',sha256='987e458b0b50d21ae8c4dbba4e6b4dc01e7d60277e2cd6d375ce784e3434b531')
FAILED=BASE/'government-xl-upton-three-original-qualified-candidate-raw-physical-v1-20261012-proposal/preserved-failed-v1'
def history_bindings():
 contract=load_contract(ROOT,HISTORY['path'],HISTORY['sha256']);receipt=read(IDENTITY/'result.json');return [exact_ref(ROOT,q,contract)for q in receipt['evidenceRefs']+[ref(IDENTITY/'result.json')]]
def schema_only():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['inputRefs']:check(q)
 proof=read(META/'metadata-only-proof.json');assert proof['validator']['passed']and proof['allFieldsExceptSourceOverlapExactlyEqual'];check(proof['metadataOnlyCandidate']);data=read(CAP/'input.json.gz');rows=read(RUNTIME/'selection.json.gz')['rows'];assert [r['uid']for r in rows]==OWNED and data['expectedNativeCount']==6649 and len(data['basicRows'])==1911 and [r['uid']for r in data['nativeRows']]==[RETAINED]
 assert data['rederivedCoarseCells']==[457,449,460,451]and data['domain']==[-2477.5,-37.5,-2267.5,102.5]
 assert read(IDENTITY/'source-identification-only.json')['identityAccepted']and read(FINITE/'diagnostic.json.gz')['genuineBodyObligations']==749
 history_bindings()
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT
 return dict(passed=True,caller=ref(Path(__file__)),ownedUIDs=OWNED,retainedUID=RETAINED,completeOwnedFaces=13704,completeBasicForms=1911,noMathDBOrLease=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 schema_only();bindings=history_bindings();refs=[HISTORY]+[ref(p)for p in FAILED.iterdir()if p.is_file()]+[ref(HERE/'upton_exact_actual_history_archive_bindings_draft_v1_20261011.py')];refs+=[ref(Path(__file__)),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'schema-preflight.json')]+[ref(p)for p in code_paths()+TOOLS]
 for folder in[META,CAP,RUNTIME,AUD,FINITE,IDENTITY]:
  receipt=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for q in receipt['evidenceRefs']+[ref(folder/'result.json')]:
   actual=next(x['actualVerifiedFile']for x in bindings if x['originalEvidenceRef']==q)if folder==IDENTITY else q
   check(actual);refs.append(actual);pulse()
 for q in read(PROPOSAL/'draft-pins.json')['inputRefs']:check(q);refs.append(q)
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT;pulse(True)
 fence();inputs=read(CAP/'input.json.gz');proof=read(META/'metadata-only-proof.json');patch=check(proof['metadataOnlyCandidate']);manifest=read(ROOT/'3d-viewer/city/data/manifest.json');installed={e['uid']:e for cat in inputs['currentCatalogueRefs']for e in read(check(cat))['models']};assert len(installed)==6649 and not set(OWNED)&set(installed)
 DOC.mkdir(parents=True);save(DOC/'exact-historical-identity-receipt-bindings.json',dict(actualHistoricalBytesOnly=True,contract=HISTORY,bindings=bindings,currentRuntimeProofsStillStrictCurrent=True,noHistoricalIdentityToPhysicalTransfer=True));rows=copy.deepcopy(read(RUNTIME/'selection.json.gz')['rows'])
 for row in rows:
  original=ROOT/row['candidate']['path'];assert ref(original)['sha256']==row['sourceSHA256'];dest=LOCAL/row['candidate']['entry']['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(original.read_bytes());assert ref(dest)['sha256']==row['sourceSHA256'];row['candidate']['path']=str(dest.relative_to(ROOT));refs.append(ref(dest))
 save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=CURRENT));save(LOCAL/'catalogue.json',dict(schemaVersion=1,kind='diagnostic-original-support-catalogue',area=BATCH,crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=[r['candidate']['entry']for r in rows]));save(LOCAL/'catalogue-index.json',dict(models=3,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',{r['uid']:r['source']for r in rows})
 parententry=inputs['retainedParentEntry'];assert len(parententry)==1 and parententry[0]in manifest['terrainPatches']
 c=dict(id=read(patch)['id'],path=str(patch.relative_to(ROOT)),sha256=ref(patch)['sha256'],uids=OWNED,bounds=inputs['domain'],coarseCells=inputs['rederivedCoarseCells'],replaces=dict(url=parententry[0]['url'],sha256=inputs['retainedParent']['sha256'],retainedUids=[RETAINED]));save(DOC/'terrain-candidates.json',[c])
 forms={r['uid']:r['building']for r in inputs['basicRows']+inputs['nativeRows']+inputs['ownedRows']};allforms={f['uid']:f for f in inputs['completeCurrentForms']};deps={d['uid']for d in installed[RETAINED].get('supportDependencies',[])};nativeparent=allforms[RETAINED].get('parent')
 deps|={u for u in installed if nativeparent and allforms[u].get('parent')==nativeparent}
 for uid in deps:assert uid in allforms;forms[uid]=allforms[uid]
 assert set(OWNED+[RETAINED,FOREIGN])<=set(forms)
 save(DOC/'neighbour-inputs.json.gz',dict(rows=[dict(building=b,patchIndexes=[0],existingNative=u in installed or bool(b.get('modelGeometry')))for u,b in sorted(forms.items())],inputHashes={q['path']:q['sha256']for q in inputs['evidenceRefs']if q['path'].startswith('3d-viewer/city/data/tiles/')},candidateIds=OWNED,patches=[c]))
 save(DOC/'identity-source-only-binding.json',dict(sourceIdentity=ref(IDENTITY/'source-identification-only.json'),rootSourceCertificatePreservedByRuntimeReceipt=True,canStartTerrainWorkIsNotPhysicalOrRoleApproval=True,all23SourceCrossingsPreserved=True))
 # These are existing runtime/foreign/foundation contracts, not new topology gates.
 def call(args,allowed=(0,)):
  fence();p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);save(DOC/(Path(args[1]).stem+'-actual-log.json'),dict(exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode in allowed,p.stderr;fence()
 rel=lambda p:str(p.relative_to(ROOT));call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')])
 call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],(0,1))
 call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/']);call(['node',str(HERE/'check-native-neighbours.mjs'),rel(DOC)+'/'])
 runtime={r['uid']:r for r in read(LOCAL/'runtime-geometry.json.gz')['rows']};final=module(HERE/'xl-final-script-pass.py','upton_existing_foundation');foundations=[]
 for row in rows:
  g=runtime[row['uid']];tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert len(tri)==row['candidate']['entry']['triangles'];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);b=row['source']['building'];f=final.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));foundations.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],foundation=f,strictFoundationAccepted=f['completeTerrainTriangles']==f['triangles']and not f['fullyBuriedUpwardTriangles']and f['fullyBuriedAreaFraction']==0));pulse()
 save(DOC/'foundation.json',dict(rows=foundations,existingSampledContractOnly=True,completeOrdinaryFourWorldProof=ref(AUD/'complete-candidate-clearance.json.gz'),sourceGeometryChanges=0))
 raw=dict(metrics=ref(DOC/'metrics.json'),runtimeValidation=ref(DOC/'validation.json'),foundation=ref(DOC/'foundation.json'),foreignForms=ref(DOC/'neighbour-checks.json'),retainedNative=ref(DOC/'native-neighbour-checks.json'))
 save(DOC/'installation-gates-handoff.json',dict(rawPhysicalOutputs=raw,fullFiniteProofReused=ref(AUD/'complete-candidate-clearance.json.gz'),metadataOnlyTerrain=proof['metadataOnlyCandidate'],wholeCurrent6649SourceScope=ref(CAP/'input.json.gz'),full749GenuineBodyAnd17ZeroAccounting=ref(FINITE/'diagnostic.json.gz'),remainingTypedBodyPathsAndVisualRolesRequireQualification=True,all23ProperSourceCrossingsRetained=True,noSourceIdentityOrTerrainProofTransfersRootCredit=True,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 refs+=[ref(p)for p in DOC.rglob('*')if p.is_file()]+[ref(p)for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json'];fence();module(FREEZER,'upton_raw_physical_freezer').freeze(BATCH,'exact-reviewed-terrain-existing-runtime-foundation-and-foreign-gates-only',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=OWNED,currentManifestSHA256=CURRENT,sourceOnly=True,physicalAccepted=False,newlyInstalled=0,constructorOrTerrainNumericChanges=0))
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--check-existing-private-physical-only'in sys.argv and not DOC.exists()and not LOCAL.exists();resources=['building:'+u for u in UIDS+[FOREIGN]]+['terrain-patch:'+u for u in UIDS+[FOREIGN]]+['immutable-source-proof:'+BATCH];claim=reservations.claim('upton-existing-physical-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()

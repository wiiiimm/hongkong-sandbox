"""UNEXECUTED existing raw physical guards on the exact overlap-reviewed candidate.
No construction; no full finite/ray/overlap replay; no body-role or install credit.
"""
from pathlib import Path
import copy,json,sys,time,uuid,subprocess
import numpy as np
from shapely.geometry import Polygon
import upton_certified6170_source_bound_overlap_edge_validator_v2_20261014 as metadata
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from upton_current_nam_form_setup_v1_20261014 import merge_current_forms
import upton_certified6170_saved_actual_union_delta_v1_20261014 as finite
import upton_three_original_qualified_candidate_physical_draft_v2_20261012 as old_physical
from installed_support_acceptance import resolve_contact
from terrain_diagnostic_resolution import resolve_global_bottom_warning
from run import ROOT,HERE,read,save,connect,reservations
ref,check=metadata.ref,metadata.check;module=metadata.capture.legacy.module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-certified6170-two-original-current-physical-v3-20261014';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';PROPOSAL=BASE/(BATCH+'-proposal')
OWNED=['landsd/12728:0','landsd/338946:0'];SUPPORT,TOWER=OWNED;RETAINED=finite.baseline.NATIVE;FOREIGN=finite.baseline.FOREIGN;SECONDARY=finite.baseline.SECONDARY;CURRENT=finite.baseline.CURRENT;FREEZER=finite.baseline.FREEZER
CAP=finite.baseline.CAP;RUNTIME=BASE/'government-xl-upton-three-original-complete-current-runtime-capture-v4-20261012';ROOT_BODY=BASE/'government-xl-upton-three-original-complete-current-finite-ground-v5-20261012';IDENTITY=old_physical.IDENTITY;TOWER_IDENTITY=BASE/'government-xl-upton338946-podium12728-current-unchanged-owned-identity-v1-20261011'
TOOLS=[HERE/'acceptance-metrics.mjs',HERE.parent/'building-batch/validate_candidates.mjs',HERE/'check-neighbours.mjs',HERE/'check-native-neighbours.mjs',HERE/'original-support-closure-interfaces.mjs',HERE/'support-interface.mjs',HERE/'source-face-query.mjs',HERE/'native-neighbour-policy.mjs',HERE/'xl-final-script-pass.py',HERE/'acceptance-policy.py',HERE/'installed_support_acceptance.py',HERE/'terrain_diagnostic_resolution.py']

def tower_history_bindings():
 contract=old_physical.load_contract(ROOT,old_physical.HISTORY['path'],old_physical.HISTORY['sha256']);receipt=read(TOWER_IDENTITY/'result.json');out=[]
 archive=ref(TOWER_IDENTITY/'captured-manifest.json')
 for q in receipt['evidenceRefs']+[ref(TOWER_IDENTITY/'result.json')]:
  if q['path']=='3d-viewer/city/data/manifest.json' and q['sha256']==archive['sha256']:
   out.append(dict(originalEvidenceRef=q,actualVerifiedFile=archive,historicalArchiveUsed=True,explicitCompletedIdentityCapturedManifestOnly=True))
  else:out.append(old_physical.exact_ref(ROOT,q,contract))
 return out

NAM_PACKET=BASE/'government-xl-complete-native-actual-position-post-nam-delta-v1-20261013'
NAM_JOB='2202e62655e42b58e4e277e10dc2018be4e69ac99c4ef0b487cf5c98db8d239c'
def current_form_setup(inp,fresh):
 check(fresh['currentNamDeltaComposition']);composition=read(check(fresh['currentNamDeltaComposition']))
 receipt=read(NAM_PACKET/'result.json');verified=read(NAM_PACKET/'independent-completed-readback-summary.json')
 assert receipt['jobId']==verified['jobId']==NAM_JOB and verified['status']=='complete' and verified['terminalExitCode']==0
 assert verified['result']==ref(NAM_PACKET/'result.json') and verified['composition']==fresh['currentNamDeltaComposition']
 assert verified['allEvidenceRefsVerified']==len(receipt['evidenceRefs']) and verified['allFourUnusedBoundsStrictlyDisjoint']
 assert all(not row['active'] and row['releasedAt']for row in verified['allBatchReservationGroupsReleased'])
 naminput=read(NAM_PACKET/'input.json.gz');inventory=read(check(composition['actualNewDelta']))
 live=read(ROOT/'3d-viewer/city/data/manifest.json');installed={}
 for url in live['officialModelCatalogues']:
  for e in read(ROOT/'3d-viewer'/url)['models']:assert e['uid']not in installed;installed[e['uid']]=e
 for q in naminput['currentCatalogueRefs']:check(q)
 for path,digest in naminput['currentNativeViewerTileHashes'].items():check(dict(path=path,sha256=digest))
 source=naminput['rows'][0]['source'];check(source)
 form=naminput['rows'][0]['currentBuilding'];tile=ROOT/'3d-viewer/city/data/tiles'/(form['tile']+'.json')
 assert next(b for b in read(tile)['buildings']if b['uid']==form['uid'])==form
 return merge_current_forms(inp['completeCurrentForms'],installed,naminput,inventory,composition,current_manifest=CURRENT,domain=inp['domain'])

def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 receipt=read(metadata.DOC/'result.json');v=read(metadata.DOC/'ROOT-VERIFIED.json');assert receipt['jobId']==pins['completedMetadataJob']==v['jobId'] and v['exactNeonReadback'] and v['allEvidenceHashesVerified'] and v['leaseReleased']
 proof=read(metadata.DOC/'metadata-only-proof.json');assert proof['validator']['passed'] and proof['allFieldsExceptSourceOverlapExactlyEqual'];check(proof['metadataOnlyCandidate'])
 rows=[r for uid in OWNED for r in read(RUNTIME/'selection.json.gz')['rows']if r['uid']==uid];assert [r['uid']for r in rows]==OWNED and sum(r['candidate']['entry']['triangles']for r in rows)==13312
 for r in rows:assert ref(ROOT/r['candidate']['path'])['sha256']==r['sourceSHA256']==r['candidate']['entry']['sha256']
 inp=read(CAP/'input.json.gz');fresh=read(metadata.capture.DOC/'input.json.gz');assert inp['domain']==fresh['domain']==finite.baseline.DOMAIN and inp['rederivedCoarseCells']==fresh['coarseCells']==[457,449,460,451] and len(inp['basicRows'])==1911
 for q in fresh['allCurrentInputRefs']:check(q)
 old_physical.history_bindings();tower_history_bindings();tower_identity=next(r for r in read(TOWER_IDENTITY/'identities.json')['rows']if r['uid']==TOWER)['rawFullCellIdentity'];assert tower_identity['passed'] and tower_identity['sourceSHA256']==rows[1]['sourceSHA256']
 identified=read(IDENTITY/'source-identification-only.json');assert identified['identityAccepted'] and identified['uid']==SUPPORT and identified['sourceSHA256']==rows[0]['sourceSHA256'] and not identified['physicalAccepted'] and not identified['rootCredit'] and not identified['foreignCollisionExemption']
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT
 setup=current_form_setup(inp,fresh)
 return pins,proof,rows,inp,fresh,identified,setup

def schema_only():
 p,proof,rows,inp,fresh,identified,setup=load();return dict(passed=True,caller=ref(Path(__file__)),ownedUIDs=OWNED,completeOwnedFacets=13312,sourceOnlyIdentityNotRootOrPhysicalCredit=True,currentNativeScope=6650,all1911BASIC52AffectedAndFourModeOrdinaryEvidenceRetained=True,secondary12662StrictlyForeign=True,strictOriginalPair=dict(uid=TOWER,supportUid=SUPPORT),noMetricsSupportFoundationRuntimeIdentityDBLeaseOrWorker=True)

def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins,proof,source_rows,inputs,fresh,identified,setup=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed'] and prep['caller']==ref(Path(__file__))
 bindings=old_physical.history_bindings()+tower_history_bindings();refs=pins['codeRefs']+pins['inputRefs']+[ref(Path(__file__)),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'actual-readonly-preparation.json')]+prep['evidenceRefs']
 for folder in [metadata.DOC,metadata.capture.DOC,finite.DOC,IDENTITY,TOWER_IDENTITY,NAM_PACKET]:
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for q in receipt['evidenceRefs']+[ref(folder/'result.json')]:
   actual=next(x['actualVerifiedFile']for x in bindings if x['originalEvidenceRef']==q)if folder in [IDENTITY,TOWER_IDENTITY] else q
   check(actual);refs.append(actual);pulse()
 def fence():
  for q in distinct_refs(refs):check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT;pulse(True)
 fence();patch=check(proof['metadataOnlyCandidate']);manifest=read(ROOT/'3d-viewer/city/data/manifest.json');installed={e['uid']:e for url in manifest['officialModelCatalogues']for e in read(ROOT/'3d-viewer'/url)['models']};assert len(installed)==6650 and not set(OWNED)&set(installed)
 DOC.mkdir(parents=True);save(DOC/'exact-historical-identity-receipt-bindings.json',dict(actualHistoricalBytesOnly=True,contract=old_physical.HISTORY,bindings=bindings,currentRuntimeProofsStillStrictCurrent=True,noHistoricalIdentityToPhysicalTransfer=True));rows=copy.deepcopy(source_rows)
 for row in rows:
  original=ROOT/row['candidate']['path'];assert ref(original)['sha256']==row['sourceSHA256'];dest=LOCAL/row['candidate']['entry']['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(original.read_bytes());assert ref(dest)['sha256']==row['sourceSHA256'];row['candidate']['path']=str(dest.relative_to(ROOT));refs.append(ref(dest))
 save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=CURRENT));save(LOCAL/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',counts=dict(packedModels=2),area=BATCH,crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=[r['candidate']['entry']for r in rows]));save(LOCAL/'catalogue-index.json',dict(models=2,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',{r['uid']:r['source']for r in rows})
 parententry=inputs['retainedParentEntry'];assert len(parententry)==1 and parententry[0]in manifest['terrainPatches']
 c=dict(id=read(patch)['id'],path=str(patch.relative_to(ROOT)),sha256=ref(patch)['sha256'],uids=OWNED,bounds=inputs['domain'],coarseCells=inputs['rederivedCoarseCells'],replaces=dict(url=parententry[0]['url'],sha256=inputs['retainedParent']['sha256'],retainedUids=[RETAINED]));save(DOC/'terrain-candidates.json',[c])
 forms={r['uid']:r['building']for r in inputs['basicRows']+inputs['nativeRows']+inputs['ownedRows']};allforms=setup['currentForms'];deps={d['uid']for d in installed[RETAINED].get('supportDependencies',[])};nativeparent=allforms[RETAINED].get('parent')
 deps|={u for u in installed if nativeparent and allforms[u].get('parent')==nativeparent}
 for uid in deps:assert uid in allforms;forms[uid]=allforms[uid]
 assert set(OWNED+[RETAINED,FOREIGN,SECONDARY])<=set(forms)
 save(DOC/'neighbour-inputs.json.gz',dict(rows=[dict(building=b,patchIndexes=[0],existingNative=u in installed or bool(b.get('modelGeometry')))for u,b in sorted(forms.items())],inputHashes={q['path']:q['sha256']for q in inputs['evidenceRefs']if q['path'].startswith('3d-viewer/city/data/tiles/')},candidateIds=OWNED,patches=[c]))
 save(DOC/'identity-source-only-binding.json',dict(sourceIdentity=ref(IDENTITY/'source-identification-only.json'),rootSourceCertificatePreservedByRuntimeReceipt=True,canStartTerrainWorkIsNotPhysicalOrRoleApproval=True,all23SourceCrossingsPreserved=True))
 save(DOC/'current-native-form-setup.json',dict(**{k:v for k,v in setup.items()if k!='currentForms'},completedNamPacket=ref(NAM_PACKET/'result.json'),completeCurrentForms=len(setup['currentForms']),all6650InstalledFormsExactlyCurrent=True));save(DOC/'support-inputs.json',dict(sources=rows,pairs=[dict(uid=TOWER,supportUid=SUPPORT)]))
 # Existing complete strict original interface; no same-parent/low-point substitute.
 # These are existing runtime/foreign/foundation contracts, not new topology gates.
 def call(args,allowed=(0,)):
  fence();p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);save(DOC/(Path(args[1]).stem+'-actual-log.json'),dict(exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode in allowed,p.stderr;fence()
 rel=lambda p:str(p.relative_to(ROOT));call(['node',str(HERE/'original-support-closure-interfaces.mjs'),rel(DOC)+'/']);call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')])
 call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],(0,1))
 call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/']);call(['node',str(HERE/'check-native-neighbours.mjs'),rel(DOC)+'/'])
 runtime={r['uid']:r for r in read(LOCAL/'runtime-geometry.json.gz')['rows']};final=module(HERE/'xl-final-script-pass.py','upton_fresh_compound_foundation');policy=module(HERE/'acceptance-policy.py','upton_unchanged_numeric_policy');foundations=[];decisions=[];reasons=[]
 def body(g):return np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 supports=read(DOC/'support-checks.json.gz');assert len(supports['rows'])==1;interface=supports['rows'][0];assert interface['uid']==TOWER and interface['supportUid']==SUPPORT and interface['sourceSHA256']==rows[1]['sourceSHA256'] and interface['supportSHA256']==rows[0]['sourceSHA256']
 for p,h in supports['inputHashes'].items():check(dict(path=p,sha256=h))
 metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json');metric_rows={r['uid']:r for r in metrics['rows']};val_rows={r['uid']:r for r in validation['results']}
 # Existing raw whole source ownership/current projection records remain negative
 # where negative. Accepted precise identification grants no crossing/root credit.
 raw_identity=read(IDENTITY/'identities.json');save(DOC/'identity-source-interpretation-and-raw-negatives.json',dict(sourceOnlyInterpretationVerbatim=identified,priorRawOriginalIdentityVerbatim=raw_identity,exactHistoricalVersionBindings=bindings,physicalRootSupportAnd23CrossingsIndependent=True))
 for row in rows:
  uid=row['uid'];g=runtime[uid];tri=body(g);assert len(tri)==row['candidate']['entry']['triangles'];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3)
  if uid==TOWER:ground=np.concatenate([ground,body(runtime[SUPPORT])])
  b=row['source']['building'];f=final.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));proofrow=dict(uid=uid,sourceSHA256=row['sourceSHA256'],foundation=f,strictFoundationAccepted=f['completeTerrainTriangles']==f['triangles']and not f['fullyBuriedUpwardTriangles']and f['fullyBuriedAreaFraction']==0);foundations.append(proofrow);pulse()
  diag=resolve_global_bottom_warning(val_rows[uid],metric_rows[uid],proofrow)
  # ExactObject/CSUID routing and original unchanged source preserve source identity;
  # explicit identification is the scoped accepted12728 source interpretation only.
  tower_identity=next(r for r in read(TOWER_IDENTITY/'identities.json')['rows']if r['uid']==TOWER)['rawFullCellIdentity']
  assert tower_identity['passed'] and tower_identity['sourceSHA256']==rows[1]['sourceSHA256']
  identityproof=identified['proof']if uid==SUPPORT else tower_identity['proof']
  raw=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=row['sourceSHA256'],identityProof=identityproof),metric_rows[uid],metrics['profiles']['mobile'])
  remaining=resolve_contact(raw,interface['interface'],proofrow)if uid==TOWER else raw;warnings=resolve_contact(diag['remaining'],interface['interface'],proofrow)if uid==TOWER else diag['remaining'];decisions.append(dict(uid=uid,rawPolicyReasons=raw,rawDiagnosticReasons=diag['remaining'],remainingPolicyReasons=remaining,remainingDiagnosticReasons=warnings,diagnosticResolution=diag));reasons.extend(uid+':'+r for r in remaining+warnings)
  if not proofrow['strictFoundationAccepted']:reasons.append(uid+':whole-source-foundation')
 strict=interface['interface'];strictpass=strict['passed'] and strict['samples']>0 and strict['strictContacts']==strict['samples'] and strict['wallIntersections']==0 and not strict['unresolved']
 if not strictpass:reasons.append('original-support-interface-unresolved')
 if validation['checksPassed']!=2 or validation['loaderAccepted']!=2 or validation['exceptions']:reasons.append('runtime-validation')
 native=read(DOC/'native-neighbour-checks.json');resolved=set(native['resolved']);reasons.extend('native-neighbour-regression:'+u for u in set(native['blocked'])-resolved);reasons.extend('terrain-regresses-neighbour:'+r['uid']for r in read(DOC/'neighbour-checks.json')['rows']if r['reasons'] and r['uid']not in resolved)
 save(DOC/'foundation.json',dict(rows=foundations,existingCompleteCompoundContractUnchanged=True,completeOrdinaryFourWorldProof=ref(finite.DOC/'complete-actual-union-finite-delta.json.gz'),sourceGeometryChanges=0));save(DOC/'support-ground-resolution.json',dict(rows=decisions,strictInterface=strict,modelGeometryChanges=0,publication=False));save(DOC/'current-physical-raw-gates.json',dict(ordinaryExistingPhysicalToolsPassed=not reasons,rawReasons=sorted(set(reasons)),originalSourceOnlyIdentityAndAllRawSpatialNegativesRetained=True,source737BodyTypedRootPathsAnd23ProperOriginalCrossingsStillRequireCompleteQualification=True,originalRootBodyPacket=ref(ROOT_BODY/'diagnostic.json.gz'),secondary12662ForeignNoSupportOrJointCredit=True,metadataOnlyTerrain=proof['metadataOnlyCandidate'],fullScope6650All1911Basic52AffectedAndFourModeNegatives=ref(finite.DOC/'complete-actual-union-finite-delta.json.gz'),physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 refs+=[ref(p)for p in DOC.rglob('*')if p.is_file()]+[ref(p)for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json'];fence();module(FREEZER,'upton_certified6170_physical_freezer').freeze(BATCH,'certified6170-two-original-fresh-strict-support-compound-foundation-runtime-foreign-gates',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=OWNED,currentManifestSHA256=CURRENT,sourceOnly=True,physicalAccepted=False,newlyInstalled=0,constructorOrTerrainNumericChanges=0))
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--check-fresh-two-original-current-physical-only'in sys.argv and not DOC.exists() and not LOCAL.exists();load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed'] and prep['caller']==ref(Path(__file__))
 uids=finite.baseline.OWNED+[SECONDARY,RETAINED,FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH];claim=reservations.claim('upton-certified6170-physical-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

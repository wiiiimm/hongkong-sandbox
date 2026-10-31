"""UNEXECUTED metadata-schema recovery; reuse actual v2 outputs, only missing validator runs."""
from pathlib import Path
import copy,json,sys,time,uuid,subprocess
import upton_three_original_qualified_candidate_physical_draft_v2_20261012 as prior
from run import ROOT,HERE,read,save,connect,reservations
from upton_geometry_bound_inherited_overlap_replay_draft_v1_20261012 import ref,check,module,code_paths,CURRENT,UIDS,FOREIGN,FREEZER
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-three-original-qualified-candidate-raw-physical-v3-20261012';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';PROPOSAL=BASE/(BATCH+'-proposal')
OWNED=UIDS[:3];RETAINED=UIDS[3];OLD=prior.DOC;OLDLOCAL=prior.LOCAL
FAILURE=prior.PROPOSAL/'preserved-failed-v2/actual-failure-and-release-audit.json'
TEMPLATE=HERE/'local/government-xl-terrain-recovery-elements-sun-star-unchanged-current-physical-v1-20261011/catalogue.json'
TEMPLATE_VALIDATION=BASE/'government-xl-terrain-recovery-elements-sun-star-unchanged-current-physical-v1-20261011/validation.json'
REUSED=['metrics.json','foundation.json','neighbour-checks.json','native-neighbour-checks.json','selection.json.gz','terrain-candidates.json','neighbour-inputs.json.gz','identity-source-only-binding.json','exact-historical-identity-receipt-bindings.json']
def corrected_catalogue():
 old=read(OLDLOCAL/'catalogue.json');template=read(TEMPLATE)
 assert template['kind']=='staged-official-model-catalogue'and template['counts']['packedModels']==len(template['models'])
 new=copy.deepcopy(old);new['kind']=template['kind'];new['counts']=dict(packedModels=len(new['models']))
 bare=copy.deepcopy(new);bare['kind']=old['kind'];bare.pop('counts');assert bare==old and len(new['models'])==3
 return new

def schema_only():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['inputRefs']:check(q)
 assert prior.schema_only()['passed'];audit=read(FAILURE)
 assert audit['noCompletedJob']and audit['actualJobCount']==0 and audit['missingValidationOutput']and all(not q['active']and q['releasedAt']for q in audit['allBatchGroupsReleased'])
 for q in audit['actualProducedFiles']:check(q)
 assert not(OLD/'validation.json').exists()and not(OLD/'result.json').exists()
 for name in REUSED:assert (OLD/name).is_file()
 logs=[read(OLD/(n+'-actual-log.json'))for n in ['acceptance-metrics','check-neighbours','check-native-neighbours']];assert all(q['exitCode']==0 for q in logs)
 assert read(OLD/'validate_candidates-actual-log.json')['exitCode']==1
 new=corrected_catalogue();oldrows=read(OLD/'selection.json.gz')['rows'];assert [r['uid']for r in oldrows]==OWNED and new['models']==[r['candidate']['entry']for r in oldrows]
 for row in oldrows:assert ref(ROOT/row['candidate']['path'])['sha256']==row['sourceSHA256']==row['candidate']['entry']['sha256']
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT
 return dict(passed=True,caller=ref(Path(__file__)),onlyCatalogueKindAndPackedModelsCountChanged=True,reusedRawOutputRefs=[ref(OLD/n)for n in REUSED],validatorOnly=True,noMathDBOrLease=True)

def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 schema_only();pre=read(PROPOSAL/'schema-preflight.json');assert pre['passed']and pre['caller']==ref(Path(__file__))and pre['validatorOnly']
 refs=[ref(p)for p in code_paths()+prior.TOOLS]+[ref(Path(__file__)),ref(Path(prior.__file__)),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'schema-preflight.json'),ref(FAILURE),ref(TEMPLATE),ref(TEMPLATE_VALIDATION),prior.HISTORY]
 refs += read(FAILURE)['actualProducedFiles']+read(FAILURE)['preservedFailedAttemptFiles']
 bindings=prior.history_bindings()
 for folder in[prior.META,prior.CAP,prior.RUNTIME,prior.AUD,prior.FINITE,prior.IDENTITY]:
  receipt=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for q in receipt['evidenceRefs']+[ref(folder/'result.json')]:
   actual=next(x['actualVerifiedFile']for x in bindings if x['originalEvidenceRef']==q)if folder==prior.IDENTITY else q
   check(actual);refs.append(actual);pulse()
 refs += read(PROPOSAL/'draft-pins.json')['inputRefs']
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT;pulse(True)
 fence();DOC.mkdir(parents=True)
 for row in read(OLD/'selection.json.gz')['rows']:
  oldasset=ROOT/row['candidate']['path'];dest=LOCAL/row['candidate']['entry']['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(oldasset.read_bytes());assert ref(dest)['sha256']==row['sourceSHA256'];refs.append(ref(dest))
 for name in ['catalogue-index.json','source-forms.json']:
  dest=LOCAL/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((OLDLOCAL/name).read_bytes());assert dest.read_bytes()==(OLDLOCAL/name).read_bytes();refs.append(ref(dest))
 save(LOCAL/'catalogue.json',corrected_catalogue());refs.append(ref(LOCAL/'catalogue.json'))
 reuse=[]
 for name in REUSED:
  dest=DOC/name;dest.write_bytes((OLD/name).read_bytes());assert dest.read_bytes()==(OLD/name).read_bytes();reuse.append(dict(original=ref(OLD/name),byteIdenticalCopy=ref(dest)));refs.append(ref(dest))
 save(DOC/'schema-correction-and-exact-output-reuse.json',dict(failedV2=ref(FAILURE),originalCatalogue=ref(OLDLOCAL/'catalogue.json'),correctedCatalogue=ref(LOCAL/'catalogue.json'),successfulOriginalCatalogueTemplate=ref(TEMPLATE),templateValidation=ref(TEMPLATE_VALIDATION),changedFields=['kind','counts.packedModels'],allOtherCatalogueFieldsExactlyEqual=True,reusedOutputs=reuse,metricsNeighboursNativeFoundationRerun=False))
 fence();args=['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',str(LOCAL.relative_to(ROOT)),'--source-forms',str((LOCAL/'source-forms.json').relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'validation.json').relative_to(ROOT))]
 actual=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);save(DOC/'validate_candidates-actual-log.json',dict(command=args,exitCode=actual.returncode,stdout=actual.stdout,stderr=actual.stderr));fence()
 assert actual.returncode in(0,1),actual.stderr
 output=ref(DOC/'validation.json')if(DOC/'validation.json').is_file()else None
 raw=dict(metrics=ref(DOC/'metrics.json'),runtimeValidation=output,foundation=ref(DOC/'foundation.json'),foreignForms=ref(DOC/'neighbour-checks.json'),retainedNative=ref(DOC/'native-neighbour-checks.json'))
 save(DOC/'installation-gates-handoff.json',dict(rawPhysicalOutputs=raw,sixBasicSavedGapAndFiniteReconciliation=ref(PROPOSAL/'six-basic-gap-versus-saved-full-finite-reconciliation.json'),validatorProcessExitCode=actual.returncode,validatorOutputActuallyCreated=output is not None,reuseProvenance=ref(DOC/'schema-correction-and-exact-output-reuse.json'),fullFiniteProofReused=ref(prior.AUD/'complete-candidate-clearance.json.gz'),metadataOnlyTerrain=read(prior.META/'metadata-only-proof.json')['metadataOnlyCandidate'],wholeCurrent6649SourceScope=ref(prior.CAP/'input.json.gz'),full749GenuineBodyAnd17ZeroAccounting=ref(prior.FINITE/'diagnostic.json.gz'),remainingTypedBodyPathsAndVisualRolesRequireQualification=True,all23ProperSourceCrossingsRetained=True,sixBasicIncreasedGapFindingsRetained=True,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 refs+=[ref(p)for p in DOC.rglob('*')if p.is_file()]+[ref(p)for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json'];fence()
 module(FREEZER,'upton_validator_schema_recovery_freezer').freeze(BATCH,'metadata-only-private-catalogue-schema-and-existing-validator-replay',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=OWNED,currentManifestSHA256=CURRENT,sourceOnly=True,physicalAccepted=False,newlyInstalled=0,constructorOrTerrainNumericChanges=0,validatorOnlyRerun=True,validatorProcessExitCode=actual.returncode,validatorOutputActuallyCreated=output is not None))
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--reuse-existing-private-physical-only'in sys.argv and not DOC.exists()and not LOCAL.exists()
 resources=['building:'+u for u in UIDS+[FOREIGN]]+['terrain-patch:'+u for u in UIDS+[FOREIGN]]+['immutable-source-proof:'+BATCH];claim=reservations.claim('upton-validator-schema-recovery-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()

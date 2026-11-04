"""Fresh saved-site actual full-native MAX/ray; no overlap approval or geometry edit."""
from pathlib import Path
import json,sys,time,uuid,subprocess
import numpy as np
import upton_certified6170_actual_production_capture_v1_20261014 as capture
from upton_v6_saved64_actual_max_geometry_bound_validator_draft_v1_20261013 import canonical
from run import ROOT,HERE,read,save,connect,reservations
ref,check=capture.ref,capture.check
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-certified6170-saved64-actual-max-v1-20261014'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';RUNTIME=HERE/'upton_certified6170_saved64_actual_max_runtime_v1_20261014.mjs'
def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__)) and pins['runtime']==ref(RUNTIME)
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 receipt=read(capture.DOC/'result.json');v=read(capture.DOC/'ROOT-VERIFIED.json');assert receipt['jobId']==pins['completedCaptureJob']==v['jobId'] and v['exactNeonReadback'] and v['allEvidenceHashesVerified'] and v['leaseReleased']
 _,_,nom,raw,pv,inp,whole=capture.load();patch=read(capture.DOC/'private-native-terrain-candidate.json.gz');assert canonical(patch)==pins['geometryCanonicalSHA256'] and not patch['nativeMesh'].get('sourceOverlap')
 measured=read(capture.DOC/'new-scoped-geometry-measured-overlap.json.gz')['measured'];assert measured['candidateGeometryCanonicalSHA256']==pins['geometryCanonicalSHA256'] and measured['completeCandidateFaces']==pins['completeNewNativeFacets']==len(raw)
 assert measured['nativeProjectedExcessM2']==pins['actualMeasuredExcessM2'] and measured['float32HighestRayAgreement']['samples']==len(measured['float32HighestRayAgreement']['rows'])==64
 pos=np.asarray(patch['nativeMesh']['position'],dtype='<f8').reshape(-1,3);ix=np.asarray(patch['nativeMesh']['index'],dtype=np.int64).reshape(-1,3);assert pos[ix].tobytes()==raw.tobytes()
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==capture.legacy.CURRENT
 return pins,patch,measured,whole
def schema_only():
 pins,p,m,whole=load();return dict(passed=True,caller=ref(Path(__file__)),runtime=ref(RUNTIME),completeNewNativeFacets=pins['completeNewNativeFacets'],canonicalGeometrySHA256=pins['geometryCanonicalSHA256'],actualSavedSites=64,noProductionMAXRayGeometryDBLeaseOrApproval=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease) and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok'] and reservations.owns(lease);last=time.monotonic()
 pins,patch,measured,whole=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed'] and prep['caller']==ref(Path(__file__)) and prep['runtime']==ref(RUNTIME)
 closure=read(PROPOSAL/'actual-literal-runtime-closure-preflight.json');assert closure['computedImportsRejected'] and closure['completeAuditedLiteralImportClosure'] and closure['unsupportedDynamicImports']==0 and closure['entryPath']==str(RUNTIME.relative_to(ROOT))
 refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'actual-readonly-preparation.json'),ref(PROPOSAL/'actual-literal-runtime-closure-preflight.json')]+prep['evidenceRefs']+[dict(path=k,sha256=v)for k,v in closure['inputHashes'].items()]
 receipt=read(capture.DOC/'result.json')
 with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(pins['completedCaptureJob'],)).fetchone()==('complete',receipt)
 refs+=[ref(capture.DOC/'result.json')]+receipt['evidenceRefs'];refs=list({(q['path'],q['sha256']):q for q in refs}.values())
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==capture.legacy.CURRENT and reservations.owns(lease)
 fence();DOC.mkdir();save(DOC/'input.json.gz',dict(currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),candidate=ref(capture.DOC/'private-native-terrain-candidate.json.gz'),measuredOverlap=ref(capture.DOC/'new-scoped-geometry-measured-overlap.json.gz'),geometryCanonicalSHA256=pins['geometryCanonicalSHA256'],completeNewNativeFacets=pins['completeNewNativeFacets'],runtimeInputRefs=pins['inputRefs']+[dict(path=k,sha256=v)for k,v in closure['inputHashes'].items()]))
 cmd=['node',str(RUNTIME),str(DOC.relative_to(ROOT))]
 with (DOC/'actual-saved64-runtime.log').open('xb')as log:r=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 save(DOC/'actual-runtime-command.json',dict(command=cmd,exitCode=r.returncode,noGeometryChanges=True,noApprovalWritten=True));pulse(True)
 rays=None
 if r.returncode==0:
  rays=read(DOC/'actual-saved64-full-candidate-native-max-ray-findings.json.gz');assert rays['samples']==len(rays['rows'])==64 and rays['completeCandidateFacets']==pins['completeNewNativeFacets'] and rays['startEndAllInputsVerified'] and rays['noGeometryChanges'] and rays['noApprovalWrittenByRuntime']
  refs+=[dict(path=k,sha256=v)for k,v in rays['inputHashes'].items()]+[dict(path=k,sha256=v)for k,v in rays['completeRecursiveProductionModuleClosure']['inputHashes'].items()]
 save(DOC/'diagnostic.json.gz',dict(canonicalNewGeometrySHA256=pins['geometryCanonicalSHA256'],actualMeasuredExcessM2=pins['actualMeasuredExcessM2'],runtimeExitCode=r.returncode,actualSavedSiteMAXRayResult=ref(DOC/'actual-saved64-full-candidate-native-max-ray-findings.json.gz')if rays else None,allLatestFullFiniteNegativesVerbatim=whole['latestFullFiniteNegativesVerbatim'],rawValidatorFailurePreserved=ref(capture.DOC/'real-validator-outcome.json'),noMetadataApprovalOrValidatorWaiver=True,savedSitesNotCompleteContinuousMAXRootSupportOrInstallationProof=True,freshFiniteAllPairsAncestorsCanonicalBoundaryRuntimeBrowserStillMandatory=True,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 fence();refs+=[ref(p)for p in DOC.rglob('*')if p.is_file()]
 capture.legacy.module(capture.legacy.FREEZER,'upton_certified6170_max_freezer').freeze(BATCH,'certified6170-fresh-saved64-actual-full-native-max-ray-only',[check(q)for q in refs],dict(uids=capture.legacy.OWNED+[capture.legacy.SECONDARY,capture.legacy.NATIVE],sourceOnly=True,physicalAccepted=False,newlyInstalled=0))
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--check-certified6170-saved64-actual-max-only'in sys.argv and not DOC.exists() and not LOCAL.exists();load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed'] and prep['caller']==ref(Path(__file__)) and prep['runtime']==ref(RUNTIME)
 uids=capture.legacy.OWNED+[capture.legacy.SECONDARY,capture.legacy.NATIVE,capture.legacy.FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('upton-certified6170-max-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

"""Source-bound IFC applicability; preserve failed numeric checks, no publication."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ifc-mall-functional-applicability-v1-20261019';DOC=BASE/BATCH
UID='landsd/64856:0';SHA='d0cf990103d9c85bd3adc101d015de2eeed97314cfaaed14b88e0dd8d87c7b5f'
def folder(name):return BASE/('government-xl-ifc-mall-'+name+'-20261019')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 names=['original-column-review-v2','loader-v1','loader-warning-audit-v1','identity-review-v1','unchanged-four-mode-foundations-v1','unchanged-ground-v1']
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for name in names:
   p=folder(name)/'result.json';r=read(p)
   assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   refs.append(p)
   for e in r['evidenceRefs']:
    assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 review=read(folder('original-column-review-v2')/'ROOT-GRADE-REVIEW.json')
 assert review['sourceSHA256']==SHA and review['sourceSpecificGradeInterpretationAccepted'] and review['oneExactSharedEdgeComponent']
 assert review['sourceFaces']==list(range(6121,6168))+[26239]
 assert review['strictTerrainIntersectionCheckPassed'] is False
 identity=read(folder('identity-review-v1')/'64856:0-review.json');assert identity['identityOnlyApproved'] and identity['sourceSHA256']==SHA
 metrics=read(folder('unchanged-ground-v1')/'metrics.json');m=metrics['rows'][0]
 assert m['uid']==UID and m['sourceSHA256']==SHA and m==review['rawNumericMetrics']
 policy=module('ifc_functional_policy',HERE/'acceptance-policy.py')
 raw=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SHA,identityProof=identity['identityProof']),m,metrics['profiles']['mobile'])
 assert raw==review['rawPolicyReasons']==['terrain-intersects-source-over-0.5m']
 validation=read(folder('loader-v1')/'validation.json')
 assert validation['models']==validation['loaderAccepted']==validation['checksPassed']==1 and validation['exceptions']==0
 assert len(validation['results'])==1 and validation['results'][0]['uid']==UID
 assert validation['results'][0]['concerns']==['sampled-terrain-above-model-bottom']
 for p,h in validation['hashes'].items():assert digest((ROOT/p).read_bytes())==h,p
 audit=read(folder('loader-warning-audit-v1')/'audit.json');assert audit['canonicalWarningResolved'] is False and len(audit['modes'])==4
 bindings=[]
 for b in review['sourceBindings']:
  f=read(folder('unchanged-four-mode-foundations-v1')/('64856:0-'+b['mode']+'.json'))
  assert f['uid']==UID and f['sourceSHA256']==b['sourceSHA256']==SHA and f['wholeWorldSHA256']==b['wholeWorldSHA256']
  assert f['strictFoundationAccepted'] and f['foundation']['completeTerrainTriangles']==36305 and f['foundation']['fullyBuriedTriangles']==0 and f['foundation']['fullyBuriedUpwardTriangles']==0
  bindings.append(dict(uid=UID,**b))
 assert read(folder('unchanged-ground-v1')/'terrain-candidates.json')==read(folder('loader-v1')/'terrain-candidates.json')==[]
 qualification=dict(uids=[UID],sourceBindings=bindings,sourceScopedApplicabilityAccepted=True,rawPolicyReasons=raw,resolvedByExactSourceFunctionalApplicability=raw,remainingPhysicalReasons=[],identityReview=ref(folder('identity-review-v1')/'64856:0-review.json'),gradeReview=ref(folder('original-column-review-v2')/'ROOT-GRADE-REVIEW.json'),loaderWarningAudit=ref(folder('loader-warning-audit-v1')/'audit.json'),rawLoaderConcerns=validation['results'][0]['concerns'],canonicalLoaderWarningResolved=False,strictTerrainIntersectionCheckPassed=False,loaderConcernSourceSpecificInterpretation='The global-minimum-versus-remote-ground diagnostic is superseded here by all36305 actual faces in four coordinate modes. No wholly buried or upward floor face occurs. The only local over0.5m crossing comprises the exact48 exposed vertical column faces identified in the pinned original-column review. This is source-specific functional applicability; neither canonical numeric check is relabelled passed.',completeLoaderPickingCollisionPassed=True,terrainReplacement=False,neighbourTerrainRegressionRequired=False,neighbourTerrainRationale='No terrain bytes or existing actor bytes/pose are changed. Staged/live retained original visibility checks remain required; legacy tower support failures are not resolved by this mall installation.',sourceGeometryChanges=0,sourcePoseChanges=0,publication=False,installationApproved=False,stagedLiveBrowserStillRequired=True,currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'))
 save(DOC/'qualification.json',qualification)
 refs.extend([HERE/'acceptance-policy.py',HERE/'terrain_diagnostic_resolution.py'])
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('ifc_functional_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'ifc-exact-original-column-functional-applicability',list(dict.fromkeys(refs)),dict(uids=[UID],sourceScopedApplicabilityAccepted=True,canonicalNumericChecksRemainFailed=True,installationApproved=False))
if __name__=='__main__':main()
